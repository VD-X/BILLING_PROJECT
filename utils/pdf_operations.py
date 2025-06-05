import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PyPDF2 import PdfReader

def save_bill_to_pdf(bill_content, bill_number, bills_directory=None, customer_name=None, phone_number=None, 
                    cosmetic_items=None, grocery_items=None, drink_items=None, totals=None, prices=None):
    """Save bill content to a PDF file."""
    import streamlit as st
    import os
    st.warning(f"save_bill_to_pdf called! Current working directory: {os.getcwd()}")
    st.warning(f"bills_directory argument received: {bills_directory}")
    # Always use the provided directory, or default to project 'saved_bills'
    if not bills_directory:
        bills_directory = os.path.join(os.getcwd(), "saved_bills")
    st.warning(f"Resolved bills_directory: {bills_directory}")
    os.makedirs(bills_directory, exist_ok=True)
    pdf_path = os.path.join(bills_directory, f"{bill_number}.pdf")
    st.warning(f"Attempting to save PDF at: {pdf_path}")
    try:
        # Create a PDF document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create the content for the PDF
        styles = getSampleStyleSheet()
        flowables = []
        
        # Add bill content to PDF
        for line in bill_content.split('\n'):
            if line.startswith('='):
                # Section separator
                flowables.append(Paragraph('<hr/>', styles['Normal']))
            elif line.startswith('-'):
                # Line separator
                flowables.append(Paragraph('<hr/>', styles['Normal']))
            elif 'GROCERY BILLING SYSTEM' in line:
                # Title
                flowables.append(Paragraph(line, styles['Title']))
            elif line.startswith('Bill Number:') or line.startswith('Date:') or line.startswith('Customer Name:') or line.startswith('Phone Number:'):
                # Header information
                flowables.append(Paragraph(f'<b>{line}</b>', styles['Normal']))
            elif line.startswith('COSMETICS:') or line.startswith('GROCERY:') or line.startswith('DRINKS:'):
                # Section headers
                flowables.append(Paragraph(f'<b>{line}</b>', styles['Heading2']))
            elif line.startswith('Subtotal:') or line.startswith('Tax') or line.startswith('Total:'):
                # Totals
                flowables.append(Paragraph(f'<b>{line}</b>', styles['Normal']))
            elif line.strip():
                # Regular content
                flowables.append(Paragraph(line, styles['Normal']))
        
        # Build the PDF
        doc.build(flowables)
        
        return f"Bill saved as PDF: {pdf_path}"
    except Exception as e:
        # Add this missing except block
        return f"Error creating PDF: {str(e)}"

def extract_pdf_text(pdf_path):
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Extracted text from the PDF
    """
    try:
        if not os.path.exists(pdf_path):
            return "PDF file not found."
        
        pdf_text = ""
        pdf = PdfReader(pdf_path)
        
        for page in pdf.pages:
            pdf_text += page.extract_text() + "\n\n"
            
        return pdf_text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def get_pdf_bytes(pdf_path):
    """
    Read a PDF file and return its bytes.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        bytes: The PDF file as bytes
    """
    try:
        if not os.path.exists(pdf_path):
            return None
        
        with open(pdf_path, "rb") as pdf_file:
            return pdf_file.read()
    except Exception as e:
        return None

def create_pdf_display_solution(pdf_path):
    """
    Create a solution for displaying PDF in Streamlit.
    Returns a dictionary with PDF bytes, text content, filename, and date.
    """
    try:
        # Check if file exists
        if not os.path.exists(pdf_path):
            return None
        
        # Read PDF file
        pdf_bytes = get_pdf_bytes(pdf_path)
        if pdf_bytes is None:
            return None
        
        # Extract text from PDF
        pdf_text = extract_pdf_text(pdf_path)
        
        # Get filename and date
        filename = os.path.basename(pdf_path)
        date_str = datetime.now().strftime("%d-%m-%Y")
        
        return {
            "pdf_bytes": pdf_bytes,
            "pdf_text": pdf_text,
            "filename": filename,
            "date": date_str
        }
    except Exception as e:
        return None