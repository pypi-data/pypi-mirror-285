import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import os

class Prismbreak:
    def __init__(self, root, fname, savedir=".", dpi=100):
        self.root = root
        self.fname = fname
        self.savedir = savedir
        self.dpi = dpi

        self.save_r = f'{savedir}/r_{fname}'
        self.save_g = f'{savedir}/g_{fname}'
        self.save_b = f'{savedir}/b_{fname}'

    def splitrgb(self):

        # Check if the filename ends with .png
        if not self.fname.lower().endswith('.png'):
            raise ValueError("File must have a .png extension.")

        # Check if the file path exists
        file_path = os.path.join(self.root, self.fname)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Open the image
        img = Image.open(file_path)

        # Check if the image size is 0x0
        if img.size == (0, 0):
            raise ValueError("The image size is 0x0.")

        M = np.asarray(img)

        # Check if the image has 3 channels
        if M.ndim != 3 or M.shape[2] != 3:
            raise ValueError("The image must have 3 channels (RGB).")

        M = np.asarray(img)
        height, width, c = M.shape
        height = height/self.dpi
        width = width/self.dpi

        fig, ax = plt.subplots(figsize=(width, height), dpi=self.dpi)
        ax.imshow(M[:, :, 0], cmap='Reds', vmin=0, vmax=255)
        ax.set_axis_off()
        fig.savefig(self.save_r, bbox_inches='tight', pad_inches=0)
        print(f'saved {self.save_r}')

        fig, ax = plt.subplots(figsize=(width, height), dpi=self.dpi)
        plt.imshow(M[:, :, 1], cmap='Greens', vmin=0, vmax=255)
        ax.set_axis_off()
        fig.savefig(self.save_g, bbox_inches='tight', pad_inches=0)
        print(f'saved {self.save_g}')

        fig, ax = plt.subplots(figsize=(width, height), dpi=self.dpi)
        plt.imshow(M[:, :, 2], cmap='Blues', vmin=0, vmax=255)
        ax.set_axis_off()
        fig.savefig(self.save_b, bbox_inches='tight', pad_inches=0)
        print(f'saved {self.save_b}')

