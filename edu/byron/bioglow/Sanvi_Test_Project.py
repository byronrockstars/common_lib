from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time

LARGE_MOTOR_MAX_VELOCITY = 1050

class MyDefaults:
    def __init__(self, port1, port2):
        self.port1 = port1
        self.port2 = port2

def moveForward(degreesToMove):
    print("In moveForward function, degrees to move = " +str(degreesToMove))
    
    motor_pair.move_for_degrees(motor_pair.PAIR_1, degreesToMove, 0, velocity=263, stop=motor.BRAKE, acceleration=500, deceleration=1000)

    return

async def main():
    myDef = MyDefaults(port.A, port.E)

    motor_pair.pair(motor_pair.PAIR_1, myDef.port1, myDef.port2)

    moveForward(360)
    return

runloop.run(main())
