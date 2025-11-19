#!/usr/bin/env python3
"""Standardize all MP4 videos to the same resolution and FPS, and generate posters."""

import subprocess
from pathlib import Path

# Target specifications
TARGET_WIDTH = 416
TARGET_HEIGHT = 256
TARGET_FPS = 30

# Base directory
BASE_DIR = Path("/mnt/sma-intern25-zeqi/projects/wan_ttt/lact_ar_video/minVid/no_uploading/eliahuhorwitz.github.io/Academic-project-page-template/assets")

def get_video_info(video_path: Path) -> tuple[int, int, float] | None:
    """Get video resolution and FPS."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate",
                "-of", "csv=p=0",
                str(video_path)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        width, height, fps_str = result.stdout.strip().split(",")
        # Parse FPS (might be in format "30/1")
        if "/" in fps_str:
            num, den = map(float, fps_str.split("/"))
            fps = num / den
        else:
            fps = float(fps_str)
        return int(width), int(height), fps
    except Exception as e:
        print(f"  ✗ Error getting video info: {e}")
        return None

def convert_video(video_path: Path) -> bool:
    """Convert video to target resolution and FPS."""
    temp_output = video_path.with_suffix(".temp.mp4")
    
    try:
        # Convert video
        subprocess.run(
            [
                "ffmpeg", "-i", str(video_path),
                "-vf", f"scale={TARGET_WIDTH}:{TARGET_HEIGHT}:force_original_aspect_ratio=decrease,pad={TARGET_WIDTH}:{TARGET_HEIGHT}:(ow-iw)/2:(oh-ih)/2,fps={TARGET_FPS}",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "23",
                "-c:a", "aac",
                "-b:a", "128k",
                "-y", str(temp_output)
            ],
            capture_output=True,
            check=True
        )
        
        # Replace original with converted video
        temp_output.replace(video_path)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Conversion failed: {e}")
        if temp_output.exists():
            temp_output.unlink()
        return False

def generate_poster(video_path: Path) -> bool:
    """Generate poster image from first frame."""
    poster_path = video_path.with_suffix(".jpg")
    
    try:
        subprocess.run(
            [
                "ffmpeg", "-i", str(video_path),
                "-vframes", "1",
                "-f", "image2",
                "-y", str(poster_path)
            ],
            capture_output=True,
            check=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Poster generation failed: {e}")
        return False

def main():
    """Process all MP4 files."""
    print("Starting video standardization...")
    print(f"Target: {TARGET_WIDTH}x{TARGET_HEIGHT} @ {TARGET_FPS}fps")
    print()
    
    # Find all MP4 files
    video_files = sorted(BASE_DIR.rglob("*.mp4"))
    
    for video_path in video_files:
        rel_path = video_path.relative_to(BASE_DIR)
        print(f"Processing: {rel_path}")
        
        # Get current video info
        info = get_video_info(video_path)
        if info:
            width, height, fps = info
            print(f"  Current: {width}x{height} @ {fps:.2f}fps")
            
            # Check if conversion is needed
            if width == TARGET_WIDTH and height == TARGET_HEIGHT and abs(fps - TARGET_FPS) < 0.1:
                print("  ⚡ Already at target specs, skipping conversion")
            else:
                # Convert video
                if convert_video(video_path):
                    print("  ✓ Video converted")
                else:
                    print("  ✗ Video conversion failed")
                    continue
        else:
            print("  Attempting conversion anyway...")
            if convert_video(video_path):
                print("  ✓ Video converted")
            else:
                print("  ✗ Video conversion failed")
                continue
        
        # Generate poster
        if generate_poster(video_path):
            print(f"  ✓ Poster generated: {rel_path.stem}.jpg")
        else:
            print("  ✗ Poster generation failed")
        
        print()
    
    print("All videos processed!")

if __name__ == "__main__":
    main()


