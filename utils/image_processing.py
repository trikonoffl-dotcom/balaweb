import numpy as np
from PIL import Image
import io
import cv2
import hashlib
try:
    import pillow_avif
except ImportError:
    pass
from rembg import remove, new_session
from utils.settings_manager import load_settings

# Global sessions and caches to avoid redundant work
_REMBG_SESSION = None
_IMAGE_CACHE = {} # Key: Hash, Value: Processed Bytes

def get_rembg_session():
    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        print("Creating new rembg session (u2net)...")
        _REMBG_SESSION = new_session("u2net")
        print("rembg session created.")
    return _REMBG_SESSION

def get_image_hash(image_bytes: bytes, prefix: str = ""):
    """Generates a unique hash for the image content."""
    return prefix + hashlib.md5(image_bytes).hexdigest()

def normalize_image(image_bytes: bytes) -> bytes:
    """
    Ensures image is in a format compatible with OpenCV (PNG/JPEG).
    Especially handles AVIF and WebP if plugins are present.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        # Convert to RGBA to preserve transparency if it's there
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
    except Exception as e:
        print(f"Normalization failed: {e}")
        return image_bytes

def resize_image_bytes(image_bytes, max_width=1024):
    """
    Resizes image bytes to a maximum width to speed up processing.
    Returns bytes.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        # Calculate new dimensions
        width, height = image.size
        if width > max_width:
            ratio = max_width / width
            new_height = int(height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save back to bytes
            buf = io.BytesIO()
            # Convert to RGB if necessary (e.g. for JPEG saving) BUT we want to keep transparency if PNG
            if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
                 format = "PNG"
            else:
                 format = "JPEG"
                 
            image.save(buf, format=format, quality=85)
            return buf.getvalue()
        
        return image_bytes
    except Exception as e:
        print(f"Resize failed: {e}")
        return image_bytes

def remove_background(image_bytes):
    """Local background removal using rembg with session support."""
    # Normalize first
    image_bytes = normalize_image(image_bytes)
    
    img_hash = get_image_hash(image_bytes, "bg_")
    if img_hash in _IMAGE_CACHE:
        print(f"Cache hit for BG removal")
        return _IMAGE_CACHE[img_hash]
        
    try:
        # Optimize: Resize before processing to significantly boost speed
        optimized_bytes = resize_image_bytes(image_bytes, max_width=800)
        session = get_rembg_session()
        result = remove(optimized_bytes, session=session)
        
        # Cache the result
        _IMAGE_CACHE[img_hash] = result
        return result
    except Exception as e:
        print(f"Local background removal failed: {e}")
        return None

def get_face_cascade():
    """Returns the face cascade classifier."""
    return cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def auto_crop_face(image_bytes):
    """
    Smartly crops the image to a Head-to-Chest composition for ID Cards.
    Target Ratio: ~0.97 (95x98)
    """
    # Normalize first to support AVIF/WebP in CV2
    image_bytes = normalize_image(image_bytes)
    
    img_hash = get_image_hash(image_bytes, "crop_id_")
    if img_hash in _IMAGE_CACHE:
        print(f"Cache hit for Auto-crop ID")
        return _IMAGE_CACHE[img_hash]

    try:
        # Optimize: Resize first
        image_bytes = resize_image_bytes(image_bytes, max_width=1024)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return image_bytes

        # Convert to grayscale for detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        face_cascade = get_face_cascade()
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return image_bytes # No face found, return original
            
        # Pick the largest face (x, y, w, h)
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        x, y, w, h = faces[0]
        
        settings = load_settings().get("auto_crop", {}).get("id_card", {})
        
        # Widened Ratio to preserve shoulders (more horizontal space)
        target_ratio = settings.get("target_ratio", 1.2)
        
        # Determine crop height - slightly higher headroom
        crop_top = max(0, int(y - settings.get("top_headroom", 0.7) * h))
        crop_bottom = min(img.shape[0], int(y + h + settings.get("bottom_extension", 1.2) * h))
        crop_h = crop_bottom - crop_top
        
        # Determine crop width based on ratio
        crop_w = int(crop_h * target_ratio)
        
        # Centering width around face center
        face_center_x = x + w // 2
        crop_left = max(0, face_center_x - crop_w // 2)
        crop_right = min(img.shape[1], crop_left + crop_w)
        
        # Adjust if we hit edges
        if crop_right - crop_left < crop_w:
            crop_left = max(0, crop_right - crop_w)
            
        # Crop
        cropped_img = img[crop_top:crop_bottom, crop_left:crop_right]
        
        # Convert back to bytes
        is_success, buffer = cv2.imencode(".png", cropped_img)
        result = buffer.tobytes()
        _IMAGE_CACHE[img_hash] = result
        return result
        
    except Exception as e:
        print(f"Auto-crop failed: {e}")
        return image_bytes

def smart_crop_welcome(image_bytes):
    """
    Smartly crops the image for Welcome Aboard (Head focused, Center Face).
    Target: Square-ish or slightly rectangular to fit the rounded box.
    """
    # Normalize first
    image_bytes = normalize_image(image_bytes)
    
    img_hash = get_image_hash(image_bytes, "crop_welcome_")
    if img_hash in _IMAGE_CACHE:
        print(f"Cache hit for Welcome crop")
        return _IMAGE_CACHE[img_hash]
        
    try:
        # Optimize: Resize first
        image_bytes = resize_image_bytes(image_bytes, max_width=1024)
        
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return image_bytes

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_cascade = get_face_cascade()
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return image_bytes

        # Largest face
        faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
        x, y, w, h = faces[0]
        
        face_center_x = x + w // 2
        
        # For Welcome Aboard, we want a nice portrait crop.
        # Let's aim for a ratio similar to the box (421/502 ~= 0.84)
        target_ratio = 422 / 502
        
        # More generous vertical framing for welcome card
        crop_top = max(0, int(y - 0.8 * h)) # More headroom
        crop_bottom = min(img.shape[0], int(y + h + 1.5 * h)) # Down to chest/mid-torso
        crop_h = crop_bottom - crop_top
        
        crop_w = int(crop_h * target_ratio)
        
        crop_left = max(0, face_center_x - crop_w // 2)
        crop_right = min(img.shape[1], crop_left + crop_w)
        
        if crop_right - crop_left < crop_w:
             crop_left = max(0, crop_right - crop_w)
             
        cropped_img = img[crop_top:crop_bottom, crop_left:crop_right]
        
        is_success, buffer = cv2.imencode(".png", cropped_img)
        result = buffer.tobytes()
        _IMAGE_CACHE[img_hash] = result
        return result

    except Exception as e:
        print(f"Welcome Smart Crop failed: {e}")
        return image_bytes
