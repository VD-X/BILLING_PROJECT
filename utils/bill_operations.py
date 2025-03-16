import os
import datetime
import random
import pandas as pd
from fpdf import FPDF
import win32print
import win32api
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def generate_bill_number():
    """Generate a unique bill number based on date and random number."""
    now = datetime.datetime.now()
    date_part = now.strftime("%Y%m%d")
    random_part = random.randint(1000, 9999)
    return f"BILL-{date_part}-{random_part}"

def calculate_total(cosmetic_items, grocery_items, drink_items, prices):
    """Calculate the total amount for all items."""
    # Calculate subtotals for each category
    cosmetic_total = sum(qty * prices.get(item, 0) for item, qty in cosmetic_items.items() if qty > 0)
    grocery_total = sum(qty * prices.get(item, 0) for item, qty in grocery_items.items() if qty > 0)
    drink_total = sum(qty * prices.get(item, 0) for item, qty in drink_items.items() if qty > 0)
    
    # Calculate overall total
    subtotal = cosmetic_total + grocery_total + drink_total
    tax = subtotal * 0.18  # 18% GST
    total = subtotal + tax
    
    return {
        "cosmetic_total": cosmetic_total,
        "grocery_total": grocery_total,
        "drink_total": drink_total,
        "subtotal": subtotal,
        "total_tax": tax,  # Renamed for consistency
        "grand_total": total  # Renamed for consistency
    }

def generate_bill(customer_name, phone_number, bill_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Generate the bill content as a formatted string."""
    now = datetime.datetime.now()
    date_str = now.strftime("%d-%m-%Y %H:%M:%S")
    
    # Start building the bill
    bill = []
    bill.append("=" * 60)
    bill.append("                 GROCERY BILLING SYSTEM")
    bill.append("=" * 60)
    bill.append(f"Bill Number: {bill_number}")
    bill.append(f"Date: {date_str}")
    bill.append(f"Customer Name: {customer_name}")
    bill.append(f"Phone Number: {phone_number}")
    bill.append("-" * 60)
    bill.append(f"{'Item':<30}{'Qty':<10}{'Price':<10}{'Total':<10}")
    bill.append("-" * 60)
    
    # Add cosmetic items
    if any(qty > 0 for qty in cosmetic_items.values()):
        bill.append("COSMETICS:")
        for item, qty in cosmetic_items.items():
            if qty > 0:
                price = prices.get(item, 0)
                total = qty * price
                bill.append(f"{item:<30}{qty:<10}{price:<10.2f}{total:<10.2f}")
    
    # Add grocery items
    if any(qty > 0 for qty in grocery_items.values()):
        bill.append("GROCERY:")
        for item, qty in grocery_items.items():
            if qty > 0:
                price = prices.get(item, 0)
                total = qty * price
                bill.append(f"{item:<30}{qty:<10}{price:<10.2f}{total:<10.2f}")
    
    # Add drink items
    if any(qty > 0 for qty in drink_items.values()):
        bill.append("DRINKS:")
        for item, qty in drink_items.items():
            if qty > 0:
                price = prices.get(item, 0)
                total = qty * price
                bill.append(f"{item:<30}{qty:<10}{price:<10.2f}{total:<10.2f}")
    
    # Add totals
    bill.append("-" * 60)
    bill.append(f"{'Subtotal:':<40}{totals['subtotal']:<20.2f}")
    bill.append(f"{'Tax (18%):':<40}{totals['total_tax']:<20.2f}")
    bill.append(f"{'Total:':<40}{totals['grand_total']:<20.2f}")
    bill.append("-" * 60)
    bill.append("Thank you for shopping with us!")
    bill.append("=" * 60)
    
    return "\n".join(bill)

def save_bill(bill_content, bill_number, customer_name, phone_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Save the bill to a text file and PDF."""
    try:
        # Create bills directory if it doesn't exist
        bill_directory = "d:\\adv billing\\bills"
        os.makedirs(bill_directory, exist_ok=True)
        
        # Save as text file
        bill_file = os.path.join(bill_directory, f"{bill_number}.txt")
        with open(bill_file, "w", encoding="utf-8") as f:
            f.write(bill_content)
        
        # Save as PDF
        pdf_file = os.path.join(bill_directory, f"{bill_number}.pdf")
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=10)
        
        # Add each line with proper encoding handling
        for line in bill_content.split('\n'):
            try:
                # Try to add the line directly with encoding conversion
                safe_line = line.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 5, txt=safe_line, ln=1)
            except Exception:
                # If that fails, replace any problematic characters
                safe_line = ''.join(c if ord(c) < 128 else '?' for c in line)
                pdf.cell(0, 5, txt=safe_line, ln=1)
        
        # Save the PDF
        pdf.output(pdf_file)
        
        return f"Bill saved as {pdf_file}"
    except Exception as e:
        return f"Error saving bill: {str(e)}"

def print_bill(bill_content):
    """Print the bill to the default printer."""
    try:
        # Create a temporary file
        temp_file = os.path.join(os.environ['TEMP'], "temp_bill.txt")
        with open(temp_file, "w", encoding="utf-8") as f:
            f.write(bill_content)
        
        # Get the default printer
        printer_name = win32print.GetDefaultPrinter()
        
        if not printer_name:
            return "Error: No default printer found."
        
        # Print the file
        try:
            win32api.ShellExecute(
                0, 
                "print", 
                temp_file,
                f"/d:{printer_name}", 
                ".", 
                0
            )
            return f"Bill sent to printer: {printer_name}"
        except Exception as e:
            return f"Error printing: {str(e)}"
    except ImportError:
        return "Printing is only available on Windows systems."
    except Exception as e:
        return f"Error: {str(e)}"

def export_bill_to_excel(customer_name, phone_number, bill_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Export the bill to an Excel file."""
    try:
        # Create excel_bills directory if it doesn't exist
        excel_directory = "d:\\adv billing\\excel_bills"
        os.makedirs(excel_directory, exist_ok=True)
        
        # Individual bill Excel file
        excel_file = os.path.join(excel_directory, f"{bill_number}.xlsx")
        
        # Create a pandas DataFrame for the bill
        data = []
        
        # Add header information
        now = datetime.datetime.now()
        date_str = now.strftime("%d-%m-%Y %H:%M:%S")
        
        data.append(["GROCERY BILLING SYSTEM", "", "", ""])
        data.append(["Bill Number:", bill_number, "", ""])
        data.append(["Date:", date_str, "", ""])
        data.append(["Customer Name:", customer_name, "", ""])
        data.append(["Phone Number:", phone_number, "", ""])
        data.append(["", "", "", ""])
        data.append(["Item", "Quantity", "Price", "Total"])
        
        # Add cosmetic items
        if any(qty > 0 for qty in cosmetic_items.values()):
            data.append(["COSMETICS:", "", "", ""])
            for item, qty in cosmetic_items.items():
                if qty > 0:
                    price = prices.get(item, 0)
                    total = qty * price
                    data.append([item, qty, price, total])
        
        # Add grocery items
        if any(qty > 0 for qty in grocery_items.values()):
            data.append(["GROCERY:", "", "", ""])
            for item, qty in grocery_items.items():
                if qty > 0:
                    price = prices.get(item, 0)
                    total = qty * price
                    data.append([item, qty, price, total])
        
        # Add drink items
        if any(qty > 0 for qty in drink_items.values()):
            data.append(["DRINKS:", "", "", ""])
            for item, qty in drink_items.items():
                if qty > 0:
                    price = prices.get(item, 0)
                    total = qty * price
                    data.append([item, qty, price, total])
        
        # Add totals
        data.append(["", "", "", ""])
        data.append(["Subtotal:", "", "", totals['subtotal']])
        data.append(["Tax (18%):", "", "", totals['total_tax']])
        data.append(["Total:", "", "", totals['grand_total']])
        
        # Create DataFrame and export to individual Excel file
        df = pd.DataFrame(data)
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, header=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Sheet1']
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).map(len).max(), len(str(col)))
                worksheet.column_dimensions[chr(65 + i)].width = max_length + 2
        
        # Save to the main Excel file in the "main excel bill" folder
        main_excel_dir = "d:\\adv billing\\main excel bill"
        os.makedirs(main_excel_dir, exist_ok=True)
        main_excel_file = os.path.join(main_excel_dir, "excel_bills.xlsx")
        
        # Prepare data for the main Excel file
        main_data = {
            'Bill Number': bill_number,
            'Date': date_str,
            'Customer Name': customer_name,
            'Phone Number': phone_number,
            'Subtotal': totals['subtotal'],
            'Tax': totals['total_tax'],
            'Total': totals['grand_total']
        }
        
        # Convert to DataFrame (single row)
        main_df = pd.DataFrame([main_data])
        
        try:
            # Check if the main Excel file exists
            if os.path.exists(main_excel_file):
                # If it exists, read it and append the new data
                existing_df = pd.read_excel(main_excel_file)
                updated_df = pd.concat([existing_df, main_df], ignore_index=True)
                updated_df.to_excel(main_excel_file, index=False)
            else:
                # If it doesn't exist, create a new file
                main_df.to_excel(main_excel_file, index=False)
        except Exception as e:
            print(f"Error saving to main Excel file: {str(e)}")
        
        return f"Bill exported to {excel_file} and added to main record"
    except Exception as e:
        return f"Error exporting to Excel: {str(e)}"


def send_bill_pdf_to_customer(customer_email, bill_number, pdf_path=None):
    """
    Send the bill PDF to the customer via email.
    
    Args:
        customer_email (str): Customer's email address
        bill_number (str): Bill number for reference
        pdf_path (str, optional): Path to the PDF file. If None, it will be constructed
        
    Returns:
        str: Success or error message
    """
    try:
        # Construct PDF path if not provided
        if pdf_path is None:
            pdf_path = os.path.join("d:\\adv billing\\bills", f"{bill_number}.pdf")
        
        # Check if PDF exists
        if not os.path.exists(pdf_path):
            return f"Error: PDF file not found at {pdf_path}"
        
        # Get email credentials from environment or configuration
        # For security, you should use environment variables or a secure configuration
        # This is a placeholder - replace with your actual email configuration
        sender_email = "your_email@gmail.com"  # Replace with your email
        sender_password = "your_app_password"  # Replace with your app password
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = customer_email
        msg['Subject'] = f"Your Bill Receipt - {bill_number}"
        
        # Email body
        body = f"""
        Dear Customer,
        
        Thank you for your purchase. Please find attached your bill receipt (Bill #{bill_number}).
        
        If you have any questions about your purchase, please contact our customer service.
        
        Best regards,
        The Grocery Store Team
        """
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        with open(pdf_path, 'rb') as file:
            attachment = MIMEApplication(file.read(), _subtype="pdf")
            attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
            msg.attach(attachment)
        
        # Connect to SMTP server (using Gmail as an example)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        
        # Login and send
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return f"Bill PDF successfully sent to {customer_email}"
    except Exception as e:
        return f"Error sending bill PDF: {str(e)}"