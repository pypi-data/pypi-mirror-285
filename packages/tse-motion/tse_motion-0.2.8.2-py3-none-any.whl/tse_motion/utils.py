import sys
import torch
import nibabel as nib
from torchvision.transforms import CenterCrop
from monai.networks.nets import DenseNet121
from pkg_resources import resource_filename
from monai.visualize import GradCAM, GradCAMpp
import pdb
import matplotlib.pyplot as plt
from monai.visualize import OcclusionSensitivity
from tqdm import tqdm
from tse_motion.__init__ import model, unet
import torchio as tio
import numpy as np

def rate(input_array, model=model, save_gradcam=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ratings = []
    cam = GradCAM(nn_module=model, target_layers="class_layers.relu")
    transform = CenterCrop((512, 512))
    if len(input_array.shape) > 2:
        imgs = torch.tensor(input_array).permute(-1, 0, 1).to(device).float()
        imgs = torch.stack([img/img.max() for img in imgs])
        
        for img in tqdm(imgs):
            ratings.append(model(transform(img).unsqueeze(0).unsqueeze(0)).softmax(dim=1).argmax().detach().cpu())
        rating = torch.stack(ratings).float().mean()
        if save_gradcam:
            grad_cam = cam(x=imgs.unsqueeze(1))
            return rating.item(), grad_cam.squeeze()
    
    else:
        imgs = torch.tensor(input_array/input_array.max()).float()
        rating = model(transform(imgs).unsqueeze(0).unsqueeze(0)).softmax(dim=1).argmax().detach().cpu()
        if save_gradcam:
            grad_cam = cam(x=imgs.unsqueeze(0).unsqueeze(0))
            return rating.item(), grad_cam.squeeze()
    
    return rating.item()

def segment(tse, unet=unet):
    predictions = []
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if len(tse.shape) > 2:
        height, width, _ = tse.shape
        subject_transform = CenterCrop((height, width))
        center_crop = tio.transforms.CropOrPad((512, 512, tse.shape[-1]))
        
        if isinstance(tse, (nib.Nifti1Image, nib.Nifti2Image)):
            tse = center_crop(tse)
            imgs = tse.get_fdata()
        elif isinstance(tse, np.ndarray):
            imgs = center_crop(np.expand_dims(tse, 0)).squeeze()

        imgs = torch.tensor((imgs/imgs.max())).permute(-1,0,1).to(device)
        for img in tqdm(imgs):
            
            prediction = unet(img.unsqueeze(0).unsqueeze(0).float())
            predictions.append(prediction)
        predictions = torch.stack(predictions)
        predictions = subject_transform(predictions.squeeze())
        return predictions.permute(1,2,3,0).detach().cpu()
    
    else:
        height, width, = tse.shape
        subject_transform = CenterCrop((height, width))
        center_crop = tio.transforms.CropOrPad((512, 512, 1))
        
        tse = center_crop(np.expand_dims(np.expand_dims(tse,0),-1)).squeeze()
        prediction = unet(torch.tensor(tse/tse.max()).unsqueeze(0).unsqueeze(0).float()).squeeze().detach().cpu()
        
        return prediction

def main():
    if len(sys.argv) < 2:
        print("Usage: rate-motion <path_to_nifti_file>")
        sys.exit(1)
    input_path = sys.argv[1]
    rating = rate(input_path)
    print(f'Input: {input_path} | Motion Rating: {rating}')

if __name__ == '__main__':
    main()
    
