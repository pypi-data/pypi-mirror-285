import numpy as np
import cv2
from matplotlib import pyplot as plt
def show_cam_on_image(img: np.ndarray,
                      mask: np.ndarray,
                      use_rgb: bool = False,
                      colormap: int = cv2.COLORMAP_JET,
                      image_weight: float = 0.3) -> np.ndarray:
    """ This function overlays the cam mask on the image as an heatmap.
    By default the heatmap is in BGR format.

    :param img: The base image in RGB or BGR format.
    :param mask: The cam mask.
    :param use_rgb: Whether to use an RGB or BGR heatmap, this should be set to True if 'img' is in RGB format.
    :param colormap: The OpenCV colormap to be used.
    :param image_weight: The final result is image_weight * img + (1-image_weight) * mask.
    :returns: The default image with the cam overlay.
    """
    
    img = np.where(img > 0, 1, img)
    
    img = 1.0 - img
    img = np.where(img > 1, 1, img )
    #print(img)
    rgb_img = np.dstack([img,img,img])
    heatmap = cv2.applyColorMap(np.uint8(255 * mask), colormap)
    if use_rgb:
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    heatmap = np.float32(heatmap) / 255
    alpha = np.where(mask > 0, 1, 0)
    heatmap = np.dstack([heatmap, alpha])
    print(np.max(img))

    if np.max(img) > 1:
        raise Exception(
            "The input image should np.float32 in the range [0, 1]")

    if image_weight < 0 or image_weight > 1:
        raise Exception(
            f"image_weight should be in the range [0, 1].\
                Got: {image_weight}")
    
    cam = (1 - image_weight) * heatmap + image_weight * np.dstack([rgb_img, np.ones(rgb_img.shape[:-1])])
    
    cam = cam / np.max(cam)
    return np.uint8(255 * cam)


def cam_image(X, y, cam, fs, threshold, le_mapping):
    fig, axs = plt.subplots(ncols=2, nrows=1, figsize=(14, 7),
                            constrained_layout=True)
    for cat in np.unique(y):
        row = cat // 4
        col = cat % 4
        cat_idx = np.where(y == cat)[0]
        X_cat = X[cat_idx,:,:,:].detach().mean(dim=0).cpu().numpy()
        cam_cat = cam[cat].copy()
        cam_cat[cam_cat <= threshold] = 0
        visualization = show_cam_on_image(
            np.transpose(X_cat, (1,2,0)),
            cam_cat,
            use_rgb=True
        )
        _ = axs[row, col].imshow(visualization)
        axs[row,col].text(0,0,le_mapping[cat],c="black",ha="left",va="top",weight="bold",size="x-large")
        axs[row,col].text(159,159,f"{fs[cat].shape[0]} Taxa",c="black",ha="right",va="bottom",weight="bold",size="large")
        axs[row,col].axis('off')
    return fig, axs