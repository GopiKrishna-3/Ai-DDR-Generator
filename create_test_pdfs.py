from fpdf import FPDF
import os

def create_inspection_report(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Property Inspection Report", 0, 1, "C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Area: Living Room", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, "Observation: Visible water stains on the ceiling near the north wall.\nSupporting Details: The plaster is starting to peel. No active dripping during inspection.")
    pdf.ln(5)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Area: Kitchen", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, "Observation: Small crack in the backsplash tiling.\nSupporting Details: Located behind the stove area.")
    pdf.ln(5)
    
    pdf.output(path)
    print(f"Created {path}")

def create_thermal_report(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Thermal Imagery Report", 0, 1, "C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Area: Living Room (North Wall)", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, "Thermal Anomaly: Temperature drop of 5 degrees Celsius compared to surrounding surface.\nReading: 12.5 C (Ambient: 17.5 C).\nNote: Indicates significant moisture accumulation behind the ceiling.")
    pdf.ln(10)
    
    # We can't easily add real images here without having them, but we'll simulate the text.
    # In a real test, the user would provide PDFs with real images.
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Area: Roof / Exterior", 0, 1)
    pdf.set_font("Arial", "", 10)
    pdf.multi_cell(0, 5, "Observation: Heat signature indicates insulation gap near the chimney stack.")
    
    pdf.output(path)
    print(f"Created {path}")

if __name__ == "__main__":
    if not os.path.exists("tests"):
        os.makedirs("tests")
    create_inspection_report("tests/mock_inspection.pdf")
    create_thermal_report("tests/mock_thermal.pdf")
