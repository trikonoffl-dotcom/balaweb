import fitz
import json

def analyze_pdf(pdf_path):
    print(f"Analyzing {pdf_path}")
    doc = fitz.open(pdf_path)
    page = doc[1]
    
    # Text Analysis
    text_dict = page.get_text("dict")
    print("\n--- TEXT ELEMENTS ---")
    for block in text_dict["blocks"]:
        if block["type"] == 0: # text
            for line in block["lines"]:
                for span in line["spans"]:
                    print(f"Text: '{span['text']}'")
                    print(f"  BBox: {span['bbox']}")
                    print(f"  Origin: {span['origin']}")
                    print(f"  Size: {span['size']}")
                    print(f"  Font: {span['font']}")
                    print(f"  Color: {span['color']}")

    # Image Analysis
    print("\n--- IMAGE ELEMENTS ---")
    for img in page.get_image_info():
        # Rect to list for easier reading
        r = img['bbox']
        print(f"Image BBox: [{round(r[0], 2)}, {round(r[1], 2)}, {round(r[2], 2)}, {round(r[3], 2)}]")
    
    doc.close()

if __name__ == "__main__":
    analyze_pdf(r"C:\Users\pabal\Documents\Businesscard\Templates\idcard\idcard.pdf")
