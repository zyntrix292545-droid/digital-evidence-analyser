import os
import datetime
import hashlib
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER

def get_file_hashes(filepath):
    """Calculates MD5 and SHA256 hashes of a file."""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    with open(filepath, "rb") as f:
        # Read file in 4KB chunks
        for byte_block in iter(lambda: f.read(4096), b""):
            md5_hash.update(byte_block)
            sha256_hash.update(byte_block)
            
    return md5_hash.hexdigest(), sha256_hash.hexdigest()

def draw_page_number(canvas, doc):
    """Adds a page number to the bottom of the PDF."""
    page_num = canvas.getPageNumber()
    text = f"Page {page_num}"
    canvas.saveState()
    canvas.setFont('Helvetica', 10)
    canvas.drawCentredString(letter[0] / 2.0, 20, text)
    canvas.restoreState()

def generate_report(filepath, metadata, stego):
    # 2. Automatically create the "reports/" folder if it doesn't exist
    # Create it in the current working directory
    reports_dir = os.path.abspath("reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # 3. Save the PDF with filename like: forensic_20250509_143022.pdf
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"forensic_{timestamp}.pdf"
    pdf_path = os.path.join(reports_dir, pdf_filename)
    
    # Setup Document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=50)
    
    # Configure styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', parent=styles['Heading1'], alignment=TA_CENTER))
    styles.add(ParagraphStyle(name='BoldHeading', parent=styles['Heading2'], spaceAfter=10))
    styles.add(ParagraphStyle(name='BulletItem', parent=styles['Normal'], leftIndent=20, spaceAfter=5))
    
    Story = []
    
    # SECTION 1 - Header
    Story.append(Paragraph("Digital Forensic Evidence Report", styles['CenterTitle']))
    Story.append(HRFlowable(width="100%", thickness=1, color="black", spaceBefore=10, spaceAfter=20))
    
    filename_only = os.path.basename(filepath)
    generated_time = now.strftime("%Y-%m-%d %H:%M:%S")
    
    Story.append(Paragraph(f"<b>Generated:</b> {generated_time}", styles['Normal']))
    Story.append(Paragraph(f"<b>Analyzed File:</b> {filename_only}", styles['Normal']))
    Story.append(Spacer(1, 25))
    
    # SECTION 2 - File Metadata
    Story.append(Paragraph("FILE METADATA", styles['BoldHeading']))
    
    # Ensure file size has units if it's a number
    file_size = metadata.get("file_size", "N/A")
    if isinstance(file_size, int):
        file_size = f"{file_size} bytes"
        
    metadata_fields = [
        ("File Type", metadata.get("file_type", "N/A")),
        ("Author", metadata.get("author", "N/A")),
        ("Date Created", metadata.get("created", "N/A")),
        ("File Size", file_size),
        ("GPS Latitude", metadata.get("gps_latitude", "N/A")),
        ("GPS Longitude", metadata.get("gps_longitude", "N/A")),
        ("Image Width", metadata.get("image_width", "N/A")),
        ("Image Height", metadata.get("image_height", "N/A")),
        ("Image Format", metadata.get("image_format", "N/A"))
    ]
    
    for label, val in metadata_fields:
        Story.append(Paragraph(f"<b>{label}:</b> {val}", styles['Normal']))
        
    Story.append(Spacer(1, 25))
    
    # SECTION 3 - Steganography Analysis
    Story.append(Paragraph("STEGANOGRAPHY ANALYSIS", styles['BoldHeading']))
    
    detected = stego.get("detected", False)
    if detected:
        status_text = "YES ⚠"
    else:
        status_text = "NO ✓"
        
    Story.append(Paragraph(f"<b>Hidden Data Detected:</b> {status_text}", styles['Normal']))
    
    for finding in stego.get("findings", []):
        Story.append(Paragraph(f"• {finding}", styles['BulletItem']))
        
    Story.append(Spacer(1, 25))
    
    # SECTION 4 - File Integrity
    Story.append(Paragraph("FILE INTEGRITY", styles['BoldHeading']))
    try:
        md5_hash, sha256_hash = get_file_hashes(filepath)
    except Exception as e:
        md5_hash, sha256_hash = f"Error: {e}", f"Error: {e}"
        
    Story.append(Paragraph(f"<b>MD5:</b> {md5_hash}", styles['Normal']))
    Story.append(Paragraph(f"<b>SHA256:</b> {sha256_hash}", styles['Normal']))
    
    # 1. & 6. Build PDF and return the path
    doc.build(Story, onFirstPage=draw_page_number, onLaterPages=draw_page_number)
    
    return pdf_path
