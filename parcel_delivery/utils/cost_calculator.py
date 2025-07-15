class CostCalculator:
    def calculate(self, weight, distance):
        base = 5.0
        weight_cost = weight * 2.5
        distance_cost = (distance / 1000) * 0.15
        return round(base + weight_cost + distance_cost, 2)