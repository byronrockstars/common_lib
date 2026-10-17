from hub import port
import runloop, time
import Combined as RW
import motor


async def carTurn(degreesToTurn, velocity=554) -> None:
    '''Completes a pivot turn up to 179 degrees. \n
            Input parameters:
                degreesToTurn: positive value if turning to right and negative if turning to left
                velocity: (deg/sec) Medium motor range = -1110 to 1110
    '''

    print("In pivotTurn, degreesToTurn = " + str(degreesToTurn) + ", velocity = " + str(velocity) + ".")

    motion_sensor.reset_yaw(0)
    time.sleep(0.1) #reset yaw can take a bit of time to complete
    #await runloop.until(motion_sensor.stable) #commented out because this check was taking too long each call for little gain

    if(degreesToTurn > 0):
        motor_pair.move_tank(motor_pair.PAIR_1, int(velocity*0.75), int(velocity*0.25)) #right turn
        #motor_pair.move(motor_pair.PAIR_1, 50, velocity=velocity) #alternative way to pivot turn right
    else:
        motor_pair.move_tank(motor_pair.PAIR_1, int(velocity*0.25), int(velocity*0.75)) #left turn
        #motor_pair.move(motor_pair.PAIR_1, -50, velocity=velocity) #alternative way to pivot turn left

    #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
    await runloop.until(lambda: __turnCompleted(degreesToTurn))
    motor_pair.stop(motor_pair.PAIR_1)

    #multiplying by -0.1 makes yaw angle match values in hub
    print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

    return

async def runMission3() -> None:
    #Mission 3 (Flip the Rock)
    #19.6035381584 WHEEL CIRCUMFERENCE
    # Works 100% of the time even with interesting obstacles sometimes
    await RW.moveForward(rotations=2.38, velocityPercentage=40)
    await RW.moveBackward(rotations=2.35, velocityPercentage=100, acceleration=10000, deceleration=4000) #acceleration/deceleration of 10,000 is max
    return


async def runMission1() -> None:
    #Mission 1 (Drone Survey)
    await RW.moveForward(rotations=4.76, velocityPercentage=100)
    await RW.moveBackward(rotations=2, velocityPercentage=100)
    await RW.pivotTurnLeft(23)
    await RW.moveForward(rotations=2.9, velocityPercentage=100)
    await carTurn(degreesToTurn=45)
    await RW.moveForward(rotations=3, velocityPercentage=100, acceleration=10000, deceleration=4000)
    return


async def runMission2and3() -> None:
    #Mission 3 (Flip the Rock)
    await RW.moveForward(rotations=2.40, velocityPercentage=50, acceleration=10000, deceleration=4000)
    motor.run_for_degrees(port.C, -1600, 1110) # New addition
    await RW.moveBackward(rotations=2.39, velocityPercentage=100, acceleration=10000, deceleration=4000) #acceleration/deceleration of 10,000 is max
    #Mission 2 (Exploding Seeds)
    #await motor.run_for_degrees(port.C, -1600, 1110) # Originally here
    await RW.pivotTurnRight(46) # Angle was too much
    await RW.moveForward(rotations=2.2, velocityPercentage=60)
    await motor.run_for_degrees(port.C, 800, 1110) #1110 is 100% velocity on a medium motor # maybe too high
    #time.sleep(0.5)
    await RW.moveForward(rotations=-2.3, velocityPercentage=100)
    #1110 is 100% velocity on a medium motor
    return

async def runMission2():
    #Mission 2 (Exploding Seeds)
    await RW.pivotTurnRight(46)
    await RW.moveForward(rotations=2.25, velocityPercentage=100)
    await motor.run_for_degrees(port.C, 400, 1110) #1110 is 100% velocity on a medium motor
    #time.sleep(0.5)
    await RW.moveForward(rotations=-2, velocityPercentage=100)
    motor.run_for_degrees(port.C, -400, 1110)
    #1110 is 100% velocity on a medium motor
    return


async def main():

    robot = RW.initializeRobot(
        name="Misty",
        mainPortLeft=port.A,
        mainPortRight=port.B
    )

    await runMission1()
    #await runMission3()
    #motor.run_for_degrees(port.C, 1600, 1110)
    #await runMission2and3()
    #await motor.run_for_degrees(port.C, -800, 1110)

runloop.run(main())