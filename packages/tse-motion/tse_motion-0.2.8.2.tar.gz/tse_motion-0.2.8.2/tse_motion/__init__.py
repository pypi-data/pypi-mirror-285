# from .artifact_rating import rate
from monai.networks.nets import DenseNet121
from pkg_resources import resource_filename
import torch
import pdb
from tse_motion.unet import UNet

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DenseNet121(spatial_dims=2, in_channels=1, out_channels=5)
model_path = resource_filename('tse_motion', 'weight.pth')
model.load_state_dict(torch.load(model_path, map_location=device))
model = model.to(device)
model.eval()

unet = UNet(in_channels=1, out_channels=2, init_features=32)
unet_path = resource_filename('tse_motion', 'unet-checkpoint.pth')
unet.load_state_dict(torch.load(unet_path, map_location=device))
unet = unet.to(device)
unet.eval()