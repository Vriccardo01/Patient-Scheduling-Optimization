# Mapping for days
DAY_MAPPING = {
    "mon": "Monday",
    "monday": "Monday",
    "Mon": "Monday",
    "Monday": "Monday",
    "Tue": "Tuesday",
    "tue": "Tuesday",
    "tuesday": "Tuesday",
    "Tuesday": "Tuesday",
    "Wed": "Wednesday",
    "wed": "Wednesday",
    "wednesday": "Wednesday",
    "Wednesday": "Wednesday",
    "Thu": "Thursday",
    "thu": "Thursday",
    "thursday": "Thursday",
    "Thursday": "Thursday",
    "Fri": "Friday",
    "fri": "Friday",
    "friday": "Friday",
    "Friday": "Friday",
    "Sat": "Saturday",
    "sat": "Saturday",
    "saturday": "Saturday",
    "Saturday": "Saturday",
    "Sun": "Sunday",
    "sun": "Sunday",
    "sunday": "Sunday",
    "Sunday": "Sunday"
}

# Mapping for time slots
TIME_SLOT_MAPPING = {
    "Morning": "morning",
    "morning": "morning",
    "mor": "morning",
    "Afternoon": "afternoon",
    "afternoon": "afternoon",
    "aft": "afternoon"
}

def normalize_name(turno):
    """
    Normalize a shift string by correcting day names and time slots.
    Example: "lun mattina" → "Monday morning"

    :param turno: The shift string to normalize (e.g., "lun mattina").
    :return: Normalized shift string (e.g., "Monday morning").
    """

    if isinstance(turno, str):
        # Split the string into parts
        parts = turno.strip().split()
        if len(parts) == 1:
            # Only the day (e.g., "lun")
            day = parts[0].lower()
            return DAY_MAPPING.get(day, day)  # Return the corrected day or the original if not found
        elif len(parts) == 2:
            # Day and time slot (e.g., "lun mattina")
            day, time_slot = parts
            day = DAY_MAPPING.get(day.lower(), day)  # Normalize the day
            time_slot = TIME_SLOT_MAPPING.get(time_slot.lower(), time_slot)  # Normalize the time slot
            return f"{day} {time_slot}"
    return turno  # If not a string or cannot be normalized, return the original value