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
MASTER = "master.jpg"

fa = face_alignment.FaceAlignment(face_alignment.LandmarksType._2D, device='cpu')

def extract_face(img):
    faces = fa.get_landmarks_from_image(img)

    if len(faces) == 0:
        return None

    return faces[0]

def master_align(img, face):
    A = np.zeros((2*face.shape[0], 4))
    A[0::2,0] =  face[:,0]
    A[0::2,1] =  face[:,1]
    A[0::2,2] =  1
    A[1::2,0] =  face[:,1]
    A[1::2,1] = -face[:,0]
    A[1::2,3] =  1

    return np.matmul(np.linalg.inv(np.matmul(A.T, A)), A.T)

def align(img, face, master_trans, master_shape):
    # A least squares transformation that does
    # translation, rotation and uniform scaling
    # (if it were affine, the face can stretch in weird ways)
    affine_trans = np.matmul(master_trans, face.flatten())
    affine_trans = np.array([
        [ affine_trans[0], affine_trans[1], affine_trans[2]],
        [-affine_trans[1], affine_trans[0], affine_trans[3]]])

    img = cv2.warpAffine(
            img, affine_trans,
            (master_shape[1], master_shape[0]),
            flags=cv2.WARP_INVERSE_MAP)

    return img

def extract_eyes(img, face):
    start, end = 36, 48
    xmin = int(np.amin(face[start:end,0]))
    xmax = int(np.amax(face[start:end,0]))
    ymin = int(np.amin(face[start:end,1]))
    ymax = int(np.amax(face[start:end,1]))

    return img[ymin:ymax, xmin:xmax]

def rgb_to_lab(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2LAB).astype("float32")

def lab_to_rgb(img):
    return cv2.cvtColor(img.astype("uint8"), cv2.COLOR_LAB2RGB)

def color_stats(img):
    avg = np.mean(img, (0,1))
    dev = np.std (img, (0,1))

    return avg, dev

def color_correct(img, eyes, master_avg, master_dev):
    avg, dev = color_stats(eyes)

    img =  (img - avg) * (master_dev/dev) + master_avg

    return np.clip(img, 0, 255)

if __name__ == "__main__":
    # Open the master
    master_dat = Image.open(MASTER)
    master = np.array(master_dat)

    # Extract facial landmarks and transform
    master = np.rot90(master, -1)
    master_face = extract_face(master)
    master_trans = master_align(master, master_face)

    # Extract color information from eyes
    master = rgb_to_lab(master)
    master_eyes = extract_eyes(master, master_face)
    master_avg, master_dev = color_stats(master_eyes)

    print("Preprocessed master image")

    # Open all the files
    for f in os.listdir(INPUT_DIR):
        if f.endswith(".jpg"):
            # Open the image
            fn = os.path.join(INPUT_DIR, f)
            img_dat = Image.open(fn)
            img = np.array(img_dat)

            # Rotate?
            img = np.rot90(img, -1)

            # Extract facial landmarks
            face = extract_face(img)

            # Convert to lab space and color correct
            img = rgb_to_lab(img)
            eyes = extract_eyes(img, face)
            img  = color_correct(img, eyes, master_avg, master_dev)
            img = lab_to_rgb(img)

            # Align the image
            img = align(img, face, master_trans, master.shape)

            # Save the image
            if img is not None:
                # Extract the time
                try:
                    t = img_dat.getexif().get(306)
                    t = datetime.datetime.strptime(t, "%Y:%m:%d %H:%M:%S")
                    t = int(time.mktime(t.timetuple()))
                except:
                    t = 0

                img_dat = Image.fromarray(img)
                fn = os.path.join(OUTPUT_DIR, str(t) + ".jpg")
                img_dat.save(fn)

                print("Processed image from time", t)
