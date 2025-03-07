# Patient Scheduling Optimization

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Gurobi](https://img.shields.io/badge/Gurobi-Optimization-orange)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-green)


## Project Description

This project is a Python-based application for optimizing patient scheduling. It uses `tkinter` for the graphical user interface (GUI) and `gurobipy` for solving the optimization problem. The application allows scheduling patients based on various constraints and objectives, such as minimizing the number of days with more than one country, balancing time usage across time slots, and more.

## Project Structure

The project is organized as follows:
```
patient_scheduling/
│
├── gui/
│ ├── main_window.py # Main application window
│ ├── availability_window.py # Window for managing daily availability
│ ├── preview_window.py # Window for solution preview
│
├── model/
│ ├── optimization.py # Optimization model
│
├── data/
│ ├── load_data.py # Loading patient data
│ ├── export_data.py # Exporting results to Excel
│ └── utils.py # Utility functions
│
└── main.py # Application entry point
```

## Features
- **Load Patient Data**: Import patient data from an Excel file.
- **Optimize Schedule**: Use Gurobi to optimize the schedule based on constraints and objectives.
- **Preview Solution**: View the optimized schedule in a user-friendly interface.
- **Export Results**: Export the optimized schedule to an Excel file.

## Requirements
- Python 3.8+
- Gurobi Optimizer
- Libraries: `pandas`, `tkinter`, `openpyxl`

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Vriccardo01/Patient-Scheduling-Optimization.git
