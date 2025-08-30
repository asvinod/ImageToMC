from PIL import Image
from amulet import load_level, Block
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist
from csv_functions import csv_to_dict
from getblock import fetchblock
import numpy as np
import time
from tqdm import tqdm
import math
import os
from multiprocessing import Pool

def image_to_chunk(img, point):
    width, height = img.size
    base_y = -60 
    color_conversion = csv_to_dict("csv/filtered_blocks_cleaned.csv")

    chunk_x = point[0]
    chunk_z = point[1]
    chunk = Chunk(chunk_x, chunk_z)

    cy = base_y // 16
    air = Block("minecraft", "air")
    air_index = chunk.block_palette.get_add_block(air)
    empty = np.full((16, 16, 16), air_index, dtype=np.uint32)
    chunk.blocks.add_sub_chunk(cy, empty)

    section = chunk.blocks.get_sub_chunk(cy)

    for w in range(16):
        for h in range(16):
            world_x = chunk_x * 16 + w
            world_z = chunk_z * 16 + h

            if world_x >= width or world_z >= height:
                continue

            world_y = 4

            r, g, b = img.getpixel((world_x, world_z))
            block_name = fetchblock((r, g, b), color_conversion)
            block = Block("minecraft", block_name)
            idx = chunk.block_palette.get_add_block(block)
 
            x_in_chunk = world_x % 16
            z_in_chunk = world_z % 16
            section[x_in_chunk, world_y % 16, z_in_chunk] = idx

            if world_y % 16 > 0:
                barrier = Block("minecraft", "barrier")
                barrier_index = chunk.block_palette.get_add_block(barrier)
                section[x_in_chunk, (world_y % 16) - 1, z_in_chunk] = barrier_index
    chunk.changed = True
    return chunk

def image_to_chunk_wrapper(args):
    img_path, point = args
    img = Image.open(img_path).convert("RGB")
    return image_to_chunk(img, point)

def image_to_mc(img_path, mc_path):
    img = Image.open(img_path).convert("RGB")
    MC_PATH = mc_path

    width, height = img.size
    size = width * height
    base_y = -60

    level = load_level(MC_PATH)
    dimension = "minecraft:overworld"
    color_conversion = csv_to_dict("csv/filtered_blocks_cleaned.csv")

    chunk_cache = {}
    x_chunks = math.ceil(width / 16)
    z_chunks = math.ceil(height / 16)
    
    start_time = time.perf_counter()

    tasks = [(img_path, (i, j)) for i in range(x_chunks) for j in range(z_chunks)]

    with Pool(8) as p:
        results = list(p.map(image_to_chunk_wrapper, tasks))

    for chunk in results:
        print(chunk)
        level.put_chunk(chunk, dimension)
    level.save()
    level.close()
    end_time = time.perf_counter()
    print("Chunk loading completed for", img.size, "pixel image in", end_time - start_time)

if __name__ == "__main__":
    img_path = "/Users/ashwin/imagetomc/ImageToMC/flask_app/uploads/1024by1024.jpg"
    mc_path = "/Users/ashwin/Library/Application Support/minecraft/saves/test"
    image_to_mc(img_path, mc_path)