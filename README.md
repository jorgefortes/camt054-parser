# CAMT054 Consolidation Tool

## Description

The CAMT054 Consolidation Tool is a Python-based application designed to consolidate CAMT054 XML files into a single CSV file based on user-selected tags. The tool provides a graphical user interface (GUI) for selecting the input directory, output file, and the specific tags to parse from the XML files.

## Features

- Consolidates multiple CAMT054 XML files into a single CSV file.
- Allows users to select which tags to parse from the XML files.
- Provides a simple GUI for easy operation.

## Requirements

- Python 3.x
- tkinter
- xml.etree.ElementTree
- pandas
- os

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/camt054-consolidation-tool.git
   cd camt054-consolidation-tool
2. **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
## Running the Application

1. **Execute the script:**
    ````bash
    python camt054_consolidation_tool.py
2. **Using the GUI:**
- Select the input directory containing CAMT054 XML files.
- Choose the output file path for the consolidated CSV file.
- Select the tags you want to parse.
- Click 'Start' to process the XML files and save the consolidated data to the CSV file.

## Usage

1. **Run the script:**
    ```bash
    python camt054_consolidation_tool.py
2. **Using the GUI:**
- Input Directory: Use the 'Browse' button to select the directory containing your CAMT054 XML - files.
- Output File: Use the 'Browse' button to choose where to save the consolidated CSV file.
- Select Tags to Parse: Check the boxes next to the tags you want to include in the CSV file.
- Start Process: Click the 'Start' button to begin parsing the XML files and creating the CSV file.

## Author

Jorge Fortes

## Version

1.0 (Date: 2024-05-26)

## License

This project is licensed under the GNU General Public License.

- For any issues or contributions, please open a new issue or submit a pull request on the GitHub repository.

- This tool simplifies the process of consolidating CAMT054 XML files, making it easier to work with large sets of transaction data. Enjoy using the CAMT054 Consolidation Tool!