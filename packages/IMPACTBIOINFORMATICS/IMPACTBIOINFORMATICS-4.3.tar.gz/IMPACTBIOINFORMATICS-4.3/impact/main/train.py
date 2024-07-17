import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import argparse
import pandas as pd
import numpy as np
from utils import *
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader,Dataset, Subset, random_split
from sklearn.model_selection import StratifiedKFold, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score
from sklearn.manifold import TSNE
import re
import warnings
import umap.umap_ as umap
from math import ceil, sqrt
from collections import Counter
from network import *
import random, pickle
from matplotlib import pyplot as plt

def train(input_file, metabolites_file, isize, check_feature_importance):
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    warnings.simplefilter('ignore')

    ## data has phylum information as last line, while img_data does not
    data = pd.read_csv(input_file, index_col=0 )
    data.index = data.index.str.replace('^X', '', regex=True)
    img_data = data.copy()
    img_data = img_data.drop(img_data.index[-1])
    img_data['y'] = img_data['y'].str.extract('(\d)').astype(int)
    def clean_index(index):
        return re.sub('[^a-zA-Z0-9]', '', index)
    data.index = data.index.map(clean_index).str.lower()
    img_data.index = img_data.index.map(clean_index).str.lower()
    
    species_values = [col.split('_')[2] if len(col.split('_')) > 1 else col for col in data.columns]
    
    y_phy = img_data['y']
    le = LabelEncoder()
    le = le.fit(y_phy) 
    y_phy = le.transform(y_phy)
    X_noy = data.drop('y',axis=1)
    dataset = PhylumDataset(X_noy, y_phy)
    y_img= le.transform(img_data['y'])
    y_img_np = y_img.reshape(-1)
    ### would be used to transfer to tensor following 
    
    
    X_img = img_data.drop('y', axis=1)
    X_img = X_img.apply(pd.to_numeric)
    # contains_str = X_img.applymap(lambda x: isinstance(x, str))
    # print(contains_str)
    # raise
    
    metabs = pd.read_csv(metabolites_file, index_col=0)
    transposed_df = metabs.T
    transposed_df.rename(columns=lambda x: re.sub(r'\W+', '', x), inplace=True)
    common_cols = set(transposed_df.columns) & set(species_values)
    current_df = transposed_df[list(common_cols)]
    missing_cols = set(X_img.columns) - set(current_df.columns) 
    for col in missing_cols:
        current_df[col] = 0
    current_df= current_df[X_img.columns]
    combined_df = pd.concat([current_df,X_img])
    isize=isize
    reducer_tsne = TSNE(n_components=2,metric="braycurtis", n_jobs=32,perplexity = 50, early_exaggeration=20, learning_rate=100)
    it = ImageTransformer(pixels=(isize,isize), feature_extractor= reducer_tsne )
    it.fit(combined_df, y=y_img, plot=False)
    with open('img_trans.pkl', 'wb') as f:
        pickle.dump(it, f)
    X_img_transformed= it.transform(X_img)[:, :, :, 0] 
    ## rgb format is useless since it just copies the single channel 3 times
    

    preprocess = transforms.Compose([
        transforms.ToTensor()
    ])

    #Filters, Kernel Size, Stride
    resblocks_params = [[16, 3, 1], [32, 3, 2]]
    big_acc = []
    X_full_img_tensor = torch.stack([preprocess(img) for img in X_img_transformed]).to(device).float()
    y_img  = torch.from_numpy(y_img_np)
    for rep in range(5):
        skf = StratifiedKFold(n_splits=5, random_state=random.randint(1,1000), shuffle=True)
        for train_temp_indices, test_indices in skf.split(X_img_transformed, y_img):
            train_indices, valid_indices = train_test_split(train_temp_indices, test_size=0.25, random_state=random.randint(1,1000), stratify=y_img[train_temp_indices])

            X_train = X_full_img_tensor[train_indices]
            y_train = y_img [train_indices]
            train_dataset = TensorDataset(X_train, y_train)

            X_valid = X_full_img_tensor[valid_indices]
            y_valid = y_img [valid_indices]
            valid_dataset = TensorDataset(X_valid, y_valid)

            X_test = X_full_img_tensor[test_indices]
            y_test = y_img [test_indices]
            test_dataset = TensorDataset(X_test, y_test)

            train_dataloader_img = DataLoader(train_dataset, batch_size=32, shuffle=True)
            valid_dataloader_img= DataLoader(valid_dataset, batch_size=32, shuffle=True)

            fname = "model.pth"
            mod = ResClass(isize, resblocks_params)
            mod.to(device)
            criterion = nn.CrossEntropyLoss()

            opt_impact =   optim.Adam(mod.parameters(),  lr=0.00001, betas=(0.9, 0.999), eps=1e-08, weight_decay=0.0001)    
            results = train_best_image(mod,  device, criterion, opt_impact, train_dataloader_img , valid_dataloader_img, 1000,250,fname)
            
            impact = ResClass(isize, resblocks_params)
            impact.load_state_dict(torch.load(fname))
            results = collect_dlmetrics_bin(impact,device,X_test, y_test, fname)
            big_acc.append(results)
            
            if check_feature_importance:
                cm_method='EigenCAM'
                camfs = CAMFeatureSelector(
                    model=impact,
                    it=it,
                    cam_method=cm_method
                )
                y_img_tensor = torch.tensor(y_img)
                class_mean = camfs.calculate_class_activations(X_full_img_tensor, y_img_tensor, batch_size=128, flatten_method="mean")
                le_mapping = dict(zip(le.transform(le.classes_), le.classes_))
                fs_threshold = 0.2
                feat_mean = camfs.select_class_features(cams=class_mean, threshold=fs_threshold)
                _ = cam_image(X_full_img_tensor, y_img_tensor.detach().cpu().numpy(), class_mean, feat_mean, fs_threshold, le_mapping)
                plt.savefig("Saliency_multi180.png")
           