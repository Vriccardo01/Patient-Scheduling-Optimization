import tkinter as tk
from tkinter import ttk
from gui.availability_window import AvailabilityWindow
from gui.preview_window import PreviewWindow
from data.load_data import load_patients, load_previous_solution
from data.export_data import export_to_excel
from model.optimization import optimize_schedule

class MainWindow:
    """
    Main application window for patient scheduling optimization.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Patient Scheduling Optimization")

        self.patients = {}
        self.previous_schedule = {}
        self.current_solution = None

        self._initialize_variables()
        self._create_ui()

    def _initialize_variables(self):
   
        self.objective_vars = {
                "Minimize days with more than one country": tk.BooleanVar(value=True),
                "Minimize time slots with more than one country": tk.BooleanVar(value=False),
                "Minimize total working time slots": tk.BooleanVar(value=False),
                "Minimize total working days": tk.BooleanVar(value=False),
                "Minimize differences from previous schedule": tk.BooleanVar(value=False),
            }

        self.constraint_vars = {
            "Maximum two countries per day and time slot": tk.BooleanVar(value=True),
            "Maximum two countries per day": tk.BooleanVar(value=True),
            "Minimum patients per country in time slots with more than two countries": tk.BooleanVar(value=True)
        }

        self.availability_table = {
            ("Monday", "morning"): {"hours": 4, "country": "Any"},
            ("Monday", "afternoon"): {"hours": 4, "country": "Any"},
            ("Tuesday", "morning"): {"hours": 4, "country": "Any"},
            ("Tuesday", "afternoon"): {"hours": 4, "country": "Any"},
            ("Wednesday", "morning"): {"hours": 4, "country": "Any"},
            ("Wednesday", "afternoon"): {"hours": 4, "country": "Any"},
            ("Thursday", "morning"): {"hours": 4, "country": "Any"},
            ("Thursday", "afternoon"): {"hours": 4, "country": "Any"},
            ("Friday", "morning"): {"hours": 4, "country": "Any"},
            ("Friday", "afternoon"): {"hours": 4, "country": "Any"},
            ("Saturday", "morning"): {"hours": 4, "country": "Any"},
            ("Saturday", "afternoon"): {"hours": 4, "country": "Any"},
            ("Sunday", "morning"): {"hours": 0, "country": "Any"},
            ("Sunday", "afternoon"): {"hours": 0, "country": "Any"},
        }

    def _create_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Button(main_frame, text="Load Patients", command=self._load_patients).grid(row=0, column=0, columnspan=2, pady=10)

        left_frame = ttk.LabelFrame(main_frame, text="", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.N))

        ttk.Button(left_frame, text="Open Availability", command=self._open_availability).grid(row=0, column=0, pady=10)

        objective_frame = ttk.LabelFrame(left_frame, text="Objective Function", padding="10")
        objective_frame.grid(row=1, column=0, pady=5, sticky=tk.W)

        for i, (text, var) in enumerate(self.objective_vars.items()):
            ttk.Checkbutton(objective_frame, text=text, variable=var).grid(row=i, column=0, sticky=tk.W)

        constraints_frame = ttk.LabelFrame(left_frame, text="Constraints", padding="10")
        constraints_frame.grid(row=2, column=0, pady=5, sticky=tk.W)

        for i, (text, var) in enumerate(self.constraint_vars.items()):
            ttk.Checkbutton(constraints_frame, text=text, variable=var).grid(row=i, column=0, sticky=tk.W)

        right_frame = ttk.LabelFrame(main_frame, text="", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.N))

        ttk.Button(right_frame, text="Load Previous Solution", command=self._load_previous_solution).grid(row=0, column=0, pady=5)

        start_day_frame = ttk.LabelFrame(right_frame, text="Start Day", padding="10")
        start_day_frame.grid(row=1, column=0, pady=5, sticky=tk.W)

        self.start_day_var = tk.StringVar(value="Monday")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(days):
            ttk.Radiobutton(start_day_frame, text=day, variable=self.start_day_var, value=day).grid(row=0, column=i, padx=5)

        ttk.Checkbutton(right_frame, text="Minimize differences from previous schedule", variable=self.objective_vars["Minimize differences from previous schedule"]).grid(row=2, column=0, pady=5, sticky=tk.W)

        ttk.Button(main_frame, text="Run Optimization", command=self._run_optimization).grid(row=2, column=0, columnspan=2, pady=10)

        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.results_text = tk.Text(results_frame, height=12, width=120)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.results_text['yscrollcommand'] = scrollbar.set

        ttk.Button(results_frame, text="Clear Results", command=self._clear_results).grid(row=0, column=2, pady=10, padx=1, sticky=tk.E)

        ttk.Button(main_frame, text="Preview Solution", command=self._open_preview).grid(row=4, column=0, padx=10, pady=10, sticky=tk.E)

        ttk.Button(main_frame, text="Export to Excel", command=self._export_to_excel).grid(row=4, column=1, padx=120, pady=10, sticky=tk.W)

    def _load_patients(self):
        self.patients = load_patients()
        if self.patients:
            self.results_text.insert(tk.END, f"Loaded {len(self.patients)} patients\n")

    def _load_previous_solution(self):
        self.previous_schedule = load_previous_solution()
        if self.previous_schedule:
            self.results_text.insert(tk.END, "Loaded previous solution\n")

    def _run_optimization(self):
        if not self.patients:
            tk.messagebox.showwarning("Warning", "Load patients first")
            return

        self.current_solution, patients_changed, total_changes = optimize_schedule(self.patients, self.previous_schedule, self.objective_vars, self.constraint_vars, self.start_day_var.get(), self.availability_table)
        
        if self.current_solution:
            self.results_text.insert(tk.END, "Optimal solution found! Ready to export.\n")
            if self.previous_schedule:
                self.results_text.insert(tk.END, f"Compared to the previous schedule, {len(patients_changed)} patients have changed, with a total of {total_changes} changes\n")
        else:
            self.results_text.insert(tk.END, "Impossible find a solution.\n")

    def _export_to_excel(self):
        if not self.current_solution:
            tk.messagebox.showwarning("Warning", "Find a solution first")
            return

        export_to_excel(self.current_solution)
        tk.messagebox.showinfo("Success", "Excel file exported successfully")

    def _open_availability(self):
        AvailabilityWindow(self.root, self.availability_table, self.patients)

    def _open_preview(self):
        if not self.current_solution:
            tk.messagebox.showwarning("Warning", "Find a solution first")
            return
        
        PreviewWindow(self.root, self.current_solution)

    def _clear_results(self):
        self.results_text.delete(1.0, tk.END)