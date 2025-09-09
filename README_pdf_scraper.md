# PDF Data Scraper

This script extracts data from PDF files in a folder and saves it to a CSV file. It specifically looks for the following fields:
- **PL** (Place/Position)
- **NAME** (Athlete Name)
- **TEAM** (Team/School)
- **TIME** (Race Time/Result)
- **SOURCE_FILE** (Name of the PDF file)
- **EVENT_DATE** (Event Date)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Method 1: Using the runner script (Recommended)
```bash
python run_pdf_scraper.py "folder_path"
```

### Method 2: Using the main script directly
```bash
python pdf_scraper.py "folder_path"
```

### Examples
```bash
# Process PDFs in the "page 1-3" folder
python run_pdf_scraper.py "page 1-3"

# Process PDFs in a specific directory
python run_pdf_scraper.py "C:\\path\\to\\pdf\\folder"
```

## Output

The script will:
1. Process all PDF files in the specified folder
2. Extract data from tables and text within the PDFs
3. Save all data to `extracted_data.csv`
4. Display a summary showing:
   - Total number of records extracted
   - Sample records
   - Source folder information

## How it Works

1. **Table Detection**: The script first tries to extract data from tables within the PDFs
2. **Column Identification**: It automatically identifies which columns contain the target fields (PL, NAME, TEAM, TIME, EVENT_DATE)
3. **Text Fallback**: If no tables are found, it attempts to extract data from plain text using pattern matching
4. **Data Combination**: All data from all PDFs is combined into a single CSV file
5. **Source Tracking**: Each record includes the source PDF filename

## Supported PDF Formats

- PDFs with embedded tables (preferred)
- PDFs with structured text data
- Multi-page PDFs
- Various table formats and layouts

## Error Handling

The script includes comprehensive error handling:
- Skips corrupted or unreadable PDFs
- Logs warnings for pages with no data
- Continues processing even if individual files fail
- Provides detailed logging information

## Output CSV Format

The CSV file will contain columns in this order:
- PL
- NAME  
- TEAM
- TIME
- SOURCE_FILE
- EVENT_DATE

Each row represents one record extracted from the PDFs, with the SOURCE_FILE column indicating which PDF the data came from.
