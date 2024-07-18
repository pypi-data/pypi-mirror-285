# Standard library imports
import os, sys, requests, ast, gc
from pathlib import Path
from time import time

# Third-party imports
import cv2
import matplotlib
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numba as nb
import numpy as np
import pandas as pd
import torch
import math
import tifffile
import json
from ultralytics import FastSAM
from ultralytics.models.fastsam import FastSAMPrompt
from tqdm import tqdm
from numba.extending import overload, register_jitable
from skimage.measure import regionprops
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from PyQt6.QtWidgets import QFileDialog, QApplication
from .segment_anything import sam_model_registry, SamAutomaticMaskGenerator

def get_filepath(directory='./',filter=None):
    app = QApplication(sys.argv)
    fname = QFileDialog.getOpenFileName(None, "Select file...", directory, filter=filter)
    print(f"filepath = '{fname[0]}'")
    return fname[0]


def get_filepaths(directory='./',filter=None):
    app = QApplication(sys.argv)
    fname = QFileDialog.getOpenFileNames(None, "Select file(s)...", directory, filter=filter)
    print(f'filepath = {fname[0]}'.replace(', ', ',\n'))
    return fname[0]


def get_directory_path(directory='./'):
    app = QApplication([])
    folder = QFileDialog.getExistingDirectory(None, "Select a folder...", directory)
    print(f'filepath = "{folder}"')
    return folder


def FastSAM_segmentation(image, device='cpu'):
    """
    This function takes an image with shape (w, h, c) and segments it using FastSAM. It 
    returns a numpy array of masks with shape (m, w, h) with m being the number of
    masks.
    """
    sam_checkpoint = Path(os.path.dirname(__file__)) / 'FastSAM.pt'
    if not sam_checkpoint.is_file():
        download_weights('fast')
    fast_sam = FastSAM(sam_checkpoint)
    results = fast_sam(
        source=image,
        device=device,
        retina_masks=True,  # imgsz=image.shape[0],
        imgsz=int(np.ceil(max(image.shape[0], image.shape[1]) / 32) * 32),
        conf=0.2,
        iou=0.9,
        verbose=False)
    prompt_process = FastSAMPrompt(image, results, device=device)
    masks = prompt_process.everything_prompt()[0].masks.data.cpu().numpy().astype('uint8')
    return masks


def SAM_segmentation(image,model_type='huge',device='gpu',PPS=64,min_mask_area=35,**kwargs):
    """
    This function takes an image with shape (w, h, c) and segments it using SAM. It 
    returns a numpy array of masks with shape (m, w, h) with m being the number of
    masks.

    Several parameters are important for the segmentation:
     - model_type: 'huge', 'large' or 'base', determines the image encoder used for the
       segmentation
     - device: 'gpu' or 'cpu', if a CUDA compatible GPU is available, it is usually much
       faster
     - PPS: integer, default 64, PPS means points per side and determines the number of 
       sampling points
     - min_mask_area: integer, default 35, determines the minimum area of masks kept by
       SAM
    """
    model_info = {'base': ['vit_b', 'sam_vit_b_01ec64.pth'],
                  'large': ['vit_l', 'sam_vit_l_0b3195.pth'],
                  'huge': ['vit_h', 'sam_vit_h_4b8939.pth']}
    sam_checkpoint = Path(os.path.dirname(__file__)) / model_info.get(model_type)[1]
    if not sam_checkpoint.is_file():
        download_weights(model_type)
    # set up model
    sam = sam_model_registry[model_info.get(model_type)[0]](checkpoint=sam_checkpoint).to(device=device)
    mask_generator = SamAutomaticMaskGenerator(sam, points_per_side=PPS, min_mask_region_area=min_mask_area,**kwargs)
    masks = mask_generator.generate(image)
    masks = np.stack([mask['segmentation'].astype(np.uint8) for mask in masks])
    if device in {'cuda', 'cuda:0'}:
        gc.collect()
        torch.cuda.empty_cache()
    return masks


def save_df_to_csv(df,filepath):
    df.attrs['filepath'] = Path(filepath).as_posix()
    attrs_keys = list(df.attrs.keys())
    attrs_keys.sort()
    with open(filepath, 'w', encoding='utf-8') as f:
        for key in attrs_keys:
            f.write(f"{key} : {df.attrs[key]}\n")
        df.to_csv(f, encoding='utf-8', header='true', index=False, lineterminator='\n')


def load_df_from_csv(filepath):
    metadatarows = 3
    df = pd.read_csv(filepath,skiprows=metadatarows)
    with open(filepath) as f:
        for n in range(metadatarows):
            line = f.readline().strip('\n')
            key, value = line.split(' : ')
            df.attrs[key] = value
    return df


def masks_to_2D(masks):
    weights = np.arange(1, masks.shape[0] + 1)[:, np.newaxis, np.newaxis]
    weighted_masks = masks * weights
    labels = np.sum(weighted_masks, axis=0)
    return labels


def plot_images(filepaths):
    n = len(filepaths)
    columns = min(n, 3)
    rows = n // 3 + int(n % 3 != 0)

    fig, axes = plt.subplots(rows, columns, figsize=(5 * columns, 5 * rows))
    if n > 1:
        axes = axes.flatten()
    else:
        axes = [axes]

    for ax, filepath in zip(axes, filepaths):
        img = mpimg.imread(filepath)
        ax.imshow(img, cmap='gray')
        ax.set_title(f"filepath = '{filepath}'", fontsize=8)
        ax.axis('off')

    if n > 3:
        for i in range(n, len(axes)):
            axes[i].axis('off')

    plt.tight_layout()
    plt.show()


def process_filepath(filepath):
    if type(filepath) == str:
        filepath = Path(filepath).absolute()

        if filepath.is_file():
            if filepath.suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}:
                list_of_images = [filepath.as_posix()]
            else:
                print('Error: File must be .png, .jpg, .jpeg, .tif or .tiff')
                return None
        elif filepath.is_dir():
            folder_content = [filepath / filename for filename in os.listdir(filepath)]
            list_of_images = [filename.as_posix() for filename in folder_content
                              if filename.suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}]
        else:
            print('Error: The string did not contain a path to a folder or an image.')

    elif type(filepath) == list:
        for filename in filepath:
            if not Path(filename).is_file():
                print(f'Error: Not all list entries are valid filenames. \nThe issue is: {Path(filename).as_posix()} \nINFO: Folder paths should be given as a string, not a list.')
                return None
        list_of_images = [Path(filename).absolute().as_posix() for filename in filepath
                          if Path(filename).suffix in {'.png', '.jpg', '.jpeg', '.tif', '.tiff'}]
    else:
        print('Unexpected error')
        return None

    return list_of_images

def process_filepath_all_files(filepath):
    if type(filepath) == str:
        filepath = Path(filepath)

        if filepath.is_file():
            list_of_images = [filepath.as_posix()]
        elif filepath.is_dir():
            folder_content = [filepath / filename for filename in os.listdir(filepath)]
            list_of_images = [filename.as_posix() for filename in folder_content]
        else:
            print('Error: The string did not contain a path to a folder or an image.')

    elif type(filepath) == list:
        for filename in filepath:
            if not Path(filename).is_file():
                print(f'Error: Not all list entries are valid filenames. \nThe issue is: {Path(filename).as_posix()} \nINFO: Folder paths should be given as a string, not a list.')
                return None
        list_of_images = [Path(filename).absolute().as_posix() for filename in filepath]
    else:
        print('Unexpected error')
        return None

    return list_of_images


def set_scaling(signal,scaling):
    """
    Given a signal and scaling, this function applies the scaling to the signal.
    The scaling argument must be given as a string that tells the scaling of 1 pixel,
    e.g. '2.5 nm', 5 mm', '2.7 µm' or '2.7 um'.
    """
    for axis in get_x_and_y_axes(signal):
        axis.scale_as_quantity = scaling


def convert_to_units(signal,units):
    """
    Given a signal and unit, this function applies the scaling to the signal. The units 
    argument must be given as a string that tells the unit of 1 pixel, e.g. 'nm', 'µm',
    or 'um'.
    """
    for axis in get_x_and_y_axes(signal):
        axis.convert_to_units(units)


def load_image_RGB(filepath):
    if Path(filepath).suffix in {'.tif', '.tiff'}:
        try:
            im = tifffile.imread(filepath)
        except ValueError:
            im = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

        if im.ndim == 3 and im.shape[-1] in {3, 4}:
            im = im[:, :, 0]
        elif im.ndim == 3:
            im = np.mean(im, axis=-1)

        im_shift_to_zero = im - im.min()
        im_max = im_shift_to_zero.max()
        im_normalized = im_shift_to_zero / im_max
        im_max_255 = im_normalized * 255
        im_8bit = im_max_255.astype('uint8')
        im_RGB = np.dstack([im_8bit] * 3)
    elif Path(filepath).suffix in {'.png', '.jpg', '.jpeg', }:
        im = cv2.imread(filepath)
        im_RGB = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    return im_RGB


def make_randomized_cmap(cmap='viridis', seed=42, randomize=True):
    '''Genarates randomized colormap with the first color being black'''
    cmap = matplotlib.colormaps[cmap]
    cmap_colors = cmap(np.linspace(0, 1, 2000))
    black_color = np.array([0, 0, 0, 1])
    cmap_rest_colors = cmap_colors[1:, :]
    if randomize:
        np.random.seed(seed)
        np.random.shuffle(cmap_rest_colors)
    randomized_cmap = matplotlib.colors.ListedColormap(np.vstack((np.expand_dims(black_color, 0), cmap_rest_colors)))
    return randomized_cmap


def is_scaled(signal):
    scaled = True
    for axis in get_x_and_y_axes(signal):
        if format(axis.scale_as_quantity,'~') in ['1.0','1.0 ','1.0 px']:
            scaled = False
    return scaled


def get_scaling(signal):
    axes = get_x_and_y_axes(signal)
    return format(axes[0].scale_as_quantity,'~')
    

def get_x_and_y_axes(signal):
    if str(signal).split(',')[0][1:] == 'Signal2D':
        axes = signal.axes_manager.signal_axes
    elif str(signal).split(',')[0][1:] in ['BaseSignal','Signal1D']:
        axes = signal.axes_manager.navigation_axes
    else:
        raise ValueError("The signal argument doesn't seem to be Signal2D, Signal1D or BaseSignal.")
    return axes


def preprocess(image, crop_and_enlarge=False, invert=False, double=False):
    """
    This function takes in an image in the form of a HyperSpy signal, converts it to an 
    RGB image numpy array, and it can also crop it into four enlarged sections and/or
    invert the image. It return a list of RGB image arrays ready for segmentation.
    """
    image = PNGize(image.data)
    if crop_and_enlarge:
        images = crop_and_enlarge_image(image)
    else:
        images = [image]
    if invert:
        images = [invert_image(im) for im in images]
        if double:
            images += [invert_image(im) for im in images]
    else:
        if double:
            print("Ignoring double=True, since it requires inversion to be True.")
    return images


def PNGize(image):
    """
    PNGize takes an image array as input and returns the corresponding PNG (RGB) version.
    If the input is a 1 channel grey-scale image, it return a 3 channels grey image.
    """
    if image.ndim == 2:
        image_normalized = np.round((image-image.min())/(image.max()-image.min())*255).astype('uint8')
        image = np.dstack([image_normalized]*3)
    return image


def invert_image(image):
    return cv2.bitwise_not(image)


def crop_and_enlarge_image(image):
    h = image.shape[0]
    w = image.shape[1]
    
    nw = np.kron(image[:int(h*0.625), :int(w*0.625), :], np.ones((2, 2, 1))).astype('uint8')
    ne = np.kron(image[:int(h*0.625), math.ceil(w*0.375):, :], np.ones((2, 2, 1))).astype('uint8')
    sw = np.kron(image[math.ceil(h*0.375):, :int(w*0.625), :], np.ones((2, 2, 1))).astype('uint8')
    se = np.kron(image[math.ceil(h*0.375):, math.ceil(w*0.375):, :], np.ones((2, 2, 1))).astype('uint8')
    
    return [nw, ne, sw, se]


def rearrange_masks(masks_from_four_crops,original_image_shape,verbose=False):
    h = original_image_shape[0]
    w = original_image_shape[1]

    nw,ne,sw,se = masks_from_four_crops
    total_masks = len(nw)+len(ne)+len(sw)+len(se)
    rearranged_masks = np.zeros((total_masks, h*2, w*2)).astype('uint8')
    rearranged_masks[:len(nw),:nw.shape[1],:nw.shape[2]] = nw
    rearranged_masks[len(nw):len(nw)+len(ne),:ne.shape[1],-ne.shape[2]:] = ne
    rearranged_masks[len(nw)+len(ne):len(nw)+len(ne)+len(sw),-sw.shape[1]:,:sw.shape[2]] = sw
    rearranged_masks[len(nw)+len(ne)+len(sw):,-se.shape[1]:,-se.shape[2]:] = se
    
    return rearranged_masks


def bb_iou(boxA, boxB):
    xA = np.maximum(boxA[0], boxB[0])
    yA = np.maximum(boxA[1], boxB[1])
    xB = np.minimum(boxA[2], boxB[2])
    yB = np.minimum(boxA[3], boxB[3])

    interArea = np.maximum(0, xB - xA) * np.maximum(0, yB - yA)

    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    iou = interArea / (boxAArea + boxBArea - interArea)
    return iou


def split_list(to_keep, split_conditions):
    start = 0
    result = []
    for split in split_conditions:
        while split not in to_keep:
            split += 1
        idx = to_keep.index(split)
        result.append(to_keep[start:idx])
        start = idx
    result.append(to_keep[start:])
    return result

def remove_overlapping_masks(masks, iou_threshold=0.9, verbose=False):
    # This will store the indices of the bboxes to keep
    to_keep = []
    array_of_bboxes = np.array([list(regionprops(mask)[0]['bbox']) for mask in masks]) # if mask.sum()>0
    for i, boxA in enumerate(array_of_bboxes):
        if verbose:
            print(f'Mask {i + 1}/{array_of_bboxes.shape[0]}', sep=',',
              end='\r' if i + 1 < array_of_bboxes.shape[0] else '\n', flush=True)
        keep = True
        for j, boxB in enumerate(array_of_bboxes):
            if i != j:
                iou = bb_iou(boxA, boxB)
                if iou >= iou_threshold:
                    if i not in to_keep and j not in to_keep:
                        to_keep.append(i)
                    keep = False
                    break
        if keep:
            to_keep.append(i)

    unique_masks = masks[to_keep]

    print(f'{len(masks) - len(unique_masks)} masks have been removed because they were indentical.')
    return unique_masks

def bin_masks(masks):
    if masks.shape[1] % 2 or masks.shape[2] % 2:
        raise ValueError("The x and y dimensions of the array must be even for 2x2 binning.")

    # If one of four pixels in a 2x2 pixel group is True, the binned will also be True
    binned_masks = ((masks[:,::2,::2]+masks[:,1::2,::2]+masks[:,::2,1::2]+masks[:,1::2,1::2])>0).astype('uint8')
    return binned_masks


def stitch_crops_together(masks_from_four_crops, original_image_shape, iou_threshold=0.8, verbose=False):
    print('Rearranging masks.')
    rearranged_masks = rearrange_masks(masks_from_four_crops,original_image_shape,verbose=verbose)
    
    print('Removing masks with identical bounding boxes.')
    unique_masks = remove_overlapping_masks(rearranged_masks, iou_threshold=iou_threshold, verbose=verbose)

    binned_masks = bin_masks(unique_masks)
    return binned_masks


def format_time(elapsed_time):
    minutes, seconds = divmod(elapsed_time, 60)
    time_string = ""
    if minutes >= 1:
        minute_label = "minute" if minutes == 1 else "minutes"
        time_string += f"{int(minutes)} {minute_label} and "
    second_label = "second" if seconds == 1 else "seconds"
    time_string += f"{round(seconds)} {second_label}"
    return time_string


def download_weights(model,noconfirm=False, app=False):
    model_checkpoints = {
        'huge': ['https://osf.io/download/65b0d08399d01005546266f2/', 'sam_vit_h_4b8939.pth', '2.5 GB'],
        'large': ['https://osf.io/download/65b0d0624aa63c05c2df18f4/', 'sam_vit_l_0b3195.pth', '1.2 GB'],
        'base': ['https://osf.io/download/k6ce8/', 'sam_vit_b_01ec64.pth', '366 MB'],
        'fast': ['https://osf.io/download/p7kmb/', 'FastSAM.pt', '144 MB']
    }
    if not noconfirm:
        ask_for_download = input((
            f"SAM weights were not found. \n"
            f"This is probably because it is the first time running NP-SAM \n"
            f"with this option. Do you want to download the {model} weights "
            f"file (size: {model_checkpoints.get(model)[2]})? Y/n"
        ))
    else:
        ask_for_download = ''
        
    if ask_for_download.lower() in ['y','yes',''] or noconfirm:
        directory = os.path.dirname(__file__)

        if not os.path.exists(directory):
            print('NP-SAM is not correctly installed')
            return
    
        file_path = os.path.join(directory, model_checkpoints.get(model)[1])
        try:
            response = requests.get(model_checkpoints.get(model)[0], stream=True)
            response.raise_for_status()
    
            total_length = int(response.headers.get('content-length', 0))
    
            if app:
                with open(file_path, 'wb') as file, tqdm(
                        desc=model_checkpoints.get(model)[1], total=total_length, unit='iB', unit_scale=True,
                        unit_divisor=1024, file=sys.stdout, colour='GREEN', ncols=0,
                        smoothing=0.1) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
            else:
                with open(file_path, 'wb') as file, tqdm(
                        desc=model_checkpoints.get(model)[1], total=total_length, unit='iB', unit_scale=True,
                        unit_divisor=1024, file=sys.stdout, colour='GREEN', dynamic_ncols=True,
                        smoothing=0.1) as bar:
                    for data in response.iter_content(chunk_size=1024):
                        size = file.write(data)
                        bar.update(size)
            print(f"File downloaded successfully: {file_path}")
        except requests.RequestException as e:
            print(f"Failed to download {model_checkpoints.get(model)[1]}: {e}")
    else:
        print("Download stopped.")


def choose_device():
    if torch.cuda.is_available() and  torch.cuda.get_device_properties(0).total_memory / 1024 ** 3 > 5:
        device = 'cuda'
    else:
        device = 'cpu'
    return device


def choose_SAM_model(SAM_model, device, verbose = True):
    model_mapping = {'a': 'auto',
                     'f': 'fast', 'fastsam': 'fast',
                     'b': 'base',
                     'l': 'large',
                     'h': 'huge'
                     }
    SAM_model = SAM_model.lower()
    SAM_model = model_mapping.get(SAM_model, SAM_model)

    if SAM_model == 'auto':
        if device == 'cpu':
            model = 'fast'
        elif device == 'cuda':
            model = 'base'
            if torch.cuda.get_device_properties(0).total_memory / 1024 ** 3 > 7:
                model = 'huge'
            elif torch.cuda.get_device_properties(0).total_memory / 1024 ** 3 > 5:
                model = 'large'
        if verbose:
            print(f'The {model} SAM model was chosen.\n')
        return model
    elif SAM_model in {'fast', 'base', 'large', 'huge'}:
        model = SAM_model
        return model
    else:
        print("Invalid input. Valid inputs are 'a' for auto, 'h' for huge, 'l' for large, 'b' for base and 'f' for fast.")
        return None


@overload(np.all)
def np_all(x, axis=None):
    # ndarray.all with axis arguments for 2D arrays.
    @register_jitable
    def _np_all_axis0(arr):
        out = np.logical_and(arr[0], arr[1])
        for v in iter(arr[2:]):
            for idx, v_2 in enumerate(v):
                out[idx] = np.logical_and(v_2, out[idx])
        return out

    @register_jitable
    def _np_all_axis1(arr):
        out = np.logical_and(arr[:, 0], arr[:, 1])
        for idx, v in enumerate(arr[:, 2:]):
            for v_2 in iter(v):
                out[idx] = np.logical_and(v_2, out[idx])
        return out

    def _np_all_impl(x, axis=None):
        if axis == 0:
            return _np_all_axis0(x)
        else:
            return _np_all_axis1(x)

    return _np_all_impl


@nb.njit(cache=True)
def nb_unique_caller(input_data):
    '''Numba compatible solution to numpy.unique() function'''

    data = input_data.copy()
    if len(data) == 0:
        return None
        
    for i in range(data.shape[1] - 1, -1, -1):
        sorter = data[:, i].argsort(kind="mergesort")
        # mergesort to keep associations
        data = data[sorter]

    idx = [0]

    bool_idx = ~np.all((data[:-1] == data[1:]), axis=1)
    additional_uniques = np.nonzero(bool_idx)[0] + 1

    idx = np.append(idx, additional_uniques)

    return data[idx]
