from rembg import remove, new_session
import PIL.Image
import io

def test_rembg():
    try:
        print("Initializing rembg session...")
        session = new_session("u2net")
        print("Session initialized.")
        
        # Create a dummy image
        img = PIL.Image.new('RGB', (100, 100), color = 'red')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()
        
        print("Removing background...")
        result = remove(img_bytes, session=session)
        print(f"Success! Result size: {len(result)} bytes")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_rembg()
