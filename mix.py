#!/usr/bin/env python3

import os
import numpy as np
from PIL import Image

MIX_TIME = 5 # days
FRAME_TIME = 2. # days
EPSILON = 0.0001
INPUT_DIR = "dst"
OUTPUT_DIR = "mixed"
IMAGE_WIDTH = 960
IMAGE_HEIGHT = 1280

def gaussian_pdf(x, mean, std_dev):
    normalization = 1/(std_dev * np.sqrt(2 * np.pi))
    x_ = (x - mean)/std_dev
    return normalization * np.exp(-0.5 * x_ * x_)

# Get a list of all the image times
files = os.listdir(INPUT_DIR)
files = [f for f in files if f.endswith(".jpg")]
files.sort()
times = [int(x[:-4]) for x in files]

# Convert the times to days
times = np.array(times)
times -= times[0]
times = times/86400.

# Calculate a weight for each time
weights = np.empty(times.shape)
for i, t in enumerate(times):
    weights[i] = 1./np.sum(gaussian_pdf(times, t, MIX_TIME))

# Sample time at a constant rate
frames = np.arange(times[0], times[-1], FRAME_TIME)

for i, t in enumerate(frames):
    # Calculate the relative weight of every picture in the frame
    probs = weights * gaussian_pdf(times, t, MIX_TIME)
    # Get rid of ones with negligible effect
    # so this doesn't take forever
    probs[probs < EPSILON] = 0
    probs = probs/np.sum(probs)

    # Open and mix all the in the frame
    out = np.zeros((IMAGE_HEIGHT, IMAGE_WIDTH, 3))
    for j, p in enumerate(probs):
        if p > 0:
            # Open the image
            f = os.path.join(INPUT_DIR, files[j])
            img = np.array(Image.open(f)).astype("float32")
            out += p * img

    # Write the output
    img = Image.fromarray(out.astype("uint8"))
    fn = os.path.join(OUTPUT_DIR, str(i).zfill(5) + ".jpg")
    img.save(fn)
    print("processed", fn)
