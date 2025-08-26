from PIL import Image
import numpy as np

value = np.zeros((16, 16, 16), dtype=np.uint32)
value[0][0][0] = 5
print(value)
