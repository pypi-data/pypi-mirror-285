import matplotlib.pyplot as plt
import torch
import nibabel as nib
import numpy as np
from tqdm import tqdm
import random
import glob
from scipy.linalg import norm
import pdb
from scipy.fft import fftn, ifftn, fftshift
import cv2
from scipy.ndimage import affine_transform
import sys

def rotateImg(image, angle, trans_x, trans_y):
    image_center = (image.shape[1] / 2, image.shape[0] / 2)
    rotation_matrix = cv2.getRotationMatrix2D(image_center, angle, 1)
    rotation_matrix[0, 2] += trans_x
    rotation_matrix[1, 2] += trans_y
    transformed_image = cv2.warpAffine(image, rotation_matrix, (image.shape[1], image.shape[0]))

    return transformed_image

def convert_to_k_space(mri_data):
    # Assuming mri_data is a 3D numpy array representing the MRI volume
    k = np.zeros_like(mri_data).astype('complex128')
    
    # Fourier Transform the MRI data
    for idx in range(mri_data.shape[-1]):
        k[:,:,idx] = fftshift(fftn(mri_data[:,:,idx]))

    return k

def convert_to_k_space_2d(mri_data):
    # Assuming mri_data is a 3D numpy array representing the MRI volume
    k = np.zeros_like(mri_data).astype('complex128')
    
    # Fourier Transform the MRI data
    k = fftshift(fftn(mri_data))

    return k

def convert_to_image_domain(k_space_data):
    # Adjust for voxel size and dwell time
    img = np.zeros_like(k_space_data).astype('float64')
    for idx in range(k_space_data.shape[-1]):
        img[:,:,idx] = np.abs(ifftn(fftshift(k_space_data[:,:,idx])))
    # Shift zero frequency components back to the corners

    return img  # Take the absolute value to get the magnitude

def convert_to_image_domain_2d(k_space_data):
    # Adjust for voxel size and dwell time
    img = np.zeros_like(k_space_data).astype('float64')
    img = np.abs(ifftn(fftshift(k_space_data)))

    return img  # Take the absolute value to get the magnitude

def kcatImg_segs(img_segments):
    segments = [[0, 43], [43, 87], [87, 131], [131, 175], [175, 217], [217, 239], [239, 279], [279, 323], [323, 367], [367, 411], [411, 455], [455, 512]]

    k_segs = [convert_to_k_space_2d(segment) for segment in img_segments]
    k_segs_clean = []
    for idx, seg in enumerate(k_segs):
        k_segs_temp = np.zeros_like(k_segs[idx])
        k_segs_temp[:, segments[idx][0]:segments[idx][1]] = k_segs[idx][:, segments[idx][0]:segments[idx][1]]
        k_segs_clean.append(k_segs_temp)
    kcat = np.sum(np.array(k_segs_clean),0)
    img = convert_to_image_domain_2d(kcat)
    return img
        

def get_rotation_matrix(x=0, y=0, z=0):
    """ Computes the rotation matrix.
    
    Parameters
    ----------
    x : float
        Rotation in the x (first) dimension in degrees
    y : float
        Rotation in the y (second) dimension in degrees
    z : float
        Rotation in the z (third) dimension in degrees
    
    Returns
    -------
    rot_mat : numpy ndarray
        Numpy array of shape 4 x 4
    """
    
    x = np.deg2rad(x)
    y = np.deg2rad(y)
    z = np.deg2rad(z)
    
    rot_roll = np.array([
        [1, 0, 0, 0],
        [0, np.cos(x), -np.sin(x), 0],
        [0, np.sin(x), np.cos(x), 0],
        [0, 0, 0, 1]
    ])

    rot_pitch = np.array([
        [np.cos(y), 0, np.sin(y), 0],
        [0, 1, 0, 0],
        [-np.sin(y), 0, np.cos(y), 0],
        [0, 0, 0, 1]
    ])

    rot_yaw = np.array([
        [np.cos(z), -np.sin(z), 0, 0],
        [np.sin(z), np.cos(z), 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])

    rot_mat = rot_roll @ rot_pitch @ rot_yaw
    return rot_mat

def get_translation_matrix(x=0, y=0, z=0):
    """ Computes the translation matrix.
    
    Parameters
    ----------
    x : float
        Translation in the x (first) dimension in voxels
    y : float
        Rotation in the y (second) dimension in voxels
    z : float
        Rotation in the z (third) dimension in voxels
    
    Returns
    -------
    trans_mat : numpy ndarray
        Numpy array of shape 4 x 4
    """
    
    trans_mat = np.eye(4)
    trans_mat[:, -1] = [x, y, z, 1]
    return trans_mat

def resample_image(image, trans_mat, rot_mat):
    """ Resamples an image given a translation and rotation matrix.
    
    Parameters
    ----------
    image : numpy array
        A 3D numpy array with image data
    trans_mat : numpy array
        A numpy array of shape 4 x 4
    rot_mat : numpy array
        A numpy array of shape 4 x 4
    
    Returns
    -------
    image_reg : numpy array
        A transformed 3D numpy array
    """
    
    # We need to rotate around the origin, not (0, 0), so
    # add a "center" translation
    center = np.eye(4)
    center[:3, -1] = np.array(image.shape) // 2 - 0.5
    A = center @ trans_mat @ rot_mat @ np.linalg.inv(center)
    
    # affine_transform does "pull" resampling by default, so
    # we need the inverse of A
    image_corr = affine_transform(image, matrix=np.linalg.inv(A))
    
    return image_corr

def calculate_frobenius_norm(reference_img, artifact_img):
    # Compute the difference image
    difference_img = artifact_img - reference_img
    
    # Calculate the Frobenius norm
    frobenius_norm = norm(difference_img[0], 'fro')
    
    return frobenius_norm

def split_matrix_with_zeros(matrix, times, row=True):
    num_rows, num_cols = matrix.shape
    segment_size = num_cols // times

    split_matrices = []
    for i in range(times):
        split_matrix = np.zeros_like(matrix)  # Create a zero-filled matrix
        start_col = i * segment_size
        end_col = min((i + 1) * segment_size, num_cols)
        if i == times - 1:
            if row:
                split_matrix[start_col:, :] = matrix[start_col:, :]
            else:
                split_matrix[:, start_col:] = matrix[:, start_col:]
        else:
            if row:
                split_matrix[start_col:end_col, :] = matrix[start_col:end_col, :]  # Replace columns with values from the original matrix
            else:
                split_matrix[:, start_col:end_col] = matrix[:, start_col:end_col]
        split_matrices.append(split_matrix)

    return split_matrices

def split_matrix(matrix, times):
    num_columns = len(matrix[0])
    split_size = num_columns // times

    # Splitting the matrix column-wise
    split_matrices = []
    for i in range(times):
        start_col = i * split_size
        end_col = start_col + split_size
        if i == times - 1:
            split_matrices.append(np.array([row[start_col:] for row in matrix]))
        else:
            split_matrices.append(np.array([row[start_col:end_col] for row in matrix]))

    return split_matrices

def stack_matrices(matrix1, matrix2):
    return np.hstack((matrix1, matrix2))

def piece_ksegs(matrix):
    mats = matrix[0]
    for mat in matrix[1:]:
        mats = stack_matrices(mats, mat)
    return mats

def random_rotation(img, angle, x_trans, y_trans):
    angle = random.sample(range(-angle, angle), 1)[0]
    trans_x = random.sample(range(-x_trans, x_trans), 1)[0]
    trans_y = random.sample(range(-y_trans, y_trans), 1)[0]

    rotated_img = rotateImg(img, angle, trans_x, trans_y)
    return rotated_img, [angle, trans_x, trans_y]

def random_2d_motion(k_img, img, times, angle, x_trans, y_trans):
    seg_idx = random.choices(range(0, 11), k=times)
    segs = 12
    rotated_imgs = []
    angles = []
    for _ in range(times):
        rotated_img, param = random_rotation(img, angle, x_trans, y_trans)
        rotated_imgs.append(rotated_img)
        angles.append(param)
    k_segments = split_matrix_with_zeros(k_img, segs)
    for idx, rotated_img in enumerate(rotated_imgs):
        k_segments[seg_idx[idx]] = split_matrix_with_zeros(convert_to_k_space_2d(rotated_img), segs)[seg_idx[idx]]

    k_img_rotated = np.sum(k_segments, 0)
    simulated = convert_to_image_domain_2d(k_img_rotated)
    severity = np.max(seg_idx)
    return simulated, severity + 1, param

def process_tse_images(tse_path, num_seg=random.sample(range(1, 10), 1)[0], angle=3, x_trans=3, y_trans=3):
    
    nii = nib.load(tse_path)
    img = nii.get_fdata().squeeze()

    simulateds = []
    for slice_idx in tqdm(range(img.shape[-1])):
        k_img = convert_to_k_space_2d(img[:, :, slice_idx])
        simulated, segment, param = random_2d_motion(k_img.squeeze(), img[:, :, slice_idx], num_seg, angle, x_trans, y_trans)
        X = torch.tensor(img[:, :, slice_idx] / img[:, :, slice_idx].max()).squeeze()
        Y = torch.tensor(simulated / simulated.max()).squeeze()
        X = X.unsqueeze(0).unsqueeze(0).repeat(1, 3, 1, 1).float()
        Y = Y.unsqueeze(0).unsqueeze(0).repeat(1, 3, 1, 1).float()

        simulateds.append(simulated)

    simulated = np.array(simulateds).transpose(1, 2, 0)
    return img, simulated

def main():
    if len(sys.argv) < 2:
        print("Usage: gen-motion <path_to_nifti_file> <output_file_name>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    input_nii = nib.load(input_path)
    _, motion = process_tse_images(input_path)
    motion_nii = nib.Nifti1Image(motion, input_nii.affine, header=input_nii.header)
    motion_nii.to_filename(output_path)
    