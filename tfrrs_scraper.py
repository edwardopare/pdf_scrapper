#!/usr/bin/env python3
"""
TFRRS Track & Field Results Scraper
Scrapes table data from TFRRS website and exports to CSV format
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TFRRSScraper:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.soup = None
        
    def fetch_page(self):
        """Fetch the webpage content"""
        try:
            logger.info(f"Fetching data from: {self.url}")
            response = self.session.get(self.url, timeout=30)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("Page fetched successfully")
            return True
        except requests.RequestException as e:
            logger.error(f"Error fetching page: {e}")
            return False
    
    def extract_table_data(self, table, table_name="table"):
        """Extract data from a specific table"""
        if not table:
            logger.warning(f"No table found for {table_name}")
            return None
            
        # Extract headers
        headers = []
        header_row = table.find('tr')
        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = th.get_text(strip=True)
                if header_text:  # Only add non-empty headers
                    headers.append(header_text)
        
        # Extract rows
        rows = []
        for row in table.find_all('tr')[1:]:  # Skip header row
            cells = row.find_all(['td', 'th'])
            row_data = []
            for cell in cells:
                cell_text = cell.get_text(strip=True)
                # Clean up the text - remove extra whitespace and newlines
                cell_text = re.sub(r'\s+', ' ', cell_text)
                row_data.append(cell_text)
            
            # Only add rows that have data
            if any(cell.strip() for cell in row_data):
                rows.append(row_data)
        
        logger.info(f"Extracted {len(rows)} rows from {table_name}")
        return {'headers': headers, 'rows': rows}
    
    def find_all_tables(self):
        """Find all tables on the page and categorize them"""
        tables = self.soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        table_data = {}
        
        for i, table in enumerate(tables):
            # Try to identify table type by looking for specific text or structure
            table_name = f"table_{i+1}"
            
            # Look for table captions or nearby headings
            caption = table.find('caption')
            if caption:
                table_name = caption.get_text(strip=True).lower().replace(' ', '_')
            
            # Look for nearby headings
            prev_heading = table.find_previous(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if prev_heading:
                heading_text = prev_heading.get_text(strip=True).lower()
                if any(keyword in heading_text for keyword in ['result', 'finish', 'time', 'place', 'rank']):
                    table_name = heading_text.replace(' ', '_')
            
            # Extract data from this table
            data = self.extract_table_data(table, table_name)
            if data and data['rows']:
                table_data[table_name] = data
        
        return table_data
    
    def save_to_csv(self, table_data, base_filename="tfrrs_results"):
        """Save all table data to separate CSV files"""
        saved_files = []
        
        for table_name, data in table_data.items():
            if not data or not data['rows']:
                continue
                
            filename = f"{base_filename}_{table_name}.csv"
            
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    if data['headers']:
                        writer.writerow(data['headers'])
                    
                    # Write rows
                    writer.writerows(data['rows'])
                
                logger.info(f"Saved {len(data['rows'])} rows to {filename}")
                saved_files.append(filename)
                
            except Exception as e:
                logger.error(f"Error saving {filename}: {e}")
        
        return saved_files
    
    def save_combined_csv(self, table_data, filename="tfrrs_combined_results.csv"):
        """Save all tables to a single CSV with table identification"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Table_Name', 'Row_Number'] + ['Column_' + str(i) for i in range(20)])  # Adjust column count as needed
                
                for table_name, data in table_data.items():
                    if not data or not data['rows']:
                        continue
                    
                    for row_num, row in enumerate(data['rows'], 1):
                        # Pad row with empty strings if needed
                        padded_row = row + [''] * (20 - len(row))
                        writer.writerow([table_name, row_num] + padded_row)
            
            logger.info(f"Combined data saved to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error saving combined CSV: {e}")
            return None
    
    def display_table_summary(self, table_data):
        """Display a summary of extracted tables"""
        print("\n" + "="*60)
        print("TFRRS SCRAPING RESULTS SUMMARY")
        print("="*60)
        
        for table_name, data in table_data.items():
            if data and data['rows']:
                print(f"\nTable: {table_name}")
                print(f"Headers: {data['headers']}")
                print(f"Number of rows: {len(data['rows'])}")
                
                # Show first few rows as preview
                print("Preview (first 3 rows):")
                for i, row in enumerate(data['rows'][:3]):
                    print(f"  Row {i+1}: {row}")
                
                if len(data['rows']) > 3:
                    print(f"  ... and {len(data['rows']) - 3} more rows")
        
        print("\n" + "="*60)

def main():
    # URL to scrape
    url = "https://www.tfrrs.org/results/82468/5018295/FRIDAY_KNIGHT_LIGHTS_INDOOR_MEET/Mens-200-Meters"
    
    # Create scraper instance
    scraper = TFRRSScraper(url)
    
    # Fetch the page
    if not scraper.fetch_page():
        print("Failed to fetch the webpage. Please check the URL and try again.")
        return
    
    # Extract all table data
    table_data = scraper.find_all_tables()
    
    if not table_data:
        print("No table data found on the webpage.")
        return
    
    # Display summary
    scraper.display_table_summary(table_data)
    
    # Save to separate CSV files
    saved_files = scraper.save_to_csv(table_data)
    
    # Save combined CSV
    combined_file = scraper.save_combined_csv(table_data)
    
    print(f"\nScraping completed!")
    print(f"Individual CSV files created: {saved_files}")
    if combined_file:
        print(f"Combined CSV file created: {combined_file}")

if __name__ == "__main__":
    main()
