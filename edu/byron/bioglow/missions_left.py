from hub import port, motion_sensor
import runloop, time
import Combined as RW
import motor, motor_pair


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


#Returns true if the gyro yaw angle has reached the degreesToTurn value indicating that a turn has been completed.
def __turnCompleted(degreesToTurn) -> bool:
    #multiplying by -0.1 makes yaw angle match values in hub
    return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degreesToTurn)


async def runMission1() -> None:
    #Mission 1 (Drone Survey)
    await RW.moveForward(rotations=4.78, velocityPercentage=100, acceleration=10000, deceleration=4000)
    await RW.moveBackward(rotations=2, velocityPercentage=100, acceleration=10000, deceleration=4000)
    await RW.pivotTurnLeft(15)
    await RW.moveForward(rotations=2.9, velocityPercentage=100, acceleration=10000, deceleration=4000)
    await carTurn(degreesToTurn=45)
    await RW.moveForward(rotations=3, velocityPercentage=100, acceleration=10000, deceleration=4000)
    return

async def runMission2():
    #Mission 2 (Exploding Seeds)
    await RW.pivotTurnRight(35)
    await RW.moveForwardGyro(1.78, 100)
    #await RW.moveForward(rotations=2.25, velocityPercentage=100)
    await motor.run_for_degrees(port.C, 1000, 1110) #1110 is 100% velocity on a medium motor
    #time.sleep(0.5)
    await RW.moveForward(rotations=-2, velocityPercentage=100)
    motor.run_for_degrees(port.C, -1000, 1110)
    await RW.moveBackward(1, velocityPercentage=100)

    return

async def runMission3() -> None:
    #Mission 3 (Flip the Rock)
    #19.6035381584 WHEEL CIRCUMFERENCE
    motor.run_for_degrees(port.C, 2000, 1110) #was 1600 
    time.sleep(0.5)
    #don't need gyro correction because masher aligns
    await RW.moveForward(rotations=2.38, velocityPercentage=100, acceleration=5000, deceleration=1000)
    motor.run_for_degrees(port.C, -1800, 1110)
    #await RW.moveBackwardGyro(2.41, 30) #this is best if combining with another mission 
    
    #this works if running alone
    await RW.moveBackward(rotations=2.41, velocityPercentage=100, acceleration=10000, deceleration=4000) #acceleration/deceleration of 10,000 is max
    
    #await RW.moveBackwardGyro(2.41, 30)

    return

async def runMission2and3() -> None:
    #Mission 3 (Flip the Rock)
    motor.run_for_degrees(port.C, 1600, 1110)
    await RW.moveForwardGyro(2.40, velocityPercentage=80, acceleration=1000)
    motor.run_for_degrees(port.C, -1600, 1110)
    await RW.moveBackwardGyro(2.39, velocityPercentage=40, acceleration=10000)#acceleration/deceleration of 10,000 is max
    await RW.moveBackwardGyro(0.5, velocityPercentage=100) #square up against wall

    #Mission 2 (Exploding Seeds)
    await RW.pivotTurnRight(42) # Angle was too much
    await RW.moveForwardGyro(2.35, velocityPercentage=40, correctionMultiplier=-1.5)
    await motor.run_for_degrees(port.C, 850, 1110) #1110 is 100% velocity on a medium motor # maybe too high
    #time.sleep(0.5)
    await RW.moveForwardGyro(-2.35, velocityPercentage=40, correctionMultiplier=-1.5)
    await motor.run_for_degrees(port.C, -800, 1110)
    return


async def main():
    robot = RW.initializeRobot(
        name="Misty",
        mainPortLeft=port.A,
        mainPortRight=port.B
    )

    await runMission1()
    
    
    #await runMission2()
    #time.sleep(2)
    #await runMission3()
    

    #await runMission2and3()

runloop.run(main())