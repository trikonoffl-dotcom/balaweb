from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import sys
import os
import datetime

# Add root directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_processing import remove_background, auto_crop_face, smart_crop_welcome
from utils.pdf_generator import generate_id_card_pdf, generate_id_card_preview
from utils.welcome_generator import generate_welcome_image
from utils.business_card_generator import generate_business_card_pdf, generate_business_card_preview

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
    contents = await file.read()
    processed = remove_background(contents)
    if processed:
        return Response(content=processed, media_type="image/png")
    return {"status": "error", "message": "Failed to process"}

@app.post("/api/auto-crop")
async def api_auto_crop(file: UploadFile = File(...), type: str = Form("id_card")):
    contents = await file.read()
    if type == "welcome":
        processed = smart_crop_welcome(contents)
    else:
        processed = auto_crop_face(contents)
    
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
    
    if use_auto_crop:
        contents = auto_crop_face(contents)
    
    if use_ai_removal:
         contents = remove_background(contents) or contents

    preview_bytes = generate_id_card_preview(
        first_name, last_name, title, id_number, doj,
        contents, emergency_no, blood_group, office_address,
        scale, x_offset, y_offset
    )
    
    if preview_bytes:
        return Response(content=preview_bytes, media_type="image/png")
    
    return {"status": "error", "message": "Failed to generate preview"}

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
    
    # Pre-processing pipeline
    if use_auto_crop:
        contents = auto_crop_face(contents)
    
    if use_ai_removal:
         # Note: bg removal returns png bytes
         contents = remove_background(contents) or contents # Fallback if fail

    # Generate PDF
    pdf_bytes = generate_id_card_pdf(
        first_name, last_name, title, id_number, doj,
        contents, emergency_no, blood_group, office_address,
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
        contents = smart_crop_welcome(contents)
        
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
    
    img_bytes = generate_business_card_preview(template, data)
    
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
    
    pdf_bytes = generate_business_card_pdf(template, data)
    
    if pdf_bytes:
         return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=BusinessCard_{first_name}.pdf"})
    return {"status": "error", "message": "Failed to generate PDF"}
