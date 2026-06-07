from hub import port
import Combined as RL


def main():
    myRobot = RL.initializeRobot(
        name="Pez",
        mainPortLeft=port.A,
        mainPortRight=port.E,
    )

    myRobot.showMyRobotConfig()

    RL.displayMessage(myRobot, "Pez")

    # Movement wrappers in Combined.py are synchronous for end users.
    # Uncomment one test at a time when the robot is safely positioned.
    # RL.moveForward(myRobot, 1)
    # RL.moveBackward(myRobot, 1)
    # RL.pivotTurnRight(myRobot, 90)
    # RL.pivotTurnLeft(myRobot, 90)
    # RL.spinTurnRight(myRobot, 90)
    # RL.spinTurnLeft(myRobot, 90)
    # RL.proportionalSpinTurnRight(myRobot, 90)
    # RL.proportionalSpinTurnLeft(myRobot, 90)
    # RL.moveForwardGyro(myRobot, 1)
    # RL.moveBackwardGyro(myRobot, 1)


main()