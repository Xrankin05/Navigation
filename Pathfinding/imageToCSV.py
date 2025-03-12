import os
import csv
from PIL import Image
import math
import tkinter as tk
from tkinter import filedialog

# Constants
PIXEL_PER_WIDTH = 2  # Width of each grid cell
PIXEL_PER_HEIGHT = 2  # Height of each grid cell
OUTPUT_DIR = "Pathfinding/Grids/"

# Hardcoded color palette
color_map = {
    "BLUE": (171, 211, 223),
    "RED": (233, 151, 163),
    "YELLOW": (245, 244, 198),
    "GREY": (198, 193, 189),
    "ORANGE": (255, 183, 156),
    "WHITE": (255, 255, 255)
}

def euclidean_distance(c1, c2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def closest_palette_color(rgb):
    return min(color_map.values(), key=lambda color: euclidean_distance(rgb, color))

def process_image(image_path):
    image = Image.open(image_path).convert("RGB")
    width, height = image.size
    print(f'Image Width: {width}')
    print(f'Image Height: {height}')
    grid_width = width // PIXEL_PER_WIDTH
    grid_height = height // PIXEL_PER_HEIGHT

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_csv = os.path.join(OUTPUT_DIR, os.path.basename(image_path).rsplit(".", 1)[0] + ".csv")
    print(f'Grid Cols or Width: {grid_width}')
    print(f'Grid Rows or Height: {grid_height}')
    
    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        
        for y in range(grid_height):
            row_colors = []
            for x in range(grid_width):
                region = image.crop((
                    x * PIXEL_PER_WIDTH, y * PIXEL_PER_HEIGHT,
                    (x + 1) * PIXEL_PER_WIDTH, (y + 1) * PIXEL_PER_HEIGHT
                ))
                avg_color = tuple(sum(channel) // (PIXEL_PER_WIDTH * PIXEL_PER_HEIGHT) for channel in zip(*region.getdata()))
                mapped_color = closest_palette_color(avg_color)
                row_colors.append(f"{mapped_color}")
            writer.writerow(row_colors)
    
    print(f"Grid saved to {output_csv}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main Tkinter window
    file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    
    if file_path:
        process_image(file_path)
    else:
        print("No file selected.")
