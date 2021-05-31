# Feed The Fish - Manual Control for driving and firing using DIY NERF launcher motors controlled using MOSFET and GPIOZero PWMLED function
# Bill Harvey 16 Feb 2021
# Last update 31 May 2021

from gpiozero import PWMLED
from time import sleep
from approxeng.input.selectbinder import ControllerResource # Import Approx Eng Controller libraries
import ThunderBorg3 as ThunderBorg
import UltraBorg3 as UltraBorg
#import os
import sys

global TB

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

# Set servo to centre
UB.SetServoPosition4(-0.02) #Test Servo positioning using ultra_gui.py to obtain start position and insert here

# Setup Nerf Launcher motor variable (BCM numbering system)
global launcher_motors
global launcher_on
launcher = LED(17) 
launcher.value = 0 #ensure launcher motors are off

def start_launcher_motors():
    print("Starting launcher Motors")
    print("Press X to fire and Cross to stop")
    launcher.value = 0.33

def fire():
    # Activate loading servo
    UB.SetServoPosition4(-0.02) #was Test Servo positioning using ultra_gui.py to obtain start position and insert here
    sleep(0.5) # Insert loading time here
    UB.SetServoPosition4(-0.55) #was -0.47 Test Servo positioning using ultra_gui.py to obtain loading position and insert here
    sleep(0.5)
    UB.SetServoPosition4(-0.02) #Test Servo positioning using ultra_gui.py to obtain start position and insert here

def stop_launcher_motors():
    print("Stopping launcher Motors")
    launcher.value = 0

def main():
    print("Drive using joystick")
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
                        left_y = joystick["ly"]
                        #print("Left Joy")
                        right_y = joystick["ry"]
                        #print("Right Joy")
                        driveLeft = left_y
                        driveRight = right_y

                        TB.SetMotor1(driveRight)
                        TB.SetMotor2(driveLeft)

                        # Read the buttons to determine Nerf launcher controls
                        presses = joystick.check_presses()
                        if presses.square:
                            print("Square pressed")
                            # Start launcher motors
                            launcher_on = "yes"
                            start_launcher_motors()
                            # Fire NERF
                            # Need to add some error checking here to prevent firing if motors are nut turning?

                        elif presses.cross
                            print("Circle Pressed")
                            if launcher_on == "yes":
                                fire()
                            else:
                                print("Motors aren't running, press 'Square' to start")

                        elif presses.circle:
                            # Stop launcher motors
                            print("Circle pressed")
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
            motors.off()
            #motor1.stop()
            #motor2.stop()
            sys.exit()

main()
