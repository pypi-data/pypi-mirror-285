# Installation
```
pip install tse-motion
```
# CLI

```
rate-motion <path_to_nifti_file>
gen-motion <path_to_nifti_file> <output_file_name>

```
# Python
```python
from tse_rating.utils import rate, segment
img = nib.load('tse.nii.gz').get_fdata()
score = rate_motion_artifact(img)

score, grad_cam = rate_motion_artifact(img, save_gradcam=True)

masks = segment(nib.load('tse.nii.gz')) # returns a [2, W, H, Z] 4-dimensional tensor with the first and the second channel containing the left and the right hippocampus
mask = segment(nib.load('tse.nii.gz').get_fdata()[:,:,10]) # returns a [2, W, H] 3-dimensional tensor with the first and the second channel containing the left and the right hippocampus

```
