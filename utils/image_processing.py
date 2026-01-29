import cv2
import numpy as np
import streamlit as st
from rembg import remove

def remove_background(image_bytes):
    """Local background removal using rembg."""
    try:
        return remove(image_bytes)
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
    try:
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
        
        face_center_x = x + w // 2
        
        # ID Card Slot Ratio (Matches the PDF slot 95x98 approx 0.97)
        target_ratio = 95 / 98 
        
        # Determine crop height based on face size logic
        crop_top = max(0, int(y - 0.6 * h))
        crop_bottom = min(img.shape[0], int(y + h + 1.2 * h))
        crop_h = crop_bottom - crop_top
        
        # Determine crop width based on ratio
        crop_w = int(crop_h * target_ratio)
        
        # Centering width around face center
        crop_left = max(0, face_center_x - crop_w // 2)
        crop_right = min(img.shape[1], crop_left + crop_w)
        
        # Adjust if we hit edges
        if crop_right - crop_left < crop_w:
            crop_left = max(0, crop_right - crop_w)
            
        # Crop
        cropped_img = img[crop_top:crop_bottom, crop_left:crop_right]
        
        # Convert back to bytes
        is_success, buffer = cv2.imencode(".png", cropped_img)
        return buffer.tobytes()
        
    except Exception as e:
        print(f"Auto-crop failed: {e}")
        return image_bytes

def smart_crop_welcome(image_bytes):
    """
    Smartly crops the image for Welcome Aboard (Head focused, Center Face).
    Target: Square-ish or slightly rectangular to fit the rounded box.
    """
    try:
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
        return buffer.tobytes()

    except Exception as e:
        print(f"Welcome Smart Crop failed: {e}")
        return image_bytes
