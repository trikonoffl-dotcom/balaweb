from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from typing import Optional
import sys
import os
import datetime
import asyncio

# Add root directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processing import remove_background, auto_crop_face, smart_crop_welcome
from utils.pdf_generator import generate_id_card_pdf, generate_id_card_preview
from utils.welcome_generator import generate_welcome_image
from utils.business_card_generator import generate_business_card_pdf, generate_business_card_preview
from utils.settings_manager import load_settings, save_settings

app = FastAPI()

# Allow CORS for local dev and Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, restrict this to your Cloudflare domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Trikon API is running"}

@app.post("/api/remove-bg")
async def api_remove_bg(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        print(f"BG Removal request: {file.filename}, {len(contents)} bytes")
        # Offload heavy ML task to threadpool
        processed = await run_in_threadpool(remove_background, contents)
        if processed:
            print(f"BG Removal success: {len(processed)} bytes")
            return Response(content=processed, media_type="image/png")
        
        print("BG Removal failed: remove_background returned None")
        return Response(content='{"error": "Failed to process"}', status_code=500, media_type="application/json")
    except Exception as e:
        print(f"BG Removal Critical error: {e}")
        return Response(content=f'{{"error": "{str(e)}"}}', status_code=500, media_type="application/json")

@app.post("/api/auto-crop")
async def api_auto_crop(file: UploadFile = File(...), type: str = Form("id_card")):
    contents = await file.read()
    if type == "welcome":
        processed = await run_in_threadpool(smart_crop_welcome, contents)
    else:
        processed = await run_in_threadpool(auto_crop_face, contents)
    
    return Response(content=processed, media_type="image/png")

@app.post("/api/preview-id-card")
async def api_preview_id_card(
    file: UploadFile = File(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    title: str = Form(...),
    id_number: str = Form(...),
    doj: str = Form(...),
    emergency_no: str = Form(...),
    blood_group: str = Form(...),
    office_address: str = Form(...),
    scale: float = Form(1.0),
    x_offset: int = Form(0),
    y_offset: int = Form(0),
    use_auto_crop: bool = Form(True),
    use_ai_removal: bool = Form(True)
):
    contents = await file.read()
    
    # Parallelize pre-processing
    tasks = []
    if use_auto_crop:
        tasks.append(run_in_threadpool(auto_crop_face, contents))
    else:
        # If no crop, just pass contents through
        async def identity(c): return c
        tasks.append(identity(contents))
        
    if use_ai_removal:
        tasks.append(run_in_threadpool(remove_background, contents))

    # Wait for both (if both enabled)
    results = await asyncio.gather(*tasks)
    
    # Logic: If both enabled, results[0] is crop, results[1] is bg removal of ORIGINAL.
    # We actually want them chained: Crop -> BG Removal.
    # Re-evaluating: To save time, we crop the result of BG removal? No, BG removal is slower.
    # Let's keep them chained for quality, but parallel is only possible if they are independent.
    # Current implementation: they both act on ORIGINAL "contents". 
    # This might result in a BG removed full image that isn't cropped.
    
    # Correct Parallel Strategy: 
    # 1. Resize is done internally in both.
    # 2. Both are ML tasks.
    # To be fast AND correct: 
    # If both enabled, we can't truly parallelize them perfectly because they depend on each other for final result.
    # HOWEVER, we can use the cache!
    
    final_contents = contents
    if use_auto_crop:
        final_contents = await run_in_threadpool(auto_crop_face, final_contents)
    if use_ai_removal:
        final_contents = await run_in_threadpool(remove_background, final_contents)

    preview_bytes = generate_id_card_preview(
        first_name, last_name, title, id_number, doj,
        final_contents, emergency_no, blood_group, office_address,
        scale, x_offset, y_offset
    )
    
    if preview_bytes:
        return Response(content=preview_bytes, media_type="image/png")
    
    return Response(content='{"error": "Failed to generate preview"}', status_code=500, media_type="application/json")

@app.post("/api/generate-id-card")
async def api_generate_id_card(
    file: UploadFile = File(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    title: str = Form(...),
    id_number: str = Form(...),
    doj: str = Form(...), # ISO string YYYY-MM-DD
    emergency_no: str = Form(...),
    blood_group: str = Form(...),
    office_address: str = Form(...),
    scale: float = Form(1.0),
    x_offset: int = Form(0),
    y_offset: int = Form(0),
    use_auto_crop: bool = Form(True),
    use_ai_removal: bool = Form(True)
):
    contents = await file.read()
    
    final_contents = contents
    if use_auto_crop:
        final_contents = await run_in_threadpool(auto_crop_face, final_contents)
    if use_ai_removal:
        final_contents = await run_in_threadpool(remove_background, final_contents)

    # Generate PDF
    pdf_bytes = generate_id_card_pdf(
        first_name, last_name, title, id_number, doj,
        final_contents, emergency_no, blood_group, office_address,
        scale, x_offset, y_offset
    )
    
    if pdf_bytes:
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=ID_{id_number}.pdf"})
    
    return {"status": "error", "message": "Failed to generate PDF"}

@app.post("/api/generate-welcome")
async def api_generate_welcome(
    file: UploadFile = File(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    title: str = Form(...),
    doj: str = Form(...), # ISO string
    use_auto_crop: bool = Form(True)
):
    contents = await file.read()
    
    if use_auto_crop:
        contents = await run_in_threadpool(smart_crop_welcome, contents)
        
    date_obj = datetime.datetime.strptime(doj, "%Y-%m-%d")
    
    img_bytes = generate_welcome_image(first_name, last_name, title, date_obj, contents)
    
    if img_bytes:
        return Response(content=img_bytes, media_type="image/jpeg")
    
    return {"status": "error", "message": "Failed to generate Welcome Image"}

@app.post("/api/preview-business-card")
async def api_preview_business_card(
    template: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    title: str = Form(...),
    phone_mobile: str = Form(...),
    phone_office: str = Form(...),
    email: str = Form(...),
    website: str = Form(...),
    address: str = Form(...),
    address_line1: str = Form(...),
    address_line2: str = Form(...)
):
    data = locals()
    del data["template"]
    
    img_bytes = await run_in_threadpool(generate_business_card_preview, template, data)
    
    if img_bytes:
         return Response(content=img_bytes, media_type="image/png")
    return {"status": "error", "message": "Failed to generate preview"}

@app.post("/api/generate-business-card")
async def api_generate_business_card(
    template: str = Form(...),
    first_name: str = Form(...),
    last_name: str = Form(...),
    title: str = Form(...),
    phone_mobile: str = Form(...),
    phone_office: str = Form(...),
    email: str = Form(...),
    website: str = Form(...),
    address: str = Form(...),
    address_line1: str = Form(...),
    address_line2: str = Form(...)
):
    data = locals()
    del data["template"]
    
    pdf_bytes = await run_in_threadpool(generate_business_card_pdf, template, data)
    
    if pdf_bytes:
         return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=BusinessCard_{first_name}.pdf"})
@app.get("/api/admin/settings")
async def get_admin_settings():
    return load_settings()

@app.post("/api/admin/settings")
async def update_admin_settings(settings: dict):
    if save_settings(settings):
        return {"status": "success"}
    return Response(content='{"error": "Failed to save settings"}', status_code=500, media_type="application/json")

@app.get("/api/admin/assets")
async def list_assets():
    """Lists available templates and fonts for the admin UI."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "Templates")
    fonts_dir = os.path.join(base_dir, "fonts")
    
    templates = []
    if os.path.exists(templates_dir):
        templates = [f for f in os.listdir(templates_dir) if f.endswith(('.pdf', '.jpg', '.jpeg', '.png'))]
    
    fonts = []
    if os.path.exists(fonts_dir):
        for root, dirs, files in os.walk(fonts_dir):
            for f in files:
                if f.endswith(('.ttf', '.otf')):
                    rel_path = os.path.relpath(os.path.join(root, f), fonts_dir)
                    fonts.append(rel_path)
                    
    return {
        "templates": templates,
        "fonts": fonts
    }

@app.post("/api/admin/upload-asset")
async def upload_asset(file: UploadFile = File(...), category: str = Form(...)):
    """Handles uploading of templates or fonts."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    if category == "template":
        target_dir = os.path.join(base_dir, "Templates")
        allowed = ('.pdf', '.jpg', '.jpeg', '.png')
    elif category == "font":
        target_dir = os.path.join(base_dir, "fonts")
        allowed = ('.ttf', '.otf')
    else:
        return Response(content='{"error": "Invalid category"}', status_code=400, media_type="application/json")

    if not file.filename.lower().endswith(allowed):
        return Response(content=f'{{"error": "Invalid file type. Allowed: {allowed}"}}', status_code=400, media_type="application/json")

    os.makedirs(target_dir, exist_ok=True)
    file_path = os.path.join(target_dir, file.filename)
    
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
        return {"status": "success", "filename": file.filename, "path": file_path}
    except Exception as e:
        return Response(content=f'{{"error": "{str(e)}"}}', status_code=500, media_type="application/json")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
