from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time
import Combined as RL

LARGE_MOTOR_MAX_VELOCITY = 1050

async def main():
    myRobot = RL.initializeRobot(name = "Pez",  
        mainPortLeft = port.A,
        mainPortRight = port.E,        
    )

    motor_pair.pair(motor_pair.PAIR_1, myConfig.mainPortLeft, myConfig.mainPortRight)

    RL.moveForward(myRobot, 360)
    return

runloop.run(main())
