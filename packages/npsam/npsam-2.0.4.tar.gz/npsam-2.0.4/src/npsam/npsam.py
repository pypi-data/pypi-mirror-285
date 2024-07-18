# Standard library imports
import os, sys, warnings, platform, subprocess
from pathlib import Path
from time import time

# Third-party imports

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import hyperspy.api as hs
import skimage
import math
import scipy
import tifffile
import torch
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.widgets import Button, RadioButtons, RangeSlider, Slider
from skimage.measure import label, regionprops_table
from datetime import datetime
from PIL import Image
from rsciio import emd, digitalmicrograph, tia
from copy import copy
from collections.abc import MutableSequence
from .utils import *


class NPSAMImage:
    """
    This class handles a single image and is meant as a base for the NPSAM class that
    handles more images, but NPSAMImage can also be used on its own.
    
    It loads the image upon initialization and offers methods for segmentation, 
    characterization and filtering of the resulting masks. It can also make an overview 
    .pdf file showing the segmentation and histograms of selected characteristics. 
    Finally, the segmented masks and characteristcs can be exported in different ways 
    (image files, numpy arrays and .csv files).
    """

    def __init__(self, filepath=None, select_image=None, segmentation_filepath=None):
        """
        Takes a given or prompted filepath and loads the file. Also loads any previous
        segmentation if saved to file.
        """
        if filepath is None:
            filepath = get_filepath()
        self.filepath = filepath
        self.load_image(filepath, select_image=select_image)
        self.seg = None
        self.cha = None
        try:
            self.load_segmentation(filepath=segmentation_filepath)
        except:
            pass


    def __repr__(self):
        """Returns the image name, masks segmented and how many passed the filtering."""
        # return f"NPSAMImage('{self.filepath}')"
        return self.__str__()


    def __str__(self):
        """Returns the image name, masks segmented and how many passed the filtering."""
        string = f"<NPSAM: {self.img.metadata.General.title}"
        if self.seg:
            string += f", {len(self.seg)} masks"
        if not self.cha is None:
            if self.seg.metadata.Filtering.Conditions is None:
                string += ", unfiltered"
            else:
                string += f", {self.cha['passed_filter'].sum()} passed filter"
        string += ">"
        return string


    def load_image(self, filepath, select_image=None):
        """
        This function loads either an image file (.png, .jpg, .tif, etc.) or an electron
        microscopy file (.emd, .bcf, .dm4, etc.). It returns the loaded image as a
        HyperSpy signal.
        """
        filepath = Path(filepath)

        # Hyperspy can't load all three channels in regular images, so we load them 
        # without
        if filepath.suffix in [".png", ".jpg", ".jpeg", ".gif"]:
            # Load image file as numpy array
            image_RGB = load_image_RGB(filepath)
            # Create hyperspy signal from image numpy array
            image = hs.signals.Signal1D(image_RGB)
        else:
            # Lazy loading doesn't seem to work with tif files
            if filepath.suffix in [".tif", ".tiff"]:
                lazy = False
            else:
                lazy = True
            
            if filepath.suffix in [".emd", ".bcf"]:
                # Apparently only works for .emd and .bcf. Throws error for .dm4
                signal = hs.load(filepath, lazy=lazy, select_type="images")
            else:
                signal = hs.load(filepath, lazy=lazy)

            # If there is more than one image in the file, we have to choose
            if isinstance(signal, list):

                # Check for empty list
                if len(signal) == 0:
                    print(f"No images found in {filepath}")
                    return

                # We take selection input until an image is found
                image_found = False
                while image_found == False:
                    if select_image is None:
                        print(f"Several signals are present in {filepath.name}:\n")
                        # Print name of the images in the file
                        for subsignal in signal:
                            print(str(subsignal))
                        select_image = input((
                            "\nPlease choose the image of interest by providing an "
                            "index or the image title:"
                        ))

                    try:
                        # If selection is an index
                        select_image = int(select_image)
                        image = signal[select_image]
                        image_found = True
                    except:
                        # If selection is not an index we check the title of the signal
                        for subsignal in signal:
                            if select_image == subsignal.metadata.General.title:
                                image = subsignal
                                image_found = True
                        if not image_found:
                            print("Image of interest not found.")
                            select_image = None
            else:
                image = signal
            if lazy:
                image.compute(show_progressbar=False)
            image = image.transpose()

        image.metadata.General.filepath = filepath.as_posix()
        image.metadata.General.title = filepath.name
        if not is_scaled(image):
            set_scaling(image, "1 px")
        self.img = image
        self.name = filepath.name


    def set_scaling(self, scaling, verbose=True):
        """
        Sets the scaling of the image. Scaling must be given as a Pint compatible
        quantity, e.g. '1 nm', '3.5 µm', '0.3 um' or '4 Å'.
        """
        set_scaling(self.img, scaling)
        try:
            set_scaling(self.seg, scaling)
            self._set_scaling_cha(scaling)
            if not self.seg.metadata.Filtering.Conditions is None and verbose:
                print("Scaling set, but area filtering conditions not updated.")
                print("Consider rerunning the filter function.")
        except:
            pass
            
    def _set_scaling_cha(self, scaling):
        length_per_pixel = float(get_scaling(self.seg).split()[0])
        unit = get_scaling(self.seg).split()[1]
        self.cha["scaling [unit/px]"] = length_per_pixel
        self.cha["unit"] = unit

        for prop in [
            "equivalent_diameter_area",
            "feret_diameter_max",
            "perimeter",
            "perimeter_crofton",
        ]:
            self.cha[prop] = self.cha[prop+"_px"]*length_per_pixel
        for prop in ["area", "area_convex"]:
            self.cha[prop] = self.cha[prop+"_px"]*length_per_pixel**2

    def convert_to_units(self, units, verbose=True):
        """
        Converts the units of the image. units must be given as a Pint compatible
        unit, e.g. 'nm', 'µm', 'um' or 'Å'.
        """
        convert_to_units(self.img, units)
        try:
            convert_to_units(self.seg, units)
            self._set_scaling_cha(scaling)
            if not self.seg.metadata.Filtering.Conditions is None and verbose:
                print("Scaling set, but area filtering conditions not updated.")
                print("Consider rerunning the filter function.")
        except:
            pass

    def segment(
        self,
        device="auto",
        SAM_model="auto",
        PPS=64,
        shape_filter=True,
        edge_filter=True,
        crop_and_enlarge=False,
        invert=False,
        double=False,
        min_mask_area=16,
        stepsize=1,
        verbose=True,
        **kwargs,
    ):
        """
        This function segments the loaded image using either SAM or FastSAM. It saves 
        the masks in the .seg attribute as a HyperSpy signal and the segmentation 
        parameters stored in the .metadata attribute of this HyperSpy signal.

        Several parameters are available for the segmentation:
         - device: 'auto', 'cpu' or 'cuda'
         - SAM_model: 'auto', 'huge', 'large', 'base' or 'fast'
         - PPS (points per side) number of sampling points, default 64
         - shape_filter: True or False
         - edge_filter: True or False
         - crop_and_enlarge: True or False
         - invert: True or False
         - double: True or False
         - min_mask_area: 16 as default
         - verbose: True or False
        """
        if device.lower() in ["auto", "a"]:
            device = choose_device()

        SAM_model = choose_SAM_model(SAM_model, device, verbose)

        image_shape = self.img.data.shape

        sub_images = preprocess(
            self.img, crop_and_enlarge=crop_and_enlarge, invert=invert, double=double
        )

        list_of_mask_arrays = []
        start = time()
        for sub_image in sub_images:
            if SAM_model == "fast":
                masks = FastSAM_segmentation(sub_image, device)
            else:
                masks = SAM_segmentation(
                    sub_image, SAM_model, device, PPS, min_mask_area, **kwargs
                )

            if edge_filter:
                edge_sums = masks[:, :, [0, -1]].sum(axis=1).sum(axis=1) + masks[
                    :, [0, -1], :
                ].sum(axis=2).sum(axis=1)
                # Only keep those where the edges are empty
                masks = masks[edge_sums == 0]

            if shape_filter:
                list_of_filtered_masks = []
                for mask in masks:
                    labels_of_masks = skimage.measure.label(mask)
                    props = skimage.measure.regionprops_table(
                        labels_of_masks, properties=["label", "area", "solidity"]
                    )
                    if len(props.get("label")) == 1 and (
                        props.get("area") < 400 or props.get("solidity") > 0.95
                    ):
                        list_of_filtered_masks.append(mask)
                masks = np.stack(list_of_filtered_masks)

            list_of_mask_arrays.append(masks)

        if crop_and_enlarge:
            stitched_masks = []
            for i in range(0, len(list_of_mask_arrays), 4):
                stitched_masks.append(
                    stitch_crops_together(list_of_mask_arrays[i : i + 4], image_shape)
                )
            list_of_mask_arrays = stitched_masks
        if double:
            masks = remove_overlapping_masks(np.concatenate(list_of_mask_arrays))
        else:
            masks = list_of_mask_arrays[0]

        if len(masks) == 0:
            elapsed_time = time() - start
            if verbose:
                print(
                    f"0 masks found for {self.name}, so no masks were saved."
                )
                print(f"It took {format_time(elapsed_time)}")
        else:
            segmentation_metadata = {
                "SAM_model": SAM_model,
                "PPS": PPS,
                "shape_filter": shape_filter,
                "edge_filter": edge_filter,
                "crop_and_enlarge": crop_and_enlarge,
                "invert": invert,
                "double": double,
                "min_mask_area": min_mask_area,
            }
            elapsed_time = time() - start
            if verbose:
                print(f"{len(masks)} masks found. It took {format_time(elapsed_time)}")

        self.seg = hs.signals.Signal2D(
            masks,
            metadata={
                "General": {
                    "title": self.img.metadata.General.title,
                    "image_filepath": self.filepath,
                },
                "Segmentation": segmentation_metadata,
                "Filtering": {"Conditions": None, "passed_filter": "N/A"},
            },
        )
        set_scaling(self.seg, get_scaling(self.img))

        self.characterize(stepsize=stepsize, verbose=verbose)

    def import_segmentation_from_image(self, filepath=None, stepsize=1, verbose=True):
        """
        Imports segmentation from an image file (black and white) instead of segmenting 
        with SAM. The segmentation is converted to a HyperSpy signal and saved in the
        .seg attribute.
        """
        if filepath is None:
            filepath = get_filepath()
        segmentation = load_image_RGB(filepath)
        if segmentation.ndim == 3:
            segmentation = segmentation[:, :, 0] > 0
        elif segmentation.ndim == 2:
            segmentation = segmentation > 0
        labels = label(segmentation)
        masks = np.stack([labels == n for n in range(1, labels.max() + 1)]).astype(
            "uint8"
        )
        self.seg = hs.signals.Signal2D(
            masks,
            metadata={
                "General": {
                    "title": self.img.metadata.General.title,
                    "image_filepath": self.img.metadata.General.filepath,
                },
                "Filtering": {"Conditions": None, "passed_filter": "N/A"},
                "Segmentation": f"Imported from file '{filepath}'",
            },
        )
        set_scaling(self.seg, get_scaling(self.img))
        self.characterize(stepsize=stepsize, verbose=verbose)

    def characterize(self, stepsize=1, verbose=True):
        """
        Calculates a range of characteristics for each mask and saves it as a Pandas
        DataFrame in the .cha attribute.
        """
        masks = self.seg.data
        dfs_properties = []
        for m, mask in enumerate(masks):
            if verbose:
                print(
                    f"Finding mask characteristics: {m + 1}/{len(masks)}",
                    sep=",",
                    end="\r" if m + 1 < len(masks) else "\n",
                    flush=True,
                )
            if self.img.data.ndim == 3:
                img = self.img.data.mean(axis=2)
            else:
                img = self.img.data
            dfs_properties.append(
                pd.DataFrame(
                    regionprops_table(
                        mask,
                        img,
                        properties=(
                            "area",
                            "area_convex",
                            "axis_major_length",
                            "axis_minor_length",
                            "bbox",
                            "centroid",
                            "centroid_local",
                            "centroid_weighted",
                            "eccentricity",
                            "equivalent_diameter_area",
                            "euler_number",
                            "extent",
                            "feret_diameter_max",
                            "inertia_tensor",
                            "inertia_tensor_eigvals",
                            "intensity_max",
                            "intensity_mean",
                            "intensity_min",
                            "moments_hu",
                            "moments_weighted_hu",
                            "orientation",
                            "perimeter",
                            "perimeter_crofton",
                            "solidity",
                        ),
                    )
                )
            )
        df = pd.concat(dfs_properties)
        length_per_pixel = float(get_scaling(self.seg).split()[0])
        unit = get_scaling(self.seg).split()[1]
        df["scaling [unit/px]"] = length_per_pixel
        df["unit"] = unit
        df["mask"] = np.arange(df.shape[0])
        df["mask_index"] = np.arange(df.shape[0])
        column_to_move = df.pop("mask_index")
        df.insert(0, "mask_index", column_to_move)
        df = df.set_index("mask")

        for prop in [
            "equivalent_diameter_area",
            "feret_diameter_max",
            "perimeter",
            "perimeter_crofton",
        ]:
            df[prop+"_px"] = df[prop]
            df[prop] *= length_per_pixel
        for prop in ["area", "area_convex"]:
            df[prop+"_px"] = df[prop].astype(int)
            df[prop] *= length_per_pixel**2

        flattened_multiple_masks = np.moveaxis(masks[:, masks.sum(axis=0) > 1], 0, -1)
        unique_multiple_masks = nb_unique_caller(flattened_multiple_masks[::stepsize])
        df["overlap"] = 0
        df["overlapping_masks"] = [set() for _ in range(len(df))]

        overlap_counts = np.zeros(len(df), dtype=int)

        if not (unique_multiple_masks is None):
            for n, unique in enumerate(unique_multiple_masks):
                if verbose:
                    print((
                            "Finding areas with overlap: "
                            f"{n + 1}/{len(unique_multiple_masks)}"
                        ),
                        sep=",",
                        end="\r" if n + 1 < len(unique_multiple_masks) else "\n",
                        flush=True,
                    )
                    

                mask_indices = np.where(unique)[0]

                for idx in mask_indices:
                    df.at[idx, "overlapping_masks"].update(mask_indices)

                summed_masks = masks[mask_indices].sum(axis=0)
                overlaps = (summed_masks > 1).sum(axis=(0, 1))

                overlap_counts[mask_indices] += overlaps

        df["overlap"] = overlap_counts
        df["number_of_overlapping_masks"] = df["overlapping_masks"].apply(len)

        df["number_of_overlapping_masks"] = [
            len(masks) for masks in df["overlapping_masks"].to_list()
        ]
        df["passed_filter"] = True
        df.attrs = {
            "title": self.img.metadata.General.title,
            "image_filepath": self.filepath,
            "filepath": "Not saved yet",
        }
        self.cha = df

    def save_segmentation(self, save_as=None, overwrite=None):
        """
        Saves the segmentation as a .hspy file and the characterization as a .csv file
        for loading later. Filtering conditions are also saved in the .hspy file.
        """
        filepath = Path(self.filepath if save_as is None else save_as)
        self.seg.save(filepath.with_suffix(".hspy"), overwrite=overwrite)
        save_df_to_csv(self.cha, filepath.with_suffix(".csv"))

    def load_segmentation(self, filepath=None):
        """
        Loads segmentation, characterization and filtering from a .hspy and .csv file.
        """
        filepath = Path(self.filepath if filepath is None else filepath)
        self.seg = hs.load(filepath.with_suffix(".hspy"))
        self.cha = load_df_from_csv(filepath.with_suffix(".csv"))

    def plot_masks(self, cmap="default", figsize=[8, 4],filtered=False):
        """
        Plots the original image and the masks found through segmentation. If
        filtered is True, it only plots the masks that passed the filtering 
        conditions.
        """
        if cmap == "default":
            cmap = make_randomized_cmap()
        masks = self.seg.data
        if filtered:
            try:
                masks = masks[self.seg.metadata.Filtering.passed_filter]
            except:
                pass

        labels = masks_to_2D(masks)
        fig, ax = plt.subplots(1, 2, figsize=figsize)
        ax[0].imshow(self.img.data, cmap="gray")
        ax[0].axis("off")
        ax[1].imshow(labels, cmap=cmap, interpolation="nearest")
        ax[1].axis("off")
        plt.suptitle(self.img.metadata.General.title)
        plt.tight_layout()
        plt.show()

    def plot_particle(self, mask_index, cmap="grey"):
        """
        Given a particle/mask index, it plots the smallest image that contains the given
        mask. It plots both filtered and non-filtered masks.
        """
        try:
            bbox = self.cha.loc[mask_index, [f"bbox-{n}" for n in range(4)]].tolist()
        except:
            raise ValueError(f"Only indices between 0 and {self.cha['mask_index'].max()} are accepted.")
        fig, ax = plt.subplots()
        ax.imshow(self.img.data[bbox[0] : bbox[2], bbox[1] : bbox[3]], cmap=cmap)
        plt.show()

    def filter(self):
        """
        Runs the interactive filtering window to filter masks based on selected
        characteristcs.
        """
        filter(self.img, self.seg, self.cha)

    def filter_nogui(self, conditions):
        """
        Filters the masks based on a set of conditions with respect to the mask
        characteristics. No interactive window opens.
        """
        filter_nogui(self.seg, self.cha, conditions)
        
    def overview(
        self, 
        save_as=None,
        characteristics=["area"], 
        bin_list=None, 
        timestamp=False
    ):
        """
        Produces and saves an overview .pdf file showing the segmentation and histograms
        of selected characteristics.
        """
        if characteristics == ["all"]:
            characteristics = [
                "area",
                "area_convex",
                "axis_major_length",
                "axis_minor_length",
                "eccentricity",
                "equivalent_diameter_area",
                "extent",
                "feret_diameter_max",
                "intensity_max",
                "intensity_mean",
                "intensity_min",
                "orientation",
                "perimeter",
                "perimeter_crofton",
                "solidity",
                "overlap",
            ]

        for n, prop in enumerate(characteristics):
            if prop == "intensity":
                characteristics[n] = "intensity_mean"
            elif prop == "diameter":
                characteristics[n] = "equivalent_diameter_area"
            elif prop == "max diameter":
                characteristics[n] = "feret_diameter_max"
            elif prop == "crofton perimeter":
                characteristics[n] = "perimeter_crofton"
            elif prop == "convex area":
                characteristics[n] = "area_convex"

        df = copy(self.cha[self.cha["passed_filter"]])

        if bin_list is None:
            bin_list = ["auto"] * len(characteristics)

        unit = df["unit"].to_list()[0]
        unit2 = unit + "$^2$" if unit != "px" else unit
        name_dict = {
            "area": f"area ({unit2})",
            "area_convex": f"convex area ({unit2})",
            "eccentricity": "eccentricity",
            "solidity": "solidity",
            "intensity_mean": "mean intensity",
            "overlap": "overlap (px)",
            "equivalent_diameter_area": f"area equivalent diameter ({unit})",
            "feret_diameter_max": f"Max diameter (Feret) ({unit})",
            "orientation": "orientation",
            "perimeter": f"perimeter ({unit})",
            "perimeter_crofton": f"crofton perimeter ({unit})",
            "axis_major_length": f"Major axis length ({unit})",
            "axis_minor_length": f"Minor axis length ({unit})",
            "extent": "Ratio of pixels in the mask the pixels in the bounding box",
            "intensity_max": "Max intensity of the mask",
            "intensity_min": "minimum intensity of the mask",
            "overlap": f"amount of overlap ({unit2})",
        }
        figs = []
        for n, prop in enumerate(characteristics):
            fig, ax = plt.subplots(figsize=(12, 9))
            ax.set_xlabel(name_dict.get(prop).capitalize(), fontsize=16)
            ax.set_title(f"Histogram of {name_dict.get(prop)} for all images", fontsize=18)
            df[prop].hist(bins=bin_list[n], ax=ax, edgecolor="k", color="#0081C6")
            ax.grid(False)
            ax.set_ylabel("Count", fontsize=16)
            ax.tick_params(axis="both", which="major", labelsize=14)
            data = df[prop]
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data)
            variance = np.var(data)
            skewness = scipy.stats.skew(data)
            kurtosis = scipy.stats.kurtosis(data)
            data_range = np.ptp(data)
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = scipy.stats.iqr(data)
            minimum = np.min(data)
            maximum = np.max(data)
            count = len(data)
            total_sum = np.sum(data)
            coeff_variation = std_dev / mean

            def format_value(val):
                if val == 0:
                    return 0
                elif val < 10:
                    return f"{val:.2f}"
                elif 10 <= val < 100:
                    return f"{val:.1f}"
                elif 100 <= val:
                    return f"{int(val)}"

            x_r = 1 - len(f"Upper quantile: {format_value(q3)}") * 0.0108
            x_m = (
                x_r - 0.025 - len(f"Sum: {format_value(total_sum)}") * 0.0108
                if total_sum > 100000000
                else x_r - 0.155
            )
            x_l = (
                x_m - 0.055 - len(f"Sum: {format_value(variance)}") * 0.0108
                if variance > 1000000000000
                else x_m - 0.22
            )

            stats_text_left = (
                f"Mean: {format_value(mean)}\nStd Dev: {format_value(std_dev)}\n"
                f"Median: {format_value(median)}\nVariance: {format_value(variance)}\n"
                f"Coeff of Variation: {format_value(coeff_variation)}\n"
                f"Total number of masks: {len(df['area'].to_list())}"
            )

            stats_text_middle = (
                f"Skewness: {format_value(skewness)}\nKurtosis: {format_value(kurtosis)}\n"
                f"Count: {count}\nSum: {format_value(total_sum)}\nIQR: {format_value(iqr)}"
            )

            stats_text_right = (
                f"Lower quantile: {format_value(q1)}\nUpper quantile: {format_value(q3)}\n"
                f"Min: {format_value(minimum)}\nMax: {format_value(maximum)}\n"
                f"Range: {format_value(data_range)}"
            )
            n = "i" * int((194 * (1 - x_l + 0.011)))

            text = f"{n}\n{n}\n{n}\n{n}\n{n}\n{n}"
            text_properties = {
                "fontsize": 12,
                "color": "none",
                "verticalalignment": "top",
                "bbox": dict(
                    boxstyle="round,pad=0.3",
                    edgecolor="black",
                    facecolor="white",
                    alpha=0.5,
                ),
            }

            plt.text(x_l, 0.98, text, transform=plt.gca().transAxes, **text_properties)
            for x, txt in zip([x_l,x_m,x_r],[stats_text_left,stats_text_middle,stats_text_right]):
                plt.text(
                    x, 0.98,
                    txt,
                    ha="left",
                    va="top",
                    transform=plt.gca().transAxes,
                    fontsize=12,
                )
            
            figs.append(fig)

        figs.append(self._make_overview_figure())

        if timestamp:
            d = datetime.now()
            stamp = f"_{d.year}{d.month}{d.day}_{d.hour}{d.minute}{d.second}"
        else:
            stamp = ""

        filepath = self._save_as_to_filepath(save_as, end=f"_overview{stamp}.pdf")

        p = PdfPages(filepath)

        for fig in figs:
            fig.savefig(p, format="pdf")

        p.close()
        plt.show()
        
    def _make_overview_figure(self):
        df = self.cha[self.cha["passed_filter"]]
        cmap = make_randomized_cmap()
        
        fig, ax = plt.subplot_mosaic(
            [["left", "right"], ["left2", "right2"]],
            constrained_layout=True,
            figsize=(12, 9),
        )
        ax["left"].imshow(self.img.data, cmap="gray")
        ax["left"].axis("off")

        labels = masks_to_2D(self.get_filtered_masks())
        ax["right"].imshow(labels, interpolation="nearest", cmap=cmap)
        ax["right"].axis("off")

        ax["right2"].axis("off")

        plt.suptitle(self.seg.metadata.General.title, fontsize=18)

        df["area"].hist(
            bins="auto", ax=ax["left2"], edgecolor="k", color="#0081C6"
        )
        unit = df["unit"].to_list()[0]
        unit2 = unit + "$^2$" if unit != "px" else unit
        ax["left2"].set_title(f"Histogram of area ({unit})")
        ax["left2"].set_xlabel(f"area ({unit})")
        ax["left2"].grid(False)
        ax["left2"].set_ylabel("Count")

        filters = self.seg.metadata.Filtering.Conditions
        if filters is None:
            self.filter_nogui({"min_area":0})
        filters = self.seg.metadata.Filtering.Conditions
        min_area = round(filters["min_area"], 1)
        max_area = round(filters["max_area"], 1)
        min_solidity = round(filters["min_solidity"], 3)
        max_solidity = round(filters["max_solidity"], 3)
        min_intensity = filters["min_intensity"]
        max_intensity = filters["max_intensity"]
        min_eccentricity = round(filters["min_eccentricity"], 3)
        max_eccentricity = round(filters["max_eccentricity"], 3)
        overlap = filters["overlap"]
        overlapping_masks = filters["overlapping_masks"]
        scaling = round(filters["scaling"], 3)
        removed = filters["removed"]
        remain = filters["remain"]
        seg_params = self.seg.metadata.Segmentation
        if isinstance(seg_params, str): 
            # Happens when segmentation is imported from elsewhere
            segmentation = seg_params
        else:
            segmentation = (
                seg_params.SAM_model
                + (f", PPS={seg_params.PPS}" if seg_params.SAM_model != "fast" else "")
                + (", C&E" if seg_params.crop_and_enlarge else "")
                + (", I" if seg_params.invert else "")
                + (", D" if seg_params.double else "")
                + (", no EF" if not seg_params.edge_filter else "")
                + (", no SF" if not seg_params.shape_filter else "")
                + (
                    f", MMA={seg_params.min_mask_area}"
                    if seg_params.min_mask_area != 35
                    else ""
                )
            )

        x1 = 0.5845
        x2 = 0.8
        fig.text(x1, 0.495, "Used parameter values:", fontsize=18)

        fig.text(x1, 0.455, "Segmentation:", fontsize=18)
        fig.text(0.75, 0.455, segmentation, fontsize=18)

        fig.text(x1, 0.415, f"Area ({unit2}):", fontsize=18)
        fig.text(
            x2, 0.415, f"({round(min_area, 1)}, {round(max_area, 1)})", fontsize=18
        )

        fig.text(x1, 0.375, "Solidity:", fontsize=18)
        fig.text(x2, 0.375, f"({min_solidity}, {max_solidity})", fontsize=18)

        fig.text(x1, 0.335, "Intensity:", fontsize=18)
        fig.text(x2, 0.335, f"({min_intensity}, {max_intensity})", fontsize=18)

        fig.text(x1, 0.295, "Eccentricity:", fontsize=18)
        fig.text(x2, 0.295, f"({min_eccentricity}, {max_eccentricity})", fontsize=18)

        fig.text(x1, 0.255, "Overlap:", fontsize=18)
        fig.text(x2, 0.255, f"{overlap}", fontsize=18)

        fig.text(x1, 0.185, "Number of \noverlapping masks:", fontsize=18)
        fig.text(x2, 0.185, f"{overlapping_masks}", fontsize=18)

        fig.text(x1, 0.145, f"Scaling (px/{unit}):", fontsize=18)
        fig.text(x2, 0.145, f"{scaling}", fontsize=18)
        fig.text(
            0.63,
            0.055,
            f"{removed} masks removed.\n {remain} remain.",
            fontsize=18,
            multialignment="center",
        )
        
        return fig
        

    def get_filtered_masks(self):
        """
        Returns the masks that passed the filtering conditions.
        """
        if self.seg.metadata.Filtering.passed_filter == "N/A":
            filtered_masks = self.seg.data
        else:
            filtered_masks = self.seg.data[
                self.seg.metadata.Filtering.passed_filter
            ]
        return filtered_masks

    def export_filtered_characteristics(self, save_as=None):
        """
        Exports the characteristics of the masks that passed the filtering conditions as
        a .csv file.
        """
        filtered_characteristic = self.cha[self.cha["passed_filter"] == True]
        filtered_characteristic.loc[:, "mask_index"] = np.arange(
            len(filtered_characteristic)
        )
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks.csv")
        save_df_to_csv(filtered_characteristic, filepath.with_suffix(".csv"))

    def export_filtered_masks_png(self, save_as=None, cmap="default"):
        """
        Exports an image of the masks that passed the filtering conditions as a .png
        file.
        """
        if cmap == "default":
            cmap = make_randomized_cmap()
        labels = masks_to_2D(self.get_filtered_masks())
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks.png")
        plt.imsave(filepath.with_suffix(".png"), labels, cmap=cmap)

    def export_filtered_masks_tif(self, save_as=None):
        """
        Exports an image of the masks that passed the filtering conditions as a .tif
        file.
        """
        labels = masks_to_2D(self.get_filtered_masks())
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks.tif")
        tifffile.imwrite(filepath.with_suffix(".tif"), labels.astype("uint16"))

    def export_filtered_masks_binary(self, save_as=None):
        """
        Exports an image of the masks that passed the filtering conditions as a binary 
        .tif file.
        """
        labels = masks_to_2D(self.get_filtered_masks())
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks_binary.tif")
        tifffile.imwrite(
            filepath.with_suffix(".tif"), ((labels > 0) * 255).astype("uint8")
        )

    def export_filtered_masks_numpy(self, save_as=None):
        """
        Exports the masks that passed the filtering conditions as a compressed .npz
        file. Can be loaded again with:
        
        import numpy as np
        masks = np.load('filename.npz')['array']
        """
        filepath = self._save_as_to_filepath(save_as, end="_filtered_masks_binary.npz")
        np.savez_compressed(
            filepath.with_suffix(".npz"), array=self.get_filtered_masks()
        )

    def export_all(self, save_as=None):
        """
        Exports all the different outputs possible.
        """
        self.export_filtered_characteristics(save_as=save_as)
        self.export_filtered_masks_png(save_as=save_as, cmap="default")
        self.export_filtered_masks_tif(save_as=save_as)
        self.export_filtered_masks_binary(save_as=save_as+"_binary" if save_as else save_as)
        self.export_filtered_masks_numpy(save_as=save_as)
        
        
    def _save_as_to_filepath(self, save_as, end=None):
        """
        Helper function. Chooses a default filename or the given save_as and returns it 
        as a Path object.
        """
        if save_as is None:
            filepath = Path(self.filepath.split(".")[0] + end)
        else:
            filepath = Path(save_as)
        return filepath


class NPSAM(MutableSequence):
    """
    This class is a wrapper around the NPSAMImage class that enables segmentation of
    multiple images with NP-SAM.
    
    Upon initialization, it loads images from filepaths given as input. If no filepaths
    are given, the user is prompted to select files.

    The loaded images can then be segmented with the .segment() function, and the masks 
    stored in the .seg attribute. The masks are then characterized and the 
    characteristics are stored as pandas DataFrames in the .cha attribute. If no scaling 
    is given or extracted from the image files, the user is prompted for a scaling. The 
    scaling can also be changed with .set_scaling() at any time.

    Once segmented, the masks can be filtered with .filter() or .filter_nogui(). Only
    masks that passed the filtering conditions will have True in their 'passed_filter' 
    characteristic.

    Finally, a range of different outputs can be made. An overview .pdf file with
    .overview(), a .csv file with the characteristics of the filtered masks, an .npz
    file with a numpy array of the filtered masks and .png or .tif images of the 
    filtered masks.
    """

    def __init__(self, images=None, select_image=None):
        if images is None:
            images = get_filepaths()
        self.data = [
            self._validatetype(image, select_image=select_image) for image in images
        ]
        self._update()


    def __repr__(self):
        return repr(self.data).replace(">, <", ">,\n <")
      
      
    def __str__(self):
        return str(self.data).replace(">, <", ">,\n <")


    def __len__(self):
        return len(self.data)


    def __getitem__(self, i):
        return self.data[i]


    def __setitem__(self, i, image):
        self.data[i] = self._validatetype(image)
        self._update()


    def __delitem__(self, i):
        del self.data[i]
        self._update()


    def __add__(self, other):
        if isinstance(other, NPSAM):
            return self.__class__(self.data + other.data)
        elif isinstance(other, NPSAMImage):
            return self.__class__(self.data + [other])
        else:
            raise TypeError("Can only add NPSAM objects")


    def insert(self, i, image):
        self.data.insert(i, self._validatetype(image))
        self._update()


    def _validatetype(self, item, select_image=None):
        if isinstance(item, NPSAMImage):
            return item
        if isinstance(item, str):
            return NPSAMImage(item, select_image=select_image)
        raise TypeError("Only NPSAMImage objects or filepaths are supported")


    def _update(self):
        self.img = [image.img for image in self.data]
        self.seg = [image.seg for image in self.data]
        self.cha = [image.cha for image in self.data]
        self.filepaths = [image.filepath for image in self.data]

    def set_scaling(self, scaling = True):
        """
        Sets the scaling of the images. Scaling must be given as a (list of) Pint 
        compatible quantity, e.g. '1 nm', '3.5 µm', '0.3 um' or '4 Å'. If none are
        given, the user is prompted.
        """
        if scaling is True:
            common_scaling = input("Do you want to use the same scaling for all images? (Y/n) ")
            if common_scaling.lower() in ["y","yes",""]:
                scalings = input("What is the scaling? (E.g. '2.5 nm') ")
                scalings = len(self)*[scalings]
            else:
                scalings = []
                for image in self:
                    scalings.append(input(f"What is the scaling for {image.img.metadata.General.title}? (E.g. '2.5 nm') "))
        elif scaling is False:
            scalings = len(self)*["1 px"]
        elif isinstance(scaling, str):
            scalings = len(self)*[scaling]
        elif isinstance(scaling, list):
            scalings = scaling
        else:
            raise ValueError("scaling must be given as a string or a list of strings.")
            
        if len(self) == len(scalings):
            printed_yet = False
            for image, scaling in zip(self, scalings):
                image.set_scaling(scaling,verbose=not printed_yet)
                try:
                    if not image.seg.metadata.Filtering.Conditions is None:
                        printed_yet = True
                except:
                    pass
        else:
            raise ValueError(f"The number of scalings ({len(scalings)}) does not correspond to the number of images ({len(self)}).")
       

    def convert_to_units(self, units=None):
        """
        Converts the units of the image. units must be given as a (list of) Pint 
        compatible unit, e.g. 'nm', 'µm', 'um' or 'Å'. If none are given, the user is 
        prompted.
        """
        if units is None:
            common_units = input("Do you want to convert to the same units for all images? (Y/n) ")
            if common_units.lower() in ["y","yes",""]:
                units = input("What is the units? (E.g. 'nm') ")
                units = len(self)*[units]
            else:
                units = []
                for image in self:
                    units.append(input(f"What is the units for {image.img.metadata.General.title}? (E.g. 'nm') "))
        elif isinstance(units, str):
            units = len(self)*[units]
        elif isinstance(units, list):
            pass
        else:
            raise ValueError("units must be given as a string or a list of strings.")
            
        if len(self) == len(units):
            printed_yet = False
            for image, unit in zip(self, units):
                image.convert_to_units(unit,verbose=not printed_yet)
                try:
                    if not image.seg.metadata.Filtering.Conditions is None:
                        printed_yet = True
                except:
                    pass
        else:
            raise ValueError(f"The number of units ({len(units)}) does not correspond to the number of images ({len(self)}).")


    def segment(
        self,
        device="auto",
        SAM_model="auto",
        PPS=64,
        shape_filter=True,
        edge_filter=True,
        crop_and_enlarge=False,
        invert=False,
        double=False,
        min_mask_area=35,
        stepsize=1,
        verbose=True,
        **kwargs,
    ):
        if device.lower() in ["auto", "a"]:
            device = choose_device()

        SAM_model = choose_SAM_model(SAM_model, device, verbose)

        for n, image in enumerate(self):
            if len(self) > 1:
                print(
                    f"{n + 1}/{len(self)} - Now working on: {image.name}"
                )

            image.segment(
                device=device,
                SAM_model=SAM_model,
                PPS=PPS,
                shape_filter=shape_filter,
                edge_filter=edge_filter,
                crop_and_enlarge=crop_and_enlarge,
                invert=invert,
                double=double,
                min_mask_area=min_mask_area,
                stepsize=stepsize,
                verbose=verbose,
                **kwargs,
            )

            if len(self) > 1:
                print("")

            self._update()


    def save_segmentation(self, save_as = None, overwrite = None):
        if not save_as is None:
            raise NotImplementedError("The save_as keyword is not implemented for multiple image files yet.")
        for image in self:
            image.save_segmentation(overwrite = overwrite)
            
    
    def plot_masks(self, cmap="default", figsize=[8, 4],filtered=False):
        for image in self:
            image.plot_masks(cmap=cmap, figsize=figsize, filtered=filtered)
            
    
    def plot_particle(self, image_index, mask_index, cmap="grey"):
        self[image_index].plot_particle(mask_index,cmap=cmap)
    

    def filter(self, app=False, position=None):
        filter(self.img, self.seg, self.cha, app=app, position=position)
        self._update()
        
    def filter_nogui(self, conditions):
        """
        Filters the masks based on a set of conditions with respect to the mask
        characteristics. No interactive window opens.
        """
        filter_nogui(self.seg, self.cha, conditions)
        
    def export_filtered_characteristics(self):
        """
        Exports the characteristics of the masks that passed the filtering conditions as
        a .csv file.
        """
        for image in self:
            image.export_filtered_characteristics()

    def export_filtered_masks_png(self, cmap="default"):
        """
        Exports an image of the masks that passed the filtering conditions as a .png
        file.
        """
        for image in self:
            image.export_filtered_masks_png()

    def export_filtered_masks_tif(self):
        """
        Exports an image of the masks that passed the filtering conditions as a .tif
        file.
        """
        for image in self:
            image.export_filtered_masks_tif()

    def export_filtered_masks_binary(self):
        """
        Exports an image of the masks that passed the filtering conditions as a binary 
        .tif file.
        """
        for image in self:
            image.export_filtered_masks_binary()

    def export_filtered_masks_numpy(self):
        """
        Exports the masks that passed the filtering conditions as a compressed .npz
        file. Can be loaded again with:
        
        import numpy as np
        masks = np.load('filename.npz')['array']
        """
        for image in self:
            image.export_filtered_masks_numpy()

    def export_all(self):
        for image in self:
            image.export_all()
        
    def overview(
        self, 
        save_as=None,
        characteristics=["area"], 
        bin_list=None, 
        timestamp=False,
        save_csv=False,
        show_all_figures=True,
    ):
        """
        Produces and saves an overview .pdf file showing the segmentation and histograms
        of selected characteristics.
        """
        if characteristics == ["all"]:
            characteristics = [
                "area",
                "area_convex",
                "axis_major_length",
                "axis_minor_length",
                "eccentricity",
                "equivalent_diameter_area",
                "extent",
                "feret_diameter_max",
                "intensity_max",
                "intensity_mean",
                "intensity_min",
                "orientation",
                "perimeter",
                "perimeter_crofton",
                "solidity",
                "overlap",
            ]

        for n, prop in enumerate(characteristics):
            if prop == "intensity":
                characteristics[n] = "intensity_mean"
            elif prop == "diameter":
                characteristics[n] = "equivalent_diameter_area"
            elif prop == "max diameter":
                characteristics[n] = "feret_diameter_max"
            elif prop == "crofton perimeter":
                characteristics[n] = "perimeter_crofton"
            elif prop == "convex area":
                characteristics[n] = "area_convex"

        dfs = []
        imagenumber = 1
        for image in self:
            df_filtered = copy(image.cha[image.cha["passed_filter"]])
            df_filtered["imagename"] = image.cha.attrs["title"]
            df_filtered["imagenumber"] = imagenumber
            imagenumber += 1
            dfs.append(df_filtered)
        df = pd.concat(dfs)

        
        if save_csv:
            filepath = self[0].cha.attrs["filepath"]
            file_p = Path(filepath).parent / (
                Path(filepath).parent.name + "_overview_filtered_dataframe.csv"
            )
            first_column = df.pop("imagename")
            second_column = df.pop("imagenumber")
            df.insert(0, "imagename", first_column)
            df.insert(1, "imagenumber", second_column)
            df.to_csv(file_p, encoding="utf-8", header="true", index=False)

        if bin_list is None:
            bin_list = ["auto"] * len(characteristics)

        unit = df["unit"].to_list()[0]
        unit2 = unit + "$^2$" if unit != "px" else unit
        name_dict = {
            "area": f"area ({unit2})",
            "area_convex": f"convex area ({unit2})",
            "eccentricity": "eccentricity",
            "solidity": "solidity",
            "intensity_mean": "mean intensity",
            "overlap": "overlap (px)",
            "equivalent_diameter_area": f"area equivalent diameter ({unit})",
            "feret_diameter_max": f"Max diameter (Feret) ({unit})",
            "orientation": "orientation",
            "perimeter": f"perimeter ({unit})",
            "perimeter_crofton": f"crofton perimeter ({unit})",
            "axis_major_length": f"Major axis length ({unit})",
            "axis_minor_length": f"Minor axis length ({unit})",
            "extent": "Ratio of pixels in the mask the pixels in the bounding box",
            "intensity_max": "Max intensity of the mask",
            "intensity_min": "minimum intensity of the mask",
            "overlap": f"amount of overlap ({unit2})",
        }
        figs = []
        for n, prop in enumerate(characteristics):
            fig, ax = plt.subplots(figsize=(12, 9))
            ax.set_xlabel(name_dict.get(prop).capitalize(), fontsize=16)
            ax.set_title(f"Histogram of {name_dict.get(prop)} for all images", fontsize=18)
            df[prop].hist(bins=bin_list[n], ax=ax, edgecolor="k", color="#0081C6")
            ax.grid(False)
            ax.set_ylabel("Count", fontsize=16)
            ax.tick_params(axis="both", which="major", labelsize=14)
            data = df[prop]
            mean = np.mean(data)
            median = np.median(data)
            std_dev = np.std(data)
            variance = np.var(data)
            skewness = scipy.stats.skew(data)
            kurtosis = scipy.stats.kurtosis(data)
            data_range = np.ptp(data)
            q1 = np.percentile(data, 25)
            q3 = np.percentile(data, 75)
            iqr = scipy.stats.iqr(data)
            minimum = np.min(data)
            maximum = np.max(data)
            count = len(data)
            total_sum = np.sum(data)
            coeff_variation = std_dev / mean

            def format_value(val):
                if val == 0:
                    return 0
                elif val < 10:
                    return f"{val:.2f}"
                elif 10 <= val < 100:
                    return f"{val:.1f}"
                elif 100 <= val:
                    return f"{int(val)}"

            x_r = 1 - len(f"Upper quantile: {format_value(q3)}") * 0.0108
            x_m = (
                x_r - 0.025 - len(f"Sum: {format_value(total_sum)}") * 0.0108
                if total_sum > 100000000
                else x_r - 0.155
            )
            x_l = (
                x_m - 0.055 - len(f"Sum: {format_value(variance)}") * 0.0108
                if variance > 1000000000000
                else x_m - 0.22
            )

            stats_text_left = (
                f"Mean: {format_value(mean)}\nStd Dev: {format_value(std_dev)}\n"
                f"Median: {format_value(median)}\nVariance: {format_value(variance)}\n"
                f"Coeff of Variation: {format_value(coeff_variation)}\n"
                f"Total number of masks: {len(df['area'].to_list())}"
            )

            stats_text_middle = (
                f"Skewness: {format_value(skewness)}\nKurtosis: {format_value(kurtosis)}\n"
                f"Count: {count}\nSum: {format_value(total_sum)}\nIQR: {format_value(iqr)}"
            )

            stats_text_right = (
                f"Lower quantile: {format_value(q1)}\nUpper quantile: {format_value(q3)}\n"
                f"Min: {format_value(minimum)}\nMax: {format_value(maximum)}\n"
                f"Range: {format_value(data_range)}"
            )
            n = "i" * int((194 * (1 - x_l + 0.011)))

            text = f"{n}\n{n}\n{n}\n{n}\n{n}\n{n}"
            text_properties = {
                "fontsize": 12,
                "color": "none",
                "verticalalignment": "top",
                "bbox": dict(
                    boxstyle="round,pad=0.3",
                    edgecolor="black",
                    facecolor="white",
                    alpha=0.5,
                ),
            }

            plt.text(x_l, 0.98, text, transform=plt.gca().transAxes, **text_properties)
            for x, txt in zip([x_l,x_m,x_r],[stats_text_left,stats_text_middle,stats_text_right]):
                plt.text(
                    x, 0.98,
                    txt,
                    ha="left",
                    va="top",
                    transform=plt.gca().transAxes,
                    fontsize=12,
                )
            
            figs.append(fig)
        
        for image in self:
            figs.append(image._make_overview_figure())

        if timestamp:
            d = datetime.now()
            stamp = f"_{d.year}{d.month}{d.day}_{d.hour}{d.minute}{d.second}"
        else:
            stamp = ""
        
        parent_folder = Path(self[0].filepath).parent
        
        if save_as is None:
            filepath = Path(parent_folder / f"NP-SAM_overview{stamp}.pdf")
        else:
            filepath = Path(save_as)

        p = PdfPages(filepath)

        for fig in figs:
            fig.savefig(p, format="pdf")

        p.close()
        
        if show_all_figures:
            plt.show()
        else:
            for fig in figs:
                plt.close(fig)
            if platform.system() == 'Darwin':       # macOS
                subprocess.call(('open', filepath))
            elif platform.system() == 'Windows':    # Windows
                os.startfile(filepath)
            else:                                   # linux variants
                subprocess.call(('xdg-open', filepath))


def filter(images, segmentations, characteristics, app=False, position=None):
    if not app:
        original_backend = matplotlib.get_backend()
        if original_backend != "QtAgg":
            try:
                #matplotlib.use("QtAgg")
                get_ipython().magic('matplotlib qt')
                print("Matplotlib backend was set to 'qt'.")
            except:
                print("Could not set matplotlib backend to 'qt'.")
                
    filtergui = ImageFilter(images, segmentations, characteristics, app=app,position=position)
    filtergui.filter()


class ImageFilter:
    def __init__(
        self,
        images,
        segmentations,
        characteristics,
        image_number=1,
        label_cmap="default",
        app=False,
        position=None,
    ):
        if label_cmap == "default":
            self.label_cmap = make_randomized_cmap()
        else:
            self.label_cmap = label_cmap

        self.images = [images] if not isinstance(images, list) else images
        self.segmentations = (
            [segmentations] if not isinstance(segmentations, list) else segmentations
        )
        self.characteristics = (
            [characteristics]
            if not isinstance(characteristics, list)
            else characteristics
        )

        self.image_number = image_number
        self.app = app
        if self.app is True:
            matplotlib.use("tkagg")
        self.position = position

        self.labels = None
        self.vmax = None
        self.image = None
        self.fig = None
        self.ax = None
        self.text = None
        self.filtered_label_image = None
        self.buttons = {}

        self.min_area = None
        self.max_area = None
        self.min_solidity = None
        self.max_solidity = None
        self.min_intensity = None
        self.max_intensity = None
        self.min_eccentricity = None
        self.max_eccentricity = None
        self.max_overlap = None
        self.overlapping_masks = None
        self.overlapping_masks_dict = {"All": "Not applied", "0": 0, "1": 2, "2": 3}

        self.ax_slider_area = None
        self.unit = None
        self.ax_slider_solidity = None
        self.ax_slider_intensity = None
        self.ax_slider_eccentricity = None
        self.ax_slider_overlap = None
        self.ax_radio_overlapping_masks = None
        self.ax_save = None
        self.ax_next = None
        self.ax_previous = None
        self.ax_return_all_removed = None
        self.ax_return_last_removed = None
        self.pressed_keys = set()
        self.last_interacted_slider = None

        self.slider_color = "#65B6F3"
        self.radio_color = "#387FBE"

        self.directory = Path(__file__).resolve().parent / "button_images"

    def get_df_params(self):
        return (
            (self.df["area"] >= self.min_area)
            & (self.df["area"] <= self.max_area)
            & (self.df["solidity"] >= self.min_solidity)
            & (self.df["solidity"] <= self.max_solidity)
            & (self.df["intensity_mean"] >= self.min_intensity)
            & (self.df["intensity_mean"] <= self.max_intensity)
            & (self.df["eccentricity"] >= self.min_eccentricity)
            & (self.df["eccentricity"] <= self.max_eccentricity)
            & (~self.df["mask_index"].isin(self.removed_index))
            & (
                self.df["number_of_overlapping_masks"] == self.overlapping_masks
                if type(self.overlapping_masks) == int
                else self.df["number_of_overlapping_masks"] >= 0
            )
            & (self.df["overlap"] <= self.max_overlap)
        )

    def plot_df(self, df):
        mask_indices = df.index.to_numpy().astype(np.uint16)

        selected_masks = self.weighted_masks_rebinned[mask_indices]

        self.filtered_label_image = np.sum(selected_masks, axis=0, dtype=np.uint16)

        self.fig.canvas.restore_region(self.background)
        self.im_lab.set_data(self.filtered_label_image)
        self.ax["left2"].draw_artist(self.im_lab)
        self.fig.canvas.blit(self.ax["left2"].bbox)

        self.text.set_text(
            f"{self.df.shape[0] - df.shape[0]} masks removed. {df.shape[0]} remain."
        )

    def create_button(
        self, x, y, w, h, default_img_path, hover_img_path, click_action, rotate=False
    ):
        ax = plt.axes([x, y, w, h], frameon=False)
        ax.set_axis_off()

        default_img = mpimg.imread(self.directory / default_img_path)
        hover_img = mpimg.imread(self.directory / hover_img_path)
        if rotate:
            default_img = np.flipud(np.fliplr(default_img))
            hover_img = np.flipud(np.fliplr(hover_img))

        img_display = ax.imshow(default_img)

        self.buttons[ax] = {
            "default": default_img,
            "hover": hover_img,
            "display": img_display,
        }
        ax.figure.canvas.mpl_connect(
            "button_press_event",
            lambda event: self.on_button_click(event, ax, click_action),
        )

    def on_hover(self, event):
        redraw_required = False
        for ax, img_info in self.buttons.items():
            if event.inaxes == ax:
                if not np.array_equal(
                    img_info["display"].get_array(), img_info["hover"]
                ):
                    img_info["display"].set_data(img_info["hover"])
                    ax.draw_artist(img_info["display"])
                    redraw_required = True
            elif not np.array_equal(
                img_info["display"].get_array(), img_info["default"]
            ):
                img_info["display"].set_data(img_info["default"])
                ax.draw_artist(img_info["display"])
                redraw_required = True
        if redraw_required:
            if self.app is False:
                self.fig.canvas.update()
            else:
                self.fig.canvas.draw_idle()

    def on_button_click(self, event, ax, action):
        if event.inaxes == ax:
            action()

    def update_area(self, slider_area):
        self.last_interacted_slider = self.slider_area
        self.min_area = int(slider_area[0])
        self.max_area = int(slider_area[1])

        self.area_val_text.set_text(
            f"Area ({self.unit2}): ({self.min_area}, {self.max_area})"
        )

        df_area = self.df.loc[self.get_df_params()]

        self.plot_df(df_area)

    def update_solidity(self, slider_solidity):
        self.last_interacted_slider = self.slider_solidity
        self.min_solidity = float(slider_solidity[0])
        self.max_solidity = float(slider_solidity[1])

        self.solidity_val_text.set_text(
            f"Solidity: ({self.min_solidity:.3f}, {self.max_solidity:.3f})"
        )

        df_solidity = self.df.loc[self.get_df_params()]

        self.plot_df(df_solidity)

    def update_intensity(self, slider_intensity):
        self.last_interacted_slider = self.slider_intensity
        self.min_intensity = int(slider_intensity[0])
        self.max_intensity = int(slider_intensity[1])

        self.intensity_val_text.set_text(
            f"Intensity: ({self.min_intensity}, {self.max_intensity})"
        )

        df_intensity = self.df.loc[self.get_df_params()]

        self.plot_df(df_intensity)

    def update_eccentricity(self, slider_eccentricity):
        self.last_interacted_slider = self.slider_eccentricity
        self.min_eccentricity = float(slider_eccentricity[0])
        self.max_eccentricity = float(slider_eccentricity[1])

        self.eccentricity_val_text.set_text(
            f"Eccentricity: ({self.min_eccentricity:.2f}, {self.max_eccentricity:.2f})"
        )

        df_eccentricity = self.df.loc[self.get_df_params()]

        self.plot_df(df_eccentricity)

    def update_overlap(self, slider_overlap):
        self.last_interacted_slider = self.slider_overlap
        self.max_overlap = slider_overlap

        self.overlap_val_text.set_text(f"Overlap: {self.max_overlap}")

        df_overlap = self.df.loc[self.get_df_params()]

        self.plot_df(df_overlap)

    def update_overlapping_masks(self, label):
        self.overlapping_masks = self.overlapping_masks_dict[label]

        df_overlapping_masks = self.df.loc[self.get_df_params()]

        self.plot_df(df_overlapping_masks)

        self.fig.canvas.draw()

    def on_key_press(self, event):
        if self.last_interacted_slider == self.slider_overlap:
            high = self.last_interacted_slider.val
        else:
            low, high = self.last_interacted_slider.val
        self.pressed_keys.add(event.key)

        if self.last_interacted_slider == self.slider_eccentricity:
            step = 0.01
        elif self.last_interacted_slider == self.slider_solidity:
            step = 0.001
        else:
            step = 1
        if "shift" in self.pressed_keys:
            if self.last_interacted_slider == self.slider_eccentricity:
                step = 0.1
            elif self.last_interacted_slider == self.slider_solidity:
                step = 0.005
            else:
                step = 10

        if event.key in {
            "left",
            "right",
            "up",
            "down",
            "shift+left",
            "shift+right",
            "shift+up",
            "shift+down",
        }:
            if self.last_interacted_slider == self.slider_overlap:
                if event.key in {"up", "shift+up"}:
                    val = high
                elif event.key in {"down", "shift+down"}:
                    val = high
                elif event.key in {"right", "shift+right"}:
                    val = high + step
                elif event.key in {"left", "shift+left"}:
                    val = high - step
                self.last_interacted_slider.set_val(val)

            else:
                if event.key in {"up", "shift+up"}:
                    val = (low + step, high)
                elif event.key in {"down", "shift+down"}:
                    val = (low - step, high)
                elif event.key in {"right", "shift+right"}:
                    val = (low, high + step)
                elif event.key in {"left", "shift+left"}:
                    val = (low, high - step)
                self.last_interacted_slider.set_val(val)

        if event.key == "z":
            self.return_last_removed()

        if event.key == "a":
            self.return_all_removed()

        if event.key == "enter":
            if self.image_number < len(self.filepaths):
                self.update_next()
            else:
                self.final_save()

        if event.key == "backspace":
            if self.image_number != 1:
                self.update_previous()

    def on_key_release(self, event):
        if event.key in self.pressed_keys:
            self.pressed_keys.remove(event.key)

    def on_click(self, event):
        df = self.df.loc[self.get_df_params()]
        if event.inaxes == self.ax["left2"]:
            for idx, row in df.iterrows():
                if (
                    row["bbox-1"] <= event.xdata <= row["bbox-3"]
                    and row["bbox-0"] <= event.ydata <= row["bbox-2"]
                ):
                    self.removed_index.append(idx)

                    df_removed = self.df.loc[self.get_df_params()]

                    self.fig.canvas.draw_idle()

                    self.plot_df(df_removed)
                    break

    def return_all_removed(self):
        self.removed_index = []

        df_removed = self.df.loc[self.get_df_params()]

        self.fig.canvas.draw_idle()

        self.plot_df(df_removed)

    def return_last_removed(self):
        try:
            self.removed_index.pop()

            df_removed = self.df.loc[self.get_df_params()]

            self.fig.canvas.draw_idle()

            self.plot_df(df_removed)
        except IndexError:
            pass

    def update_button(self):
        df_filtered = self.df.loc[self.get_df_params()]
        self.plot_df(df_filtered)

        filters = {
            "min_area": self.min_area,
            "max_area": self.max_area,
            "min_solidity": self.min_solidity,
            "max_solidity": self.max_solidity,
            "min_intensity": self.min_intensity,
            "max_intensity": self.max_intensity,
            "min_eccentricity": self.min_eccentricity,
            "max_eccentricity": self.max_eccentricity,
            "scaling": self.df["scaling [unit/px]"].to_list()[0],
            "overlap": self.max_overlap,
            "overlapping_masks": self.overlapping_masks,
            "removed_list": self.removed_index,
            "removed": self.df.shape[0] - df_filtered.shape[0],
            "remain": df_filtered.shape[0],
        }

        self.df["passed_filter"] = self.get_df_params()
        self.segmentation.metadata.Filtering = {
            "Conditions": filters,
            "passed_filter": self.df["passed_filter"].to_list(),
        }

        self.filtered_label_image = np.zeros(self.weighted_masks[0].shape)
        for n in df_filtered.index.to_list():
            self.filtered_label_image += self.weighted_masks[n]

        plt.close(self.fig)

    def final_save(self):
        self.update_button()

    def update_next(self):
        self.update_button()

        self.image_number += 1
        
        self.position = self.fig.canvas.manager.window.wm_geometry()

        self.filter()

    def update_previous(self):
        self.update_button()

        self.image_number -= 1
        
        self.position = self.fig.canvas.manager.window.wm_geometry()

        self.filter()

    def create_area_slider(self, ax):
        self.unit = self.df.loc[0, "unit"]
        self.unit2 = self.unit + "$^2$" if self.unit != "px" else self.unit

        self.slider_area = RangeSlider(
            ax,
            "",
            valmin=self.min_area,
            valmax=self.max_area,
            valstep=1,
            valinit=(self.min_area_init, self.max_area_init),
        )
        self.slider_area.on_changed(self.update_area)

        self.area_val_text = ax.text(
            0,
            1.12,
            f"Area ({self.unit2}): ({self.min_area}, {self.max_area})",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )
        self.slider_area.valtext.set_visible(False)
        self.update_area((self.min_area_init, self.max_area_init))

    def create_solidity_slider(self, ax):
        self.slider_solidity = RangeSlider(
            ax,
            "",
            valmin=self.min_solidity,
            valmax=self.max_solidity,
            valstep=0.001,
            valinit=(self.min_solidity_init, self.max_solidity_init),
        )
        self.slider_solidity.on_changed(self.update_solidity)

        self.solidity_val_text = ax.text(
            0,
            1.12,
            f"Solidity: ({self.min_solidity:.3f}, {self.max_solidity:.3f})",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )
        self.slider_solidity.valtext.set_visible(False)
        self.update_solidity((self.min_solidity_init, self.max_solidity_init))

    def create_intensity_slider(self, ax):
        self.slider_intensity = RangeSlider(
            ax,
            "",
            valmin=self.min_intensity,
            valmax=self.max_intensity,
            valstep=1,
            valinit=(self.min_intensity_init, self.max_intensity_init),
        )
        self.slider_intensity.on_changed(self.update_intensity)

        self.intensity_val_text = ax.text(
            0,
            1.12,
            f"Intensity slider: ({self.min_intensity}, {self.max_intensity})",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )
        self.slider_intensity.valtext.set_visible(False)
        self.update_intensity((self.min_intensity_init, self.max_intensity_init))

    def create_eccentricity_slider(self, ax):
        self.slider_eccentricity = RangeSlider(
            ax,
            "",
            valmin=self.min_eccentricity,
            valmax=self.max_eccentricity,
            valstep=0.01,
            valinit=(self.min_eccentricity_init, self.max_eccentricity_init),
        )
        self.slider_eccentricity.on_changed(self.update_eccentricity)

        self.eccentricity_val_text = ax.text(
            0,
            1.12,
            f"Eccentricity: ({self.min_eccentricity:.2f}, {self.max_eccentricity:.2f})",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )
        self.slider_eccentricity.valtext.set_visible(False)
        self.update_eccentricity(
            (self.min_eccentricity_init, self.max_eccentricity_init)
        )

    def create_overlap_slider(self, ax):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.slider_overlap = Slider(
                ax,
                "",
                valmin=0,
                valmax=self.max_overlap,
                valstep=1,
                valinit=self.max_overlap_init,
            )
            self.slider_overlap.on_changed(self.update_overlap)

            self.overlap_val_text = ax.text(
                0,
                1.12,
                f"Overlap: {self.max_overlap}",
                fontsize=14,
                ha="left",
                va="center",
                transform=ax.transAxes,
            )
            self.slider_overlap.valtext.set_visible(False)
            self.slider_overlap.vline._linewidth = 0
            self.update_overlap(self.max_overlap_init)

    def create_overlapping_masks_radio(self, ax):
        ax.set_aspect("equal")
        if type(self.overlapping_masks_init) == str:
            self.overlapping_masks_init = -1
        elif self.overlapping_masks_init > 2:
            self.overlapping_masks_init = -1
        self.radio_overlapping_masks = RadioButtons(
            ax,
            ("All", "0", "1", "2"),
            active=self.overlapping_masks_init + 1,
            activecolor=self.radio_color,
        )

        dists = [0, 0.12, 0.2245, 0.325]
        for i, (circle, label) in enumerate(
            zip(
                self.radio_overlapping_masks.circles,
                self.radio_overlapping_masks.labels,
            )
        ):
            new_x = 0.53 + dists[i]
            new_y = 0.5
            circle.set_center((new_x, new_y))
            circle.set_radius(0.02)
            label.set_position((new_x + 0.03, new_y))
            label.set_fontsize(14)

        self.overlapping_masks_val_text = ax.text(
            0,
            0.5,
            "Number of overlapping masks:",
            fontsize=14,
            ha="left",
            va="center",
            transform=ax.transAxes,
        )

        self.radio_overlapping_masks.on_clicked(self.update_overlapping_masks)
        self.update_overlapping_masks(
            ["All", "0", "1", "2"][self.overlapping_masks_init + 1]
        )

    def initiate_filter_values(self):
        self.min_area_init = self.min_area
        self.max_area_init = self.max_area
        self.min_solidity_init = self.min_solidity
        self.max_solidity_init = self.max_solidity
        self.min_intensity_init = self.min_intensity
        self.max_intensity_init = self.max_intensity
        self.min_eccentricity_init = self.min_eccentricity
        self.max_eccentricity_init = self.max_eccentricity
        self.max_overlap_init = self.max_overlap
        self.overlapping_masks_init = self.overlapping_masks
        self.removed_index = []
        if "min_area" in self.filters_init.keys():
            self.min_area_init = self.filters_init["min_area"]
            self.max_area_init = self.filters_init["max_area"]
            self.min_solidity_init = self.filters_init["min_solidity"]
            self.max_solidity_init = self.filters_init["max_solidity"]
            self.min_intensity_init = self.filters_init["min_intensity"]
            self.max_intensity_init = self.filters_init["max_intensity"]
            self.min_eccentricity_init = self.filters_init["min_eccentricity"]
            self.max_eccentricity_init = self.filters_init["max_eccentricity"]
            self.max_overlap_init = self.filters_init["overlap"]
            self.overlapping_masks_init = self.filters_init["overlapping_masks"]
            self.removed_index = self.filters_init["removed_list"]

        df_init = self.df.loc[self.get_df_params()]

        self.plot_df(df_init)

    def start_plot(self, image, labels):
        self.fig, self.ax = plt.subplot_mosaic(
            [["left", "right"], ["left2", "right2"], [".", "."]],
            gridspec_kw=dict(height_ratios=[1, 1, 0.1]),
            constrained_layout=True,
            figsize=(12, 10),
        )
        if self.app:
            self.fig.canvas.manager.window.wm_geometry(self.position)

        self.ax["left"].imshow(image.data, cmap="gray")
        self.vmax = labels.max()
        self.ax["right"].imshow(
            labels,
            cmap=self.label_cmap,
            interpolation="nearest",
            vmin=0,
            vmax=self.vmax,
        )
        self.im_lab = self.ax["left2"].imshow(
            self.filtered_masks_rebinned,
            cmap=self.label_cmap,
            interpolation="nearest",
            vmin=0,
            vmax=self.vmax,
        )

        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.ax["left2"].bbox)

        for axis in self.ax:
            self.ax[axis].axis("off")

        self.ax_slider_area = plt.axes(
            [0.525, 0.430, 0.45, 0.03], facecolor=self.slider_color, zorder=1
        )
        self.ax_slider_solidity = plt.axes(
            [0.525, 0.375, 0.45, 0.03], facecolor=self.slider_color, zorder=1
        )
        self.ax_slider_intensity = plt.axes(
            [0.525, 0.320, 0.45, 0.03], facecolor=self.slider_color, zorder=1
        )
        self.ax_slider_eccentricity = plt.axes(
            [0.525, 0.265, 0.45, 0.03], facecolor=self.slider_color, zorder=1
        )
        self.ax_slider_overlap = plt.axes(
            [0.525, 0.210, 0.45, 0.03], facecolor=self.slider_color, zorder=1
        )
        self.ax_radio_overlapping_masks = plt.axes(
            [0.525, -0.12, 0.5, 0.6], frameon=False
        )

        self.create_button(
            0.835,
            0.01,
            0.14,
            0.085,
            "Save_close.png",
            "Save_close_dark.png",
            self.final_save,
        )

        if self.image_number < len(self.images):
            self.create_button(
                0.68, 0.01, 0.14, 0.085, "arrow.png", "arrow_dark.png", self.update_next
            )

        if self.image_number != 1:
            self.create_button(
                0.525,
                0.01,
                0.14,
                0.085,
                "arrow.png",
                "arrow_dark.png",
                self.update_previous,
                rotate=True,
            )

        self.create_button(
            0.1,
            0.0,
            0.10,
            0.05,
            "plus_one.png",
            "plus_one_dark.png",
            self.return_last_removed,
        )

        self.create_button(
            0.3,
            0.0,
            0.10,
            0.05,
            "plus_all.png",
            "plus_all_dark.png",
            self.return_all_removed,
        )

        self.min_area = math.floor(self.df["area"].min())
        self.max_area = math.ceil(self.df["area"].max())

        self.min_intensity = math.floor(self.df["intensity_mean"].min())
        self.max_intensity = math.ceil(self.df["intensity_mean"].max())

        self.max_overlap = math.ceil(self.df["overlap"].max())

        self.text = self.fig.text(
            0.752, 0.12, "", fontsize=16, horizontalalignment="center"
        )

        self.min_solidity = self.df["solidity"].min()
        self.max_solidity = self.df["solidity"].max()

        self.min_eccentricity = self.df["eccentricity"].min()
        self.max_eccentricity = self.df["eccentricity"].max()

        self.overlapping_masks = "Not applied"

        self.initiate_filter_values()

        self.create_solidity_slider(self.ax_slider_solidity)
        self.create_intensity_slider(self.ax_slider_intensity)
        self.create_eccentricity_slider(self.ax_slider_eccentricity)
        self.create_overlap_slider(self.ax_slider_overlap)
        self.create_area_slider(self.ax_slider_area)
        self.create_overlapping_masks_radio(self.ax_radio_overlapping_masks)

        string_title = (
            f"{self.image_number}/{len(self.images)} - {image.metadata.General.title}"
            if len(self.images) > 1
            else image.metadata.General.title
        )

        plt.suptitle(string_title, fontsize=16)

        self.fig.canvas.mpl_connect("key_press_event", self.on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self.on_key_release)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        self.fig.canvas.mpl_connect("motion_notify_event", self.on_hover)
        
        plt.show()

    def filter(self):
        self.image = self.images[self.image_number - 1]
        self.segmentation = self.segmentations[self.image_number - 1]
        self.df = self.characteristics[self.image_number - 1]
        # Create DataFrame for storing the masks that didn't pass the filter
        self.removed_rows = pd.DataFrame(columns=self.df.columns)

        self.masks = self.segmentation.data

        self.weights = (
            np.arange(1, self.masks.shape[0] + 1)[:, np.newaxis, np.newaxis]
        ).astype(np.uint16)

        self.weighted_masks = self.masks * self.weights

        self.weighted_masks_rebinned = self.weighted_masks[:, ::4, ::4]

        self.labels = np.sum(self.weighted_masks, axis=0, dtype=np.uint16)

        self.filtered_masks_rebinned = self.labels

        try:
            self.filters_init = (
                self.segmentation.metadata.Filtering.Conditions.as_dictionary()
            )
        except:
            self.filters_init = {}

        self.start_plot(self.image, self.labels)


def filter_nogui(segmentations, characteristics, conditions):
    is_list = isinstance(segmentations, list)
    segmentations = [segmentations] if not is_list else segmentations
    is_list = isinstance(characteristics, list)
    characteristics = [characteristics] if not is_list else characteristics
    if len(segmentations) != len(characteristics):
        raise ValueError(
            "The number of segmentations must match the number of characteristics"
        )

    if type(conditions) == dict:
        conditions = [conditions] * len(segmentations)
        if len(segmentations) > 1:
            print("The filtering conditions will be used for all images.")
    elif type(conditions) == list:
        if len(conditions) == len(segmentations):
            for entry in conditions:
                if type(entry) != dict:
                    raise ValueError((
                        "The list entries must be dictionaries containing the filter ",
                        "conditions."
                    ))
        elif len(conditions) == 1:
            conditions = conditions * len(segmentations)
            print("The filtering conditions will be used for all images.")
        else:
            raise ValueError((
                "The length of the list with filtering conditions does not have the ",
                "same length as the list with segmentations."
            ))

    for segmentation, characteristic, filter_conditions in zip(
        segmentations, characteristics, conditions
    ):
        df = characteristic
        filters = {
            "min_area": math.floor(df["area"].min()),
            "max_area": math.ceil(df["area"].max()),
            "min_solidity": math.floor(df["solidity"].min()),
            "max_solidity": math.ceil(df["solidity"].max()),
            "min_intensity": math.floor(df["intensity_mean"].min()),
            "max_intensity": math.ceil(df["intensity_mean"].max()),
            "min_eccentricity": math.floor(df["eccentricity"].min()),
            "max_eccentricity": math.ceil(df["eccentricity"].max()),
            "overlap": math.ceil(df["overlap"].max()),
            "overlapping_masks": "Not applied",
            "scaling": df["scaling [unit/px]"].to_list()[1],
            "removed_list": []
        }

        filters.update(filter_conditions)

        df["passed_filter"] = (
            (df["area"] >= filters["min_area"])
            & (df["area"] <= filters["max_area"])
            & (df["solidity"] >= filters["min_solidity"])
            & (df["solidity"] <= filters["max_solidity"])
            & (df["intensity_mean"] >= filters["min_intensity"])
            & (df["intensity_mean"] <= filters["max_intensity"])
            & (df["eccentricity"] >= filters["min_eccentricity"])
            & (df["eccentricity"] <= filters["max_eccentricity"])
            & (
                df["number_of_overlapping_masks"] == filters["overlapping_masks"]
                if type(filters["overlapping_masks"]) == int
                else df["number_of_overlapping_masks"] >= 0
            )
            & (df["overlap"] <= filters["overlap"])
        )

        filters.update(
            {
                "removed": len(df) - df["passed_filter"].sum(),
                "remain": df["passed_filter"].sum(),
            }
        )

        segmentation.metadata.Filtering = {
            "Conditions": filters,
            "passed_filter": df["passed_filter"].to_list(),
        }


#def overview(
#    images,
#    segmentations,
#    characteristics,
#    property_list=["area"],
#    bin_list=None,
#    timestamp=False,
#):
#    is_list = isinstance(segmentations, list)
#    segmentations = [segmentations] if not is_list else segmentations
#    images = [images] if not is_list else images
#    characteristics = [characteristics] if not is_list else characteristics
#
#    if property_list == ["all"]:
#        property_list = [
#            "area",
#            "area_convex",
#            "axis_major_length",
#            "axis_minor_length",
#            "eccentricity",
#            "equivalent_diameter_area",
#            "extent",
#            "feret_diameter_max",
#            "intensity_max",
#            "intensity_mean",
#            "intensity_min",
#            "orientation",
#            "perimeter",
#            "perimeter_crofton",
#            "solidity",
#            "overlap",
#        ]
#
#    for n, prop in enumerate(property_list):
#        if prop == "intensity":
#            property_list[n] = "intensity_mean"
#        elif prop == "diameter":
#            property_list[n] = "equivalent_diameter_area"
#        elif prop == "max diameter":
#            property_list[n] = "feret_diameter_max"
#        elif prop == "crofton perimeter":
#            property_list[n] = "perimeter_crofton"
#        elif prop == "convex area":
#            property_list[n] = "area_convex"
#
#    dfs = []
#    imagenumber = 1
#    for image, segmentation, characteristic in zip(
#        images, segmentations, characteristics
#    ):
#        df_filtered = copy(characteristic[characteristic["passed_filter"]])
#        df_filtered["imagename"] = characteristic.attrs["title"]
#        df_filtered["imagenumber"] = imagenumber
#        imagenumber += 1
#        dfs.append(df_filtered)
#    master_df = pd.concat(dfs)
#
#    filepath = characteristics[0].attrs["filepath"]
#    if len(images) > 1:
#        file_p = Path(filepath).parent / (
#            Path(filepath).parent.name + "_overview_filtered_dataframe.csv"
#        )
#        first_column = master_df.pop("imagename")
#        second_column = master_df.pop("imagenumber")
#        master_df.insert(0, "imagename", first_column)
#        master_df.insert(1, "imagenumber", second_column)
#        master_df.to_csv(file_p, encoding="utf-8", header="true", index=False)
#
#    if bin_list is None:
#        bin_list = ["auto"] * len(property_list)
#
#    def save_image():
#        if timestamp:
#            d = datetime.now()
#            stamp = (
#                str(d.year)
#                + str(d.month)
#                + str(d.day)
#                + "-"
#                + str(d.hour)
#                + str(d.minute)
#                + str(d.second)
#            )
#        else:
#            stamp = ""
#
#        file_p = Path(filepath).parent / (
#            Path(filepath).parent.name + "_overview" + stamp + ".pdf"
#        )
#
#        p = PdfPages(file_p)
#
#        fig_nums = plt.get_fignums()
#        figs = [plt.figure(n) for n in fig_nums]
#
#        for fig in figs:
#            fig.savefig(p, format="pdf")
#
#        p.close()
#
#    unit = master_df["unit"].to_list()[0]
#    unit2 = unit + "$^2$" if unit != "px" else unit
#    name_dict = {
#        "area": f"area ({unit2})",
#        "area_convex": f"convex area ({unit2})",
#        "eccentricity": "eccentricity",
#        "solidity": "solidity",
#        "intensity_mean": "mean intensity",
#        "overlap": "overlap (px)",
#        "equivalent_diameter_area": f"area equivalent diameter ({unit})",
#        "feret_diameter_max": f"Max diameter (Feret) ({unit})",
#        "orientation": "orientation",
#        "perimeter": f"perimeter ({unit})",
#        "perimeter_crofton": f"crofton perimeter ({unit})",
#        "axis_major_length": f"Major axis length ({unit})",
#        "axis_minor_length": f"Minor axis length ({unit})",
#        "extent": "Ratio of pixels in the mask the pixels in the bounding box",
#        "intensity_max": "Max intensity of the mask",
#        "intensity_min": "minimum intensity of the mask",
#        "overlap": f"amount of overlap ({unit2})",
#    }
#    for n, prop in enumerate(property_list):
#        fig, ax = plt.subplots(figsize=(12, 9))
#        ax.set_xlabel(name_dict.get(prop).capitalize(), fontsize=16)
#        ax.set_title(f"Histogram of {name_dict.get(prop)} for all images", fontsize=18)
#        master_df[prop].hist(bins=bin_list[n], ax=ax, edgecolor="k", color="#0081C6")
#        ax.grid(False)
#        ax.set_ylabel("Count", fontsize=16)
#        ax.tick_params(axis="both", which="major", labelsize=14)
#        data = master_df[prop]
#        mean = np.mean(data)
#        median = np.median(data)
#        std_dev = np.std(data)
#        variance = np.var(data)
#        skewness = scipy.stats.skew(data)
#        kurtosis = scipy.stats.kurtosis(data)
#        data_range = np.ptp(data)
#        q1 = np.percentile(data, 25)
#        q3 = np.percentile(data, 75)
#        iqr = scipy.stats.iqr(data)
#        minimum = np.min(data)
#        maximum = np.max(data)
#        count = len(data)
#        total_sum = np.sum(data)
#        coeff_variation = std_dev / mean
#
#        def format_value(val):
#            if val == 0:
#                return 0
#            elif val < 10:
#                return f"{val:.2f}"
#            elif 10 <= val < 100:
#                return f"{val:.1f}"
#            elif 100 <= val:
#                return f"{int(val)}"
#
#        x_r = 1 - len(f"Upper quantile: {format_value(q3)}") * 0.0108
#        x_m = (
#            x_r - 0.025 - len(f"Sum: {format_value(total_sum)}") * 0.0108
#            if total_sum > 100000000
#            else x_r - 0.155
#        )
#        x_l = (
#            x_m - 0.055 - len(f"Sum: {format_value(variance)}") * 0.0108
#            if variance > 1000000000000
#            else x_m - 0.22
#        )
#
#        stats_text_left = (
#            f"Mean: {format_value(mean)}\nStd Dev: {format_value(std_dev)}\n"
#            f"Median: {format_value(median)}\nVariance: {format_value(variance)}\n"
#            f"Coeff of Variation: {format_value(coeff_variation)}\n"
#            f"Total number of masks: {len(master_df['area'].to_list())}"
#        )
#
#        stats_text_middle = (
#            f"Skewness: {format_value(skewness)}\nKurtosis: {format_value(kurtosis)}\n"
#            f"Count: {count}\nSum: {format_value(total_sum)}\nIQR: {format_value(iqr)}"
#        )
#
#        stats_text_right = (
#            f"Lower quantile: {format_value(q1)}\nUpper quantile: {format_value(q3)}\n"
#            f"Min: {format_value(minimum)}\nMax: {format_value(maximum)}\n"
#            f"Range: {format_value(data_range)}"
#        )
#        n = "i" * int((194 * (1 - x_l + 0.011)))
#
#        text = f"{n}\n{n}\n{n}\n{n}\n{n}\n{n}"
#        text_properties = {
#            "fontsize": 12,
#            "color": "none",
#            "verticalalignment": "top",
#            "bbox": dict(
#                boxstyle="round,pad=0.3",
#                edgecolor="black",
#                facecolor="white",
#                alpha=0.5,
#            ),
#        }
#
#        plt.text(x_l, 0.98, text, transform=plt.gca().transAxes, **text_properties)
#        plt.text(
#            x_l,
#            0.98,
#            stats_text_left,
#            horizontalalignment="left",
#            verticalalignment="top",
#            transform=plt.gca().transAxes,
#            fontsize=12,
#        )
#        plt.text(
#            x_m,
#            0.98,
#            stats_text_middle,
#            horizontalalignment="left",
#            verticalalignment="top",
#            transform=plt.gca().transAxes,
#            fontsize=12,
#        )
#        plt.text(
#            x_r,
#            0.98,
#            stats_text_right,
#            horizontalalignment="left",
#            verticalalignment="top",
#            transform=plt.gca().transAxes,
#            fontsize=12,
#        )
#
#        plt.show()
#
#    cmap = make_randomized_cmap()
#    for image, segmentation, characteristic in zip(
#        images, segmentations, characteristics
#    ):
#        fig, ax = plt.subplot_mosaic(
#            [["left", "right"], ["left2", "right2"]],
#            constrained_layout=True,
#            figsize=(12, 9),
#        )
#        ax["left"].imshow(image.data, cmap="gray")
#        ax["left"].axis("off")
#
#        labels = masks_to_2D(segmentation.data[characteristic['passed_filter']])
#        ax["right"].imshow(labels, interpolation="nearest", cmap=cmap)
#        ax["right"].axis("off")
#
#        ax["right2"].axis("off")
#
#        plt.suptitle(segmentation.metadata.General.title, fontsize=18)
#
#        df_filtered["area"].hist(
#            bins="auto", ax=ax["left2"], edgecolor="k", color="#0081C6"
#        )
#        ax["left2"].set_title(f"Histogram of area ({unit})")
#        ax["left2"].set_xlabel(f"area ({unit})")
#        ax["left2"].grid(False)
#        ax["left2"].set_ylabel("Count")
#
#        filters = segmentation.metadata.Filtering.Conditions
#        min_area = round(filters["min_area"], 1)
#        max_area = round(filters["max_area"], 1)
#        min_solidity = round(filters["min_solidity"], 3)
#        max_solidity = round(filters["max_solidity"], 3)
#        min_intensity = filters["min_intensity"]
#        max_intensity = filters["max_intensity"]
#        min_eccentricity = round(filters["min_eccentricity"], 3)
#        max_eccentricity = round(filters["max_eccentricity"], 3)
#        overlap = filters["overlap"]
#        overlapping_masks = filters["overlapping_masks"]
#        scaling = round(filters["scaling"], 3)
#        removed = filters["removed"]
#        remain = filters["remain"]
#        seg_params = segmentation.metadata.Segmentation
#        segmentation = (
#            seg_params.SAM_model
#            + (f", PPS={seg_params.PPS}" if seg_params.SAM_model != "fast" else "")
#            + (", C&E" if seg_params.crop_and_enlarge else "")
#            + (", I" if seg_params.invert else "")
#            + (", D" if seg_params.double else "")
#            + (", no EF" if not seg_params.edge_filter else "")
#            + (", no SF" if not seg_params.shape_filter else "")
#            + (
#                f", MMA={seg_params.min_mask_area}"
#                if seg_params.min_mask_area != 35
#                else ""
#            )
#        )
#
#        x1 = 0.5845
#        x2 = 0.8
#        fig.text(x1, 0.495, "Used parameter values:", fontsize=18)
#
#        fig.text(x1, 0.455, "Segmentation:", fontsize=18)
#        fig.text(0.75, 0.455, segmentation, fontsize=18)
#
#        fig.text(x1, 0.415, f"Area ({unit2}):", fontsize=18)
#        fig.text(
#            x2, 0.415, f"({round(min_area, 1)}, {round(max_area, 1)})", fontsize=18
#        )
#
#        fig.text(x1, 0.375, "Solidity:", fontsize=18)
#        fig.text(x2, 0.375, f"({min_solidity}, {max_solidity})", fontsize=18)
#
#        fig.text(x1, 0.335, "Intensity:", fontsize=18)
#        fig.text(x2, 0.335, f"({min_intensity}, {max_intensity})", fontsize=18)
#
#        fig.text(x1, 0.295, "Eccentricity:", fontsize=18)
#        fig.text(x2, 0.295, f"({min_eccentricity}, {max_eccentricity})", fontsize=18)
#
#        fig.text(x1, 0.255, "Overlap:", fontsize=18)
#        fig.text(x2, 0.255, f"{overlap}", fontsize=18)
#
#        fig.text(x1, 0.185, "Number of \noverlapping masks:", fontsize=18)
#        fig.text(x2, 0.185, f"{overlapping_masks}", fontsize=18)
#
#        fig.text(x1, 0.145, f"Scaling (px/{unit}):", fontsize=18)
#        fig.text(x2, 0.145, f"{scaling}", fontsize=18)
#        fig.text(
#            0.63,
#            0.055,
#            f"{removed} masks removed.\n {remain} remain.",
#            fontsize=18,
#            multialignment="center",
#        )
#
#        plt.show()
#
#    save_image()
