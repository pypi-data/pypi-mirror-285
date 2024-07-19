import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import argparse
import os

def main(args):
  root = args.root
  fname = args.fname
  savedir = args.savedir
  dpi = args.dpi
  save_r = f'{savedir}/r_{fname}'
  save_g = f'{savedir}/g_{fname}'
  save_b = f'{savedir}/b_{fname}'

  # Check if the filename ends with .png
  if not fname.lower().endswith('.png'):
    raise ValueError("File must have a .png extension.")

  # Check if the file path exists
  file_path = os.path.join(root, fname)
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
  height = height/dpi
  width = width/dpi

  fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
  ax.imshow(M[:, :, 0], cmap='Reds', vmin=0, vmax=255)
  ax.set_axis_off()
  fig.savefig(save_r, bbox_inches='tight', pad_inches=0)
  print(f'saved {save_r}')

  fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
  plt.imshow(M[:, :, 1], cmap='Greens', vmin=0, vmax=255)
  ax.set_axis_off()
  fig.savefig(save_g, bbox_inches='tight', pad_inches=0)
  print(f'saved {save_g}')

  fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
  plt.imshow(M[:, :, 2], cmap='Blues', vmin=0, vmax=255)
  ax.set_axis_off()
  fig.savefig(save_b, bbox_inches='tight', pad_inches=0)
  print(f'saved {save_b}')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Split a PNG image into its RGB components.')
  parser.add_argument('--root', type=str, required=True, help='Root directory containing the image.')
  parser.add_argument('--fname', type=str, required=True, help='Filename of the image (e.g., temp.png).')
  parser.add_argument('--savedir', type=str, required=False, default='.', help='Save destination of the output image.')
  parser.add_argument('--dpi', type=int, required=False, default=100)

  args = parser.parse_args()
  main(args)