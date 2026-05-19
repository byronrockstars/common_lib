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
        mainMotorVelocity: int = LARGE_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT/100,
        attachMotorVelocity: int = MEDIUM_MOTOR_MAX_VELOCITY * DEFAULT_VELOCITY_PERCENT/100,
        timeout: int = DEFAULT_TIMEOUT_SEC,
    ):
        self.name = name
        
        self.changeMainPorts(mainPortLeft, mainPortRight)
        
        #TODO: the default values for each motor cause this to not be set as it converts from percent to velocity above 
        self.changeMainMotorVelocity(mainMotorVelocity)
        self.changeAttachMotorVelocity(attachMotorVelocity)
        
        self.changeTimeout(timeout)
        
        self.showMyRobotConfig()
        
        return
    
    def showMyRobotConfig(self) -> None:
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
            self.mainMotorVelocity = self.LARGE_MOTOR_MAX_VELOCITY * velocityPercent/100
            print("changeMainMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("changeMainMotorVelocity: velocityPercent should be between 10 and 90\\nLeft Unchanged")
        return

    def getMainMotorVelocity(self) -> int:
        return self.mainMotorVelocity

    def changeAttachMotorVelocity(self, velocityPercent: int) -> None:
        if (10 <= velocityPercent <= 90):
            self.attachMotorVelocity = self.MEDIUM_MOTOR_MAX_VELOCITY * velocityPercent/100
            print("setAttachMotorVelocity: velocity updated to ", velocityPercent, "%")
        else:
            print("setAttachMotorVelocity: velocityPercent should be between 10 and 90\\nLeft Unchanged")
        return        

    def getAttachMotorVelocity(self) -> int:
        return self.attachMotorVelocity

    def changeTimeout(self, timeout: int) -> None:
        self.timeout = timeout
        print("changeTimeout: timeout updated to ", timeout, " seconds")

    def getTimeout(self) -> int:
        return self.timeout