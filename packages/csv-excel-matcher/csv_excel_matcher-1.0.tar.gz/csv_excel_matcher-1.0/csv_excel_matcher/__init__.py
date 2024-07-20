import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd

class CSVExcelMatcherApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSV and Excel Matcher")
        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        self.file1_label = tk.Label(self.root, text="Select first file (CSV or Excel):")
        self.file1_label.pack()

        self.file1_button = tk.Button(self.root, text="Browse", command=self.load_file1)
        self.file1_button.pack()

        self.file1_column_label = tk.Label(self.root, text="Select column from first file:")
        self.file1_column_label.pack()

        self.file1_column_combobox = ttk.Combobox(self.root, state='readonly')
        self.file1_column_combobox.pack()

        self.file2_label = tk.Label(self.root, text="Select second file (CSV or Excel):")
        self.file2_label.pack()

        self.file2_button = tk.Button(self.root, text="Browse", command=self.load_file2)
        self.file2_button.pack()

        self.file2_column_label = tk.Label(self.root, text="Select column from second file:")
        self.file2_column_label.pack()

        self.file2_column_combobox = ttk.Combobox(self.root, state='readonly')
        self.file2_column_combobox.pack()

        self.match_button = tk.Button(self.root, text="Match Records", command=self.match_records)
        self.match_button.pack()

        self.result_label = tk.Label(self.root, text="Results:")
        self.result_label.pack()

        self.result_text = tk.Text(self.root, height=10, width=50)
        self.result_text.pack()

        self.save_button = tk.Button(self.root, text="Save Results", command=self.save_results)
        self.save_button.pack()

        self.file1 = None
        self.file2 = None
        self.common_records = None
        self.unmatched_records1 = None
        self.unmatched_records2 = None

    def load_file1(self):
        self.file1 = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if self.file1:
            self.result_text.insert(tk.END, f"Loaded first file: {self.file1}\n")
            if self.file1.endswith('.csv'):
                data = pd.read_csv(self.file1)
            else:
                data = pd.read_excel(self.file1)
            self.file1_column_combobox['values'] = list(data.columns)
        else:
            messagebox.showwarning("Warning", "No file selected")

    def load_file2(self):
        self.file2 = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
        if self.file2:
            self.result_text.insert(tk.END, f"Loaded second file: {self.file2}\n")
            if self.file2.endswith('.csv'):
                data = pd.read_csv(self.file2)
            else:
                data = pd.read_excel(self.file2)
            self.file2_column_combobox['values'] = list(data.columns)
        else:
            messagebox.showwarning("Warning", "No file selected")

    def match_records(self):
        if self.file1 and self.file2:
            try:
                if self.file1.endswith('.csv'):
                    data1 = pd.read_csv(self.file1)
                else:
                    data1 = pd.read_excel(self.file1)

                if self.file2.endswith('.csv'):
                    data2 = pd.read_csv(self.file2)
                else:
                    data2 = pd.read_excel(self.file2)

                column1 = self.file1_column_combobox.get()
                column2 = self.file2_column_combobox.get()

                if not column1 or not column2:
                    messagebox.showwarning("Warning", "Please select columns to match")
                    return

                common_values = set(data1[column1]).intersection(set(data2[column2]))
                self.common_records = pd.merge(data1[data1[column1].isin(common_values)], 
                                               data2[data2[column2].isin(common_values)], 
                                               left_on=column1, right_on=column2)

                self.unmatched_records1 = data1[~data1[column1].isin(common_values)]
                self.unmatched_records2 = data2[~data2[column2].isin(common_values)]

                self.result_text.insert(tk.END, f"Total number of matched records: {len(self.common_records)}\n")
                self.result_text.insert(tk.END, f"Total number of unmatched records in second file: {len(self.unmatched_records2)}\n")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showwarning("Warning", "Please select both files")

    def save_results(self):
        if self.common_records is not None:
            output_file = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if output_file:
                with pd.ExcelWriter(output_file) as writer:
                    self.common_records.to_excel(writer, sheet_name='Matches', index=False)
                    self.unmatched_records2.to_excel(writer, sheet_name='Unmatched_File', index=False)
                self.result_text.insert(tk.END, f"Results have been written to {output_file}\n")
            else:
                messagebox.showwarning("Warning", "No output file selected")
        else:
            messagebox.showwarning("Warning", "No records to save")


# For demostration purpose how to use this feature as file!
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = CSVExcelMatcherApp(root)
#     root.mainloop()
