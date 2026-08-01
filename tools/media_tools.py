"""
Media & Image Processing Automation Tools.
Refactored from ImageEditor.py and ytdownloader.py.
"""

import os
from typing import Optional
from agent.tools import tool

@tool(is_destructive=False)
def batch_edit_images(
    input_dir: str = "./imgs",
    output_dir: str = "./editedImgs",
    sharpen: bool = True,
    convert_grayscale: bool = True,
    rotate_angle: float = -90.0,
    contrast_factor: float = 1.5
) -> str:
    """
    Batch process and edit images in a directory (sharpening, contrast, grayscale conversion, rotation).
    Refactored from ImageEditor.py.

    Args:
        input_dir: Directory containing raw unedited images. Defaults to "./imgs".
        output_dir: Target directory to save processed images. Defaults to "./editedImgs".
        sharpen: Apply sharpening filter if True.
        convert_grayscale: Convert image to black & white (L mode) if True.
        rotate_angle: Rotation angle in degrees (e.g. -90).
        contrast_factor: Contrast adjustment multiplier (e.g. 1.5).

    Returns:
        Summary of processed images.
    """
    try:
        from PIL import Image, ImageEnhance, ImageFilter
    except ImportError:
        return "Error: Pillow library is not installed. Install via `pip install pillow`."

    if not os.path.exists(input_dir):
        return f"Error: Input directory '{input_dir}' does not exist."

    os.makedirs(output_dir, exist_ok=True)
    processed_count = 0
    errors = []

    valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')

    for filename in os.listdir(input_dir):
        if not filename.lower().endswith(valid_extensions):
            continue

        filepath = os.path.join(input_dir, filename)
        try:
            with Image.open(filepath) as img:
                edit = img.copy()

                if sharpen:
                    edit = edit.filter(ImageFilter.SHARPEN)

                if convert_grayscale:
                    edit = edit.convert('L')

                if rotate_angle != 0:
                    edit = edit.rotate(rotate_angle, expand=True)

                if contrast_factor != 1.0:
                    enhancer = ImageEnhance.Contrast(edit)
                    edit = enhancer.enhance(contrast_factor)

                clean_name = os.path.splitext(filename)[0]
                out_path = os.path.join(output_dir, f"{clean_name}_edited.jpg")
                
                # Save as RGB/L JPEG
                if edit.mode not in ('RGB', 'L'):
                    edit = edit.convert('RGB')
                    
                edit.save(out_path, format="JPEG")
                processed_count += 1
        except Exception as e:
            errors.append(f"Failed '{filename}': {str(e)}")

    summary = [f"Successfully processed {processed_count} images from '{input_dir}' -> saved to '{output_dir}'."]
    if errors:
        summary.append(f"Errors ({len(errors)}):\n" + "\n".join(errors))

    return "\n".join(summary)


@tool
def download_youtube_video(url: str, output_path: str = ".") -> str:
    """
    Download a YouTube video at highest available resolution.
    Refactored from ytdownloader.py. Supports yt-dlp with pytube fallback.

    Args:
        url: The YouTube video web URL.
        output_path: Target directory to save the downloaded video file. Defaults to ".".

    Returns:
        Confirmation message with video details.
    """
    os.makedirs(output_path, exist_ok=True)

    # Attempt 1: try yt-dlp first (most robust)
    try:
        import yt_dlp
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'best',
            'quiet': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'Video')
            return f"Successfully downloaded YouTube video using yt-dlp: '{title}' to '{output_path}'."
    except Exception as e_ytdlp:
        # Attempt 2: fallback to pytube
        try:
            from pytube import YouTube
            yt = YouTube(url)
            title = yt.title
            views = yt.views
            yd = yt.streams.get_highest_resolution()
            yd.download(output_path=output_path)
            return f"Successfully downloaded YouTube video using pytube: '{title}' ({views} views) to '{output_path}'."
        except Exception as e_pytube:
            return f"Failed to download YouTube video. yt-dlp error: {str(e_ytdlp)} | pytube error: {str(e_pytube)}"


@tool
def get_youtube_video_info(url: str) -> str:
    """
    Fetch metadata (title, views, duration, author) for a YouTube video URL without downloading.

    Args:
        url: YouTube video URL.
    """
    try:
        import yt_dlp
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title')
            uploader = info.get('uploader')
            duration = info.get('duration')
            view_count = info.get('view_count')
            return (
                f"YouTube Video Info:\n"
                f"Title: {title}\n"
                f"Uploader: {uploader}\n"
                f"Duration: {duration} seconds\n"
                f"Views: {view_count}"
            )
    except Exception:
        try:
            from pytube import YouTube
            yt = YouTube(url)
            return (
                f"YouTube Video Info:\n"
                f"Title: {yt.title}\n"
                f"Views: {yt.views}\n"
                f"Length: {yt.length} seconds\n"
                f"Author: {yt.author}"
            )
        except Exception as e:
            return f"Error retrieving YouTube info: {str(e)}"
