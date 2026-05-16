## INITIALIZE

RW.resetEverything()


## DISPLAY

RW.displayMessage(messageToDisplay)


## MOVEMENT

RW.moveBackward(degreesToMove)

RW.moveForward(degreesToMove)

RW.moveForwardProporational(rotations, velocity = DEFAULT_VELOCITY)
    
RW.moveBackwardProporational(rotations, velocity = DEFAULT_VELOCITY)

RW.moveForwardWheelRotation(stoppingRotations, velocityPercentage = DEFAULT_VELOCITY)    
    
RW.moveBackwardWheelRotation(stoppingRotations, velocityPercentage = DEFAULT_VELOCITY)    


## TURN

RW.pivotTurnRight(degreesToTurn, velocity = DEFAULT_VELOCITY)

RW.pivotTurnLeft(degreesToTurn, velocity = DEFAULT_VELOCITY)

RW.spinTurnRight(degreesToTurn, velocity = DEFAULT_VELOCITY)
    
RW.spinTurnLeft(degreesToTurn, velocity = DEFAULT_VELOCITY)
        
RW.proportionalSpinTurnLeft(degreesToTurn, velocity = DEFAULT_VELOCITY, timeout = DEFAULT_TIMEOUT)

RW.proportionalSpinTurnRight(degreesToTurn, velocity = DEFAULT_VELOCITY, timeout = DEFAULT_TIMEOUT)
    
    
