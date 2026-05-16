from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time
import rockstar_lib as RL

LARGE_MOTOR_MAX_VELOCITY = 1050
MEDIUM_MOTOR_MAX_VELOCITY = 1110

DEFAULT_VELOCITY = 50 #percentage
DEFAULT_TIMEOUT = 60 #seconds

# function is like a MyBlock
def moveBackward(rotations):
    RL.moveForward(-360 * rotations)
    return

def moveForward(rotations):
    RL.moveForward(360 * rotations)
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

def moveForwardGyro(stoppingRotations, velocityPercentage = DEFAULT_VELOCITY):    
    RL.moveStraightWheelRotation(stoppingRotations, velocityPercentage)
    return
    
def moveBackwardGyro(stoppingRotations, velocityPercentage = DEFAULT_VELOCITY):    
    RL.moveStraightWheelRotation(-1 * stoppingRotations, velocityPercentage)
    return
    
def resetEverything():
    RL.allSensorReset()
    return
