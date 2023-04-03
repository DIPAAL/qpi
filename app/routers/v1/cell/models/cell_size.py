from enum import Enum

class CellSize(int, Enum):
    meter_50 = 50,
    meter_200 = 200,
    meter_1000 = 1000,
    meter_5000 = 5000