import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils import *
import argparse
import pandas as pd
import numpy as np
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




def predict(fname,input_file, isize):
    
    ### input_file should be a .csv file with no lables and phelym information 
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    warnings.simplefilter('ignore')
    resblocks_params = [[16, 3, 1], [32, 3, 2]]
    impact = ResClass(isize, resblocks_params)
    impact.load_state_dict(torch.load(fname))
    
    data = pd.read_csv(input_file, index_col=0 )
    data.index = data.index.str.replace('^X', '', regex=True)
    img_data = data
    def clean_index(index):
        return re.sub('[^a-zA-Z0-9]', '', index)
    img_data.index = img_data.index.map(clean_index).str.lower()
    
    species_values = [col.split('_')[2] if len(col.split('_')) > 1 else col for col in data.columns]
    
    with open('img_trans.pkl', 'rb') as f:
        it = pickle.load(f)
    X_img_transformed= it.transform(img_data)[:, :, :, 0] 
    test_tensor = torch.stack([preprocess(img) for img in X_img_transformed]).to(device).float()

    model_totest = impact
    model_totest.to(device)
    model_totest.eval()
    with torch.no_grad():
        test_tensor = test_tensor.to(device)
        outputs = model_totest(test_tensor)
        predicted_probs = F.softmax(outputs, dim=1).cpu().numpy()
        predicted_labels = np.argmax(predicted_probs, axis=1)
    return predict_labels
        