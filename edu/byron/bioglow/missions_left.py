from hub import port
import runloop, time
import Combined as RW
import motor


async def runMission3() -> None:
    #Mission 3 (Flip the Rock)
    # Works 100% of the time even with interesting obstacles sometimes
    await RW.moveForward(rotations=2.38, velocityPercentage=40)
    await RW.moveBackward(rotations=2.35, velocityPercentage=100, acceleration=10000, deceleration=4000) #acceleration/deceleration of 10,000 is max
    return


async def runMission1() -> None:
    #Mission 1 (Drone Survey)
    await RW.moveForward(rotations=4.726, velocityPercentage=40)
    await RW.moveForward(rotations=-4.6, velocityPercentage=100)
    return


async def runMission1and2() -> None:
    #Mission 3 (Flip the Rock)
    await RW.moveForward(rotations=2.38, velocityPercentage=40)
    motor.run_for_degrees(port.C, -1600, 1110) # New addition
    await RW.moveBackward(rotations=2.39, velocityPercentage=40, acceleration=10000, deceleration=4000) #acceleration/deceleration of 10,000 is max
    #Mission 2 (Exploding Seeds)
    #await motor.run_for_degrees(port.C, -1600, 1110) # Originally here
    await RW.pivotTurnRight(45) # Angle was too much
    await RW.moveForward(rotations=2.2, velocityPercentage=100)
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

    #await runMission1()
    #await runMission3()
    motor.run_for_degrees(port.C, 1600, 1110)
    await runMission1and2()
    await motor.run_for_degrees(port.C, -800, 1110)

runloop.run(main())