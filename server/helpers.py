# this file has helper functions for the app
# helpers are small things we use a lot

def calculate_parcel_cost(weight_kg):
    # this gets the cost by multiplying weight by 150
    rate_per_kg = 150 # how much for one kg
    return round(weight_kg * rate_per_kg, 2) # give back the cost rounded
