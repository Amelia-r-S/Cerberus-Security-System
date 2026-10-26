from gpiozero import Button, Device
from gpiozero.pins.lgpio import LGPIOFactory

from signal import pause
from pathlib import Path

import logging

#Logging configuration
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(message)s"
)

#Hardware configuration/initialization
Device.pin_factory = LGPIOFactory()
BUTTON_PIN = 27
button = Button(BUTTON_PIN, bounce_time=0.05)

#Store the current security system state in a shared file so other components can read the same state. 
STATE_FILE = Path("/var/lib/door-monitor/system_state")

#Helper function to read the state of the system state file.
def read_state():
	try:
                #Read the state file and remove surrounding whitespace. 
		state = STATE_FILE.read_text().strip()

                #Only accept recognized states to prevent invalid values. 
		if state in ("ARMED", "DISARMED"):
			return state

		logging.error("Invalid state file contents: %r", state)
		return None

        #Log filesystem errors. 
	except OSError:
		logging.exception("Failed to read system state")
		return None


#Helper function to write the state of the system state file.
def write_state(state):
	try:
                #Write the new state followed by a newline for readability. 
		with STATE_FILE.open("w") as file:
			file.write(state + "\n")
		logging.info("System state changed to %s", state)
		return True

        #Report write failures so state changes are not silently lost. 
	except OSError:
		logging.exception("Failed to write system state")
		return False


#Function to handle a button press event.  
def when_pressed():

        #Read the existing state before deciding which state to write. 
	current_state = read_state()

        #Do not change the state if it could not be read or validated. 
	if current_state is None:
		return;

        #Toggle the state: ARMED becomes DISARMED and vice versa. 
	new_state = "DISARMED" if current_state == "ARMED" else "ARMED"

	#Persist the updated state so other system components can read it. 
	write_state(new_state)

#Function to handle a button release event. 
def when_released():
        #Log at the DEBUG level so it is hidden, unless the logging level is changed. 
	logging.debug("Button released")

#Associate the event handlers with the corresponding button events. 
button.when_pressed = when_pressed
button.when_released = when_released

logging.info("Arm controller started.")

#Keep the script running to listen for events. 
pause()
