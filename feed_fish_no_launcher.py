# Feed The Fish - Manual control for driving without a launcher
# Bill Harvey 16 Feb 2021
# Last update 18 May 2021

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

def main():
    print("started main")
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
