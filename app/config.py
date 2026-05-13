
#setari precum caile folderelor de upload, extensii permise, limite de dimensiune

IMAGE_UPLOAD_DIR = "uploads/images"
VIDEO_UPLOAD_DIR = "uploads/videos"

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

# videoclipul il analizam la fiecare 10 frame-uri
DEFAULT_FRAME_SKIP = 10


MAX_VIDEO_SIZE_MB = 100
MAX_IMAGE_SIZE_MB = 10