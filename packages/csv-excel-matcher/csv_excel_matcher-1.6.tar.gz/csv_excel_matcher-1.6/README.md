# CSV and Excel Matcher

CSV and Excel Matcher is a GUI application built with Tkinter that allows users to select and compare columns from two files (either CSV or Excel). The application matches records between the two selected columns and provides both matched and unmatched records, which can then be saved to an Excel file.

## Features

- Load and select columns from CSV or Excel files
- Match records between selected columns
- Display the total number of matched and unmatched records
- Save results to an Excel file with separate sheets for matched and unmatched records

## Installation

To install CSV and Excel Matcher, you can use pip:

```bash
pip install csv-excel-matcher==1.6
```

## To run as an application.
```bash
csv_excel_matcher
```
or
```bash
python -m csv_excel_matcher
```
if above command did not start your application then try these, 

Create *.py file at desired directory.
```python
from csv_excel_matcher import CSVExcelMatcherApp
CSVExcelMatcherApp()
```
These line of code will help to execute the program. 

## In the GUI:
- Click "Browse" to select the first file (CSV or Excel).
- Select the column from the first file that need to be compared
- Click "Browse" to select the second file (CSV or Excel).
- Select the column from the second file that need to be compared
- Click "Match Records" to find common and unmatched records.
- Click "Save Results" to save the results to an Excel file.

## Support
If you encounter any issues or have any questions, feel free to contact me at hari.nikesh.r.cce@gmail.com.

## License
This project is licensed under the MIT License.



