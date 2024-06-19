import subprocess
import json
import magic

def generate_progress_bar(progress, length=20):
    filled_length = int(length * progress)
    bar = '█' * filled_length + '░' * (length - filled_length)
    return bar

def format_time(seconds):
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        return f"{int(seconds // 60)}m {int(seconds % 60)}s"
    else:
        return f"{int(seconds // 3600)}h {int((seconds % 3600) // 60)}m {int(seconds % 60)}s"

def get_file_type(filepath):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(filepath)
    return file_type

def get_video_dimensions(filepath):
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "json", filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )
        dimensions = json.loads(result.stdout)
        width = dimensions['streams'][0]['width']
        height = dimensions['streams'][0]['height']
        return width, height
    except subprocess.CalledProcessError as e:
        print(f"Failed to get video dimensions: {e}")
        return None, None

def create_video_thumbnail(filepath):
    thumbnail_path = filepath + ".jpg"
    try:
        subprocess.run(
            ["ffmpeg", "-i", filepath, "-ss", "00:00:01.000", "-vframes", "1", thumbnail_path],
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to create thumbnail: {e}")
        thumbnail_path = None
    return thumbnail_path