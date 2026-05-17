## INITIALIZE

RW.initializeRobot(name, mainPortLeft, mainPortRight)

RW.resetEverything(myConfig)


## DISPLAY

RW.displayMessage(myConfig, messageToDisplay)


## MOVEMENT

RW.moveBackward(myConfig, rotations)

RW.moveForward(myConfig, rotations)

RW.moveForwardGyro(myConfig, stoppingRotations)

RW.moveBackwardGyro(myConfig, stoppingRotations)


## TURN

RW.pivotTurnRight(myConfig, degreesToTurn)

RW.pivotTurnLeft(myConfig, degreesToTurn)

RW.spinTurnRight(myConfig, degreesToTurn)

RW.spinTurnLeft(myConfig, degreesToTurn)

RW.proportionalSpinTurnLeft(myConfig, degreesToTurn)

RW.proportionalSpinTurnRight(myConfig, degreesToTurn)
