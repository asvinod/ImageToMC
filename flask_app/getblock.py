import math

# Function to calculate distance between two points (RGB values)
def dist(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)

# Function to get the closest block based on RGB distance
def fetchblock(target, blocks):
    def distance(pair):
        return dist(pair[0], target)
    
    # Find and return the block with the closest RGB match
    return min(blocks.items(), key=distance)[1]
