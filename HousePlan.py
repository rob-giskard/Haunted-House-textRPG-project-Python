"""Draws an ASCII floor plan of both floors of the house.

Room positions and labels come from haunted_house/data.py, so the plan always
matches the house the game actually uses. Run it with: python HousePlan.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from haunted_house import data


class House:
    def __init__(self):
        self.firstFloor = [["     " for i in range(7)] for j in range(7)]
        self.secondFloor = [["     " for i in range(7)] for j in range(7)]
        self.firstFloor[0][0] = 'Flor1'
        self.secondFloor[0][0] = 'Flor2'
        for room in data.ROOMS.values():
            floor, row, col = room['position']
            grid = self.firstFloor if floor == 1 else self.secondFloor
            grid[row][col] = room['map_code'].ljust(5)

    def drawFloor1(self):
        blueprint1 = "-----------------------------------------------------------------------\n"
        plan = list(self.firstFloor)
        for i in range(len(plan)):
            plan[i] = "|  " + "  |  ".join(str(item) for item in plan[i]) + "  |" 
        blueprint1 += "\n|---------------------------------------------------------------------|\n".join(plan)
        blueprint1 += "\n-----------------------------------------------------------------------\n"
        return blueprint1

    def drawFloor2(self):
        blueprint2 = "\n-----------------------------------------------------------------------\n"
        plan = list(self.secondFloor)
        for i in range(len(plan)):
            plan[i] = "|  " + "  |  ".join(str(item) for item in plan[i]) + "  |" 
        blueprint2 += "\n|---------------------------------------------------------------------|\n".join(plan)
        blueprint2 += "\n-----------------------------------------------------------------------"
        return blueprint2


if __name__ == '__main__':
    house = House()
    print(house.drawFloor1())
    print(house.drawFloor2())
