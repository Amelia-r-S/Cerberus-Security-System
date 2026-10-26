import logging
import os
import random
import subprocess
import sys
import threading
import time

from pathlib import Path
from signal import pause

import requests
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory

#Logging configuration
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(message)s"
)

#Hardware configuration
Device.pin_factory = LGPIOFactory()
door_sensor = gpiozero.Button(17, bounce_time=0.05)

#Project directory
PROJECT_DIR = Path(__file__).resolve().parent

#Define the shared system state file 
STATE_FILE = Path(os.getenv("SYSTEM_STATE_FILE", "/var/lib/door-monitor/system_state"))

#Locate the camera controller script in the project directory
CAMERA_CONTROLLER = PROJECT_DIR / "camera_controller.py"

#Telegram configuration; load credentials from environmental variables
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"   

#Track the camera process so repeated door events do not start overlapping recordings. 
camera_process = None
#Protect recording state when multiple GPIO callbacks occur close together. 
recording_lock = threading.Lock()
#Track the most recent recording start time to prevent rapid retriggers after a recording process finishes. 
last_recording_start = 0.0
RECORDING_COOLDOWN = 2.0

#Function to launch camera controller when a recording can be started. 
def trigger_recording():
	global camera_process, last_recording_start
	
        #Protect against simultaneous GPIO callbacks
	with recording_lock:
                
                #Don't launch another recording while one is running.
                if camera_process is not None and camera_process.poll() is None:
                        logging.warning("Recording already in progress; ignoring trigger")
                        return

                #Suppress rapid retriggers using a monotonic clock, which is unaffected by changes to the system's wall-clock time. 
                now = time.monotonic()
                if now - last_recording_start < RECORDING_COOLDOWN:
                        logging.info("Recording cooldown active; ignoring trigger")
                        return

                #Launch the camera controller. 
                try:
                        camera_process = subprocess.Popen([
                                sys.executable,
                                str(CAMERA_CONTROLLER),
                        ])

                        #Update the cooldown timer only after launching succeeds. 
                        last_recording_start = now
                        logging.info(
                                "Camera recording launched")

                except OSError:
                        logging.exception("Failed to launch camera controller")

#Function to read and validate the current security system state. 
def is_system_armed():

        #Read the shared state file and remove surrounding whitespace. 
	try:
		state = STATE_FILE.read_text().strip()

                #Accept only the two recognized system states. 
		if state in ( "ARMED", "DISARMED"):
			return state

                #Log unrecognized states as UNKNOWN. 
		logging.error("Invalid system state: %r", state)
		return "UNKNOWN"

	except OSError:
		logging.exception("Unable to read system state file")
		return "UNKNOWN"

#Function to send a text notification to the configured Telegram chat. 
def send_telegram(message):

        #Do not attempt an API request if credentials are missing. 
        if not BOT_TOKEN or not CHAT_ID:
                logging.error(
                    "Telegram configuration missing; notification not sent"
                )
                return

        #Send notification to the configured chat and enforce a timeout to avoid network problems blocking the send. 
	try:
		response = requests.post(TELEGRAM_URL, data={"chat_id":CHAT_ID, "text":message,
			},
			timeout=10,
)
		#Raise an exception for unsuccessful HTTP responses. 
		response.raise_for_status()

	except requests.exceptions.Timeout:
		logging.error("Telegram request timed out")

        #Log the exception type. 
	except requests.exceptions.RequestException as exc:
		logging.error("Failed to send telegram message: %s", exc)

	else:
		logging.info("Telegram notification sent successfully")


#Function to return a randomly selected door-open notification. 
def door_message():
	messages = [
                "Your door is ajar",
                (
                        "Roses are red, violets are blue, your door is open, hope you're not in the loo"
                ),
                "YOU SHALL PASS",
                (
                        "I'm all for having an open mind... but do we also need an open door?"
                ),
        ]

	return random.choice(messages)

#Function to handle a door-open event and alert/begin recording if the system is armed. 
def door_opened():
	logging.info("Door opened")

        #Check the shared system state before deciding whether to alert. 
	state = is_system_armed()

        #An opening while armed triggers a Telegram alert and launches the camera recording process. 
	if state == "ARMED":
		logging.warning("Door opened while system is ARMED")
		send_telegram(door_message())
		trigger_recording()

        #Openings while disarmed are logged but do not trigger alerts. 
	elif state == "DISARMED":
		logging.info("System is DISARMED; Telegram alert not sent")

	#If the state can't be verified, do not assume the system is armed or disarmed. 
	else:
		logging.info("System STATE is UNKNOWN; unable to determine whether to alert.")

#Function to handle a door-closed event and log the current system state. 
def door_closed():
        #Read the state to provide context for the door-closed event. 
	state = is_system_armed()

	if state == "UNKNOWN":
		logging.error("Door closed; system state is UNKNOWN")
	else:
		logging.info("Door closed while system is in %s", state)


#Register the handlers for the sensor's state transitions. Released button signals an open door, and a pressed button signals a closed door. 
door_sensor.when_released = door_opened
door_sensor.when_pressed = door_closed

#Log startup and keep the service alive so GPIO events can be handled. 
logging.info("Door sensor service started")

pause()
