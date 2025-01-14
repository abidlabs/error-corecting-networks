from __future__ import print_function

import h5py
import os
import numpy as np
import cv2
import argparse

# Current python dir path
dir_path = os.path.dirname(os.path.realpath('__file__'))

parser = argparse.ArgumentParser()
parser.add_argument("--path", required=True, help="path of leftImg8bit folder.")
parser.add_argument("--gtpath", required=True, help="path of gtFine folder.")
parser.add_argument("--num", required=True, help="number of coarse images to consider.", type=int)

args = parser.parse_args()
img_folder_path = args.path
gt_folder_path = args.gtpath
num_images = args.num


# Reads paths from cityscape data.
def get_data(mode):
    if mode == 'train_extra' or mode == 'train':            
        x_paths = []
        y_paths = []
        tmp_img_folder_path = os.path.join(img_folder_path, mode)
        tmp_gt_folder_path = os.path.join(gt_folder_path, mode)
        file_count = 0
        
        # os.walk helps to find all files in directory.
        for (path, dirname, files) in os.walk(tmp_img_folder_path):
            for filename in sorted(files):
                x_paths.append(os.path.join(path, filename))
                file_count += 1
                if file_count >= num_images:
                    break
            if file_count >= num_images and mode == 'train_extra':
                break

        # Find ground_truth file paths with x_paths.
        idx = len(tmp_img_folder_path)
        for x_path in x_paths:
            y_paths.append(tmp_gt_folder_path + x_path[idx:-15] + 'gtCoarse_labelIds.png')

        return x_paths, y_paths
    else:
        print("Please call get_data function with arg 'train_extra'.")


# Make h5 group and write data
def write_data(h5py_file, mode, x_paths, y_paths):
    num_data = len(x_paths)

    # h5py special data type for image.
    uint8_dt = h5py.special_dtype(vlen=np.dtype('uint8'))

    # Make group and data set.
    group = h5py_file.create_group(mode)
    x_dset = group.create_dataset('x', shape=(num_data, ), dtype=uint8_dt)
    y_dset = group.create_dataset('y', shape=(num_data, ), dtype=uint8_dt)

    for i in range(num_data):
        # Read image and resize
        x_img = cv2.imread(x_paths[i])
        x_img = cv2.resize(x_img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_CUBIC)
        x_img = cv2.cvtColor(x_img, cv2.COLOR_BGR2RGB)
        
        # print(y_paths[i])
        y_img = cv2.imread(y_paths[i])
        y_img = cv2.resize(y_img, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_NEAREST)
        y_img = y_img[:, :, 0]

        x_dset[i] = x_img.flatten()
        y_dset[i] = y_img.flatten()


# Make h5 file.
def make_h5py():
    x_train_paths, y_train_paths = get_data('train_extra')
    x_train_coarse_paths, y_train_coarse_paths = get_data('train')
    print(x_train_coarse_paths)

    # Make h5py file with write option.
    h5py_file = h5py.File(os.path.join(dir_path, 'data-coarse.h5'), 'w')

    # Write data
    print('Parsing train datas...')
    write_data(h5py_file, 'train_extra', x_train_paths, y_train_paths)
    print('Finish.')
    
    print('Parsing train_coarse datas...')
    write_data(h5py_file, 'train', x_train_coarse_paths, y_train_coarse_paths)
    print('Finish.')
    

make_h5py()
