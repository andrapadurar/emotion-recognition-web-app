

IMAGE_UPLOAD_DIR = "uploads/images"
VIDEO_UPLOAD_DIR = "uploads/videos"


#extensii permise
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

#un videoclip este analizat la fiecare 10 frame-uri
DEFAULT_FRAME_SKIP = 10

#dimensiunea maximă pentru fișierele încărcate
MAX_VIDEO_SIZE_MB = 100
MAX_IMAGE_SIZE_MB = 10