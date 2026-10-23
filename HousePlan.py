class House:
    def __init__(self):
        self.firstFloor = [["     " for i in range(7)] for j in range(7)]
        self.secondFloor = [["     " for i in range(7)] for j in range(7)]
        self.firstFloor[0][0] = 'Flor1'
        self.firstFloor[6][3] = 'Foyer'
        self.firstFloor[5][3] = 'GrHal'
        self.firstFloor[5][2] = 'DrawR'
        self.firstFloor[5][1] = 'BallR'
        self.firstFloor[4][3] = 'ShHal'
        self.firstFloor[4][4] = 'Lab  '
        self.firstFloor[4][5] = 'SecSt'
        self.firstFloor[3][3] = 'Kitch'
        self.firstFloor[2][3] = 'LoHal'
        self.firstFloor[2][2] = 'Storg'
        self.firstFloor[2][4] = 'Stair'
                
        self.secondFloor[0][0] = 'Flor2'
        self.secondFloor[3][4] = 'MoHal'
        self.secondFloor[4][4] = 'GalNE'
        self.secondFloor[5][4] = 'GalE '
        self.secondFloor[6][4] = 'GalSE'
        self.secondFloor[6][3] = 'GalS '
        self.secondFloor[6][2] = 'GalSW'
        self.secondFloor[5][1] = 'MstrB'
        self.secondFloor[5][2] = 'GalW '
        self.secondFloor[4][2] = 'GalNW'
        self.secondFloor[4][3] = 'GalN '
        self.secondFloor[3][2] = 'ChldB'
        self.secondFloor[5][5] = 'Study'
        self.secondFloor[5][6] = 'Vault'
        self.secondFloor[4][6] = 'Safe '

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


house = House()
print(house.drawFloor1())
print(house.drawFloor2())

