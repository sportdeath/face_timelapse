#!/usr/bin/env python3

import os
import time
import datetime
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS
import face_alignment

INPUT_DIR  = "src"
OUTPUT_DIR = "dst"
MASTER = "src/49414767827_6abc65fd8a_o.jpg"

fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, device='cpu')

def master_align(img):
    face = fa.get_landmarks_from_image(img)[0]

    A = np.zeros((2*face.shape[0], 4))
    A[0::2,0] =  face[:,0]
    A[0::2,1] =  face[:,1]
    A[0::2,2] =  1
    A[1::2,0] =  face[:,1]
    A[1::2,1] = -face[:,0]
    A[1::2,3] =  1

    return np.matmul(np.linalg.inv(np.matmul(A.T, A)), A.T)

def align(img, master_landmarks):
    landmarks = fa.get_landmarks_from_image(img)

    if len(landmarks) == 0:
        return None

    face = landmarks[0]

    # A least squares transformation that does
    # translation, rotation and uniform scaling
    # (if it were affine, the face can stretch in weird ways)
    affine_trans = np.matmul(master_landmarks, face.flatten())
    affine_trans = np.array([
        [ affine_trans[0], affine_trans[1], affine_trans[2]],
        [-affine_trans[1], affine_trans[0], affine_trans[3]]])

    img = cv2.warpAffine(
            img, affine_trans,
            (img.shape[1], img.shape[0]),
            flags=cv2.WARP_INVERSE_MAP)

    return img

if __name__ == "__main__":
    # Preprocess the master
    img_dat = Image.open(MASTER)
    img = np.array(img_dat)
    ml = master_align(img)

    # Open all the files
    for f in os.listdir(INPUT_DIR):
        if f.endswith(".jpg"):
            # Open the image
            fn = os.path.join(INPUT_DIR, f)
            img_dat = Image.open(fn)
            img = np.array(img_dat)

            # Process the file
            img = align(img, ml)

            # Save the image
            if img is not None:
                # Extract the time
                t = img_dat.getexif().get(306)
                t = datetime.datetime.strptime(t, "%Y:%m:%d %H:%M:%S")
                t = int(time.mktime(t.timetuple()))
                print(t)

                img_dat = Image.fromarray(img)
                fn = os.path.join(OUTPUT_DIR, str(t) + ".jpg")
                img_dat.save(fn)
