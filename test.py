from PIL import Image

img = Image.open("images/john.png").convert("RGB")
print(img.size)