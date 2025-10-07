# ImageToMC 
This project utilizes mainly the following:
Amulet - https://github.com/Amulet-Team/Amulet-Core
Python Imaging Library (PIL)

# Logic
## Minecraft 
An image is simply a **width x height** image. We can think about each pixel being mapped to a Minecraft block thats color is most similar, and placing it in a Minecraft world. 

In Minecraft, we can think of a pixel as a block. A chunk consists of a 16 by 16 (x by z) space, with a height of 384 blocks. 

Let's say we have an image that is 256 by 256 pixels. This means it would take a minimm of 16 chunks [ (256 * 256) / 16^2 ] to load the image. 

Each chunk would correspond to a 16 by 16 pixel space on the image.

## Mapping pixel to image 
Let's say we take a pixel of an image, and get its (r, g, b) value. We want to then connect it to some minecraft block. This requires a list of Minecraft blocks, with an average RGB value. I found a text file created online:https://drive.google.com/file/d/1omnX-MhPuN3phjWUiAzV736McyucWY-W/view. From there I utilized polars to clean the CSV file as there were some specific blocks mentioned that either didn't exist, or were labeled incorrectly. Along with that I had to manually fix some of the values for the blocks (E.g. A black pixel being translated to a slime block in minecraft). 

With this I created a dictionary, using (r, g, b) tuples as keys, and the block name as values. 

Afterwards, we need a function to map the pixel to the block. This is relatively straightforward, as it is just the distance formula. 

## Main program
generate_blocks.py is where the main program is, utilizing the Amulet API for the actual block / chunk generation. Suppose I want to load a 256 by 256 pixel image. As mentioned earlier, this would require a minimum of 16 chunks. Each chunk has a coordinate associated with it (0, 0) being the top left chunk, (0, 15) being the top right, (15, 15) being bottom right, and (15, 0) being bottom left. Within these chunks our blocks will be placed in an xz coordinate that associates with the minecraft world. 

## Problem 1
In an earlier I looped through every pixel individually, mapped the pixel color to a Minecraft block, determined which chunk the block belonged to, and cached those blocks. Later I used set_block, a function provivded by Amulet, on each block before calling put_chunk, another function provided by Amulet that actually places the chunk into the world we are editing. 

It felt repetitive to call set_block every time, as in the initial loop we are already going through each pixel and getting its block translation. From that we should know how the chunk should be created. 

### Reviewing documentation
I read the documentation for the Amulet.api package to get a better understanding of what I was working with. The Blocks class is a wrapper around UnboundedPartial3DArray, another class part of the Amulet API. This class provides a 3D array with an unbounded height for the y axis, and a fixed x and z axis. A subchunk is a portion of this infinitely high chunk, specifically 16 blocks, meaning a subchunk is a cubical 16 by 16 by 16 area. This is represented as sections, and these sections are represented as numpy arrays that contain palette indices.

In the Chunk class, these indices are mapped to a specific Block through a BlockManager object. BlockManager has a function, get_add_block, which adds a Block object to the internal Block ID mapping. 

### Solution
Now with an understanding of how exactly chunks are represented and created within the package, I took the following steps:
1. I got the specific subchunk / section I wanted to work with using a fixed y level
2. Looping through each pixel, I created the block id for the chunk, tracked it in a dictionary, and assigned it to the section, rather than putting it in the chunk later through another loop
3. Finally, I looped through the set chunks and put them into the world

## Problem 2 
The previous solution definitely sped up my program, as rather than going through the same loop equivalent of the number of pixels on the image, it goes through the number of chunks created, which would mean iterating through a loop of (number of pixels) / 256. However, a big slowdown still comes from looping through every pixel. A large image, for example, 1000 by 2000 pixel image, would take 2 million iterations! 

### Multiprocessing
Python has a multiprocessing module. Multiprocessing involves multiple processor cores working simultaneously to execute tasks in parallel. The Python module allows work to be divided between multiple processes. 

A Pool() represents multiple workers, with methods that allow tasks to be offloaded to worker processes. 

### Solution
First, I took my existing code and made it return a chunk initialized with the correct blocks based on the pixels. This function takes the image, as well as the chunk point. 

In my main function call (image_to_mc), I initalize a list of tasks, with each task in the format of (img_path, (chunk_x_coordinate, chunk_z_coordinate)). 

Then, I create a Pool.map(), which takes a function and an iterable. I created a wrapper function for the image_to_chunk function, and provide the list of tasks. The final result is all the chunks containing minecraft blocks, which we loop through and load into the world. 



