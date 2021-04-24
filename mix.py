#!/usr/bin/env python3

import os
import numpy as np
from PIL import Image
import sys

# Mixing parameters
FRAME_TIME    =   0.25 # days
MIX_TIME      =   3.   # days
MAX_DIFF_TIME =   2.   # days
OFFSET_TIME   =  50.   # days

def gaussian_pdf(x, mean, std_dev):
    normalization = 1/(std_dev * np.sqrt(2 * np.pi))
    x_ = (x - mean)/std_dev
    return normalization * np.exp(-0.5 * x_ * x_)

# Parse the arguments
if len(sys.argv) != 3:
    print(f"usage: {sys.argv[0]} ALIGNED_DIR MIXED_DIR")
    sys.exit()
ALIGNED_DIR  = sys.argv[1]
MIXED_DIR = sys.argv[2]

# Get a list of all the image times
files = os.listdir(ALIGNED_DIR)
files = [f for f in files if f.endswith(".jpg")]
files.sort()
times = [int(x[:-4]) for x in files]

# Convert the times to days
times = np.array(times)
times -= times[0]
times = times/86400.

# Clip the difference between times
diff = np.diff(times)
diff[diff > MAX_DIFF_TIME] = MAX_DIFF_TIME
times = np.cumsum(diff)
times = np.insert(times, 0, 0)

# Calculate a weight for each time
weights = np.empty(times.shape)
for i, t in enumerate(times):
    weights[i] = 1./np.sum(gaussian_pdf(times, t, MIX_TIME))

# Sample time at a constant rate
frames = np.arange(times[0] - OFFSET_TIME, times[-1] + OFFSET_TIME, FRAME_TIME)

# Fetch the height and width
f0 = os.path.join(ALIGNED_DIR, files[0])
width, height = Image.open(f0).size

for i, t in enumerate(frames):
    # Calculate the relative weight of every picture in the frame
    probs = weights * gaussian_pdf(times, t, MIX_TIME)
    # Get rid of ones with negligible effect
    # so this doesn't take forever
    probs = probs/np.sum(probs)
    probs[probs < 0.0001] = 0
    probs = probs/np.sum(probs)

    # Open and mix all the images in the frame
    out = np.zeros((height, width, 3))
    for j, p in enumerate(probs):
        if p > 0:
            # Open the image
            f = os.path.join(ALIGNED_DIR, files[j])
            img = np.array(Image.open(f)).astype("float32")
            out += p * img

    # Write the output
    img = Image.fromarray(out.astype("uint8"))
    fn = os.path.join(MIXED_DIR, str(i).zfill(8) + ".jpg")
    img.save(fn)
    print("processed", fn)
