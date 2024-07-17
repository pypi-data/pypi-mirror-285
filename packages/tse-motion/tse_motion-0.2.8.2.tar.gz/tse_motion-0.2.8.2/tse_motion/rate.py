import sys
import torch
import nibabel as nib
from torchvision.transforms import CenterCrop
from monai.networks.nets import DenseNet121
from pkg_resources import resource_filename

def main():
    if len(sys.argv) < 2:
        print("Usage: rate-motion <path_to_nifti_file>")
        sys.exit(1)
    input_path = sys.argv[1]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=5)
    model_path = resource_filename('tse_motion', 'weight.pth')
    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()

    transform = CenterCrop((512, 512))
    imgs = torch.tensor(nib.load(input_path).get_fdata()).permute(-1, 0, 1).to(device).float()
    imgs = torch.stack([img/img.max() for img in imgs])
    ratings = []
    for img in imgs:
        ratings.append(model(transform(img).unsqueeze(0).unsqueeze(0)).softmax(dim=1).argmax().detach().cpu())
    rating = torch.stack(ratings).float().mean().item()
    
    print(f'Input: {input_path} | Motion Rating: {rating}')

if __name__ == '__main__':
    main()
