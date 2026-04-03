from fpdf import FPDF
import os
import re

class DDRReportGenerator(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Palette 4 Brand Colors
        self.clr_brand = (239, 127, 109)   # Coral (#EF7F6D)
        self.clr_text = (45, 52, 54)      # Charcoal (#2D3436)
        self.clr_accent = (253, 241, 211) # Cream (#FDF1D3)
        self.clr_muted = (99, 110, 114)   # Warm Gray

    def header(self):
        # Thin Mint Bar on every page for professional framing
        self.set_fill_color(*self.clr_brand)
        self.rect(0, 0, 210, 8, 'F')
        
        if self.page_no() == 1:
            self.set_y(15)
            self.set_font('helvetica', 'B', 22)
            self.set_text_color(*self.clr_text)
            self.cell(0, 12, 'PROPERTY DIAGNOSTIC PROTOCOL', 0, 1, 'L')
            self.set_font('helvetica', 'B', 10)
            self.set_text_color(*self.clr_brand)
            self.cell(0, 5, 'AI-POWERED STRUCTURAL & THERMAL EVALUATION', 0, 1, 'L')
            self.set_draw_color(*self.clr_brand)
            self.set_line_width(0.8)
            self.line(10, self.get_y()+2, 70, self.get_y()+2)
            self.ln(10)
        else:
            self.set_y(12)
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(*self.clr_muted)
            self.cell(0, 5, 'Detailed Diagnostic Report | Engineering Brief', 0, 1, 'R')
            self.ln(5)

    def footer(self):
        self.set_y(-18)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(*self.clr_muted)
        self.set_draw_color(226, 232, 240) # Lighter border
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.cell(0, 8, f'Confidential Report - DDR Protocol v2.5 | Page {self.page_no()}', 0, 0, 'C')

    def add_metadata_table(self, metadata_block):
        # Professional 2-Column Metadata Layout
        date = re.search(r"Date:\s*(.*)", metadata_block, re.I)
        inspector = re.search(r"Inspected By:\s*(.*)", metadata_block, re.I)
        prop_type = re.search(r"Property Type:\s*(.*)", metadata_block, re.I)
        time_field = re.search(r"Time:\s*(.*)", metadata_block, re.I)
        
        # Start Table
        self.set_fill_color(*self.clr_accent)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.2)
        
        col_w = 45
        val_w = 50
        h = 7
        
        # Row 1
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(*self.clr_brand)
        self.set_text_color(255, 255, 255)
        self.cell(col_w, h, "  INSPECTION DATE", 1, 0, 'L', fill=True)
        self.set_text_color(*self.clr_text)
        self.set_font('helvetica', '', 8)
        self.cell(val_w, h, f"  {date.group(1).strip() if date else 'N/A'}", 1, 0, 'L')
        
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(*self.clr_brand)
        self.set_text_color(255, 255, 255)
        self.cell(col_w, h, "  INSPECTED BY", 1, 0, 'L', fill=True)
        self.set_text_color(*self.clr_text)
        self.set_font('helvetica', '', 8)
        self.cell(val_w, h, f"  {inspector.group(1).strip() if inspector else 'N/A'}", 1, 1, 'L')
        
        # Row 2
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(*self.clr_brand)
        self.set_text_color(255, 255, 255)
        self.cell(col_w, h, "  PROPERTY TYPE", 1, 0, 'L', fill=True)
        self.set_text_color(*self.clr_text)
        self.set_font('helvetica', '', 8)
        self.cell(val_w, h, f"  {prop_type.group(1).strip() if prop_type else 'N/A'}", 1, 0, 'L')
        
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(*self.clr_brand)
        self.set_text_color(255, 255, 255)
        self.cell(col_w, h, "  TIME & STATUS", 1, 0, 'L', fill=True)
        self.set_font('helvetica', 'B', 8)
        st_val = time_field.group(1).strip() if time_field else "COMPLETE"
        self.cell(val_w, h, f"  {st_val}", 1, 1, 'L')
        
        self.ln(8)

    def add_section_header(self, title):
        if self.get_y() > 240: self.add_page()
        self.ln(5)
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(*self.clr_text)
        # Numerical highlighting
        num_match = re.match(r"^(\d+\.)\s*(.*)", title)
        if num_match:
            self.set_text_color(*self.clr_brand)
            self.write(8, f"{num_match.group(1)} ")
            self.set_text_color(*self.clr_text)
            self.write(8, num_match.group(2).upper())
            self.ln(8)
        else:
            self.cell(0, 8, title.upper(), 0, 1, 'L')
        
        # Thin Accent Line
        self.set_draw_color(*self.clr_brand)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 40, self.get_y())
        self.ln(4)

    def add_observation_card(self, name, finding, details, img_paths=None):
        if self.get_y() > 200: self.add_page()
        
        # Card Wrapper Start
        curr_y = self.get_y()
        self.set_draw_color(226, 232, 240)
        self.set_fill_color(255, 255, 255)
        
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(*self.clr_text)
        self.cell(0, 8, f"ZONE: {name.upper()}", 0, 1)
        
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(*self.clr_muted)
        self.write(5, "PRIMARY FINDING: ")
        self.set_font('helvetica', '', 9.5)
        self.set_text_color(*self.clr_text)
        self.multi_cell(0, 5, finding)
        
        self.ln(1)
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(*self.clr_muted)
        self.write(5, "TECHNICAL DETAILS: ")
        self.set_font('helvetica', '', 9.5)
        self.set_text_color(*self.clr_text)
        self.multi_cell(0, 5, details)
        
        # Center-Aligned Dynamic Evidence
        if img_paths:
            self.ln(4)
            for p in img_paths:
                if os.path.exists(p):
                    # Height check for large images to prevent ugly overlaps
                    if self.get_y() > 180: self.add_page()
                    try:
                        # Centering logic: Page width 210, image width 140, margin = (210-140)/2 = 35
                        self.image(p, x=35, w=140)
                        self.ln(5)
                        self.set_font('helvetica', 'I', 7)
                        self.set_text_color(*self.clr_muted)
                        self.cell(0, 4, f"Fig. - Thermal Data for {name}", 0, 1, 'C')
                        self.ln(4)
                    except Exception: pass
        
        self.ln(3)
        self.set_draw_color(241, 245, 249)
        self.line(15, self.get_y(), 195, self.get_y())
        self.ln(6)

def sanitize_text(text):
    """Deep clean text for FPDF compatibility while preserving common symbols."""
    if not text: return ""
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"', '\u2022': '*', '\u00b0': ' deg',
        '\u20b9': 'Rs.', '\u20ac': 'EUR', '\u2122': '(TM)', '\u00a9': '(C)',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(report_text, image_map, output_path, include_images=True):
    print(f"DEBUG: Starting PDF generation at {output_path}...")
    pdf = DDRReportGenerator()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    safe_text = sanitize_text(report_text)
    
    # 1. Metadata Brief
    meta_part = re.search(r"\[\[METADATA_START\]\](.*?)\[\[METADATA_END\]\]", safe_text, re.S)
    if meta_part:
        pdf.add_metadata_table(meta_part.group(1))
        safe_text = safe_text.replace(meta_part.group(0), "")

    sections = ["1. PROPERTY ISSUE SUMMARY", "2. AREA-WISE OBSERVATIONS", "3. PROBABLE ROOT CAUSE", "4. SEVERITY ASSESSMENT", "5. RECOMMENDED ACTIONS", "6. ADDITIONAL NOTES", "7. MISSING OR UNCLEAR INFORMATION"]
    header_pattern = "|".join([re.escape(s) for s in sections])
    parts = re.split(f"(?:#+\s+)?({header_pattern})", safe_text, flags=re.IGNORECASE)
    
    if len(parts) > 1:
        for i in range(1, len(parts), 2):
            header = parts[i].strip()
            content = parts[i+1].strip() if i+1 < len(parts) else ""
            print(f"DEBUG: Rendering PDF Section: {header[:30]}...")
            pdf.add_section_header(header)
            
            if "AREA-WISE" in header.upper():
                obs_blocks = content.split("[[AREA_START]]")
                for block in obs_blocks:
                    if not block.strip() or "[[AREA_END]]" not in block: continue
                    name = re.search(r"\[\[NAME\]\]\s*:\s*(.*?)(?=\[\[|$)", block, re.S)
                    finding = re.search(r"\[\[FINDING\]\]\s*:\s*(.*?)(?=\[\[|$)", block, re.S)
                    details = re.search(r"\[\[DETAILS\]\]\s*:\s*(.*?)(?=\[\[|$)", block, re.S)
                    img_ref = re.search(r"\[\[IMAGE_REF\]\]\s*:\s*(.*?)(?=\[\[|$)", block, re.S)
                    c_txt = img_ref.group(1).strip() if img_ref else ""
                    matched_paths = []
                    try:
                        # Improved regex to find Page/Photo/Image followed by numbers
                        img_pg_match = re.search(r"(?:PAGE|PHOTO|IMAGE)\s*(\d+)", c_txt.upper())
                        if img_pg_match:
                            pg_num = int(img_pg_match.group(1))
                            if pg_num in image_map:
                                matched_paths = image_map[pg_num]
                    except: pass
                    
                    pdf.add_observation_card(name.group(1).strip() if name else "Zone", finding.group(1).strip() if finding else "N/A", details.group(1).strip() if details else "None", matched_paths)
            elif "SEVERITY" in header.upper():
                severity_val = re.search(r"Level:\s*(High|Medium|Low)", content, re.I)
                if severity_val:
                    level = severity_val.group(1).lower()
                    color = (211, 47, 47) if level == "high" else (245, 124, 0) if level == "medium" else (56, 142, 60)
                    pdf.set_font('helvetica', 'B', 11)
                    pdf.set_text_color(*color)
                    pdf.cell(0, 7, f"CRITICAL STATUS: {level.upper()}", 0, 1)
                    pdf.set_text_color(*pdf.clr_text)
                pdf.set_font('helvetica', '', 10); pdf.multi_cell(0, 5.5, content)
            else:
                pdf.set_font('helvetica', '', 10.5); pdf.multi_cell(0, 6, content); pdf.ln(3)
    else:
        pdf.set_font('helvetica', '', 10.5); pdf.multi_cell(0, 6, safe_text)
    
    pdf.output(output_path)
    print("DEBUG: PDF generation successful.")
    return output_path
