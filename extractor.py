import fitz  # PyMuPDF
import os
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """
    Extracts all text from a PDF file.
    Returns a string containing the text.
    """
    print(f"DEBUG: Extracting text from {os.path.basename(pdf_path)}...")
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += f"--- Page {page_num + 1} ---\n"
        text += page.get_text()
    doc.close()
    return text

def extract_images_from_pdf(pdf_path, output_dir):
    """
    Extracts high-quality images from a PDF file and saves them.
    Filters out tiny icons and limits total images to 50 for performance.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"DEBUG: Extracting images from {os.path.basename(pdf_path)}...")
    doc = fitz.open(pdf_path)
    image_map = {}
    total_extracted = 0
    MAX_IMAGES = 50 # FAIL-SAFE: Prevent hangs on massive documents
    
    for page_num in range(len(doc)):
        if total_extracted >= MAX_IMAGES: 
            print("DEBUG: Max image limit (50) reached. Skipping further extraction.")
            break
            
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        page_images = []
        for img_index, img in enumerate(image_list):
            if total_extracted >= MAX_IMAGES: break
                
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            # Filter by size (Minimum 100x100) to skip icons
            if base_image["width"] < 100 or base_image["height"] < 100:
                continue
                
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_filename = f"page_{page_num+1}_img_{img_index+1}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            page_images.append(image_path)
            total_extracted += 1
            if total_extracted % 5 == 0:
                print(f"DEBUG: Extracted {total_extracted} quality images...")
            
        if page_images:
            image_map[page_num + 1] = page_images
            
    doc.close()
    print(f"DEBUG: Finished image extraction. Total quality images: {total_extracted}")
    return image_map

if __name__ == "__main__":
    pass
