from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time
import rockstar_lib as RL

LARGE_MOTOR_MAX_VELOCITY = 1050
MEDIUM_MOTOR_MAX_VELOCITY = 1110

DEFAULT_VELOCITY = 50 #percentage
DEFAULT_TIMEOUT = 60 #seconds

# function is like a MyBlock
def moveBackward(degreesToMove):
    print("In moveBackward function, degrees to move = " +  str(degreesToMove))
    
    RL.moveForward(-1 * degreesToMove)
    return

def moveForward(degreesToMove):
    RL.moveForward(degreesToMove)
    return

async def displayMessage(messageToDisplay):
    light_matrix.write(str(messageToDisplay))  #await keyword waits for message to complete before continuing on    
    return

def pivotTurnRight(degreesToTurn, velocity = DEFAULT_VELOCITY):
    RL.pivotTurn(degreesToTurn, (LARGE_MOTOR_MAX_VELOCITY * velocity)//100)
    return

def pivotTurnLeft(degreesToTurn, velocity = DEFAULT_VELOCITY):
    RL.pivotTurn(-1 * degreesToTurn, (LARGE_MOTOR_MAX_VELOCITY * velocity)//100)
    return

def spinTurnRight(degreesToTurn, velocity = DEFAULT_VELOCITY):
    RL.spinTurn(degreesToTurn, (LARGE_MOTOR_MAX_VELOCITY * velocity)//100)
    return
    
def spinTurnLeft(degreesToTurn, velocity = DEFAULT_VELOCITY):
    RL.spinTurn(-1 * degreesToTurn, (LARGE_MOTOR_MAX_VELOCITY * velocity)//100)
    return
    
def proportionalSpinTurnLeft(degreesToTurn, velocity = DEFAULT_VELOCITY, timeout = DEFAULT_TIMEOUT):
    RL.proportionalSpinTurn(-1 * degreesToTurn, velocity, timeout * 1000)
    return

def proportionalSpinTurnRight(degreesToTurn, velocity = DEFAULT_VELOCITY, timeout = DEFAULT_TIMEOUT):
    RL.proportionalSpinTurn(degreesToTurn, velocity, timeout * 1000)
    return
    
def moveForwardProporational(rotations, velocity = DEFAULT_VELOCITY):
    RL.__moveForwardProporational(rotations, velocity)
    return
    
def moveBackwardProporational(rotations, velocity = DEFAULT_VELOCITY):
    RL.__moveForwardProporational(-1 * rotations, velocity)
    return

def moveForwardWheelRotation(stoppingRotations, velocityPercentage = DEFAULT_VELOCITY):    
    RL.moveStraightWheelRotation(stoppingRotations, velocityPercentage)
    return
    
def moveBackwardWheelRotation(stoppingRotations, velocityPercentage = DEFAULT_VELOCITY):    
    RL.moveStraightWheelRotation(-1 * stoppingRotations, velocityPercentage)
    return
    
def resetEverything():
    RL.allSensorReset()
    return

