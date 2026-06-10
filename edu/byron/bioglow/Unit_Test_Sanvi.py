12345678910111213141516
from hub import portimport Combined as RLdef main():    Pez = RL.initializeRobot(        name="Pez",        mainPortLeft=port.A,        mainPortRight=port.E,    )    ## Sanvi's code begin    Pez.changeMainMotorVelocity(50)    RL.moveForward(Pez, 1)    ## Sanvi's code end

    ## Sanvi's code begin
    Pez.changeMainMotorVelocity(50)
    RL.moveForward(Pez, 1)
    ## Sanvi's code end



# myRobot.showMyRobotConfig()


(variable) Pez: Unknown
Getting Started
API Modules
