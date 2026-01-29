import fitz
import json

def extract_backside_info(pdf_path):
    print(f"Extracting info from page 1 of {pdf_path}")
    doc = fitz.open(pdf_path)
    page = doc[1]
    text_dict = page.get_text("dict")
    
    results = []
    for block in text_dict["blocks"]:
        if block["type"] == 0:
            for line in block["lines"]:
                for span in line["spans"]:
                    results.append({
                        "text": span["text"],
                        "bbox": span["bbox"],
                        "font": span["font"],
                        "size": span["size"],
                        "color": span["color"]
                    })
    
    with open("backside_mapping.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    
    for r in results:
        print(f"Text: '{r['text']}' @ BBox: {r['bbox']} Font: {r['font']}")
    
    doc.close()

if __name__ == "__main__":
    extract_backside_info(r"C:\Users\pabal\Documents\Businesscard\Templates\idcard\idcard.pdf")
