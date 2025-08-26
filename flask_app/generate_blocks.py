from PIL import Image
from amulet import load_level, Block
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist
from csv_functions import csv_to_dict
from getblock import fetchblock
import numpy as np
import time

def set_chunk():
    return 0

def image_to_mc(img_path, mc_path):
    pixel_num = 1
    img = Image.open(img_path).convert("RGB")
    MC_PATH = mc_path

    width, height = img.size
    size = width * height
    base_y = -60

    level = load_level(MC_PATH)
    dimension = "minecraft:overworld"
    color_conversion = csv_to_dict("csv/filtered_blocks_cleaned.csv")

    chunk_cache = {}

    for w in range(width):
        for h in range(height):
            print(f"Image loading progress: {pixel_num} / {size}")
            pixel_num += 1
            r, g, b = img.getpixel((w, h))
            block_name = fetchblock((r, g, b), color_conversion)
            block = Block("minecraft", block_name)
            
            #block = Block("minecraft", block_name)
            #block_index = block.

            world_x = w
            world_z = h
            world_y = 4

            chunk_x = world_x // 16
            chunk_z = world_z // 16
            x_in_chunk = world_x % 16
            z_in_chunk = world_z % 16

            key = (chunk_x, chunk_z)

            if key not in chunk_cache:
                try:
                    chunk = level.get_chunk(chunk_x, chunk_z, dimension)
                except ChunkDoesNotExist:
                    chunk = Chunk(chunk_x, chunk_z)
                chunk_cache[key] = chunk
            chunk = chunk_cache[key]

            cy = base_y // 16  

            if cy not in chunk.blocks:
                air = Block("minecraft", "air")
                air_index = chunk.block_palette.get_add_block(air)
                empty = np.full((16, 16, 16), air_index, dtype=np.uint32)
                chunk.blocks.add_sub_chunk(cy, empty)

            section = chunk.blocks.get_sub_chunk(cy)
            #print(section[0])
            #print()
            idx = chunk.block_palette.get_add_block(block)
            section[x_in_chunk, world_y % 16, z_in_chunk] = idx
            barrier = Block("minecraft", "barrier")
            barrier_index = chunk.block_palette.get_add_block(barrier)
            if world_y % 16 > 0:
                section[x_in_chunk, (world_y % 16) - 1, z_in_chunk] = barrier_index
            chunk.changed = True

    for chunk in chunk_cache.values():
        level.put_chunk(chunk,dimension)

    level.save()
    level.close()

img_path = "/Users/ashwin/imagetomc/ImageToMC/flask_app/uploads/1024by1024.jpg"
mc_path = "/Users/ashwin/Library/Application Support/minecraft/saves/test"

image_to_mc(img_path, mc_path)