#!/usr/bin/env python3
"""
Simple script to run the TFRRS scraper
"""

from tfrrs_scraper import TFRRSScraper
import sys

def main():
    # Default URL - can be overridden with command line argument
    default_url = "https://www.tfrrs.org/results/82468/5018295/FRIDAY_KNIGHT_LIGHTS_INDOOR_MEET/Mens-200-Meters"
    
    # Get URL from command line argument or use default
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    
    print(f"Starting TFRRS scraper for URL: {url}")
    print("-" * 60)
    
    # Create and run scraper
    scraper = TFRRSScraper(url)
    
    if scraper.fetch_page():
        table_data = scraper.find_all_tables()
        
        if table_data:
            scraper.display_table_summary(table_data)
            saved_files = scraper.save_to_csv(table_data)
            combined_file = scraper.save_combined_csv(table_data)
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"📁 Individual CSV files: {saved_files}")
            if combined_file:
                print(f"📁 Combined CSV file: {combined_file}")
        else:
            print("❌ No table data found on the webpage.")
    else:
        print("❌ Failed to fetch the webpage. Please check the URL and try again.")

if __name__ == "__main__":
    main()
