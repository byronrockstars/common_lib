from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time
import rockstar_lib as RL
from myClasses import RobotConfig

def moveBackward(myConfig:RobotConfig, rotations):
    if(isinstance(rotations, (int, float))):
        RL.moveForward(myConfig, -360 * rotations)
    else:
        print("moveBackward: rotations must be a number")
    return

def moveForward(myConfig:RobotConfig, rotations):
    if(isinstance(rotations, (int, float))):
        RL.moveForward(myConfig, 360 * rotations)
    else:
        print("moveForward: rotations must be a number")    
    return

async def displayMessage(myConfig:RobotConfig, messageToDisplay):
    light_matrix.write(str(messageToDisplay)) 
    return

def pivotTurnRight(myConfig:RobotConfig, degreesToTurn):
    if(isinstance(degreesToTurn, int)):
        RL.pivotTurn(myConfig, degreesToTurn)
    else:
        print("pivotTurnRight: degreesToTurn must be a number")    
    return

def pivotTurnLeft(myConfig:RobotConfig, degreesToTurn):
    if(isinstance(degreesToTurn, int)):
        RL.pivotTurn(myConfig, -1 * degreesToTurn)
    else:
        print("pivotTurnLeft: degreesToTurn must be a number")        
    return

def spinTurnRight(myConfig:RobotConfig, degreesToTurn):
    if(isinstance(degreesToTurn, int)):
        RL.spinTurn(myConfig, degreesToTurn)
    else:
        print("spinTurnRight: degreesToTurn must be a number")                
    return
    
def spinTurnLeft(myConfig:RobotConfig, degreesToTurn):
    if(isinstance(degreesToTurn, int)):    
        RL.spinTurn(myConfig, -1 * degreesToTurn)
    else:
        print("spinTurnLeft: degreesToTurn must be a number")                    
    return
    
def proportionalSpinTurnLeft(myConfig:RobotConfig, degreesToTurn):
    if(isinstance(degreesToTurn, int)):    
        RL.proportionalSpinTurn(myConfig, -1 * degreesToTurn)
    else:
        print("proportionalSpinTurnLeft: degreesToTurn must be a number")                        
    return

def proportionalSpinTurnRight(myConfig:RobotConfig, degreesToTurn):
    if(isinstance(degreesToTurn, int)):    
        RL.proportionalSpinTurn(myConfig, degreesToTurn)
    else:
        print("proportionalSpinTurnRight: degreesToTurn must be a number")                            
    return

def moveForwardGyro(myConfig:RobotConfig, stoppingRotations):    
    if(isinstance(stoppingRotations, int)):        
        RL.moveStraightWheelRotation(myConfig, stoppingRotations)
    else:
        print("moveForwardGyro: stoppingRotations must be a number")                                
    return
    
def moveBackwardGyro(myConfig:RobotConfig, stoppingRotations):    
    if(isinstance(stoppingRotations, int)):
        RL.moveStraightWheelRotation(myConfig, -1 * stoppingRotations)
    else:
        print("moveBackwardGyro: stoppingRotations must be a number")                                    
    return
    
def resetEverything(myConfig:RobotConfig):
    RL.allSensorReset()
    
    newConfig = RobotConfig(myConfig.name,  
        mainPortLeft = myConfig.mainPortLeft,
        mainPortRight = myConfig.mainPortRight,
    )
    
    myConfig.changeMainMotorVelocity(newConfig.getMainMotorVelocity())
    myConfig.changeAttachMotorVelocity(newConfig.getAttachMotorVelocity())
    myConfig.changeTimeout(newConfig.getTimeout())
    
    print("resetEverything: Complete")
        
    return
    
def initializeRobot(name: str,
        mainPortLeft,
        mainPortRight
        ) -> RobotConfig:
    
    #config   
    newConfig = RobotConfig(name = name,  
        mainPortLeft = mainPortLeft,
        mainPortRight = mainPortRight,        
    )
    
    #sensors
    RL.allSensorReset()
    
    #motors
    motor_pair.pair(motor_pair.PAIR_1, newConfig.mainPortLeft, newConfig.mainPortRight)
     
    print("initializeRobot: Complete")
        
    return newConfig
    