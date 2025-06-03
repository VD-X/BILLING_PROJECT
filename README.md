# Inventory-Aware Grocery Billing System

An advanced grocery billing system with inventory management, product search, and email capabilities, built with Streamlit.

## Features

- **Inventory Management**: Track product stock levels and prevent selling out-of-stock items
- **Product Management**: Add new product categories, types, and products
- **Dynamic Product Search**: Find products quickly and add them to bills
- **Bill Generation**: Create professional bills with automatic calculations
- **PDF Export**: Save bills as PDF files for easy sharing
- **Email Integration**: Send bills directly to customers via email
- **Responsive UI**: User-friendly interface with tabs and expanders

## Getting Started

### Local Development

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run streamlit_app.py
   ```

### Streamlit Cloud Deployment

1. Fork this repository to your GitHub account
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and select your forked repository
4. Set the main file to `streamlit_app_new.py`
5. Configure Streamlit secrets for email functionality:
   - In the Streamlit Cloud dashboard, go to your app settings
   - Find the "Secrets" section and add the following:
     ```toml
     [email]
     sender_email = "your-email@gmail.com"
     sender_password = "your-app-password"
     hashed_code = "your-security-code-hash"
     ```
   - For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
   - To generate the security code hash:
     1. Run the app locally
     2. Go to the "Email Setup" section in the sidebar
     3. Enter your email, password, and create a security code
     4. Click "Save Credentials" and copy the generated hash
     5. Use this hash in your Streamlit Cloud secrets
6. Deploy the app

Alternatively, you can find an example secrets file at `.streamlit/secrets.toml.example` that you can use as a template.

## Usage

### Main Billing Interface

1. Select products from different categories (Cosmetics, Groceries, Drinks)
2. Enter quantities for each product (out-of-stock products are disabled)
3. Enter customer details
4. Click "Calculate Bill" to generate the bill
5. Save, print, or email the bill as needed

### Product Management

1. Navigate to the Product Management page from the sidebar
2. Add new product categories, types, or individual products
3. Update inventory levels for existing products
4. Search for products and manage their details

### Email Configuration

#### Local Development
1. Go to the "Email Setup" section in the sidebar
2. Enter your email, app password, and create a security code
3. Save the credentials (note the generated hash for cloud deployment)
4. When sending emails, enter this security code for verification
5. Enter the customer's email address when prompted

#### Streamlit Cloud
1. Configure your email credentials in the Streamlit secrets as described in the deployment section
2. When sending emails, enter the same security code you used to generate the hash
3. The system will verify against the hash stored in Streamlit secrets

## Data Storage

- Product and inventory data are stored in JSON files in the `data` directory
- Bills are saved in a temporary directory for cloud deployment
- Excel exports are available for record-keeping

## Security

- Email credentials are stored securely:
  - In Streamlit Cloud: Using Streamlit secrets management system
  - In local development: Using encrypted storage with security code hashing
- Security code verification is required for sending emails:
  - The security code is never stored in plain text, only its hash is stored
  - Verification is done by comparing hashes, not the original code
- Temporary file storage ensures no sensitive data persists:
  - Bills and PDFs are stored in temporary directories
  - No sensitive customer data is stored permanently
- No sensitive data is exposed in the codebase or GitHub repository

## License

This project is licensed under the MIT License - see the LICENSE file for details.
