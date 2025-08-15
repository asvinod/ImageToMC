import shutil
from pathlib import Path 
from amulet import load_level
import zipfile
from PIL import Image
from generate_blocks_copy import image_to_blocks

# Creates new save folder 
def create_world_copy(world_name):
    base_world_path = Path("/Users/ashwin/Library/Application Support/minecraft/saves/")
    new_world_path = Path(world_name)
    shutil.copytree(base_world_path, new_world_path)
    return new_world_path

def modify_world(world_path, img):
    level = load_level(str(world_path))
    image_to_blocks(img, level)
    level.save()
    level.close() 

def zip_world(world_path):
    zip_path = f"{world_path}.zip" 
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in Path(world_path).rglob('*'):
            zipf.write(file, file.relative_to(world_path.parent))
    return zip_path

def build_and_export_map(world_name="CustomWorld", img=""):
    path = create_world_copy(world_name)
    modify_world(path, img)
    zip_path = zip_world(path)
    print(f"World created and zipped at: f{zip_path}")

img = Image.open("images/mompaint.jpg").convert("RGB")
build_and_export_map("MyWorld", img)




