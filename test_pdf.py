#!/usr/bin/env python3
"""
Test PDF processing
"""

import os
from pathlib import Path

# Test if we can access the PDF folder
folder_path = Path("page 1-3")
if folder_path.exists():
    pdf_files = list(folder_path.glob("*.pdf"))
    print(f"Found {len(pdf_files)} PDF files")
    print("First 5 PDF files:")
    for i, pdf_file in enumerate(pdf_files[:5]):
        print(f"  {i+1}. {pdf_file.name}")
else:
    print("Folder 'page 1-3' not found")

# Test PyPDF2 import
try:
    import PyPDF2
    print("PyPDF2 is available")
    
    # Test with first PDF
    if pdf_files:
        first_pdf = pdf_files[0]
        print(f"Testing with: {first_pdf.name}")
        
        with open(first_pdf, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"PDF has {len(pdf_reader.pages)} pages")
            
            # Extract text from first page
            first_page = pdf_reader.pages[0]
            text = first_page.extract_text()
            print(f"First page text length: {len(text)} characters")
            print("First 200 characters:")
            print(text[:200])
            
except ImportError as e:
    print(f"PyPDF2 not available: {e}")
except Exception as e:
    print(f"Error processing PDF: {e}")
