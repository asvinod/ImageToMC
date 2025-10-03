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
Let's say we take a pixel of an image, and get its (r, g, b) value. We want to then connect it to some minecraft block. This requires a list of Minecraft blocks, with an average RGB value. 

Afterwards, we need a function to map the pixel to the block. This is relatively straightforward, as it is just the distance formula. 




