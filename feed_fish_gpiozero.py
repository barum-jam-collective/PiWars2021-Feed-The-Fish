# Feed The Fish - Manual Control for driving and firing using DIY NERF launcher motors controlled using MOSFET and GPIOZero PWMLED function
# Bill Harvey 16 Feb 2021
# Last update 14 June 2021

# Current list of in use servos - identify max an min using ultra_gui.py
# Servo 4 = fire breach mechanism PS4 Controller Crosses 'X' button
# Servo 2 = Pan PS4 Controller Right Analogue y axis
# Servo 3 = Tilt (63 Max up, 0.44 max down) PS4 Controler Right analogue x axis

# Launcher motor speed control PS4 SHARE and OPTION buttons 'select' and 'start' now working correctly

from gpiozero import PWMLED, Servo
from time import sleep
from approxeng.input.selectbinder import ControllerResource  # Import Approx Eng Controller libraries
import ThunderBorg3 as ThunderBorg
import UltraBorg3 as UltraBorg
# import os
import sys

global TB

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()
# TB.i2cAddress = 0x15                 # Uncomment and change the value if you have changed the board address
TB.Init()
if not TB.foundChip:
    boards = ThunderBorg.ScanForThunderBorg()
    if len(boards) == 0:
        print("No ThunderBorg found, check you are attached :)")
    else:
        print("No ThunderBorg at address %02X, but we did find boards:" % (TB.i2cAddress))
        for board in boards:
            print("    %02X (%d) " % (board, board))
        print("If you need to change the I2C address change the setup line so it is correct, e.g.")
        print("TB.i2cAddress = 0x%02X" % (boards[0]))
    sys.exit()

# Ensure the communications failsafe has been enabled!
failsafe = False
for i in range(5):
    TB.SetCommsFailsafe(True)
    failsafe = TB.GetCommsFailsafe()
    if failsafe:
        break
if not failsafe:
    print("Board %02X failed to report in failsafe mode!" % (TB.i2cAddress))
    sys.exit()

TB.MotorsOff()
TB.SetLedShowBattery(False)
TB.SetLeds(0, 0, 1)

# Start the UltraBorg
UB = UltraBorg.UltraBorg()  # Create a new UltraBorg object
UB.Init()  # Set the board up (checks the board is connected)

# Set servo to centre
UB.SetServoPosition4(-0.6)  # Test Servo positioning using ultra_gui.py to obtain start position and insert here

# Setup Nerf Launcher motor variable (BCM numbering system)
global launcher_on

# Setup the launcher motor settings
launcher = PWMLED(17)  # Assign GPIO pin 17 to control PWM for launcher motor
launcher.value = 0  # ensure launcher motors are off

# Setup the launcher loading mechanism setting
#breach = Servo(25)  # Assign GPIO pin 25 to control breach block servo

# Set min and max travel for breacj block servo
breach_min = -0.6
breach_max = 0.3

def set_speeds(power_left, power_right):
    TB.SetMotor1(power_left / 100)
    TB.SetMotor2(power_right / 100)


def stop_motors():
    TB.MotorsOff()


def mixer(yaw, throttle, max_power=50):
    """
    Mix a pair of joystick axes, returning a pair of wheel speeds. This is where the mapping from
    joystick positions to wheel powers is defined, so any changes to how the robot drives should
    be made here, everything else is really just plumbing.
    :param yaw:
        Yaw axis value, ranges from -1.0 to 1.0
    :param throttle:
        Throttle axis value, ranges from -1.0 to 1.0
    :param max_power:
        Maximum speed that should be returned from the mixer, defaults to 100
    :return:
        A pair of power_left, power_right integer values to send to the motor driver
    """

    left = throttle - yaw  # was +
    right = throttle + yaw  # was -
    scale = float(max_power) / max(1, abs(left), abs(right))
    return int(left * scale), int(right * scale)

#def aim(aim_x, aim_y):

#    UB.SetServoPosition3(aim_y)

def aim_left_right(aim):
    UB.SetServoPosition2(aim)

def elevation_up_down(elevation):
    UB.SetServoPosition3(elevation)

#def start_launcher_motors(launcher_speed, launcher_on):
#    print("Starting launcher Motors")
#    print("Press X to fire and Circle to stop")
#    launcher.value = 0.33
#    return launcher_on

def fire():
    global breach_min
    global breach_max
    # Activate loading servo
    UB.SetServoPosition4(breach_min)  # was Test Servo positioning using ultra_gui.py to obtain start position and insert here
    sleep(0.5)  # Insert loading time here
    UB.SetServoPosition4(breach_max)  # was -0.47 Test Servo positioning using ultra_gui.py to obtain loading position and insert here
    sleep(0.5)
    UB.SetServoPosition4(breach_min)  # Test Servo positioning using ultra_gui.py to obtain start position and insert here


#def stop_launcher_motors():
#    print("Stopping launcher Motors")
#    launcher.value = 0

def main():
    global breach_min
    global breach_max
    global launcher_on
    global aim
    global elevation
    #global launcher_speed
    global launcher
    aim = 0
    elevation = 0
    print("Drive using left hand joystick")
    print("Press square to start launcher motors")
    print("Press Circle to stop launcher motors")
    print("Press X to fire")
    while True:
        try:
            try:
                print("started try joystick")
                with ControllerResource() as joystick:
                    print("Found a joystick and connected")
                    while joystick.connected:
                        # Get joystick values from the left analogue stick
                        x_axis, y_axis = joystick['lx', 'ly']

                        # Get power from mixer function
                        power_left, power_right = mixer(yaw=x_axis, throttle=y_axis)

                        # Set motor speeds
                        set_speeds(power_left, power_right)

                        # Read the buttons to determine Nerf launcher controls
                        presses = joystick.check_presses()
                        launcher_on = ""
                        if presses.square:
                            print("Square pressed")
                            # Start launcher motors
                            print("Starting launcher Motors")
                            print("Press X to fire and Circle to stop")
                            launcher_on = "yes"
                            launcher.value = 0.33 # default start speed
                            print("launcher speed =",launcher.value)

                        if presses.select:
                            launcher.value += 0.025
                            print(launcher)
                            print("launcher speed =", launcher.value)

                        if presses.start:
                            launcher.value -= 0.025
                        # Need to add some error checking here to prevent firing if motors are nut turning?
                            print(launcher)
                            print("launcher speed =", launcher.value)
                            
                        if presses.cross:
                            print("Firing")
                            print(launcher_on)
                            fire()
                            #if launcher_on == "yes":
                            #    fire()
                            #else:
                            #    print("Motors aren't running") #, press 'Square' to start")

                        if presses.circle:
                            # Stop launcher motors
                            print("Circle pressed")
                            launcher_on = "No"
                            launcher.value = 0

                        # aiming

                        if presses.l1:
                            # Pan cannon left
                            aim +=0.1
                            aim_left_right(aim)

                        if presses.r1:
                            # Pan cannon right
                            aim -=0.1
                            aim_left_right(aim)

                        if presses.l2:
                            # Raise cannon
                            elevation +=0.05
                            elevation_up_down(elevation)

                        if presses.r2:
                            # Lower cannon
                            elevation -=0.05
                            elevation_up_down(elevation)

                # Joystick disconnected.....
                print("Connection to joystick lost")
                stop_launcher_motors()
                # Stop ThunderBorg Motors

            except IOError:
                # No joystick found, wait for a bit and try again
                print("No joysticks found")
                # Set LEDs blue
                TB.SetLeds(0, 0, 1)
                sleep(1.0)
        except KeyboardInterrupt:
            # CTRL+C exit, give up
            print("\nUser aborted")
            TB.MotorsOff()
            TB.SetCommsFailsafe(False)
            TB.SetLeds(0, 0, 0)
            motors.off()
            # motor1.stop()
            # motor2.stop()
            sys.exit()

main()
