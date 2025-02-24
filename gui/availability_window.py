import tkinter as tk
from tkinter import ttk

class AvailabilityWindow:
    """
    Window for setting daily availability for patient scheduling.
    """

    def __init__(self, parent, availability_data, patients):
        """
        Initialize the availability window.

        :param parent: The parent window (main application window).
        :param availability_data: Dictionary containing current availability data.
        :param patients: Dictionary of patients to extract unique countries.
        """
        self.parent = parent
        self.availability_data = availability_data
        self.patients = patients

        # Create the window
        self.window = tk.Toplevel(parent)
        self.window.title("Daily Availability Settings")

        # Dictionary to store widget references
        self.widgets = {}

        # Create the UI
        self._create_ui()

    def _create_ui(self):
        """
        Create the user interface for the availability window.
        """
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Extract unique countries from patients
        countries = list(set(patient["country"] for patient in self.patients.values()))
        countries.sort()  # Sort alphabetically

        # Days of the week and time slots
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        time_slots = ["morning", "afternoon"]

        # Create headers for the table
        ttk.Label(main_frame, text="Day").grid(row=0, column=0, padx=5, pady=5)
        for j, slot in enumerate(time_slots):
            ttk.Label(main_frame, text=slot).grid(row=0, column=j + 1, padx=5, pady=5)

        # Create the availability table
        for i, day in enumerate(days_of_week):
            # Label for the day
            ttk.Label(main_frame, text=day).grid(row=i + 1, column=0, padx=5, pady=5)

            for j, slot in enumerate(time_slots):
                # Frame for each cell
                cell_frame = ttk.Frame(main_frame)
                cell_frame.grid(row=i + 1, column=j + 1, padx=5, pady=5)

                # Spinbox for available hours
                hours_var = tk.DoubleVar(value=self.availability_data.get((day, slot), {"hours": 0.0})["hours"])
                spinbox = ttk.Spinbox(cell_frame, from_=0, to=12, increment=0.5, textvariable=hours_var, width=5)
                spinbox.grid(row=0, column=0, padx=5)

                # Combobox for country selection
                country_var = tk.StringVar(value=self.availability_data.get((day, slot), {"country": "Any"})["country"])
                combobox = ttk.Combobox(cell_frame, textvariable=country_var, values=["Any"] + countries, width=15)
                combobox.grid(row=0, column=1, padx=5)

                # Store widgets in the dictionary
                self.widgets[(day, slot)] = {"hours": hours_var, "country": country_var}

        # Save button
        ttk.Button(main_frame, text="Save Availability", command=self._save_availability).grid(
            row=len(days_of_week) + 1, column=0, columnspan=len(time_slots) + 1, pady=10
        )

    def _save_availability(self):
        """
        Save the availability settings and close the window.
        """
        for (day, slot), widget in self.widgets.items():
            hours = widget["hours"].get()
            country = widget["country"].get()
            self.availability_data[(day, slot)] = {"hours": hours, "country": country}

        # Close the window
        self.window.destroy()