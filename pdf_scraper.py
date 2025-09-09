#!/usr/bin/env python3
"""
PDF Data Scraper
Scrapes data from PDF files in a folder and exports to CSV format
Extracts: PL, NAME, TEAM, TIME, SOURCE_FILE, EVENT DATE
"""

import os
import sys
import csv
import re
import logging
from datetime import datetime
from pathlib import Path
import pdfplumber
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFScraper:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.extracted_data = []
        self.total_records = 0
        
    def extract_data_from_pdf(self, pdf_path):
        """Extract data from a single PDF file"""
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pdf_data = []
                
                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num} of {len(pdf.pages)}")
                    
                    # Extract text from page
                    text = page.extract_text()
                    if not text:
                        logger.warning(f"No text found on page {page_num}")
                        continue
                    
                    # Extract tables from page
                    tables = page.extract_tables()
                    
                    # Process tables if found
                    if tables:
                        for table_num, table in enumerate(tables):
                            table_data = self.process_table(table, pdf_path.name, page_num, table_num)
                            pdf_data.extend(table_data)
                    
                    # If no tables found, try to extract data from text
                    if not tables:
                        text_data = self.extract_from_text(text, pdf_path.name, page_num)
                        pdf_data.extend(text_data)
                
                logger.info(f"Extracted {len(pdf_data)} records from {pdf_path.name}")
                return pdf_data
                
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return []
    
    def process_table(self, table, source_file, page_num, table_num):
        """Process a table extracted from PDF"""
        if not table or len(table) < 2:  # Need at least header and one data row
            return []
        
        # Find header row (usually first row)
        headers = [str(cell).strip() if cell else "" for cell in table[0]]
        
        # Try to identify column indices for our target fields
        field_indices = self.identify_field_columns(headers)
        
        if not any(field_indices.values()):
            logger.warning(f"Could not identify target fields in table on page {page_num}")
            return []
        
        # Process data rows
        data_rows = []
        for row_num, row in enumerate(table[1:], 1):
            if not row or len(row) < len(headers):
                continue
                
            # Extract data for each field
            record = self.extract_record_from_row(row, field_indices, source_file, page_num, table_num, row_num)
            if record:
                data_rows.append(record)
        
        return data_rows
    
    def identify_field_columns(self, headers):
        """Identify which columns contain our target fields"""
        field_indices = {
            'PL': None,
            'NAME': None,
            'TEAM': None,
            'TIME': None,
            'EVENT_DATE': None
        }
        
        for i, header in enumerate(headers):
            header_upper = header.upper()
            
            # Look for place/position columns
            if any(keyword in header_upper for keyword in ['PL', 'PLACE', 'POS', 'POSITION', 'RANK', 'RANKING']):
                field_indices['PL'] = i
            
            # Look for name columns
            elif any(keyword in header_upper for keyword in ['NAME', 'ATHLETE', 'RUNNER', 'COMPETITOR']):
                field_indices['NAME'] = i
            
            # Look for team columns
            elif any(keyword in header_upper for keyword in ['TEAM', 'SCHOOL', 'CLUB', 'UNIVERSITY', 'COLLEGE']):
                field_indices['TEAM'] = i
            
            # Look for time columns
            elif any(keyword in header_upper for keyword in ['TIME', 'RESULT', 'FINISH', 'MARK', 'PERFORMANCE']):
                field_indices['TIME'] = i
            
            # Look for date columns
            elif any(keyword in header_upper for keyword in ['DATE', 'EVENT DATE', 'MEET DATE', 'COMPETITION DATE']):
                field_indices['EVENT_DATE'] = i
        
        return field_indices
    
    def extract_record_from_row(self, row, field_indices, source_file, page_num, table_num, row_num):
        """Extract a single record from a table row"""
        record = {
            'PL': '',
            'NAME': '',
            'TEAM': '',
            'TIME': '',
            'SOURCE_FILE': source_file,
            'EVENT_DATE': ''
        }
        
        # Extract data for each field
        for field, col_index in field_indices.items():
            if col_index is not None and col_index < len(row):
                value = str(row[col_index]).strip() if row[col_index] else ''
                record[field] = value
        
        # Only return record if it has at least some meaningful data
        if any(record[field] for field in ['PL', 'NAME', 'TEAM', 'TIME']):
            return record
        
        return None
    
    def extract_from_text(self, text, source_file, page_num):
        """Extract data from plain text when no tables are found"""
        # This is a fallback method for when tables aren't detected
        # It looks for patterns in the text that might contain our target data
        
        lines = text.split('\n')
        records = []
        
        # Look for lines that might contain race results
        for line_num, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try to match common result patterns
            # Pattern: Place Name Team Time
            # Example: "1 John Smith University of State 21.45"
            pattern = r'^(\d+)\s+([A-Za-z\s]+?)\s+([A-Za-z\s]+?)\s+(\d+[:.]?\d*)$'
            match = re.match(pattern, line)
            
            if match:
                record = {
                    'PL': match.group(1),
                    'NAME': match.group(2).strip(),
                    'TEAM': match.group(3).strip(),
                    'TIME': match.group(4),
                    'SOURCE_FILE': source_file,
                    'EVENT_DATE': ''
                }
                records.append(record)
        
        return records
    
    def process_folder(self):
        """Process all PDF files in the specified folder"""
        if not self.folder_path.exists():
            logger.error(f"Folder does not exist: {self.folder_path}")
            return False
        
        pdf_files = list(self.folder_path.glob("*.pdf"))
        
        if not pdf_files:
            logger.error(f"No PDF files found in {self.folder_path}")
            return False
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                pdf_data = self.extract_data_from_pdf(pdf_file)
                self.extracted_data.extend(pdf_data)
                self.total_records += len(pdf_data)
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                continue
        
        logger.info(f"Total records extracted: {self.total_records}")
        return True
    
    def save_to_csv(self, output_file="extracted_data.csv"):
        """Save extracted data to CSV file"""
        if not self.extracted_data:
            logger.warning("No data to save")
            return False
        
        try:
            # Define the field order
            fieldnames = ['PL', 'NAME', 'TEAM', 'TIME', 'SOURCE_FILE', 'EVENT_DATE']
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.extracted_data)
            
            logger.info(f"Data saved to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving CSV file: {e}")
            return False
    
    def display_summary(self):
        """Display summary of extracted data"""
        print("\n" + "="*60)
        print("PDF SCRAPING RESULTS SUMMARY")
        print("="*60)
        print(f"Total records extracted: {self.total_records}")
        print(f"Source folder: {self.folder_path}")
        
        if self.extracted_data:
            # Show sample records
            print(f"\nSample records (first 5):")
            for i, record in enumerate(self.extracted_data[:5]):
                print(f"Record {i+1}: {record}")
            
            if len(self.extracted_data) > 5:
                print(f"... and {len(self.extracted_data) - 5} more records")
        
        print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_scraper.py <folder_path>")
        print("Example: python pdf_scraper.py 'C:\\path\\to\\pdf\\folder'")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    print(f"Starting PDF scraper for folder: {folder_path}")
    print("-" * 60)
    
    # Create and run scraper
    scraper = PDFScraper(folder_path)
    
    if scraper.process_folder():
        scraper.display_summary()
        
        if scraper.save_to_csv():
            print(f"\n✅ Scraping completed successfully!")
            print(f"📁 Data saved to: extracted_data.csv")
            print(f"📊 Total records: {scraper.total_records}")
        else:
            print("❌ Failed to save data to CSV")
    else:
        print("❌ Failed to process PDF files")

if __name__ == "__main__":
    main()
