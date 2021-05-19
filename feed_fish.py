# Feed The Fish - Manual Control for driving and firing using DIY NERF launcher motors controlled using CamJam Motor Driver Board
# Bill Harvey 16 Feb 2021
# Last update 20 Feb 2021

from gpiozero import Motor # Used for the launcher motors (not the driving motors)
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

# Set servo to centre
UB.SetServoPosition4(-0.02) #Test Servo positioning using ultra_gui.py to obtain start position and insert here

# Setup Nerf Launcher motor variable (BCM numbering system)

motor1 = Motor(27, 22)
motor2 = Motor(23, 24)

def start_launcher_motors():
    print("Starting launcher Motors")
    print("Press Circle to fire and Cross to stop")
    motor1.forward()
    motor2.forward()

def fire():
    # Activate loading servo
    UB.SetServoPosition4(-0.02) #Test Servo positioning using ultra_gui.py to obtain start position and insert here
    sleep(0.5) # Insert loading time here
    UB.SetServoPosition4(-0.47)  # Test Servo positioning using ultra_gui.py to obtain loading position and insert here
    sleep(0.5)
    UB.SetServoPosition4(-0.02) #Test Servo positioning using ultra_gui.py to obtain start position and insert here

def stop_launcher_motors():
    print("Stopping launcher Motors")
    motor1.stop()
    motor2.stop()

def main():
    print("started main")
    while True:
        try:
            try:
                print("started try joystick")
                with ControllerResource() as joystick:
                    print("Found a joystick and connected")
                    while joystick.connected:
                        left_y = joystick["ly"] # Driving control
                        #print("Left Joy")
                        right_y = joystick["ry"] # Driving control
                        #print("Right Joy")
                        driveLeft = left_y # Driving control 
                        driveRight = right_y # Driving control

                        TB.SetMotor1(driveRight) # Driving control
                        TB.SetMotor2(driveLeft) # Driving control

                        # Read the buttons to determine Nerf launcher controls
                        presses = joystick.check_presses()
                        if presses.square:
                            print("Square pressed")
                            # Start launcher motors

                            launcher = "yes"
                            start_launcher_motors()
                            # Fire NERF
                            # Need to add some error checking here to prevent firing if motors are nut turning?

                        elif presses.circle:
                            print("Circle Pressed")
                            if launcher == "yes":
                                fire()
                            else:
                                print("Motors aren't running, press 'Square' to start")

                        elif presses.cross:
                            # Stop launcher motors
                            print("Cross pressed")
                            launcher = "No"
                            stop_launcher_motors()
                        
                        # Quick pause
                        sleep(0.01)
                        
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
            motor1.stop()
            motor2.stop()
            sys.exit()

main()

