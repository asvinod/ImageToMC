from PIL import Image
from amulet import load_level, Block
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist
from csv_functions import csv_to_dict
from getblock import getblock
import threading

img = Image.open("images/mompaint.jpg").convert("RGB")
WORLD_NAME = "gerp"
MC_PATH = "/Users/ashwin/Library/Application Support/minecraft/saves/" + WORLD_NAME

width, height = img.size
base_y = -60
blocks_placed = 0
blocks_not_placed = 0

level = load_level(MC_PATH)
color_conversion = csv_to_dict("csv/filtered_blocks_cleaned.csv")

chunk_edits = {} 

def load_img_chunk(img, point, level):
    chunk_cache = {}

    dimension = "minecraft:overworld"
    width, height = img.size
    for w in range(16):
        for h in range(16):
            world_x = point[0] + w 
            world_z = point[1] + h   

            if world_x >= width or world_z >= height:
                break
                print(world_x, world_z) 
            r, g, b = img.getpixel((world_x, world_z))
            block_name = getblock((r, g, b), color_conversion)

            try:
                block = Block("minecraft", block_name)
            except Exception as e:
                print("Block not placed:", block_name)

            #print(world_x, world_z)
            chunk_x = world_x // 16
            chunk_z = world_z // 16
            x_in_chunk = world_x % 16
            z_in_chunk = world_z % 16
            key = (chunk_x, chunk_z)

            if key not in chunk_cache:
                try:
                    chunk = level.get_chunk(chunk_x, chunk_z, dimension)
                    chunk_cache[key] = chunk
                except ChunkDoesNotExist:
                    chunk = Chunk(chunk_x, chunk_z)
                    
                    for x in range(16):
                        for y in range(256):  
                            for z in range(16):
                                chunk.set_block(x, y, z, Block("minecraft", "air"))

                    chunk_cache[key] = chunk
            else:
                chunk = chunk_cache[key]
        
            chunk.set_block(x_in_chunk, base_y, z_in_chunk, Block("minecraft", block_name))
            chunk.set_block(x_in_chunk, base_y - 1, z_in_chunk, Block("minecraft", "barrier"))

    for (chunk_x, chunk_z), chunk in chunk_cache.items():
        chunk.changed = True 
        level.put_chunk(chunk, dimension)
    level.save()

    print("Chunk (" + str(x_in_chunk) + ", " + str(z_in_chunk) + ") complete.")

threads = [] 

for num1 in range(0, width, 15):
    for num2 in range(0, height, 15):
        load_img_chunk(img, (num1, num2), level)

level.close()

#print("Blocks not placed:", blocks_not_placed)

