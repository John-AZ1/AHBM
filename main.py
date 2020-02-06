import RPi.GPIO as GPIO
import time
import argparse

GPIO.setmode(GPIO.BOARD)

class Stepper:
    def __init__(self, pins):
        # A, A-, B, B-
        # Yellow, Orange, Blue, Green
        self.pins = pins
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)
        self.totalSteps = 400
        self.stepIndex = 0
        self.coilArr = [
            [1,0,1,0],
            [0,1,1,0],
            [0,1,0,1],
            [1,0,0,1],
        ]
    
    def calibrate(self):
        while True:
            self.step(1, 0.1)
            done = input()
            if done == 'y':
                break
        self.step(-1, 0.1)

    def setCoils(self, state):
        for i in range(len(state)):
            GPIO.output(self.pins[i], state[i])

    def step(self, delay=0.1, backwards=False):
        if backwards:
            self.stepIndex = self.stepIndex - 1 if self.stepIndex > 0 else 3
        else:
            self.stepIndex = self.stepIndex + 1 if self.stepIndex < 3 else 0
        self.setCoils(self.coilArr[self.stepIndex])
        time.sleep(delay)

class Cup:
    def __init__(self, index, totalSteps, totalCupNo):
        self.posLit = (totalSteps / totalCupNo) * index
        self.pos = index
        self.index = index
        self.full = False

    def incPos(self):
        self.pos = self.pos - 1 if self.pos > 0 else 7

class AHBM:
    def __init__(self, basePins=[16, 18, 7, 11], selectPins=[35, 37, 33, 31], cupNo=8):
        self.motors = {
            "base": Stepper(basePins),
            "select": Stepper(selectPins)
        }
        self.cupMovement = int(self.motors["base"].totalSteps / cupNo)
        self.cups = [Cup(i, self.motors["base"].totalSteps, cupNo) for i in range(cupNo)] 

    def debugCups(self):
        print([cup.pos for cup in self.cups])

    def turn(self):
        for i in range(self.cupMovement):
            self.motors["base"].step()
        for cupI in range(len(self.cups)):
            self.cups[cupI].incPos()
        self.debugCups()
        
    def activateTea(self, tea):
        print(tea, "is in Cup")

    def activateWater(self):
        print("Water is in Cup")

    def makeCup(self, tea):
        cupI = None
        for cup in self.cups:
            if not cup.full:
                cupI = cup.index
                break
        if cupI is None:
            print("All cups are full")
            return("Err CupsFull")

        print("Current Cup Index:", cupI)
        while True:
            if self.cups[cupI].pos is 0:
                break
            else:
                self.turn()
        print(self.cups[cupI].pos)
        self.activateTea(tea)
        self.turn()
        self.activateWater()
        self.cups[cupI].full = True

Abraham = AHBM()
Abraham.makeCup("Earl Gray")
Abraham.makeCup("Peppermint")

# motors = {
    # "base": Stepper([16, 18, 7, 11]),
    # "select": Stepper([35, 37, 33, 31])
# }
# 
# parser = argparse.ArgumentParser()
# parser.add_argument('motor', choices=motors.keys(), nargs='+')
# parser.add_argument('-s', '--steps', type=int, default=10)
# parser.add_argument('-d', '--delay', type=float, default=0.1)
# parser.add_argument('-c', '--calibrate', action="store_true")
# parser.add_argument('-l', '--loop', action="store_true")
# args = parser.parse_args()
# 
# try:
    # if args.calibrate:
        # for motor in args.motor:
            # print('Calibrating', motor)
            # motors[motor].calibrate()
# 
    # print(args.motor)
    # if args.loop:
        # while True:
            # motors[args.motor[0]].step(args.delay)
    # else:
        # for motor in args.motor:
            # for i in range(abs(args.steps)):
                # motors[motor].step(args.delay, False if args.steps > 0 else True)
    # GPIO.cleanup()
# 
# except KeyboardInterrupt:
    # GPIO.cleanup()
