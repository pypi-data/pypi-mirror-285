from setuptools import setup, find_packages


from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
setup(
    name='csv_excel_matcher',
    description='Allows users to select and compare columns from two files (either CSV or Excel). The application matches records between the two selected columns and provides both matched and unmatched records, which can then be saved to an Excel file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    version='1.6',
    packages=find_packages(),
    install_require=[
        'pandas', 'openpyxl', 'tkinter'
    ],
    entry_points = {
        "console_scripts": [
            "csv_excel_matcher = csv_excel_matcher:CSVExcelMatcherApp"
        ]
    }
)