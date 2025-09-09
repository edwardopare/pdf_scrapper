#!/usr/bin/env python3
"""Debug script to test year extraction from PDFs"""

import sys
from pathlib import Path
import pdfplumber
import re

def debug_pdf_text(pdf_path, max_lines=50):
    """Extract and display text from PDF for debugging"""
    print(f"\n=== DEBUGGING PDF: {pdf_path.name} ===")
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        
        lines = text.split('\n')
        print(f"Total lines in PDF: {len(lines)}")
        
        # Look for lines that might contain years
        year_lines = []
        for i, line in enumerate(lines[:max_lines]):
            if re.search(r'\b(20[0-9]{2})\b', line):
                year_lines.append((i, line.strip()))
        
        print(f"\nLines containing years (first {max_lines} lines):")
        for line_num, line in year_lines[:10]:  # Show first 10
            print(f"Line {line_num}: {line}")
        
        # Look for table headers
        print(f"\nLooking for table headers...")
        for i, line in enumerate(lines[:max_lines]):
            line_upper = line.upper().strip()
            if re.search(r'PL\s+', line_upper) or re.search(r'PLACE\s+', line_upper):
                print(f"Potential header at line {i}: {line.strip()}")
                
                # Show next few lines
                for j in range(i+1, min(i+6, len(lines))):
                    next_line = lines[j].strip()
                    if next_line:
                        print(f"  Data line {j}: {next_line}")
                break
                
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")

def main():
    folder_path = Path("C:/Development/page 1-3")
    pdf_files = list(folder_path.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Test first 3 PDFs
    for pdf_file in pdf_files[:3]:
        debug_pdf_text(pdf_file)

if __name__ == "__main__":
    main()
