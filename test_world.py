from amulet import load_level, Block
from amulet.api.chunk import Chunk
from amulet.api.errors import ChunkDoesNotExist

MC_PATH = "/Users/ashwin/Library/Application Support/minecraft/saves/test_art"
dimension = "minecraft:overworld"
chunk_x, chunk_z = 0, 0
x, z = 1, 1
base_y = 120

level = load_level(MC_PATH)

try:
    chunk = level.get_chunk(chunk_x, chunk_z, dimension)
except ChunkDoesNotExist:
    print("Creating new chunk")
    chunk = Chunk(chunk_x, chunk_z)
    level.put_chunk(chunk, dimension)

block = Block("minecraft", "red_concrete")
chunk.set_block(x, base_y, z, block)

level.save()
level.close()

print("✅ Placed red_concrete at (1, 120, 1)")
