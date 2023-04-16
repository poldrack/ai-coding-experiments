# create a python class to perform spatial smoothing on a nifti image using a median filter.
# please create a test image for use in the example
# please add code to present a plot of one slice from the input file next to one slice from the output file

import nibabel as nib
import numpy as np
from scipy.ndimage import median_filter
import matplotlib.pyplot as plt


class SpatialSmoothing:
    def __init__(self, input_file, output_file, filter_size=3):
        self.input_file = input_file
        self.output_file = output_file
        self.filter_size = filter_size

    def load_nifti(self):
        try:
            self.img = nib.load(self.input_file)
            self.data = self.img.get_fdata()
        except FileNotFoundError:
            print(f"File not found: {self.input_file}")
            return None

    def apply_median_filter(self):
        if not hasattr(self, 'data'):
            self.load_nifti()
        self.smoothed_data = median_filter(self.data, size=self.filter_size)

    def save_nifti(self):
        if not hasattr(self, 'smoothed_data'):
            self.apply_median_filter()
        smoothed_img = nib.Nifti1Image(self.smoothed_data, self.img.affine)
        nib.save(smoothed_img, self.output_file)

    def process(self):
        self.load_nifti()
        self.apply_median_filter()
        self.save_nifti()

    def plot_slices(self, slice_axis='z', slice_idx=None):
        if not hasattr(self, 'data') or not hasattr(self, 'smoothed_data'):
            self.process()

        if slice_axis == 'x':
            axis = 0
        elif slice_axis == 'y':
            axis = 1
        elif slice_axis == 'z':
            axis = 2
        else:
            raise ValueError("Invalid slice_axis. Choose from 'x', 'y', or 'z'.")

        if slice_idx is None:
            slice_idx = self.data.shape[axis] // 2

        original_slice = np.take(self.data, slice_idx, axis=axis)
        smoothed_slice = np.take(self.smoothed_data, slice_idx, axis=axis)

        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        axes[0].imshow(original_slice.T, origin='lower', cmap='gray')
        axes[0].set_title("Original")
        axes[1].imshow(smoothed_slice.T, origin='lower', cmap='gray')
        axes[1].set_title("Smoothed")
        plt.show()


def create_test_image(filename, shape=(64, 64, 64), affine=np.eye(4)):
    data = np.random.rand(*shape) * 255
    data = data.astype(np.float32)
    img = nib.Nifti1Image(data, affine)
    nib.save(img, filename)


# Example usage:
test_image_filename = "test_image.nii.gz"
create_test_image(test_image_filename)
input_file = test_image_filename
output_file = "output_smoothed.nii.gz"
filter_size = 3

smoother = SpatialSmoothing(input_file, output_file, filter_size)
smoother.process()
smoother.plot_slices(slice_axis='z', slice_idx=None)