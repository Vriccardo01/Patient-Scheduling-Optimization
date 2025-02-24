import pandas as pd
from tkinter import filedialog, messagebox

def export_to_excel(solution_data, filename=None):
    """
    Export the optimized schedule to an Excel file.

    :param solution_data: Dictionary containing the optimized schedule data.
    :param filename: Optional. The name of the Excel file to save. If not provided, the user will be prompted to choose a file.
    """
    if not solution_data:
        messagebox.showwarning("Warning", "No solution data to export.")
        return

    # Prepare data for export
    patients_per_day_slot = _prepare_data_for_export(solution_data["patients_per_day_slot"], True)
    countries_per_day_slot = _prepare_data_for_export(solution_data["countries_per_day_slot"], True)
    time_per_day_slot = _prepare_data_for_export(solution_data["time_per_day_slot"], True)
    shifts_per_patient = _prepare_data_for_export(solution_data["shifts_per_patient"], False)

    # If no filename is provided, prompt the user to choose a file
    if not filename:
        filename = filedialog.asksaveasfilename(
            initialdir="./",
            initialfile="schedule.xlsx",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save Schedule As"
        )
        if not filename:  # User canceled the dialog
            return

    try:
        # Write data to Excel
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            pd.DataFrame(patients_per_day_slot).T.to_excel(writer, sheet_name="Patients per Day and Slot", index=True, header=False)
            pd.DataFrame(countries_per_day_slot).T.to_excel(writer, sheet_name="Countries per Day and Slot", index=True, header=False)
            pd.DataFrame(time_per_day_slot).T.to_excel(writer, sheet_name="Time per Day and Slot", index=True, header=False)
            pd.DataFrame(shifts_per_patient).T.to_excel(writer, sheet_name="Shifts per Patient", index=True, header=False)

            # Auto-adjust column widths
            for sheet in writer.sheets.values():
                for column in sheet.columns:
                    max_length = max(len(str(cell.value)) for cell in column)
                    sheet.column_dimensions[column[0].column_letter].width = max_length + 2

        messagebox.showinfo("Success", f"Schedule exported successfully to:\n{filename}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to export schedule: {str(e)}")


def _prepare_data_for_export(data, is_day_slot_format):
    """
    Prepare data for export by formatting it into a consistent structure.

    :param data: The data to prepare (e.g., patients_per_day_slot, countries_per_day_slot, etc.).
    :param is_day_slot_format: Whether the data is in (day, slot) format (True) or patient format (False).
    :return: Formatted data ready for export.
    """    
    if is_day_slot_format:
        # Convert (day, slot) keys to "day slot" format
        formatted_data = {f"{day} {slot}": value for (day, slot), value in data.items()}
    else:
        # Convert shifts to "day slot" format
        formatted_data = {patient: [f"{day} {slot}" for (day, slot) in shifts] for patient, shifts in data.items()}

    # Ensure all rows have the same length by padding with empty strings
    max_length = max(len(v) for v in formatted_data.values())
    formatted_data = {k: v + [''] * (max_length - len(v)) for k, v in formatted_data.items()}

    return formatted_data