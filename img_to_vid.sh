#!/usr/bin/env bash

FRAMES_PER_SECOND=60

# The smaller the CRF, the higher the quality
# but bigger the video. For more info see:
# https://trac.ffmpeg.org/wiki/Encode/H.264#crf
CONSTANT_RATE_FACTOR=12

ffmpeg -v warning -r $FRAMES_PER_SECOND -i "$1/%08d.jpg" -c:v libx265 -crf $CONSTANT_RATE_FACTOR -preset fast -pix_fmt yuv420p -tag:v hvc1 -y $2
