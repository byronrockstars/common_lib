from hub import light_matrix, motion_sensor, port, sound
import runloop, motor, motor_pair, sys, time, color_sensor, color

class RL:
    MOTOR_MAX_VELOCITIES = {"SMALL": 660, "MEDIUM": 1110, "LARGE": 1050}
    WHEEL_MAX_VELOCITY = MOTOR_MAX_VELOCITIES["MEDIUM"]
    LIGHT_REFLECTIONS = {"BLACK": 25, "WHITE": 95}
    BLACK_LINE_RIGHT_EDGE = "Right"
    BLACK_LINE_LEFT_EDGE = "Left"

    def __init__(self, robot="Misty", leftMotorPort=port.A, rightMotorPort=port.B, leftSensorPort=port.E, rightSensorPort=port.F, acceleration=500, deceleration=1000, brakeStartPercentage=0.9, correctionMultiplier=-1.5):
        self.ROBOT_NAME = robot
        self.PORTS = {"LEFT_MOTOR": leftMotorPort, "RIGHT_MOTOR": rightMotorPort, "LEFT_SENSOR": leftSensorPort, "RIGHT_SENSOR": rightSensorPort}
        self.ACCELERATION = acceleration
        self.DECELERATION = deceleration
        self.BRAKE_START_PERCENTAGE = brakeStartPercentage
        self.CORRECTION_MULTIPLIER = correctionMultiplier
    
    def __percentageToUnits(self, percentage):
        return self.WHEEL_MAX_VELOCITY * percentage/100
    
    def __turnCompleted(self, degrees) -> bool:
        return abs(motion_sensor.tilt_angles()[0] * -0.1) >= abs(degrees)
    
    async def moveForward(self, rotations, velocity) -> None:
        print("In moveForward function, rotations to move = " + str(rotations) + ", velocityPercentage = " + str(velocity) + ", acceleration = " + str(self.ACCELERATION) + ", deceleration = " + str(self.DECELERATION) + ".")
        await motor_pair.move_for_degrees(motor_pair.PAIR_1, int(rotations*360), 0, velocity=int(self.percentageToUnits(velocity)), stop=motor.BRAKE, acceleration=self.ACCELERATION, deceleration=self.DECELERATION)
        return
    
    async def moveForwardWheelRotation(self, rotations, velocity) -> None:
        print("Move Forward Proportional. Rotations = " + str(rotations) + ", Velocity = " + str(velocity) + ", Acceleration = " + str(self.ACCELERATION) + ", Brake = " + str(self.BRAKE_START_PERCENTAGE) + ", Correction Multiplier = " + str(self.CORRECTION_MULTIPLIER))

        motion_sensor.reset_yaw(0)

        degrees = rotations * 360

        motor.reset_relative_position(self.PORTS["RIGHT_MOTOR"], 0)
        motor.reset_relative_position(self.PORTS["LEFT_MOTOR"], 0)

        velocity = self.__percentageToUnits(velocity)
        brakeStartDistance = degrees * self.BRAKE_START_PERCENTAGE
        endSpeed = self.WHEEL_MAX_VELOCITY * .1

        while ((motor.relative_position(self.PORTS["RIGHT_MOTOR"]) + motor.relative_position(self.PORTS["RIGHT_MOTOR"]))/2 < degrees):
            error = motion_sensor.tilt_angles()[0] * -0.1
            correction = int(error * self.CORRECTION_MULTIPLIER)

            deceleration = 0
            degreesTraveled = motor.relative_position(self.PORTS["LEFT_WHEEL"])

            if(degreesTraveled > brakeStartDistance):
                deceleration = min(velocity * degreesTraveled/degrees, velocity - endSpeed)

            motor_pair.move_tank(motor_pair.PAIR_1, velocity + correction - int(deceleration), velocity - correction - int(deceleration), acceleration=self.ACCELERATION)

        motor_pair.stop(motor_pair.PAIR_1)
        print("Final relative position = " + str((motor.relative_position(self.PORTS["RIGHT_MOTOR"]) + motor.relative_position(self.PORTS["RIGHT_MOTOR"]))/2))
        return
    
    async def turn(self, degrees, velocity, turnType) -> None: # Turn type takes "PIVOT" or "SPIN"
        print("In spinTurn, degreesToTurn = " + str(degrees) + ", velocity = " + str(velocity) + ".")

        motion_sensor.reset_yaw(0)
        time.sleep(0.1)
        if turnType == "SPIN":
            if(degrees > 0):
                motor_pair.move_tank(motor_pair.PAIR_1, velocity, -1 * velocity)
            else:
                motor_pair.move_tank(motor_pair.PAIR_1, -1 * velocity, velocity)
        
        if turnType == "PIVOT":
            if(degrees > 0):
                motor_pair.move_tank(motor_pair.PAIR_1, velocity, 0)
            else:
                motor_pair.move_tank(motor_pair.PAIR_1, 0, velocity)

        #lambda makes function with parameters callable since runloop.until() expects a function with no parameters
        await runloop.until(lambda: self.__turnCompleted(degrees))
        motor_pair.stop(motor_pair.PAIR_1)

        #multiplying by -0.1 makes yaw angle match values in hub
        print("Degrees turned: ", motion_sensor.tilt_angles()[0] * -0.1)

        return    

async def main():
    # write your code here
    await light_matrix.write("Hi!")

runloop.run(main())
