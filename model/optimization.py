from gurobipy import Model, GRB, quicksum

def optimize_schedule(patients, previous_schedule, objective_vars, constraint_vars, start_day, availability_table):
    """
    Optimize the patient scheduling based on the given constraints and objectives.

    :param patients: Dictionary of patients.
    :param previous_schedule: Dictionary of the previous schedule (if any).
    :param objective_vars: Dictionary of objective variables (e.g., minimize days with multiple countries).
    :param constraint_vars: Dictionary of constraint variables (e.g., maximum two countries per day).
    :param start_day: The day from which to start the optimization.
    :param availability_table: Dictionary of availability for each day and time slot.
    :return: Dictionary containing the optimized schedule.
    """
    try:
        # Days of the week and time slots
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        time_slots = ["morning", "afternoon"]

        # Extract unique countries from patients
        countries = list(set(patient["country"] for patient in patients.values()))
        start_day_index = 0 if start_day is None else days_of_week.index(start_day)

        # Create the Gurobi model
        model = Model("patient_scheduling")

        # Binary variable indicating whether a patient is scheduled on a specific day and time slot
        scheduling_vars = {
            (p["name"], day, slot): model.addVar(name=f"scheduling_{p['name']}_{day}_{slot}", vtype=GRB.BINARY)
            for p in patients.values() for day in days_of_week for slot in time_slots
        }

        # Optimize starting from the selected day (inclusive)
        for day_index, day in enumerate(days_of_week):
            for slot in time_slots:
                for p in patients.values():
                    if day_index < start_day_index:
                        model.addConstr(scheduling_vars[(p["name"], day, slot)] == previous_schedule.get((p["name"], day, slot), 0))

        # Constraints for the specified shifts for each patient
        for p in patients.values():
            n_rows = len(p["shift_sheet"])
            n_cols = len(p["shift_sheet"][0])

            # Constraint: The total number of schedules for each patient must equal the number of required shifts
            model.addConstr(
                quicksum(scheduling_vars[(p["name"], day, slot)] for day in days_of_week for slot in time_slots) == len(p["shift_sheet"][0])
            )

            # Auxiliary binary variable for combinations of days and time slots
            z = [model.addVar(name=f"combination_{p['name']}_{i}", vtype=GRB.BINARY) for i in range(n_rows)]
            model.addConstr(quicksum(z) == 1)

            # AND constraints for each combination of days and time slots
            for i in range(n_rows):
                feasible_combination = p["shift_sheet"][i]
                for j in range(n_cols):
                    if " " in feasible_combination[j].strip():
                        day, slot = feasible_combination[j].split()
                        model.addConstr(scheduling_vars[(p["name"], day, slot)] >= z[i])
                    else:
                        day = feasible_combination[j].strip()
                        model.addConstr(
                            scheduling_vars[(p["name"], day, "morning")] + scheduling_vars[(p["name"], day, "afternoon")] >= z[i]
                        )

        # Binary variable for the presence of a country on a specific day and time slot
        country_presence_vars = {
            (day, slot, country): model.addVar(name=f"presence_{country}_{day}_{slot}", vtype=GRB.BINARY)
            for day in days_of_week for slot in time_slots for country in countries
        }

        # Constraints for the presence of patients from a country on a specific day and time slot
        for day in days_of_week:
            for slot in time_slots:
                for country in countries:
                    for p in patients.values():
                        if p["country"] == country:
                            model.addConstr(
                                country_presence_vars[(day, slot, country)] >= scheduling_vars[(p["name"], day, slot)]
                            )

        # Constraint: Maximum two countries can be present on the same day and time slot
        if constraint_vars["Maximum two countries per day and time slot"].get():
            for day in days_of_week:
                for slot in time_slots:
                    model.addConstr(
                        quicksum(country_presence_vars[(day, slot, country)] for country in countries) <= 2
                    )

        # Constraint: Maximum two countries can be present on the same day
        if constraint_vars["Maximum two countries per day"].get():
            for day in days_of_week:
                model.addConstr(
                    quicksum(country_presence_vars[(day, slot, country)] for country in countries for slot in time_slots) <= 2
                )

        # Constraint: Minimum number of patients per country in time slots with exactly two countries
        if constraint_vars["Minimum patients per country in time slots with more than two countries"].get():
            two_countries_presence = {}
            for day in days_of_week:
                for slot in time_slots:
                    two_countries_presence[(day, slot)] = model.addVar(
                        name=f"two_countries_presence_{day}_{slot}",
                        vtype=GRB.BINARY
                    )
                    total_countries_day_slot = quicksum(country_presence_vars[(day, slot, country)] for country in countries)
                    model.addConstr(two_countries_presence[(day, slot)] <= total_countries_day_slot / 2)
                    model.addConstr(two_countries_presence[(day, slot)] >= total_countries_day_slot - 1)

                    for country in countries:
                        total_patients_country = quicksum(
                            scheduling_vars[(p["name"], day, slot)] for p in patients.values() if p["country"] == country
                        )
                        model.addConstr(total_patients_country >= 3 * two_countries_presence[(day, slot)])

        # Constraint: Maximum daily available hours
        for day in days_of_week:
            for slot in time_slots:
                model.addConstr(
                    quicksum(scheduling_vars[(p["name"], day, slot)] * p["time"] for p in patients.values()) <= availability_table[(day, slot)].get("hours") * 60
                )

        # Constraint: Daily availability for the selected country
        for day in days_of_week:
            for slot in time_slots:
                if availability_table[(day, slot)].get("country") != "Any":
                    selected_country = availability_table[(day, slot)].get("country")
                    for country in countries:
                        if country != selected_country:
                            model.addConstr(country_presence_vars[(day, slot, country)] == 0)

        # Objective function
        objective = [0, 0, 0, 0, 0, 0, 0, 0]

        # Component 1: Minimize the number of days with more than two countries
        if objective_vars["Minimize days with more than one country"].get():
            days_with_multiple_countries = {
                day: model.addVar(name=f"days_with_multiple_countries_{day}", vtype=GRB.BINARY)
                for day in days_of_week
            }
            for day in days_of_week:
                total_countries_day = quicksum(country_presence_vars[(day, slot, country)] for slot in time_slots for country in countries)
                model.addConstr(days_with_multiple_countries[day] >= (total_countries_day - 1) / len(countries))
                model.addConstr(days_with_multiple_countries[day] <= total_countries_day / 2)
            objective[0] = quicksum(days_with_multiple_countries[day] for day in days_of_week)

        # Component 2: Minimize the number of time slots with more than two countries
        if objective_vars["Minimize time slots with more than one country"].get():
            time_slots_with_multiple_countries = {
                (day, slot): model.addVar(name=f"time_slots_with_multiple_countries_{day}_{slot}", vtype=GRB.BINARY)
                for day in days_of_week for slot in time_slots
            }
            for day in days_of_week:
                for slot in time_slots:
                    total_countries_slot = quicksum(country_presence_vars[(day, slot, country)] for country in countries)
                    model.addConstr(time_slots_with_multiple_countries[(day, slot)] >= (total_countries_slot - 1) / len(countries))
                    model.addConstr(time_slots_with_multiple_countries[(day, slot)] <= total_countries_slot / 2)
            objective[1] = quicksum(time_slots_with_multiple_countries[(day, slot)] for day in days_of_week for slot in time_slots)

        # Component 3: Minimize the total number of working time slots used
        if objective_vars["Minimize total working time slots"].get():
            objective[2] = quicksum(scheduling_vars[(p["name"], day, slot)] for p in patients.values() for day in days_of_week for slot in time_slots)

        # Component 4: Minimize the total number of working days used
        if objective_vars["Minimize total working days"].get():
            days_used = {
                day: model.addVar(name=f"days_used_{day}", vtype=GRB.BINARY)
                for day in days_of_week
            }
            for day in days_of_week:
                for slot in time_slots:
                    model.addConstr(days_used[day] >= scheduling_vars[(p["name"], day, slot)] for p in patients.values())
            objective[3] = quicksum(days_used[day] for day in days_of_week)

        # Component 7: Minimize differences from a previous schedule
        if objective_vars["Minimize differences from previous schedule"].get() and previous_schedule:
            schedule_differences = {
                (p["name"], day, slot): model.addVar(name=f"schedule_difference_{p['name']}_{day}_{slot}", lb=0)
                for p in patients.values() for day in days_of_week for slot in time_slots
            }
            for p in patients.values():
                for day in days_of_week:
                    for slot in time_slots:
                        model.addConstr(schedule_differences[(p["name"], day, slot)] >= scheduling_vars[(p["name"], day, slot)] - previous_schedule.get((p["name"], day, slot), 0))
                        model.addConstr(schedule_differences[(p["name"], day, slot)] >= -(scheduling_vars[(p["name"], day, slot)] + previous_schedule.get((p["name"], day, slot), 0)))
            objective[6] = quicksum(schedule_differences[(p["name"], day, slot)] for p in patients.values() for day in days_of_week for slot in time_slots)

        # Set the objective function
        model.setObjective(quicksum(objective), GRB.MINIMIZE)

        # Set a timeout (e.g., 60 seconds)
        model.setParam("TimeLimit", 60)
        # Disable console output
        model.setParam('OutputFlag', 0)

        # Solve the model
        model.optimize()

        # Extract the solution
        if model.status == GRB.OPTIMAL:
            print("im in")
            solution = {
                "patients_per_day_slot": {},
                "countries_per_day_slot": {},
                "time_per_day_slot": {},
                "shifts_per_patient": {},
            }

            for day in days_of_week:
                for slot in time_slots:
                    # Patients scheduled in this day and slot
                    scheduled_patients = [
                        patient["name"] for patient in patients.values()
                        if scheduling_vars[(patient["name"], day, slot)].X == 1
                    ]
                    solution["patients_per_day_slot"][(day, slot)] = scheduled_patients

                    # Countries represented in this day and slot
                    scheduled_countries = [
                        patient["country"] for patient in patients.values()
                        if scheduling_vars[(patient["name"], day, slot)].X == 1
                    ]
                    solution["countries_per_day_slot"][(day, slot)] = scheduled_countries

                    # times used in this day and slot
                    times = [
                        patient["time"] for patient in patients.values()
                        if scheduling_vars[(patient["name"], day, slot)].X == 1
                    ]

                    solution["time_per_day_slot"][(day, slot)] = times

            # Shifts assigned to each patient
            for patient in patients.values():
                shifts = [
                    (day, slot) for day in days_of_week for slot in time_slots
                    if scheduling_vars[(patient["name"], day, slot)].X == 1
                ]
                solution["shifts_per_patient"][patient["name"]] = shifts
            
            # Initialize variables to track changes
            patients_changed = set()
            total_changes = 0

            # If a previous schedule exists, calculate the differences
            if previous_schedule:
                # Find patients whose schedules have changed compared to the previous schedule
                patients_changed = {
                    p["name"] for day in days_of_week for slot in time_slots for p in patients.values()
                    if scheduling_vars[(p["name"], day, slot)].X != previous_schedule.get((p["name"], day, slot), 0)
                }

                # Calculate the total number of changes in the schedule
                total_changes = sum(
                    abs(scheduling_vars[(p["name"], day, slot)].X - previous_schedule.get((p["name"], day, slot), 0))
                    for day in days_of_week for slot in time_slots for p in patients.values()
                )

            # Return the solution, the set of changed patients, and the total number of changes
            return solution, patients_changed, total_changes

        # If no solution is found, return empty results
        else:
            return {}, set(), 0
            
    except Exception as e:
        raise Exception(f"Error during optimization: {str(e)}")