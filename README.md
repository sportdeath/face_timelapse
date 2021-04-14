# Face Timelapse

This is a series of scripts designed to turn images of a face that have been casually-captured across time into a visually pleasing timelapse. For example:

*INSERT GIF HERE*

The first script automatically aligns the faces and performs basic color normalization in [LAB color space](https://en.wikipedia.org/wiki/CIELAB_color_space).
The second script mixes the images temporally to reduce flicker and account for inconsistent time intervals between photos.
The final script combines the mixed images into a ```.mp4``` file.

## Dependencies

- Python 3
- FFmpeg
- OpenCV
- NumPy
- [Pillow](https://pillow.readthedocs.io)
- [face_alignment](https://github.com/1adrianb/face-alignment)

## Usage

Put all of the images you want to make into a timelapse into a single folder.
The order doesn't matter but they must have timestamps embedded in their EXIF data.
By default this script will only search for ```.jpg``` files, but that can be changed in the [```align.py```](https://github.com/sportdeath/face_timelapse/blob/master/align.py) script.

Additionally, choose one representative photo that will define both the position of the face in the timelapse and the color normalization parameters.
This master image does not necessarily need to be in your timelapse.
Additionally, note in your choice that the color normalization is done with respect to the *eyes* (since eyes don't change much over time).

### Align

Create a directory for the aligned images. Then run:

    ./align.py MASTER_IMAGE INPUT_DIR ALIGNED_DIR

This will probably take a while.

### Mix

Create a directory for the mixed images.
Optionally, modify the constants in the [```mix.py```](https://github.com/sportdeath/face_timelapse/blob/master/mix.py) script.
All of these are measured in days:

- ```FRAME_TIME```: The length of time represented by a single frame.
- ```MIX_TIME```: The standard deviation of the temporal blurring window.
- ```OFFSET_TIME```: The additional length of time that the first and last frames of the timelapse are held.

Then run:

    ./mix.py ALIGNED_DIR MIXED_DIR

### Convert to video

Finally, convert the sequence of images to a video. Optionally, change the frame rate and quality settings in the [```img_to_vid.sh```](https://github.com/sportdeath/face_timelapse/blob/master/img_to_vid.sh) script. Then run:

    ./img_to_vid.sh MIXED_DIR OUTPUT_VIDEO.mp4
