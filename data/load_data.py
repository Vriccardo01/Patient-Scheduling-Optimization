import pandas as pd
from data.utils import normalize_name
from tkinter import filedialog, messagebox

def load_patients():
    """
    Load patient data from an Excel file.

    The Excel file should contain a main sheet with patient information and additional sheets for shift preferences.

    :return: Dictionary of patients, where each patient has a name, country, time requirement, and shift preferences.
    """
    filename = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        title="Select Patient Data File"
    )

    if not filename:
        return {}

    try:
        # Use a context manager to ensure the file is closed properly
        with pd.ExcelFile(filename) as xls:

            # Find the main sheet (contains patient information)
            main_sheet_name = None
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                if "name" in df.columns and "country" in df.columns and "time" in df.columns:
                    main_sheet_name = sheet_name
                    break

            if not main_sheet_name:
                messagebox.showerror("Error", "Main sheet not found. Ensure the file contains columns: 'name', 'country', 'time'.")
                return {}

            # Load the main sheet
            df_patients = pd.read_excel(xls, sheet_name=main_sheet_name)
            patients = df_patients.to_dict(orient="index")

            flag_error = False
            # Load shift preferences from additional sheets
            for patient_id, patient_data in patients.items():
                shift_sheet_name = str(patient_data.get("shift_sheet", ""))  # Get the shift sheet name from the patient data
                if shift_sheet_name in xls.sheet_names:
                    df_shifts = pd.read_excel(xls, sheet_name=shift_sheet_name, header=None)
                    shifts = df_shifts.values.tolist()
                    # Normalizza la tabella dei turni
                    shifts_normalized = []
                    for row in shifts:
                        riga_normalizzata = [normalize_name(cella) for cella in row]
                        shifts_normalized.append(riga_normalizzata)
                    patient_data["shift_sheet"] = shifts_normalized
                else:
                    flag_error = True

            if flag_error:
                messagebox.showerror("Errore", f"Alcuni turni non sono stati trovati")
                return {}

            return patients

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load patient data: {str(e)}")
        return {}

def load_previous_solution():
    """
    Load a previous schedule from an Excel file.

    The Excel file should contain a sheet named "Previous Schedule" with patient assignments.

    :return: Dictionary representing the previous schedule, where keys are (patient_name, day, slot) and values are 1 (assigned) or 0 (not assigned).
    """
    filename = filedialog.askopenfilename(
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        title="Select Previous Schedule File"
    )

    if not filename:
        return {}

    try:
        # Use a context manager to ensure the file is closed properly
        with pd.ExcelFile(filename) as xls:

            # Check if the "Shifts per Patient" sheet exists
            if "Shifts per Patient" not in xls.sheet_names:
                messagebox.showerror("Error", "The file must contain a sheet named 'Shifts per Patient'.")
                return {}

            # Load the "Previous Schedule" sheet
            df = pd.read_excel(xls, sheet_name="Shifts per Patient", header=None)

            # Convert the DataFrame into a dictionary
            previous_schedule = {}
            for index, row in df.iterrows():
                patient_name = row[0]  # First column contains patient names
                shifts = row[1:].dropna().tolist()  # Remaining columns contain shifts (day and slot)

                # Iterate through the shifts and add them to the dictionary
                for shift in shifts:
                    if " " in shift.strip():
                        day, slot = shift.strip().split()
                        previous_schedule[(patient_name, day, slot)] = 1  # Mark as assigned
                    else:
                        day = shift.strip()
                        previous_schedule[(patient_name, day, "morning")] = 1  # Default to morning slot
                        previous_schedule[(patient_name, day, "afternoon")] = 1  # Default to afternoon slot

            return previous_schedule

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load previous schedule: {str(e)}")
        return {}