# Troubleshooting Guide

## Common Issues and Solutions

### MongoDB Connection Issues

If you see a warning about MongoDB connection failure:

1. Check that your MongoDB Atlas cluster is running
2. Verify your connection string is correct
3. Ensure your IP address is whitelisted in MongoDB Atlas

### PDF Generation Issues

If PDF generation fails:

1. Make sure reportlab is properly installed
2. Check that the temp directory exists and is writable
3. Try running with administrator privileges locally

### Deployment Issues

If Streamlit Cloud deployment fails:

1. Check the logs in Streamlit Cloud
2. Verify all environment variables are set correctly
3. Make sure all dependencies are in requirements.txt