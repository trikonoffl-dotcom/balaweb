import fitz
import os

def extract_images(pdf_path, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    doc = fitz.open(pdf_path)
    page = doc[0]
    for i, img in enumerate(page.get_images()):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        if pix.n - pix.alpha > 3: # CMYK: convert to RGB first
            pix = fitz.Pixmap(fitz.csRGB, pix)
        pix.save(os.path.join(out_dir, f"img_{i}_{xref}.png"))
        pix = None
    doc.close()

if __name__ == "__main__":
    extract_images(r"C:\Users\pabal\Documents\Businesscard\Templates\idcard\idcard.pdf", "id_images_extract")
