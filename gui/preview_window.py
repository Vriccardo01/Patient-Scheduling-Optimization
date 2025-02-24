import tkinter as tk
from tkinter import ttk

class PreviewWindow:
    """
    Window for previewing the optimized patient scheduling solution.
    """

    def __init__(self, parent, solution_data):
        """
        Initialize the preview window.

        :param parent: The parent window (main application window).
        :param solution_data: Dictionary containing the optimized schedule data.
        """
        self.parent = parent
        self.solution_data = solution_data

        # Create the window
        self.window = tk.Toplevel(parent)
        self.window.title("Preview Solution")

        # Create the UI
        self._create_ui()

    def _create_ui(self):
        """
        Create the user interface for the preview window.
        """
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Create the first table: Details by Day and Time Slot
        self._create_table1(main_frame)

        # Create the second table: Shifts per Patient
        self._create_table2(main_frame)

    def _create_table1(self, parent_frame):
        """
        Create the first table to display details by day and time slot.

        :param parent_frame: The parent frame to attach the table to.
        """
        frame = ttk.Frame(parent_frame)
        frame.grid(row=0, column=0, padx=10, pady=10)

        # Title for the first table
        ttk.Label(frame, text="Table 1: Details by Day and Time Slot", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, pady=5
        )

        # Dropdown to select day and time slot
        day_slot_options = [f"{day} {slot}" for day, slot in self.solution_data["patients_per_day_slot"].keys()]
        self.selected_day_slot = tk.StringVar()
        day_slot_combobox = ttk.Combobox(frame, textvariable=self.selected_day_slot, values=day_slot_options)
        day_slot_combobox.grid(row=1, column=0, padx=5, pady=5, columnspan=3)
        day_slot_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_table1())

        # Table to display data
        self.table1 = ttk.Treeview(frame, columns=("Patient", "Country", "Time"), show="headings")
        self.table1.heading("Patient", text="Patient")
        self.table1.heading("Country", text="Country")
        self.table1.heading("Time", text="Time (Minutes)")
        self.table1.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # Set default values
        if day_slot_options:
            self.selected_day_slot.set(day_slot_options[0])
        self._update_table1()

    def _update_table1(self):
        """
        Update the first table based on the selected day and time slot.
        """
        self.table1.delete(*self.table1.get_children())
        day_slot_str = self.selected_day_slot.get()

        # Convert the string "day slot" into a tuple (day, slot)
        if day_slot_str:
            day, slot = day_slot_str.split()
            day_slot = (day, slot)
        else:
            day_slot = None

        if day_slot:
            # Get the list of patients scheduled for the selected day and time slot
            patients = self.solution_data["patients_per_day_slot"].get(day_slot, [])
            countries = self.solution_data["countries_per_day_slot"].get(day_slot, [])
            times = self.solution_data["time_per_day_slot"].get(day_slot, [])

            # Display patient name, country, and time in the table
            for patient, country, time in zip(patients, countries, times):
                self.table1.insert("", "end", values=(patient, country, time))

    def _create_table2(self, parent_frame):
        """
        Create the second table to display shifts per patient.

        :param parent_frame: The parent frame to attach the table to.
        """
        frame = ttk.Frame(parent_frame)
        frame.grid(row=1, column=0, padx=10, pady=10)

        # Title for the second table
        ttk.Label(frame, text="Table 2: Shifts per Patient", font=("Arial", 12, "bold")).grid(
            row=0, column=0, pady=5
        )

        # Dropdown to select a patient
        patient_options = list(self.solution_data["shifts_per_patient"].keys())
        self.selected_patient = tk.StringVar()
        patient_combobox = ttk.Combobox(frame, textvariable=self.selected_patient, values=patient_options)
        patient_combobox.grid(row=1, column=0, padx=5, pady=5)
        patient_combobox.bind("<<ComboboxSelected>>", lambda event: self._update_table2())

        # Table to display data
        self.table2 = ttk.Treeview(frame, columns=("Day", "Time Slot"), show="headings")
        self.table2.heading("Day", text="Day")
        self.table2.heading("Time Slot", text="Time Slot")
        self.table2.grid(row=2, column=0, padx=5, pady=5)

        # Set default values
        if patient_options:
            self.selected_patient.set(patient_options[0])
        self._update_table2()

    def _update_table2(self):
        """
        Update the second table based on the selected patient.
        """
        self.table2.delete(*self.table2.get_children())
        patient = self.selected_patient.get()
        shifts = self.solution_data["shifts_per_patient"].get(patient, [])

        for shift in shifts:
            self.table2.insert("", "end", values=shift)