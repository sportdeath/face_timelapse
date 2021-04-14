#!/bin/sh

filters="fps=60"
ffmpeg -v warning -pattern_type glob -i "$1/*.jpg" -vf "$filters" -c:v libx265 -pix_fmt yuv420p -b:v 10000k -y $2
