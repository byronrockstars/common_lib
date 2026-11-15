from hub import port
import hub, runloop, color, motor, time
import Combined as RW


async def _runMission7() -> None:
    #Mission 7 (Humongous Fungus)

    motor.run_for_degrees(port.C, 500, 1110)
    await RW.moveForwardGyro(3.5, velocityPercentage=60)
    await motor.run_for_degrees(port.C, 1400, 1110)
    await RW.moveForwardGyro(0.2, velocityPercentage=40)
    motor.run_for_degrees(port.C, 600, 1110)
    await RW.moveBackwardGyro(stoppingRotations=0.15, velocityPercentage=50)
    return


async def _runMission6(forwardRotations=0.51) -> None:
    #Mission 6 (Leafcutter Frenzy)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=50)
    motor.run_for_degrees(port.C, 600, 1110)
    await RW.proportionalSpinTurnLeft(degreesToTurn=82, velocityPercentage=20)
    #await RW.pidBlackLineFollow(1.4, lightSensorPort=port.F, midPointReflectionPercentage=60, edgeToFollow=RW.BLACK_LINE_LEFT_EDGE, proportionalCorrectionCoef=0.1, velocityPercentage=8) #before derivative correction
    #await RW.pidBlackLineFollow(1.4, lightSensorPort=port.F, midPointReflectionPercentage=60, edgeToFollow=RW.BLACK_LINE_LEFT_EDGE, proportionalCorrectionCoef=0.1, derivativeCorrectionCoef=3.0, velocityPercentage=8)
    await RW.moveForwardGyro(1.7, velocityPercentage=50, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5)
    await RW.proportionalSpinTurnRight(degreesToTurn=110)
    await RW.squareUpOnBlackLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, velocityPercentage=15, acceleration=500)
    await RW.moveForward(0.5, velocityPercentage=10)
    await RW.squareUpOnBlackLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, velocityPercentage=-15, acceleration=500)

    return


async def _runMission11() -> None:
    #Mission 11 (Window to the Past)
    await RW.proportionalSpinTurnRight(degreesToTurn=83, velocityPercentage=25)
    await RW.moveForwardGyro(2, velocityPercentage=75, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5)
    await RW.arcTurnRight(42, 40,velocityPercentage=50)
    return


async def runMission7_6_11() -> None:
    await _runMission7()
    await _runMission6()
    await _runMission11()
    return


async def runMission7Only() -> None:
    await _runMission7()
    await RW.moveBackward(rotations=3.5, velocityPercentage=100, acceleration=10000, deceleration=4000)
    return


async def runMission6_11() -> None:
    #use if Mission 7 (Humongous Fungus) is not to be run
    await RW.moveForwardGyro(stoppingRotations=3.3, velocityPercentage=65)
    await RW.moveStraightUntilLine(leftLightSensorPort=port.E, rightLightSensorPort=port.F, lineColor=color.BLACK, velocityPercentage=30)
    await _runMission6(0.64)
    await _runMission11()
    return


async def runMission11Only() -> None:
    #Mission 11 (Window to the Past) -> No attachments needed for this rerun
    motor.run_for_degrees(port.C, 2500, 1110)  # lifts motorized attachment out of the way as it is not needed for this
    await RW.moveForwardGyro(3.4, velocityPercentage=75, acceleration=400, brakeStartValue=0.8, correctionMultiplier=-3.5) 
    await RW.arcTurnLeft(8, 175, velocityPercentage=50)
    await RW.moveForwardGyro(0.2, velocityPercentage=25) 
    await RW.arcTurnLeft(2, 25, velocityPercentage=25) 
    await RW.moveForward(2.8, velocityPercentage=75)
    return


async def _runMission13() -> None:
    #Mission 13 (Keystone Species)
    await RW.moveForwardGyro(3.7, velocityPercentage=40)
    await RW.proportionalPivotTurnRight(45)
    await RW.moveForwardGyro(0.25, velocityPercentage=30)
    return


async def _runMission12() -> None:
    #Mission 12 (Forest Elder)
    await motor.run_for_degrees(port.D, -120, 400)
    await RW.moveBackwardGyro(0.37, velocityPercentage=30)
    await RW.proportionalPivotTurnLeft(30)
    await RW.arcTurnRight(42, 85, velocityPercentage=-50)
    return


async def runMission13_12() -> None:
    await _runMission13()
    await _runMission12()


async def runMission15() -> None:
    # Biocentric Architecture
    await RW.moveForwardGyro(1.25, velocityPercentage=25)  
    time.sleep(0.25)
    await RW.moveBackwardGyro(stoppingRotations=1.75, velocityPercentage=60, acceleration=8000)
    return


async def main():
    RW.initializeRobot(name="Misty", mainPortLeft=port.A, mainPortRight=port.B)
    
    #mission selector
    waitingForSelection = True
    missionSelected = 0

    colors = [color.PURPLE, color.AZURE, color.ORANGE, color.MAGENTA, color.YELLOW, color.GREEN]
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    hub.light.color(0, colors[missionSelected]) #set center button start color
    hub.light.color(1, colors[missionSelected]) #set bluetooth button start color
    hub.light_matrix.write(str(alphabet[missionSelected]))

    while(waitingForSelection):
        if(hub.button.pressed(hub.button.RIGHT)): #right arrow (2) increases the mission number
            time.sleep(0.25) #prevent accidental doubleclicks
            missionSelected = missionSelected + 1
            hub.light_matrix.write(str(alphabet[missionSelected % 14])) #show letters for each mission so it is different than program number
            hub.light.color(0, colors[missionSelected % 6]) #set center button color from color array
            hub.light.color(1, colors[missionSelected % 6]) #set bluetooth button color from color array
            hub.sound.beep(freq=85, volume=100, duration=250)
        elif(hub.button.pressed(hub.button.LEFT)): #left arrow (0) decreases the mission number
            time.sleep(0.25) #prevent accidental doubleclicks
            missionSelected = missionSelected - 1
            hub.light_matrix.write(str(alphabet[missionSelected % 14])) #show letters for each mission so it is different than program number
            hub.light.color(0, colors[missionSelected % 6]) #set center button color from color array
            hub.light.color(1, colors[missionSelected % 6]) #set bluetooth button color from color array
            hub.sound.beep(freq=300, volume=100, duration=250)
        elif(hub.button.pressed(3)): #bluetooth button is used to run each mission
            if missionSelected == 0:
                print("Running mission 0.")
                await runMission7_6_11()
            elif missionSelected == 1:
                print("Running mission 1.")
                await runMission13_12()
            elif missionSelected == 2:
                print("Running mission 2.")
                await runMission15()
            elif missionSelected == 3:
                print("Running mission 3.")
                await runMission7Only()
            elif missionSelected == 4:
                print("Running mission 4.")
                await runMission6_11()
            elif missionSelected == 5:
                print("Running mission 5.")
                await runMission11Only()
            elif missionSelected == 6:
                print("Running mission 6.")
                #run mission 6

    #right home base to left home base
    #await RW.arcTurnLeft(32, 90, velocityPercentage=20)
    #await RW.moveForwardGyro(4, velocityPercentage=40)
    #await RW.proportionalSpinTurnLeft(45)
    #await RW.moveForward(1.4, velocityPercentage=40)

runloop.run(main())