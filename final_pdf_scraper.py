#!/usr/bin/env python3
"""
Final PDF Data Scraper
Scrapes data from PDF files in a folder and exports to CSV format
Extracts: PL, NAME, TEAM, TIME, SOURCE_FILE, EVENT DATE
Uses multiple PDF libraries as fallbacks
"""

import os
import sys
import csv
import re
import logging
from datetime import datetime
from pathlib import Path

# Try multiple PDF libraries
PDF_AVAILABLE = False
PDF_LIBRARY = None

try:
    import pdfplumber
    PDF_AVAILABLE = True
    PDF_LIBRARY = "pdfplumber"
    print("Using pdfplumber for PDF processing")
except ImportError:
    try:
        import PyPDF2
        PDF_AVAILABLE = True
        PDF_LIBRARY = "PyPDF2"
        print("Using PyPDF2 for PDF processing")
    except ImportError:
        try:
            import pypdf
            PDF_AVAILABLE = True
            PDF_LIBRARY = "pypdf"
            print("Using pypdf for PDF processing")
        except ImportError:
            try:
                import fitz  # PyMuPDF
                PDF_AVAILABLE = True
                PDF_LIBRARY = "PyMuPDF"
                print("Using PyMuPDF for PDF processing")
            except ImportError:
                print("Warning: No PDF libraries available. Install pdfplumber, PyPDF2, pypdf, or PyMuPDF")
                print("Install with: pip install pdfplumber")

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinalPDFScraper:
    def __init__(self, folder_path):
        self.folder_path = Path(folder_path)
        self.extracted_data = []
        self.total_records = 0
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text from a PDF file using available library"""
        if not PDF_AVAILABLE:
            logger.error("No PDF libraries available. Cannot process PDF files.")
            return ""
        
        try:
            if PDF_LIBRARY == "pdfplumber":
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    
                    return text
                    
            elif PDF_LIBRARY == "PyPDF2":
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n"
                    
                    return text
                    
            elif PDF_LIBRARY == "pypdf":
                with open(pdf_path, 'rb') as file:
                    pdf_reader = pypdf.PdfReader(file)
                    text = ""
                    
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text() + "\n"
                    
                    return text
                    
            elif PDF_LIBRARY == "PyMuPDF":
                doc = fitz.open(pdf_path)
                text = ""
                
                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    text += page.get_text() + "\n"
                
                doc.close()
                return text
                
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path.name}: {e}")
            return ""
    
    def extract_data_from_pdf(self, pdf_path):
        """Extract data from a single PDF file"""
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        try:
            text = self.extract_text_from_pdf(pdf_path)
            if not text:
                logger.warning(f"No text extracted from {pdf_path.name}")
                return []
            
            # Extract data from text
            pdf_data = self.extract_from_text(text, pdf_path.name)
            logger.info(f"Extracted {len(pdf_data)} records from {pdf_path.name}")
            return pdf_data
                
        except Exception as e:
            logger.error(f"Error processing {pdf_path.name}: {e}")
            return []
    
    def extract_event_date(self, text):
        """Extract event date from PDF text"""
        # Look for common date patterns in the text
        date_patterns = [
            # Pattern: "February 23-24, 2024"
            r'([A-Za-z]+ \d{1,2}-?\d{0,2},? \d{4})',
            # Pattern: "Feb 23-24, 2024"
            r'([A-Za-z]{3} \d{1,2}-?\d{0,2},? \d{4})',
            # Pattern: "2024-02-23"
            r'(\d{4}-\d{1,2}-\d{1,2})',
            # Pattern: "02/23/2024"
            r'(\d{1,2}/\d{1,2}/\d{4})',
            # Pattern: "23/02/2024"
            r'(\d{1,2}/\d{1,2}/\d{4})',
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Return the first match found
                return matches[0].strip()
        
        # If no date pattern found, return empty string
        return ""

    def extract_from_text(self, text, source_file):
        """Extract data from plain text using pattern matching - ALL TABLES"""
        lines = text.split('\n')
        records = []
        
        # Extract event date from the text
        event_date = self.extract_event_date(text)
        
        # Look for all table headers and extract data from each table
        table_records = self.extract_all_table_data(text, source_file, event_date)
        records.extend(table_records)
        
        return records
    
    def extract_all_table_data(self, text, source_file, event_date):
        """Extract data from ALL table-like structures in text"""
        records = []
        lines = text.split('\n')
        
        # Look for header patterns that might indicate a table
        header_patterns = [
            r'PL\s+NAME\s+YEAR\s+TEAM\s+TIME',
            r'PLACE\s+NAME\s+YEAR\s+TEAM\s+TIME',
            r'POS\s+NAME\s+YEAR\s+TEAM\s+TIME',
            r'RANK\s+NAME\s+YEAR\s+TEAM\s+TIME',
            r'PL\s+ATHLETE\s+YEAR\s+TEAM\s+TIME',
            r'PLACE\s+ATHLETE\s+YEAR\s+TEAM\s+TIME',
            # Also look for patterns without YEAR
            r'PL\s+NAME\s+TEAM\s+TIME',
            r'PLACE\s+NAME\s+TEAM\s+TIME',
            r'POS\s+NAME\s+TEAM\s+TIME',
            r'RANK\s+NAME\s+TEAM\s+TIME',
            r'PL\s+ATHLETE\s+TEAM\s+TIME',
            r'PLACE\s+ATHLETE\s+TEAM\s+TIME',
            # Look for any line with PL/PLACE/POS/RANK followed by data
            r'^PL\s+',
            r'^PLACE\s+',
            r'^POS\s+',
            r'^RANK\s+',
        ]
        
        table_found = False
        for i, line in enumerate(lines):
            line_upper = line.upper().strip()
            
            # Check if this line looks like a header
            for pattern in header_patterns:
                if re.search(pattern, line_upper):
                    table_found = True
                    has_year = 'YEAR' in line_upper
                    
                    # If header doesn't explicitly mention YEAR, check the next few data lines
                    if not has_year:
                        # Look at next 5 lines to see if they contain years
                        for check_line in lines[i+1:i+6]:
                            check_parts = re.split(r'\s+', check_line.strip())
                            if len(check_parts) >= 4:
                                for part in check_parts[1:-1]:  # Skip first (place) and last (time)
                                    # Check for actual year (4 digits)
                                    if part.isdigit() and len(part) == 4 and 2020 <= int(part) <= 2030:
                                        has_year = True
                                        break
                                    # Check for academic year codes (FR-1, SO-2, JR-3, SR-4, etc.)
                                    elif re.match(r'^(FR|SO|JR|SR|GR)[-]?\d*$', part.upper()):
                                        has_year = True
                                        break
                            if has_year:
                                break
                    
                    # Process following lines as data rows
                    for j in range(i + 1, min(i + 200, len(lines))):  # Look at next 200 lines
                        data_line = lines[j].strip()
                        if not data_line:
                            continue
                        
                        # Stop if we hit another header or section
                        if re.search(r'^[A-Z\s]+$', data_line) and len(data_line) > 10:
                            # This looks like a header, stop extracting from this table
                            break
                        
                        # Try to split by whitespace
                        parts = re.split(r'\s+', data_line)
                        
                        if has_year and len(parts) >= 5:
                            # Pattern: PL NAME YEAR TEAM TIME
                            try:
                                place = parts[0]
                                if place.isdigit():
                                    # Look for year in the middle parts (not just parts[1])
                                    year = ""
                                    year_index = -1
                                    for i, part in enumerate(parts[1:-1]):  # Skip first (place) and last (time)
                                        # Check for actual year (4 digits)
                                        if part.isdigit() and len(part) == 4 and 2020 <= int(part) <= 2030:
                                            year = part
                                            year_index = i + 1  # +1 because we skipped parts[0]
                                            break
                                        # Check for academic year codes (FR-1, SO-2, JR-3, SR-4, etc.)
                                        elif re.match(r'^(FR|SO|JR|SR|GR)[-]?\d*$', part.upper()):
                                            year = part
                                            year_index = i + 1  # +1 because we skipped parts[0]
                                            break
                                    
                                    time_part = parts[-1]  # Last part should be time
                                    middle_parts = parts[1:-1]
                                    
                                    # Reconstruct name and team - better parsing
                                    if len(middle_parts) >= 2:
                                        # Remove year from middle_parts if found
                                        if year_index > 0:
                                            # Remove the year from middle_parts
                                            middle_parts = [part for i, part in enumerate(middle_parts) if i != (year_index - 1)]
                                        
                                        # Find the split point between name and team
                                        # Look for common university/team keywords
                                        team_keywords = ['University', 'Universidad', 'College', 'UPR', 'P.R.', 'Caribbean', 'Interamerican', 'Politecnica', 'State', 'Tech', 'Institute', 'Jr.', 'Sr.', 'III', 'II']
                                        
                                        name_parts = []
                                        team_parts = []
                                        found_team_start = False
                                        
                                        for part in middle_parts:
                                            if not found_team_start and any(keyword in part for keyword in team_keywords):
                                                found_team_start = True
                                                team_parts.append(part)
                                            elif found_team_start:
                                                team_parts.append(part)
                                            else:
                                                name_parts.append(part)
                                        
                                        # If no team keyword found, split at 2nd word
                                        if not found_team_start and len(middle_parts) >= 2:
                                            name_parts = middle_parts[:2]
                                            team_parts = middle_parts[2:]
                                        
                                        name = ' '.join(name_parts)
                                        team = ' '.join(team_parts)
                                        
                                        if (place.isdigit() and 
                                            len(name) > 1 and 
                                            len(team) > 1 and 
                                            re.match(r'\d+[:.]?\d*', time_part)):
                                            
                                            record = {
                                                'PL': place,
                                                'NAME': name,
                                                'YEAR': year,
                                                'TEAM': team,
                                                'TIME': time_part,
                                                'SOURCE_FILE': source_file,
                                                'EVENT_DATE': event_date
                                            }
                                            records.append(record)
                            except (IndexError, ValueError):
                                continue
                                
                        elif len(parts) >= 4:
                            # Pattern: PL NAME TEAM TIME (without YEAR)
                            try:
                                place = parts[0]
                                if place.isdigit():
                                    time_part = parts[-1]  # Last part should be time
                                    middle_parts = parts[1:-1]
                                    
                                    # Reconstruct name and team - better parsing
                                    if len(middle_parts) >= 2:
                                        # Find the split point between name and team
                                        # Look for common university/team keywords
                                        team_keywords = ['University', 'Universidad', 'College', 'UPR', 'P.R.', 'Caribbean', 'Interamerican', 'Politecnica']
                                        
                                        name_parts = []
                                        team_parts = []
                                        found_team_start = False
                                        
                                        for part in middle_parts:
                                            if not found_team_start and any(keyword in part for keyword in team_keywords):
                                                found_team_start = True
                                                team_parts.append(part)
                                            elif found_team_start:
                                                team_parts.append(part)
                                            else:
                                                name_parts.append(part)
                                        
                                        # If no team keyword found, split at 2nd word
                                        if not found_team_start and len(middle_parts) >= 2:
                                            name_parts = middle_parts[:2]
                                            team_parts = middle_parts[2:]
                                        
                                        name = ' '.join(name_parts)
                                        team = ' '.join(team_parts)
                                        
                                        if (place.isdigit() and 
                                            len(name) > 1 and 
                                            len(team) > 1 and 
                                            re.match(r'\d+[:.]?\d*', time_part)):
                                            
                                            record = {
                                                'PL': place,
                                                'NAME': name,
                                                'YEAR': '',
                                                'TEAM': team,
                                                'TIME': time_part,
                                                'SOURCE_FILE': source_file,
                                                'EVENT_DATE': event_date
                                            }
                                            records.append(record)
                            except (IndexError, ValueError):
                                continue
                    break  # Found header, continue to look for more tables
        
        if not table_found:
            logger.warning("No table headers found in the document")
        
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
            fieldnames = ['PL', 'NAME', 'YEAR', 'TEAM', 'TIME', 'SOURCE_FILE', 'EVENT_DATE']
            
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
        print(f"PDF library used: {PDF_LIBRARY if PDF_AVAILABLE else 'None'}")
        
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
        print("Usage: python final_pdf_scraper.py <folder_path>")
        print("Example: python final_pdf_scraper.py 'page 1-3'")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    print(f"Starting PDF scraper for folder: {folder_path}")
    print("-" * 60)
    
    # Create and run scraper
    scraper = FinalPDFScraper(folder_path)
    
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
