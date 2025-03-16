import streamlit as st
import os
import base64
import fitz
import pandas as pd
from datetime import datetime
from PIL import Image
import io
import glob
import re

def extract_bill_number_from_filename(filename):
    """Extract bill number from filename"""
    try:
        # Remove file extension
        name_without_ext = os.path.splitext(filename)[0]
        # Extract numbers from filename
        numbers = re.findall(r'\d+', name_without_ext)
        if numbers:
            # Return the last number found in the filename
            return numbers[-1]
        return None
    except Exception:
        return None

def get_bill_files():
    """Get list of bill files in the bills folder with metadata"""
    bills_folder = "d:\\adv billing\\bills"
    
    if not os.path.exists(bills_folder):
        st.error("Bills folder not found.")
        return []
    
    bill_files = []
    for file in glob.glob(os.path.join(bills_folder, "*.pdf")):
        filename = os.path.basename(file)
        bill_number = extract_bill_number_from_filename(filename)
        
        created_time = os.path.getctime(file)
        modified_time = os.path.getmtime(file)
        size_bytes = os.path.getsize(file)
        size_kb = size_bytes / 1024
        
        # Try to find corresponding TXT file for metadata
        txt_file = file.replace('.pdf', '.txt')
        customer_name = None
        total_amount = None
        
        if os.path.exists(txt_file):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    customer_match = re.search(r'Customer Name: (.+)', content)
                    if customer_match:
                        customer_name = customer_match.group(1).strip()
                    
                    total_match = re.search(r'Total:\s+(\d+\.\d+)', content)
                    if total_match:
                        total_amount = float(total_match.group(1))
            except Exception:
                pass
        
        bill_files.append({
            'filename': filename,
            'bill_number': bill_number,
            'path': file,
            'created': datetime.fromtimestamp(created_time),
            'modified': datetime.fromtimestamp(modified_time),
            'size': size_kb,
            'customer_name': customer_name,
            'total': total_amount
        })
    
    bill_files.sort(key=lambda x: x['created'], reverse=True)
    return bill_files

def display_pdf(pdf_path):
    """Display PDF file in Streamlit with enhanced UI"""
    try:
        with open(pdf_path, "rb") as file:
            base64_pdf = base64.b64encode(file.read()).decode('utf-8')
        
        # Add a professional header for the PDF viewer
        st.markdown("""
        <div style="background: linear-gradient(90deg, #2e7d32 0%, #388e3c 100%); padding: 15px; border-radius: 10px 10px 0 0; margin-bottom: 0;">
            <h3 style="color: white; margin: 0; text-align: center; font-size: 18px;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" style="vertical-align: middle; margin-right: 10px;" viewBox="0 0 16 16">
                    <path d="M14 14V4.5L9.5 0H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2zM9.5 3A1.5 1.5 0 0 0 11 4.5h2V9H3V2a1 1 0 0 1 1-1h5.5v2z"/>
                    <path d="M3 12v-2h2v2H3zm0 1h2v2H4a1 1 0 0 1-1-1v-1zm3 2v-2h7v1a1 1 0 0 1-1 1H6zm7-3H6v-2h7v2z"/>
                </svg>
                INVOICE DOCUMENT VIEWER
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Embed PDF viewer with improved styling
        pdf_display = f"""
        <div style="border: 1px solid #ddd; border-radius: 0 0 10px 10px; padding: 0; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
            <iframe src="data:application/pdf;base64,{base64_pdf}" 
                    width="100%" 
                    height="800" 
                    type="application/pdf"
                    style="border: none;">
            </iframe>
        </div>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)
        
        # Add spacing
        st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)
        
        # Action buttons with improved styling
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download button
            with open(pdf_path, "rb") as file:
                st.download_button(
                    label="📥 Download PDF",
                    data=file,
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            # Print button with improved styling
            st.button("🖨️ Print Invoice", on_click=lambda: None, use_container_width=True)
        
        with col3:
            # Extract text button
            if st.button("📄 Extract Text", use_container_width=True):
                try:
                    with fitz.open(pdf_path) as doc:
                        text = ""
                        for page in doc:
                            text += page.get_text()
                        
                        # Display extracted text in a nicer format
                        st.markdown("""
                        <div style="background-color: #f8f9fa; border-left: 4px solid #2e7d32; padding: 15px; margin-top: 20px; border-radius: 4px;">
                            <p style="margin: 0; color: #1b5e20;"><strong>Extracted Text Content:</strong></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.text_area("", text, height=400)
                except Exception as e:
                    st.error(f"Error extracting text: {str(e)}")
        
        # Add additional information section
        st.markdown("""
        <div style="background-color: #e8f5e9; border-left: 4px solid #2e7d32; padding: 15px; margin-top: 30px; border-radius: 4px;">
            <p style="margin: 0; color: #1b5e20;"><strong>Note:</strong> This is a digital version of your invoice. 
            You can download, print, or extract text from this document using the buttons above.</p>
        </div>
        """, unsafe_allow_html=True)
                    
    except Exception as e:
        st.error(f"Error displaying PDF: {str(e)}")

def search_bills(bills, search_term, date_range, amount_range, customer_name):
    """Search bills based on various criteria"""
    filtered_bills = bills.copy()
    
    # Filter by search term
    if search_term:
        filtered_bills = [
            bill for bill in filtered_bills
            if search_term.lower() in bill['filename'].lower()
            or (bill['bill_number'] and search_term.lower() in bill['bill_number'].lower())
        ]
    
    # Filter by date range
    if date_range:
        start_date, end_date = date_range
        filtered_bills = [
            bill for bill in filtered_bills
            if start_date <= bill['created'].date() <= end_date
        ]
    
    # Filter by amount range
    if amount_range:
        min_amount, max_amount = amount_range
        filtered_bills = [
            bill for bill in filtered_bills
            if bill.get('total') is not None
            and min_amount <= bill['total'] <= max_amount
        ]
    
    # Filter by customer name
    if customer_name:
        filtered_bills = [
            bill for bill in filtered_bills
            if bill.get('customer_name')
            and customer_name.lower() in bill['customer_name'].lower()
        ]
    
    return filtered_bills

def main():
    st.set_page_config(page_title="Bill Search Dashboard", layout="wide")
    
    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'viewing_bill' not in st.session_state:
        st.session_state.viewing_bill = None
    
    st.title("📊 Bill Search Dashboard")
    
    # Handle bill viewing
    if st.session_state.viewing_bill:
        col1, col2 = st.columns([1, 11])
        with col1:
            if st.button("← Back"):
                st.session_state.viewing_bill = None
                st.rerun()
        with col2:
            st.subheader(f"Viewing Bill: {st.session_state.viewing_bill['filename']}")
        
        display_pdf(st.session_state.viewing_bill['path'])
        return

    # Get bill files
    bill_files = get_bill_files()
    
    if not bill_files:
        st.warning("No bills found in the bills folder.")
        return
    
    # Search filters
    with st.container():
        st.subheader("Search Filters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            search_term = st.text_input("🔍 Search by Bill Number or Filename")
            customer_name = st.text_input("👤 Search by Customer Name")
        
        with col2:
            # Date range filter
            date_range = st.date_input(
                "📅 Date Range",
                value=(
                    min(bill['created'].date() for bill in bill_files),
                    max(bill['created'].date() for bill in bill_files)
                )
            )
            
            # Amount range filter - Fixed to handle cases where all bills have the same amount
            bill_amounts = [bill.get('total') for bill in bill_files if bill.get('total') is not None]
            if bill_amounts:
                min_amount = min(bill_amounts)
                max_amount = max(bill_amounts)
                
                # Fix for when min and max are the same
                if min_amount == max_amount:
                    amount_range = (min_amount, min_amount)
                    st.info(f"All bills have the same amount: ₹{min_amount:.2f}")
                else:
                    amount_range = st.slider(
                        "💰 Amount Range (₹)",
                        min_value=float(min_amount),
                        max_value=float(max_amount),
                        value=(float(min_amount), float(max_amount)),
                        step=10.0
                    )
            else:
                amount_range = None
                st.info("No bill amounts found in the data")

    # Search button
    search_clicked = st.button("🔍 Search Bills", use_container_width=True)
    
    # Process search
    if search_clicked or st.session_state.search_results is not None:
        # Update search results if button clicked
        if search_clicked:
            st.session_state.search_results = search_bills(
                bill_files,
                search_term,
                date_range,
                amount_range,
                customer_name
            )
        
        search_results = st.session_state.search_results
        
        if not search_results:
            st.info("No bills found matching your search criteria.")
            st.session_state.search_results = None
        else:
            st.success(f"Found {len(search_results)} bills matching your criteria")
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📑 Card View", "📊 Table View"])
            
            with tab1:
                # Display bills in card format
                for i, bill in enumerate(search_results):
                    with st.container():
                        st.markdown(f"""
                        <div style='padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 20px;'>
                            <h3>Bill #{bill['bill_number'] or 'Unknown'}</h3>
                            <p><strong>Filename:</strong> {bill['filename']}</p>
                            <p><strong>Created:</strong> {bill['created'].strftime('%Y-%m-%d %H:%M')}</p>
                            <p><strong>Size:</strong> {bill['size']:.1f} KB</p>
                        """, unsafe_allow_html=True)
                        
                        if bill.get('customer_name') or bill.get('total'):
                            st.markdown("<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 10px 0;'>", unsafe_allow_html=True)
                            if bill.get('customer_name'):
                                st.markdown(f"<p><strong>Customer:</strong> {bill['customer_name']}</p>", unsafe_allow_html=True)
                            if bill.get('total'):
                                st.markdown(f"<p><strong>Total:</strong> ₹{bill['total']:.2f}</p>", unsafe_allow_html=True)
                            st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # View button
                        if st.button("👁️ View Bill", key=f"view_{i}", use_container_width=True):
                            st.session_state.viewing_bill = bill
                            st.rerun()
            
            with tab2:
                # Display bills in table format
                df = pd.DataFrame(search_results)
                df['created'] = df['created'].dt.strftime('%Y-%m-%d %H:%M')
                df['size'] = df['size'].round(1)
                df = df.rename(columns={
                    'filename': 'Filename',
                    'bill_number': 'Bill Number',
                    'created': 'Created',
                    'size': 'Size (KB)',
                    'customer_name': 'Customer',
                    'total': 'Total (₹)'
                })
                st.dataframe(df, use_container_width=True)
                
                # Export button
                if st.button("📊 Export to Excel", use_container_width=True):
                    df.to_excel("d:\\adv billing\\search_results.xlsx", index=False)
                    st.success("Search results exported to Excel!")

if __name__ == "__main__":
    main()