# imported what you imported and removed the libraries that were grayed out
from hub import port, motion_sensor
import motor, motor_pair, runloop, time, color_sensor, distance_sensor


#TODO: sdc - All methods should have robust logging added (meaningful print statements) as this will be needed for debugging during the season even if unit testing has passed 

# Enums aren't supported so I used a simple class
class TurnType:
    PIVOT = "pivot"
    SPIN = "spin"
    ARC = "arc"

# Same thing here
class SquareUp:
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"

class Drivetrain:
    SPIN_CORRECTION = [0, 0]
    PIVOT_CORRECTION = [0, 0]
    ARC_CORRECTION = [0, 0]

    def __init__(self, left_wheel_port=port.A, right_wheel_port=port.E, motor_max_velocity=1350, pair=None) -> None:
        self.LEFT_WHEEL_PORT = left_wheel_port # Left wheel port (defaults for Ash)
        self.RIGHT_WHEEL_PORT = right_wheel_port # Right wheel port (defaults for Ash)
        self.MOTOR_MAX_VELOCITY = motor_max_velocity # Motor max velocity (defaults for the large motor)
        # If pair hasn't been passed
        if pair is None:
            # Pair the pair into a variable called pair that has motor_pair.PAIR_1
            pair = motor_pair.PAIR_1
            motor_pair.pair(
                pair,
                self.LEFT_WHEEL_PORT,
                self.RIGHT_WHEEL_PORT
            )
        self.PAIR = pair

    # Helper function, improves readability
    def _getYaw(self) -> float:
        return motion_sensor.tilt_angles()[0] * -0.1 # This is what I found in the other code so I used it

    # Helper function, saves me typing
    def _clamp(self, value):
        # Checks if a speed is within the limits of the motors
        return max(
            -self.MOTOR_MAX_VELOCITY,
            min(self.MOTOR_MAX_VELOCITY, int(value))
        )

    # Move forward/Move backward function
    async def move(self, rotations, velocity=40, acceleration=750, deceleration=750) -> bool: # Rotations is distance, velocity is percentage, acceleration and deceleration are fractions of 1000
        try:
            # Reset the yaw so yaw calculations are accurate
            motion_sensor.reset_yaw(0)
            # Move for degrees with the parameters
            await motor_pair.move_for_degrees(
                self.PAIR,
                int(rotations * 360),
                0,
                velocity=int(velocity * self.MOTOR_MAX_VELOCITY / 100),
                stop=motor.SMART_BRAKE,
                acceleration=acceleration,
                deceleration=deceleration
            )
            # Return successfully
            return True
        except Exception as e:
            # Print the error so I know what it is
            print("move:", e)
            # Stop the motors midway
            motor_pair.stop(self.PAIR, stop=motor.SMART_BRAKE)
            # Return failure
            return False

    # Self-correcting move forward/move backward
    # TODO: (RG) FIX CAPABILITY FOR BACKWARD ACCEL (RIGHT NOW IT IS REVERSE), FIX 
    async def proportionalMove(self, rotations, velocity=40, correctionMultiplier=-1.5, timeout=10.0, acceleration=0.2) -> bool:
        # Reset the yaw for correct calculations
        motion_sensor.reset_yaw(0)
        # Reset the positions of each motor for correct calculations
        motor.reset_relative_position(self.RIGHT_WHEEL_PORT, 0); motor.reset_relative_position(self.LEFT_WHEEL_PORT, 0)
        # Convert velocity percentage to Spike units
        velocity = int(velocity * self.MOTOR_MAX_VELOCITY / 100)
        # Convert rotations to degrees
        degrees = abs(rotations * 360)
        print(degrees)
        # Set the multiplier
        m = 1 if rotations >= 0 else -1
        # If the movement is 0 don't waste time calculating
        if degrees == 0: return True
        # Default completed to false
        completed = False
        # Start the timeout check
        startTime = time.ticks_ms()
        # Common value in the two formulas for acceleration and deceleration (i'm a lazy typer)
        common = self.MOTOR_MAX_VELOCITY * 0.1 + (velocity - self.MOTOR_MAX_VELOCITY * 0.1) / (degrees * 0.1)
        # While the timout hasn't occured
        while time.ticks_diff(time.ticks_ms(), startTime) < timeout * 1000:
            # Calculate the number of degrees traveled
            degreesTraveled = (
                abs(motor.relative_position(self.LEFT_WHEEL_PORT)) +
                abs(motor.relative_position(self.RIGHT_WHEEL_PORT))
            ) / 2
            # If the movement has been completed break
            if (degrees-degreesTraveled)<=1: completed = True; print("break"); break
            # Calculate the correction
            correction = int(self._getYaw() * m * correctionMultiplier)
            # Checks if acceleration or decelerations is eligible and then find the new velocity
            if degreesTraveled < degrees * acceleration: newVelocity = common * (degreesTraveled+1)
            elif degreesTraveled > degrees * (1-acceleration): newVelocity = common * (degrees - degreesTraveled)
            else: newVelocity=velocity
            print(newVelocity)
            # If not eligible, the new velocity is the max velocity
            #else: newVelocity = velocity
            # Make sure the left speed and right speed are within the limits of the motors
            leftSpeed = self._clamp((newVelocity + correction) * m)
            rightSpeed = self._clamp((newVelocity - correction) * m)
            # Move the robot
            motor_pair.move_tank(self.PAIR, leftSpeed, rightSpeed)
            await runloop.sleep_ms(1)
        # Stop the motor using Smart Brake
        motor_pair.stop(self.PAIR, stop=motor.BRAKE)
        # Return the completion state
        return completed

    # Normal turn functions: supports three types of turns arc, pivot, and spin
    async def turn(self, angle, velocity=30, turn_type=TurnType.PIVOT, arc_ratio=0.5, timeout=2.0, tolerance=0.3) -> bool:
        if angle == 0: return True
        # Convert percentage to Spike units
        velocity = int(self.MOTOR_MAX_VELOCITY * velocity / 100)
        tolerance = 0.8 if turn_type == TurnType.SPIN else tolerance
        # Reset the yaw for correct calculations
        motion_sensor.reset_yaw(0)
        # Start the wait time
        startTime = time.ticks_ms()
        completed = False
        # Set the multiplier
        m = 1 if angle >= 0 else -1
        # Check what type of turn and decide left and right wheel movements based on that
        if turn_type == TurnType.SPIN: pair = [velocity * m, -velocity * m]; correction=self.SPIN_CORRECTION[0]
        elif turn_type == TurnType.PIVOT: pair = [velocity, 0] if m >= 0 else [0, velocity]; correction=self.PIVOT_CORRECTION[0]
        elif turn_type == TurnType.ARC: pair = [int(velocity * (1 if m >= 0 else arc_ratio)), int(velocity * (arc_ratio if m >= 0 else 1))]; correction=self.ARC_CORRECTION[0]
        else: raise ValueError("Unknown turn type ", turn_type)
        # Move the motor with the chosen pairs
        motor_pair.move_tank(self.PAIR, pair[0], pair[1])
        # Constantly check if the turn has been completed or the timeout has occured and assign completed a value based on that
        while True:
            if abs(angle - self._getYaw() - correction) <= tolerance: completed = True; break
            if time.ticks_diff(time.ticks_ms(), startTime) >= timeout * 1000: completed = False; break
            await runloop.sleep_ms(1)
        # Stop the motors
        motor_pair.stop(self.PAIR, stop=motor.SMART_BRAKE)
        # Return the boolean state of completion
        return completed


    # Squares up the robot
    async def squareUp(self, timer=10, velocity=25, direction=SquareUp.BACKWARD, degrees=90) -> bool:
        # Set default completion
        completion = False
        # Convert velocity percentage into Spike units
        speed = int(velocity * self.MOTOR_MAX_VELOCITY / 100) * (-1 if direction in (SquareUp.LEFT, SquareUp.BACKWARD) else 1)
        # Start the timer
        startTime = time.ticks_ms()
        # Try and except loop for best practices
        try:
            # Check if we need to take a turn, and then take a pivot turn
            if direction in (SquareUp.LEFT, SquareUp.RIGHT):
                if not await self.turn(degrees): return False
            # Move the robot with the speeds we chose for chosen time
            while time.ticks_diff(time.ticks_ms(), startTime) < timer * 1000:
                motor_pair.move_tank(self.PAIR, speed, speed)
                await runloop.sleep_ms(1)
            # Completion occured successfully
            completion=True
        except Exception as e:
            print("squareUp:", e)
            # It didn't successfully complete
            completion=False
        finally:
            # Stop the motors
            motor_pair.stop(self.PAIR, stop=motor.SMART_BRAKE)
            # Reset the yaw for correct calculations later
            motion_sensor.reset_yaw(0)
        # Return the boolean state of completion
        return completion

    # Slows down turn: three types of turns, arc, pivot, and spin
    async def proportionalTurn(self, angle, velocity=40, turn_type=TurnType.PIVOT, arc_ratio=0.5, timeout=2.0, tolerance=1.5) -> bool:
        if angle == 0: return True
        # Reset the yaw
        motion_sensor.reset_yaw(0)
        # Convert the velocity percentage into Spike units
        velocity = velocity * self.MOTOR_MAX_VELOCITY / 100
        # Start the wait time
        startTime = time.ticks_ms()
        completed = False
        while True:
            # Find the turn error
            turnError = angle - self._getYaw()
            # Set the multiplier
            m = 1 if turnError > 0 else -1
            # Check what is greater, the minimum velocity or the calculated turnPower (formula taken from the original core)
            turnPower = max(self.MOTOR_MAX_VELOCITY * 0.1, abs(turnError) * velocity / (50 if turn_type==TurnType.SPIN else 40))
            # Check what type of turn and decide left and right movements based on that
            if turn_type == TurnType.SPIN: pair = [turnPower * m, -turnPower * m]; correction=self.SPIN_CORRECTION[1]
            elif turn_type == TurnType.PIVOT: pair = [turnPower, 0] if m >= 0 else [0, turnPower]; correction=self.PIVOT_CORRECTION[1]
            elif turn_type == TurnType.ARC: pair = [turnPower * (arc_ratio if m >= 0 else 1), turnPower * (1 if m >= 0 else arc_ratio)]; correction=self.ARC_CORRECTION[1]
            else: raise ValueError("Unknown turn type ", turn_type)
            # Move the motor with the chosen pairs
            motor_pair.move_tank(
                self.PAIR,
                self._clamp(pair[0]),
                self._clamp(pair[1])
            )
            # Return the boolean state of completion
            if abs(angle - self._getYaw() - correction) <= tolerance: completed = True; break
            if time.ticks_diff(time.ticks_ms(), startTime) >= timeout * 1000: completed = False; break
            await runloop.sleep_ms(1)
        # Stop the motors
        motor_pair.stop(self.PAIR, stop=motor.SMART_COAST)
        # Return the boolean state of completion
        return completed

class Motor:
    def __init__(self, port=port.B, motor_max_velocity=1350) -> None:
        self.PORT=port # The port that the attachment is connected to (Defaulted for Ash)
        self.MOTOR_MAX_VELOCITY=motor_max_velocity # Motor max velocity (defaults for the medium motor)
    
    # Helper function improves readability
    def _getPosition(self) -> int:
        # Gets the relative position of motor, acts like that get yaw function
        return motor.relative_position(self.PORT)
    
    # Stop moving, used as a helper function but the user may have to call it
    def stopMoving(self) -> bool:
        try:
            # Stop the motors
            motor.stop(self.PORT, stop=motor.SMART_BRAKE)
            # Return successfully
            return True
        except Exception as e:
            # Print the exception so I know what it is
            print("stop:", e)
        # Return failure
        return False
    
    # StartMoving starts the motor
    async def startMoving(self, velocity=40) -> bool:
        try:
            # Start the motor indefinetly
            motor.run(self.PORT, int(velocity * self.MOTOR_MAX_VELOCITY / 100))
            # Return successfully
            return True
        except Exception as e:
            # Print the error so I know what it is
            print("start:", e)
            # Stop moving early
            self.stopMoving()
        # Return false
        return False


    # Move the motor
    async def move(self, rotations, velocity=40, acceleration=750, deceleration=750) -> bool:
        try:
            # Move for certain number of degrees (convert rotations to degrees)
            await motor.run_to_relative_position(
                self.PORT,
                int(rotations * 360),
                velocity=int(velocity * self.MOTOR_MAX_VELOCITY / 100),
                stop=motor.HOLD,
                acceleration=acceleration,
                deceleration=deceleration
            )
            # Return successfully
            return True
        except Exception as e:
            # Print the error so I know what it is
            print("move/moveTo:", e)
            # Stop the motors midway
            self.stopMoving()
        # Return failure
        return False

    # Move to a certain position (mainly used in the spinny attachments and lifting/arm attachments like the forklift we made)
    async def moveTo(self, position, velocity=40, acceleration=750, deceleration=750) -> bool:
        # Wrapper around the lift function
        return await self.move((position*360 - self._getPosition()) / 360, velocity, acceleration, deceleration)

class Sensor:
    def __init__(self, ports=[port.F, port.B]):
        self.PORTS = ports # The port(s) inside a list that the sensor(s) are connected to
    
    def isBlack(self) -> bool:
        try:
            # Return whether the color the color sensor is detecting is black
            #TODO: sdc - the color thresholds should be easily configurable or a constant as it will change as robot changes 
            return color_sensor.reflection(self.PORTS[0]) < 20 or color_sensor.reflection(self.PORTS[1]) < 20
        except Exception as e:
            # Print the error so I know what it is
            print("isBlack: ", e)
            # Return unsuccessfully
            return False
    
    def isWhite(self) -> bool:
        try:
            # Return whether the color the color sensor is detecting is black
            return color_sensor.reflection(self.PORTS[0]) > 80 or color_sensor.reflection(self.PORTS[1]) > 80
        except Exception as e:
            # Print the error so I know what it is
            print("isBlack: ", e)
            # Return unsuccessfully
            return False
    

    #TODO: sdc: sensor import wasn't recognized
"""
    def getDistance(self) -> int:
        # Return the distance
        return sensor.getDistance()
    
    def isCrashing(self, crash_threshold) -> bool:
        # Check if the distance is within the crash_threshold
        return sensor.getDistance() < crash_threshold
"""
 


async def main():
    #TODO: sdc: all optional parameters should be tested in test cases as well

    # Create an object drive from the class
    drive = Drivetrain(left_wheel_port=port.C, right_wheel_port=port.D)
    # Move forward and backward using drive by 3 rotations
    #await drive.move(3)
    #await drive.move(-1, 30, 500)
    # Do it again with corrections and custom acceleration
    
    #TODO: sdc: This was what we were in the middle of debugging at last practice. More work is needed.
    #await drive.proportionalMove(5)
    #await drive.proportionalMove(-5)
    
    # Arc turn
    #await drive.turn(90, turn_type=TurnType.ARC, arc_ratio=0.7)
    #await drive.turn(-90, turn_type=TurnType.ARC)
    
    # Pivot turn (no proportional yet)
    await drive.turn(90)
    #await drive.turn(-90)
    
    # Spin turn
    #await drive.turn(90, turn_type=TurnType.SPIN)
    #await drive.turn(-90, velocity = 10, turn_type=TurnType.SPIN)
    
    #TODO: Verify that issues with this method were corrected at last practice.
    # Proportional pivot turn
    #await drive.proportionalTurn(90)
    #await drive.proportionalTurn(-90)
    
    # Proportional arc turn
    #await drive.proportionalTurn(90, turn_type=TurnType.ARC)
    #await drive.proportionalTurn(-90, turn_type=TurnType.ARC)


    # Proportional spin turn
    #await drive.proportionalTurn(90, turn_type=TurnType.SPIN)
    #await drive.proportionalTurn(-90, turn_type=TurnType.SPIN)
    
    #TODO: sdc: square up against wall. Could be used as is if rotation is estimated. Otherwise, a distance sensor could be used. 
    # Square up
    #await drive.squareUp()
    #await drive.squareUp(2)
    return True

runloop.run(main())
