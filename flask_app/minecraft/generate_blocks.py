from PIL import Image
from amulet import load_level, Block
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist
from .csv_functions import csv_to_dict
from .getblock import fetchblock

def image_to_mc(img_path, mc_path):
    img = Image.open(img_path).convert("RGB")
    MC_PATH = mc_path

    width, height = img.size
    base_y = -60

    level = load_level(MC_PATH)
    dimension = "minecraft:overworld"
    color_conversion = csv_to_dict("csv/filtered_blocks_cleaned.csv")

    chunk_cache = {}

    for w in range(width):
        for h in range(height):
            r, g, b = img.getpixel((w, h))
            block_name = fetchblock((r, g, b), color_conversion)

            world_x = w
            world_z = h

            chunk_x = world_x // 16
            chunk_z = world_z // 16
            x_in_chunk = world_x % 16
            z_in_chunk = world_z % 16

            key = (chunk_x, chunk_z)

            if key not in chunk_cache:
                chunk_cache[key] = []

            chunk_cache[key].append((x_in_chunk, base_y, z_in_chunk, block_name))
            chunk_cache[key].append((x_in_chunk, base_y - 1, z_in_chunk, "barrier"))
            
    for (chunk_x, chunk_z), keys in chunk_cache.items():
        try:
            chunk = level.get_chunk(chunk_x, chunk_z, dimension)   
        except ChunkDoesNotExist:    
            chunk = Chunk(chunk_x, chunk_z)         
            for x in range(16):
                for y in range(256):  
                    for z in range(16):
                        chunk.set_block(x, y, z, Block("minecraft", "air"))

        for (x_in_chunk, y, z_in_chunk, block_name) in keys:
            try:
                chunk.set_block(x_in_chunk, y, z_in_chunk, Block("minecraft", block_name))
            except Exception as e:
                print(f"Block not placed: {block_name}")

        chunk.changed = True
        level.put_chunk(chunk, dimension)
        print(f"Chunk ({chunk_x}, {chunk_z}) complete.")

    level.save()
    level.close()
