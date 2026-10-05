from hub import port
import runloop
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


async def runMission2() -> None:
    #Mission 2 (Exploding Seeds)
    motor.run_for_degrees(port.C, 1000, 1110) #1110 is 100% velocity on a medium motor
    return
    

async def main():

    robot = RW.initializeRobot(
        name="Misty",
        mainPortLeft=port.A,
        mainPortRight=port.B
    )

    #await runMission1()
    #await runMission3()
    await runMission2()

runloop.run(main())