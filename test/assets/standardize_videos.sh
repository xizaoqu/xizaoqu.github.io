#!/bin/bash

# Target resolution and FPS
TARGET_WIDTH=416
TARGET_HEIGHT=256
TARGET_FPS=30

# Base directory
BASE_DIR="/mnt/sma-intern25-zeqi/projects/wan_ttt/lact_ar_video/minVid/no_uploading/eliahuhorwitz.github.io/Academic-project-page-template/assets"

cd "$BASE_DIR"

echo "Starting video standardization..."
echo "Target: ${TARGET_WIDTH}x${TARGET_HEIGHT} @ ${TARGET_FPS}fps"
echo ""

# Find all MP4 files, excluding teaser directory
find . -path "./teaser" -prune -o -name "*.mp4" -type f -print | sort | while read -r video; do
    echo "Processing: $video"
    
    # Get the directory and filename without extension
    dir=$(dirname "$video")
    filename=$(basename "$video" .mp4)
    
    # Create temporary output file
    temp_output="${dir}/${filename}_temp.mp4"
    poster_output="${dir}/${filename}.jpg"
    
    # Convert video to target resolution and FPS
    # Capture output to a variable to show on error
    if output=$(ffmpeg -nostdin -i "$video" -vf "scale=${TARGET_WIDTH}:${TARGET_HEIGHT}:force_original_aspect_ratio=decrease,pad=${TARGET_WIDTH}:${TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,setpts=N/(${TARGET_FPS}*TB)" -r ${TARGET_FPS} -c:v libx264 -preset medium -crf 23 -an -y "$temp_output" 2>&1); then
        # Replace original with converted video
        mv "$temp_output" "$video"
        echo "  ✓ Video converted"
    else
        echo "  ✗ Video conversion failed"
        echo "FFmpeg output:"
        echo "$output"
        rm -f "$temp_output"
        exit 1
    fi
    
    # Generate poster (first frame)
    if output=$(ffmpeg -nostdin -i "$video" -vframes 1 -f image2 -y "$poster_output" 2>&1); then
        echo "  ✓ Poster generated: ${filename}.jpg"
    else
        echo "  ✗ Poster generation failed"
        echo "FFmpeg output:"
        echo "$output"
        exit 1
    fi
    
    echo ""
done

echo "All videos processed!"
