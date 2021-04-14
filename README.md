# Face Timelapse

This is a series of scripts designed to turn photos of a face that have been casually captured across time into a visually pleasing timelapse.
This works even if the photos have been shot at multiple locations, on an inconsistent schedule, and with a smart phone.
For example:

<p align="center">
  <img src="https://live.staticflickr.com/65535/51116327601_e2b205a9fc_o_d.gif" alt="face timelapse example"/>
</p>

The first script automatically aligns the faces and performs basic color normalization in [LAB color space](https://en.wikipedia.org/wiki/CIELAB_color_space).
The second script mixes the images temporally to reduce flicker and account for inconsistent time intervals between photos.
The final script combines the mixed images into a ```.mp4``` file.

## Usage

First, take some photos! Be sure to read the [Photo Tips section](#photo-tips) before doing that.

### Acquire Dependencies

- Python 3
- FFmpeg
- OpenCV
- NumPy
- [Pillow](https://pillow.readthedocs.io)
- [face_alignment](https://github.com/1adrianb/face-alignment)

### Align and Color Correct

Collect all of the photos you want in your timelapse into a single folder.
The order doesn't matter but they must have timestamps embedded in their EXIF data.
By default, only ```.jpg``` files will be opened but that can be changed in the [```align.py```](https://github.com/sportdeath/face_timelapse/blob/master/align.py) script.

Additionally, choose one representative photo that will define both the position of the face in the timelapse and the color normalization baseline.
This master image does not necessarily need to be in your timelapse, it just needs to include a face.
You can use any image editor to fine tune the position and color palette of that face.
Note that the color normalization is done with respect to the *eyes* (since eyes don't change much over time).

Create an empty directory for the aligned and color-corrected images. Then run:

    ./align.py MASTER_IMAGE INPUT_DIR ALIGNED_DIR

This will probably take a while.

### Mix

Create an empty directory for the mixed images.
Optionally, modify the constants in the [```mix.py```](https://github.com/sportdeath/face_timelapse/blob/master/mix.py) script.
All of these constants are measured in days:

- ```FRAME_TIME```: The length of time represented by a single output frame.
- ```MIX_TIME```: The standard deviation of the temporal blurring window (reduces flickering and jumping).
- ```OFFSET_TIME```: The additional length of time that the first and last frames of the timelapse are held.

Then run:

    ./mix.py ALIGNED_DIR MIXED_DIR

### Convert to video

Finally, convert the sequence of images to a video. Optionally, change the frame rate and quality settings in the [```img_to_vid.sh```](https://github.com/sportdeath/face_timelapse/blob/master/img_to_vid.sh) script. Then run:

    ./img_to_vid.sh MIXED_DIR OUTPUT_VIDEO.mp4

## Photo Tips

These scripts are intended to make face timelapse creation a more casual process
but a little attentiveness to how the photos are captured can have a big impact on quality.

### Lighting

The align script can correct for variations in light color but not light angle.
Shadowing from different lighting angles can cause flickering and distort one's sense of shape.
For best results, take photos that are consistently lit from the same angle.

For example, take photos lit by the lights adorning a vanity mirror.
These lights can be found in most dwellings and have a consistent placement.
They're also easy to center yourself in front of.

In addition, taking photos at night gives you better control over ambient light.

Of course, if someone were to incorporate some fancy machine learning techniques
(*e.g.*, [1](https://zhhoper.github.io/dpr.html),
[2](https://ceciliavision.github.io/project-pages/portrait))
this advice would be irrelevant.
Feel free to make a pull request :)

### Pose and Expression

The align script performs 2D corrections for faces that are off-center, tilted or scaled,
but it can't do 3D corrections like turning your head to face the camera.
So keep the pose of your head consistent.

This includes being conscious of the rotation of your chin --- you don't want your chin and forehead to grow and shrink over time.
The easiest way to maintain a consistent chin-rotation is to look forward and keep the camera at eye level (unlike your typical selfie where the camera is held above the head).

Also keep the camera at a consistent distance away (*e.g.* arms length) to avoid inconsistent [extension distortion](https://en.wikipedia.org/wiki/Selfie#Facial_distortion_effect).

Finally, try to maintain a consistent expression.
This doesn't necessarily mean a creepy deadpan; a slight smile works too.

Again, these tips would be irrelevant if someone were to incorporate some machine learning black magic.

### Scheduling

The mixing script produces a photo stream that is timed according to photo timestamps rather than photo numeracy.
Therefore, there is no need to take exactly one photo a day!
Taking bursts of photos or skipping days both work fine.
In fact, oversampling can help smooth over pose or lighting inconsistencies.
