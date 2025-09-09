# TFRRS Track & Field Results Scraper

This Python script scrapes table data from TFRRS (Track & Field Results Reporting System) websites and exports the data to CSV format.

## Features

- **Comprehensive Table Detection**: Automatically finds and extracts data from all tables on the page
- **Multiple Output Formats**: Creates both individual CSV files for each table and a combined CSV file
- **Robust Data Cleaning**: Handles various table formats and cleans up text data
- **Error Handling**: Includes proper error handling and logging
- **Flexible Usage**: Can be used with any TFRRS results page URL

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python run_scraper.py
```

This will scrape the default URL (Men's 200 Meters results from Friday Knight Lights Indoor Meet).

### Custom URL
```bash
python run_scraper.py "https://www.tfrrs.org/results/82468/5018295/FRIDAY_KNIGHT_LIGHTS_INDOOR_MEET/Mens-200-Meters"
```

### Advanced Usage
```python
from tfrrs_scraper import TFRRSScraper

# Create scraper instance
scraper = TFRRSScraper("https://www.tfrrs.org/results/82468/5018295/FRIDAY_KNIGHT_LIGHTS_INDOOR_MEET/Mens-200-Meters")

# Fetch and extract data
if scraper.fetch_page():
    table_data = scraper.find_all_tables()
    
    # Save individual CSV files
    saved_files = scraper.save_to_csv(table_data)
    
    # Save combined CSV
    combined_file = scraper.save_combined_csv(table_data)
```

## Output Files

The scraper creates several output files:

1. **Individual CSV files**: `tfrrs_results_table_1.csv`, `tfrrs_results_table_2.csv`, etc.
   - Each file contains data from one specific table
   - Headers are preserved from the original table

2. **Combined CSV file**: `tfrrs_combined_results.csv`
   - Contains all tables in one file
   - Includes table identification column
   - Useful for analysis across multiple result sections

## Example Output

The script will display a summary like this:

```
============================================================
TFRRS SCRAPING RESULTS SUMMARY
============================================================

Table: results_table
Headers: ['Place', 'Name', 'Team', 'Time', 'Heat']
Number of rows: 25
Preview (first 3 rows):
  Row 1: ['1', 'John Smith', 'University A', '21.45', '1']
  Row 2: ['2', 'Mike Johnson', 'University B', '21.67', '1']
  Row 3: ['3', 'David Brown', 'University C', '21.89', '1']
  ... and 22 more rows
```

## Technical Details

- **User Agent**: Uses a realistic browser user agent to avoid blocking
- **Timeout**: 30-second timeout for requests
- **Encoding**: UTF-8 encoding for proper character handling
- **Error Handling**: Comprehensive error handling with logging
- **Data Cleaning**: Removes extra whitespace and normalizes text

## Requirements

- Python 3.6+
- requests
- beautifulsoup4
- pandas
- lxml

## Notes

- The script respects website structure and extracts data responsibly
- All extracted data is saved locally - no data is sent to external servers
- The scraper handles various table formats commonly found on TFRRS pages
- Logging is included for debugging and monitoring scraping progress

## Troubleshooting

If you encounter issues:

1. **Connection errors**: Check your internet connection and the URL
2. **No tables found**: The page structure might have changed or the URL might be incorrect
3. **Empty CSV files**: The tables might not contain data or have a different structure

Check the console output for detailed error messages and logging information.
