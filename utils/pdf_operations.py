import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from PyPDF2 import PdfReader

def save_bill_to_pdf(bill_content, bill_number, customer_name=None, phone_number=None, cosmetic_items=None, grocery_items=None, drink_items=None, totals=None, prices=None):
    """Save bill content to a PDF file with proper formatting."""
    if not os.path.exists("bills"):
        os.makedirs("bills")
    
    file_path = f"bills/{bill_number}.pdf" if not bill_number.endswith('.pdf') else f"bills/{bill_number}"
    
    # Simple version for when only bill content is provided
    if customer_name is None or totals is None:
        # Create a simple PDF with just the bill content
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        
        # Set up the document
        c.setTitle(f"Bill {bill_number}")
        
        # Add a header
        c.setFillColor(colors.HexColor('#1b5e20'))
        c.rect(0, height - 50, width, 50, fill=True)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width/2, height - 30, "OFFICIAL RECEIPT")
        
        # Add bill content
        c.setFillColor(colors.black)
        c.setFont("Courier", 10)
        
        # Split the bill content into lines
        lines = bill_content.split('\n')
        y_position = height - 80
        
        for line in lines:
            c.drawString(50, y_position, line)
            y_position -= 15
            
            # Check if we need a new page
            if y_position < 50:
                c.showPage()
                y_position = height - 50
                c.setFont("Courier", 10)
                c.setFillColor(colors.black)
        
        # Add footer
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.gray)
        c.drawCentredString(width/2, 30, "Thank you for shopping with us!")
        
        c.save()
        return file_path
    
    # Create PDF document with modern dimensions
    doc = SimpleDocTemplate(
        file_path, 
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=30,
        bottomMargin=30
    )
    elements = []
    styles = getSampleStyleSheet()
    
    # Create a more attractive header with gradient-like effect
    elements.append(Paragraph(
        """
        <para alignment="center">
            <font size="20" color="#FFFFFF"><b>OFFICIAL RECEIPT</b></font>
        </para>
        """,
        ParagraphStyle('Header', parent=styles['Normal'], alignment=1, backColor=colors.HexColor('#1b5e20'), 
                      textColor=colors.white, spaceBefore=0, spaceAfter=15, borderPadding=(15, 15, 15, 15),
                      borderWidth=1, borderColor=colors.HexColor('#c8e6c9'), borderRadius=5)
    ))
    
    # Add store logo placeholder and store info
    store_info = """
    <para alignment="center">
        <font size="12" color="#1b5e20"><b>PREMIUM MART</b></font><br/>
        <font size="9" color="#333333">123 Main Street, City, State 12345</font><br/>
        <font size="9" color="#333333">Phone: +91 1234567890 | Email: contact@premiummart.com</font><br/>
    </para>
    """
    elements.append(Paragraph(store_info, ParagraphStyle('StoreInfo', parent=styles['Normal'], alignment=1, 
                                                        spaceBefore=10, spaceAfter=10)))
    
    # Add decorative separator
    elements.append(Paragraph(
        """
        <para alignment="center">
            <font size="12" color="#1b5e20">══════════════════════════════════════════</font>
        </para>
        """,
        ParagraphStyle('Separator', parent=styles['Normal'], alignment=1, spaceBefore=5, spaceAfter=10)
    ))
    
    # Add bill information in a more structured format
    bill_info_style = ParagraphStyle('BillInfo', parent=styles['Normal'], fontName='Courier-Bold', 
                                   spaceBefore=0, spaceAfter=5, leading=14, fontSize=10)
    
    # Create a table for bill information
    bill_data = [
        [Paragraph(f"<para><font color='#1b5e20'><b>Bill Number:</b></font></para>", bill_info_style), 
         Paragraph(f"<para>{bill_number}</para>", bill_info_style)],
        [Paragraph(f"<para><font color='#1b5e20'><b>Date:</b></font></para>", bill_info_style), 
         Paragraph(f"<para>{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}</para>", bill_info_style)],
        [Paragraph(f"<para><font color='#1b5e20'><b>Customer:</b></font></para>", bill_info_style), 
         Paragraph(f"<para>{customer_name}</para>", bill_info_style)],
        [Paragraph(f"<para><font color='#1b5e20'><b>Phone:</b></font></para>", bill_info_style), 
         Paragraph(f"<para>{phone_number}</para>", bill_info_style)]
    ]
    
    bill_table = Table(bill_data, colWidths=[1.5*inch, 4*inch])
    bill_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f8e9')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1b5e20')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8f5e9')),
    ]))
    elements.append(bill_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Add item header with better styling
    item_header_data = [["Item", "Qty", "Price", "Total"]]
    item_header = Table(item_header_data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch])
    item_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(item_header)
    
    # Process items and create tables for each category
    def add_category_items(category_name, items_dict):
        if not any(qty > 0 for qty in items_dict.values()):
            return
        
        # Add category header
        elements.append(Paragraph(
            f"<para><font size='10' color='#1b5e20'><b>{category_name}</b></font></para>",
            ParagraphStyle('CategoryHeader', parent=styles['Normal'], spaceBefore=10, spaceAfter=5, 
                          leftIndent=5, textColor=colors.HexColor('#1b5e20'))
        ))
        
        # Create table data
        table_data = []
        for item, qty in items_dict.items():
            if qty > 0:
                price = prices[item]
                total = price * qty
                table_data.append([item, str(qty), f"₹{price:.2f}", f"₹{total:.2f}"])
        
        if table_data:
            # Create and style the table
            item_table = Table(table_data, colWidths=[3.5*inch, 1*inch, 1*inch, 1*inch])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e8f5e9')),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ]))
            elements.append(item_table)
    
    # Add items by category
    add_category_items("COSMETICS", cosmetic_items)
    add_category_items("GROCERIES", grocery_items)
    add_category_items("DRINKS", drink_items)
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Add totals with better styling
    totals_data = [
        ["Subtotal:", f"₹{totals['subtotal']:.2f}"],
        ["Tax (18%):", f"₹{totals['total_tax']:.2f}"],
        ["Grand Total:", f"₹{totals['grand_total']:.2f}"]
    ]
    
    totals_table = Table(totals_data, colWidths=[5.5*inch, 1*inch])
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 1), colors.white),
        ('BACKGROUND', (0, 2), (1, 2), colors.HexColor('#e8f5e9')),
        ('TEXTCOLOR', (0, 0), (0, 1), colors.black),
        ('TEXTCOLOR', (0, 2), (1, 2), colors.HexColor('#1b5e20')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, 1), 'Helvetica'),
        ('FONTNAME', (0, 2), (1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 2), (1, 2), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('LINEABOVE', (0, 2), (1, 2), 1, colors.HexColor('#2e7d32')),
    ]))
    elements.append(totals_table)
    
    # Add thank you message
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        """
        <para alignment="center">
            <font size="11" color="#1b5e20"><b>Thank you for shopping with us!</b></font><br/>
            <font size="9" color="#666666">We appreciate your business.</font>
        </para>
        """,
        ParagraphStyle('ThankYou', parent=styles['Normal'], alignment=1, spaceBefore=10, spaceAfter=10)
    ))
    
    # Add footer with terms and conditions
    elements.append(Spacer(1, 0.2*inch))
    elements.append(Paragraph(
        """
        <para alignment="center">
            <font size="8" color="#666666">This is a computer-generated invoice and does not require a signature.</font><br/>
            <font size="8" color="#666666">For questions or concerns, please contact us at support@premiummart.com</font>
        </para>
        """,
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, spaceBefore=5, spaceAfter=5)
    ))
    
    # Build PDF
    doc.build(elements)
    return file_path

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

# After the get_pdf_bytes function, add the create_pdf_display_solution function:

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