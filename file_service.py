import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import qrcode
from PIL import Image
import io
import base64
import streamlit as st

class FileService:
    def __init__(self, config):
        self.config = config
        self.temp_dir = config["temp_dir"]
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def generate_pdf(self, data, filename, title="Report"):
        """Generate PDF report from data"""
        filepath = os.path.join(self.temp_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        elements.append(Paragraph(title, styles['Heading1']))
        
        # Convert data to table format
        if isinstance(data, pd.DataFrame):
            # Add column headers
            table_data = [data.columns.tolist()]
            # Add rows
            table_data.extend(data.values.tolist())
            
            # Create table
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        return filepath
    
    def generate_excel(self, data, filename):
        """Generate Excel file from data"""
        filepath = os.path.join(self.temp_dir, filename)
        
        if isinstance(data, dict):
            # Multiple sheets
            with pd.ExcelWriter(filepath) as writer:
                for sheet_name, sheet_data in data.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
        elif isinstance(data, pd.DataFrame):
            # Single sheet
            data.to_excel(filepath, index=False)
        else:
            raise ValueError("Data must be a pandas DataFrame or a dict of DataFrames")
            
        return filepath
    
    def generate_qr_code(self, data, filename=None):
        """Generate QR code image from data"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        if filename:
            filepath = os.path.join(self.temp_dir, filename)
            img.save(filepath)
            return filepath
        else:
            # Return as base64 for direct display
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
    
    def get_download_link(self, filepath, link_text):
        """Create a download link for a file"""
        with open(filepath, "rb") as file:
            contents = file.read()
            b64 = base64.b64encode(contents).decode()
            filename = os.path.basename(filepath)
            mime_type = "application/pdf" if filepath.endswith(".pdf") else "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            href = f'<a href="data:{mime_type};base64,{b64}" download="{filename}">{link_text}</a>'
            return href