from hub import port
import runloop
import color
import Combined as RW


async def main():
    # One simple active wrapper call.
    # This is safe to run because it only writes to the light matrix.

    # ------------------------------------------------------------
    # Optional rockstar_wrapper calls
    # Uncomment the call you want to test.
    # For movement functions, also uncomment initializeRobot first.
    # ------------------------------------------------------------

    robot = RW.initializeRobot(
        name="Pez",
        mainPortLeft=port.A,
        mainPortRight=port.E,
    )
    
    print("Type '1' or '2' to select the mission.")
    mission = input("Which mission do you want to run? ")

    if mission == "1":
        await displayMessage("M1")
        await moveForwardGyro(stoppingRotations=4, velocityPercentage=50)        
        time.sleep(0.5)            
    elif mission == "2":
        await displayMessage("M2")
        await moveBackwardGyro(stoppingRotations=3, velocityPercentage=15)
        time.sleep(0.5)            
    else:
        # Error handling for typos
        await displayMessage("ERR")
        

    # RW.resetEverything()

    # velocity = RW.__velocity(25)# Private helper; usually do not call directly.
    # await RW.displayMessage("I like donuts :)")
    # await RW.moveForward(rotations=3, velocityPercentage=25, acceleration=500, deceleration=1000)
    # await RW.moveBackward(rotations=5, velocityPercentage=25, acceleration=500, deceleration=1000)

    # await RW.pivotTurnRight(degreesToTurn=90, velocityPercentage=25)
    # await RW.pivotTurnLeft(degreesToTurn=90, velocityPercentage=25)

    # await RW.spinTurnRight(degreesToTurn=90, velocityPercentage=25)
    # await RW.spinTurnLeft(degreesToTurn=90, velocityPercentage=25)

    # await RW.proportionalPivotTurnRight(degreesToTurn=90, velocityPercentage=40, timeout=2.0)
    # await RW.proportionalPivotTurnLeft(degreesToTurn=90, velocityPercentage=40, timeout=2.0)

    # await RW.proportionalSpinTurnRight(degreesToTurn=90, velocityPercentage=30, timeout=2.0)
    # await RW.proportionalSpinTurnLeft(degreesToTurn=90, velocityPercentage=30, timeout=2.0)

    # await RW.moveForwardGyro(stoppingRotations=1, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5)
    # await RW.moveBackwardGyro(stoppingRotations=1, velocityPercentage=25, acceleration=500, brakeStartValue=0.9, correctionMultiplier=-3.5)

    # await RW.moveStraightUntilLine(
    #    leftLightSensorPort=port.C,
    #    rightLightSensorPort=port.D,
    #    lineColor=color.BLACK,
    #    bothSensorsOnLine=False,
    #    velocityPercentage=25,
    #    acceleration=500,
    # )

    # await RW.getSecondLightSensorOnLine(
    #    leftLightSensorPort=port.C,
    #    rightLightSensorPort=port.D,
    #    lineColor=color.BLACK,
    #    velocityPercentage=25,
    #    acceleration=500,
    # )

    # await RW.squareUpOnBlackLine(
    #    leftLightSensorPort=port.C,
    #    rightLightSensorPort=port.D,
    #    leftMoveFirst=True,
    #    velocityPercentage=10,
    #    acceleration=500,
    # )


runloop.run(main())
