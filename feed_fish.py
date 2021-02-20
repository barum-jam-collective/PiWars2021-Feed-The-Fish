# Feed The Fish - Manual Control - Driving and Firing
# Bill Harvey 16 Feb 2021 - Not tested yet
# Last update 20 Feb 2021

from gpiozero import Motor
from time import sleep
from approxeng.input.selectbinder import ControllerResource # Import Approx Eng Controller libraries
import ThunderBorg3 as ThunderBorg
import UltraBorg3 as UltraBorg
#import os
import sys

global launcher
global TB
launcher = False

# Setup the ThunderBorg
TB = ThunderBorg.ThunderBorg()
#TB.i2cAddress = 0x15                 # Uncomment and change the value if you have changed the board address
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
TB.SetLeds(0,0,1)

# Start the UltraBorg
UB = UltraBorg.UltraBorg()      # Create a new UltraBorg object
UB.Init()                       # Set the board up (checks the board is connected)

# Setup Nerf Launcher motor variable (BCM numbering system)

motor1 = Motor(27, 22)
motor2 = Motor(23, 24)

def start_launcher_motors():
    motor1.forward()
    motor2.forward()

def fire():
    # Activate loading servo
    UB.SetServoPosition4(0) #Test Servo positioning using ultra_gui.py to obtain start position and insert here
    sleep(0.5) # Insert loading time here
    UB.SetServoPosition4(0)  # Test Servo positioning using ultra_gui.py to obtain loading position and insert here

def stop_launcher_motors():
    motor1.stop()
    motor2.stop()

def main():
    while True:
        try:
            try:
                with ControllerResource as joystick:
                    print("Found a joystick and connected")
                    while joystick.connected:
                        left_y = joystick["ly"]
                        right_y = joystick["ry"]
                        driveLeft = left_y
                        driveRight = right_y

                        TB.SetMotor1(driveRight)
                        TB.SetMotor2(driveLeft)

                        # Read the buttons to determine Nerf launcher controls
                        presses = joystick.check_presses()
                        if presses["square"]:
                            print("Square Button")
                            # Start launcher motors

                            launcher = "yes"
                            start_launcher_motors()
                            # Fire NERF
                            # Need to add some error checking here to prevent firing if motors are nut turning?

                        if presses["Cross"]:
                            print("Cross Pressed")
                            if launcher == "yes":
                                fire()
                            else:
                                print("Motors aren't running, press 'Square' to start")

                        if presses["Triangle"]:
                            # Stop launcher motors
                            launcher = "No"
                            stop_launcher_motors()
                # Joystick disconnected.....
                print("Connection to joystick lost")
                stop_launcher_motors()
                # Stop ThunderBorg Motors

            except IOError:
                # No joystick found, wait for a bit and try again
                print("No joysticks found")
                # Set LEDs blue
                TB.SetLeds(0,0,1)
                sleep(1.0)
        except KeyboardInterrupt:
            # CTRL+C exit, give up
            print("\nUser aborted")
            TB.MotorsOff()
            TB.SetCommsFailsafe(False)
            TB.SetLeds(0,0,0)
            sys.exit()

main()

