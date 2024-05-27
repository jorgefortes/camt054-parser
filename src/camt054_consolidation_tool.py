""" CAMT054 Consolidation Tool ===========================

This script consolidates CAMT054 XML files into a CSV file based on user-selected tags.
It provides a graphical user interface (GUI) for selecting the input directory, output file,
and the tags to parse.

Author: Jorge Fortes
Version: 1.0
Date: 2024-05-26

Requirements:
- Python 3.x
- tkinter
- xml.etree.ElementTree
- pandas
- os

Usage:
1. Run the script.
2. Use the GUI to select the input directory containing CAMT054 XML files.
3. Choose the output file path for the consolidated CSV file.
4. Select the tags you want to parse.
5. Click 'Start' to process the XML files and save the consolidated data to the CSV file.

License: GNU General Public License

"""

import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import pandas as pd
import os

# Function to parse the CAMT054 XML file and extract the specified tags
def parse_camt054(xml_file, selected_tags):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except ET.ParseError as e:
        messagebox.showerror(
            "XML Parse Error", f"Failed to parse {xml_file}.\nError: {e}"
        )
        return []

    # Define namespace
    ns = {"a": "urn:iso:std:iso:20022:tech:xsd:camt.054.001.04"}

    entries = []
    for entry in root.findall(".//a:Ntry", ns):
        common_data = {
            "Booking Date": entry.find(".//a:BookgDt/a:Dt", ns).text
            if "Booking Date" in selected_tags
            and entry.find(".//a:BookgDt/a:Dt", ns) is not None
            else None,
            "Value Date": entry.find(".//a:ValDt/a:Dt", ns).text
            if "Value Date" in selected_tags
            and entry.find(".//a:ValDt/a:Dt", ns) is not None
            else None,
        }

        for ntry_dtls in entry.findall(".//a:NtryDtls", ns):
            for transaction in ntry_dtls.findall(".//a:TxDtls", ns):
                tx_data = common_data.copy()
                tx_data["Transaction Amount"] = (
                    transaction.find(".//a:Amt", ns).text
                    if "Transaction Amount" in selected_tags
                    and transaction.find(".//a:Amt", ns) is not None
                    else None
                )
                tx_data["Transaction Currency"] = (
                    transaction.find(".//a:Amt", ns).attrib["Ccy"]
                    if "Transaction Currency" in selected_tags
                    and transaction.find(".//a:Amt", ns) is not None
                    else None
                )

                # Related Parties - Debtor
                if (
                    "Debtor Name" in selected_tags
                    or "Debtor Address Line 1" in selected_tags
                    or "Debtor Address Line 2" in selected_tags
                ):
                    debtor = transaction.find(".//a:RltdPties/a:Dbtr", ns)
                    if debtor is not None:
                        tx_data["Debtor Name"] = (
                            debtor.find(".//a:Nm", ns).text
                            if "Debtor Name" in selected_tags
                            and debtor.find(".//a:Nm", ns) is not None
                            else None
                        )
                        address = debtor.find(".//a:PstlAdr", ns)
                        if address is not None:
                            tx_data["Debtor Address Line 1"] = (
                                address.find(".//a:AdrLine[1]", ns).text
                                if "Debtor Address Line 1" in selected_tags
                                and address.find(".//a:AdrLine[1]", ns) is not None
                                else None
                            )
                            tx_data["Debtor Address Line 2"] = (
                                address.find(".//a:AdrLine[2]", ns).text
                                if "Debtor Address Line 2" in selected_tags
                                and address.find(".//a:AdrLine[2]", ns) is not None
                                else None
                            )

                # Debtor Account
                tx_data["Debtor IBAN"] = (
                    transaction.find(".//a:RltdPties/a:DbtrAcct/a:Id/a:IBAN", ns).text
                    if "Debtor IBAN" in selected_tags
                    and transaction.find(".//a:RltdPties/a:DbtrAcct/a:Id/a:IBAN", ns)
                    is not None
                    else None
                )

                # Ultimate Debtor
                tx_data["Ultimate Debtor Name"] = (
                    transaction.find(".//a:RltdPties/a:UltmtDbtr/a:Nm", ns).text
                    if "Ultimate Debtor Name" in selected_tags
                    and transaction.find(".//a:RltdPties/a:UltmtDbtr/a:Nm", ns)
                    is not None
                    else None
                )

                # Remittance Information
                if "Additional Remittance Info 3" in selected_tags:
                    remittance_infos = transaction.findall(
                        ".//a:RmtInf/a:Strd/a:AddtlRmtInf", ns
                    )
                    if len(remittance_infos) >= 3:
                        tx_data["Additional Remittance Info 3"] = remittance_infos[
                            2
                        ].text
                    else:
                        tx_data["Additional Remittance Info 3"] = None

                # Creditor Reference Information
                tx_data["Creditor Reference Type"] = (
                    transaction.find(
                        ".//a:RmtInf/a:Strd/a:CdtrRefInf/a:Tp/a:CdOrPrtry/a:Prtry", ns
                    ).text
                    if "Creditor Reference Type" in selected_tags
                    and transaction.find(
                        ".//a:RmtInf/a:Strd/a:CdtrRefInf/a:Tp/a:CdOrPrtry/a:Prtry", ns
                    )
                    is not None
                    else None
                )
                tx_data["Creditor Reference"] = (
                    transaction.find(".//a:RmtInf/a:Strd/a:CdtrRefInf/a:Ref", ns).text
                    if "Creditor Reference" in selected_tags
                    and transaction.find(".//a:RmtInf/a:Strd/a:CdtrRefInf/a:Ref", ns)
                    is not None
                    else None
                )

                # Charges Information (only under TxDtls)
                if "Total Charges Amount" in selected_tags or any(
                    tag.startswith("Charge") for tag in selected_tags
                ):
                    charges = transaction.find(".//a:Chrgs", ns)
                    if charges is not None:
                        tx_data["Total Charges Amount"] = (
                            charges.find(".//a:TtlChrgsAndTaxAmt", ns).text
                            if "Total Charges Amount" in selected_tags
                            and charges.find(".//a:TtlChrgsAndTaxAmt", ns) is not None
                            else None
                        )
                        charge_records = charges.findall(".//a:Rcrd", ns)
                        if charge_records:
                            for idx, charge in enumerate(charge_records):
                                tx_data[f"Charge {idx + 1} Amount"] = (
                                    charge.find(".//a:Amt", ns).text
                                    if f"Charge {idx + 1} Amount" in selected_tags
                                    and charge.find(".//a:Amt", ns) is not None
                                    else None
                                )
                                tx_data[f"Charge {idx + 1} Currency"] = (
                                    charge.find(".//a:Amt", ns).attrib["Ccy"]
                                    if f"Charge {idx + 1} Currency" in selected_tags
                                    and charge.find(".//a:Amt", ns) is not None
                                    else None
                                )
                                tx_data[f"Charge {idx + 1} Type"] = (
                                    charge.find(".//a:Tp/a:Prtry/a:Id", ns).text
                                    if f"Charge {idx + 1} Type" in selected_tags
                                    and charge.find(".//a:Tp/a:Prtry/a:Id", ns)
                                    is not None
                                    else None
                                )

                entries.append(tx_data)

    return entries


# Function to consolidate data from multiple XML files
def consolidate_camt054(directory, selected_tags):
    all_entries = []
    successful_files = 0

    for filename in os.listdir(directory):
        if filename.endswith(".xml"):
            file_path = os.path.join(directory, filename)
            entries = parse_camt054(file_path, selected_tags)
            if entries:  # Check if entries were parsed successfully
                all_entries.extend(entries)
                successful_files += 1

    consolidated_df = pd.DataFrame(all_entries)
    # Filter the DataFrame to include only the selected tags
    consolidated_df = consolidated_df[selected_tags]
    return consolidated_df, successful_files


# Function to validate parsed entries
def validate_entries(df, selected_tags):
    for tag in selected_tags:
        if df[tag].isnull().all():
            return False, tag
    return True, None


# Function to select the input directory
def select_input_directory():
    directory = filedialog.askdirectory()
    input_dir_entry.delete(0, tk.END)
    input_dir_entry.insert(0, directory)


# Function to select the output file
def select_output_file():
    file = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )
    output_file_entry.delete(0, tk.END)
    output_file_entry.insert(0, file)


# Function to start the process
def start_process():
    input_directory = input_dir_entry.get()
    output_file = output_file_entry.get()

    if not input_directory or not output_file:
        messagebox.showwarning(
            "Input Error", "Please specify an input directory and an output file."
        )
        return

    selected_tags = [tag for tag, var in tag_vars.items() if var.get()]

    if not selected_tags:
        messagebox.showwarning(
            "Input Error", "Please select at least one tag to parse."
        )
        return

    try:
        consolidated_df, successful_files = consolidate_camt054(
            input_directory, selected_tags
        )
        is_valid, invalid_tag = validate_entries(consolidated_df, selected_tags)

        if is_valid:
            consolidated_df.to_csv(output_file, index=False, encoding="utf-8-sig")
            messagebox.showinfo(
                "Success",
                f"Data has been successfully consolidated and saved.\n{successful_files} XML files were successfully parsed.",
            )
        else:
            messagebox.showwarning(
                "Validation Error",
                f"All entries for the tag '{invalid_tag}' are missing. Please check the XML files.",
            )
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")


# Create the GUI
root = tk.Tk()
root.title("CAMT054 Consolidation")

# Input directory
tk.Label(root, text="Input Directory:").grid(
    row=0, column=0, padx=10, pady=10, sticky="e"
)
input_dir_entry = tk.Entry(root, width=50)
input_dir_entry.grid(row=0, column=1, padx=10, pady=10)
input_dir_button = tk.Button(root, text="Browse", command=select_input_directory)
input_dir_button.grid(row=0, column=2, padx=10, pady=10)

# Output file
tk.Label(root, text="Output File:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
output_file_entry = tk.Entry(root, width=50)
output_file_entry.grid(row=1, column=1, padx=10, pady=10)
output_file_button = tk.Button(root, text="Browse", command=select_output_file)
output_file_button.grid(row=1, column=2, padx=10, pady=10)

# Tag selection
tk.Label(root, text="Select Tags to Parse:").grid(
    row=2, column=0, padx=10, pady=10, sticky="e"
)

# Define the tags and create checkboxes for each tag
tags = [
    "Booking Date",
    "Value Date",
    "Transaction Amount",
    "Transaction Currency",
    "Debtor Name",
    "Debtor Address Line 1",
    "Debtor Address Line 2",
    "Debtor IBAN",
    "Ultimate Debtor Name",
    "Additional Remittance Info 3",
    "Creditor Reference Type",
    "Creditor Reference",
    "Total Charges Amount",
    "Charge 1 Amount",
    "Charge 1 Currency",
    "Charge 1 Type",
    "Charge 2 Amount",
    "Charge 2 Currency",
    "Charge 2 Type",
]

tag_vars = {tag: tk.BooleanVar() for tag in tags}

tag_frame = tk.Frame(root)
tag_frame.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

for i, tag in enumerate(tags):
    chk = tk.Checkbutton(tag_frame, text=tag, variable=tag_vars[tag])
    chk.grid(row=i // 3, column=i % 3, sticky="w")

# Start button
start_button = tk.Button(root, text="Start", command=start_process)
start_button.grid(row=4, column=0, columnspan=3, pady=20)

# Start the GUI
root.mainloop()
