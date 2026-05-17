from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time

class RobotConfig:
    LARGE_MOTOR_MAX_VELOCITY = 1050
    MEDIUM_MOTOR_MAX_VELOCITY = 1110

    DEFAULT_VELOCITY_PERCENT = 25 #percentage
    DEFAULT_TIMEOUT_SEC = 2 #seconds

    def __init__(
        self,
        name: str,
        mainPortLeft,
        mainPortRight,        
        mainMotorVelocity: int = LARGE_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT,
        attachMotorVelocity: int = MEDIUM_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT,
        timeout: int = DEFAULT_TIMEOUT_SEC,
    ):
        self.name = name
        
        changeMainPorts(portLeft, portRight)
        changeMainMotorVelocity(velocityPercent)
        changeAttachMotorVelocity(velocityPercent)
        changeTimeout(timeout)
        
        showMyRobotConfig()
        
        return
    
    def showMyRobotConfig() -> None:
        print("Motor Config for: ", self.name)
        
        print("mainPortLeft: ", self.mainPortLeft)
        print("mainPortRight: ", self.mainPortRight)
        print("mainMotorVelocity: ", self.mainMotorVelocity)
        print("attachMotorVelocity: ", self.attachMotorVelocity)
        print("timeout: ", self.timeout)
        
        return

    def changeMainPorts(self, portLeft, portRight) -> None:
        self.mainPortLeft = portLeft
        self.mainPortRight = portRight
        print("changeMainPorts: ports changed to: ", portLeft, ", ", portRight)
        return

    def changeMainMotorVelocity(self, velocityPercent: int) -> None:
        if (10 <= velocityPercent <= 90):
            self.mainMotorVelocity = LARGE_MOTOR_MAX_VELOCITY * velocityPercent
            print("changeMainMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("changeMainMotorVelocity: velocityPercent should be between 10 and 90\nLeft Unchanged")
        return

    def getMainMotorVelocity(self) -> int:
        return self.mainMotorVelocity

    def changeAttachMotorVelocity(self, velocityPercent: int) -> None:
        if (10 <= velocityPercent <= 90):
            self.attachMotorVelocity = MEDIUM_MOTOR_MAX_VELOCITY * velocityPercent
            print("setAttachMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("setAttachMotorVelocity: velocityPercent should be between 10 and 90\nLeft Unchanged")
        return        

    def getAttachMotorVelocity(self) -> int:
        return self.attachMotorVelocity

    def changeTimeout(self, timeout: int) -> None:
        self.timeout = timeout
        print("changeTimeout: timeout updated to ", timeout, " seconds")

    def getTimeout(self) -> int:
        return self.timeout