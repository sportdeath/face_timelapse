#!/bin/sh

palette="/tmp/palette.png"
filters="fps=30:flags=lanczos"

ffmpeg -v warning -pattern_type glob -i "$1/*.jpg" -vf  "$filters,palettegen" -y $palette
ffmpeg -v warning -pattern_type glob -i "$1/*.jpg" -i $palette -lavfi "$filters [x]; [x][1:v] paletteuse" -y $2
