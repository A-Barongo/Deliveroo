def calculate_parcel_cost(weight_kg: float) -> float:
    """
    Calculate the cost of a parcel based on its weight.
    :param weight_kg: Weight of the parcel in kilograms
    :return: Cost in Ksh
    """
    rate_per_kg = 150
    return round(weight_kg * rate_per_kg, 2) 