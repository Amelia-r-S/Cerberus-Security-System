import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import PyavOutput

#Directory path - I stored everything in the parent directory for simplicity
PROJECT_DIR = Path(__file__).resolve().parent
VIDEO_DIR = PROJECT_DIR / "footage"

#Recording settings - intialized to 30 second recordings, and the microphone is on USB slot 3. 
RECORD_LEN = 30
AUDIO_DEVICE = "plughw:3,0"

#Logging configuration
logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)s %(message)s",
)

#Function to record audio and video, then combine them into one MP4 file. 
def record_vid():
        #Generate a timestamp so each recording has a unique name. 
	timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        #While recording, keep audio and video files separate.
        #FFmpeg will combine temporary files into the final MP4. 
	video_path = VIDEO_DIR / f"{timestamp}_video.mp4"
	audio_path = VIDEO_DIR / f"{timestamp}.wav"
	mp4_path = VIDEO_DIR / f"{timestamp}.mp4"

        #Initialize resource references so cleanup can determine which resources were successfully opened or started. 
	camera = None
	microphone = None
	recording_started = False

        #Create the footage directory if it does not already exist. 
	try:
		VIDEO_DIR.mkdir(parents=True, exist_ok=True)

                #Initialize the camera and configure 1080p video capture.
		#FrameDurationLimits sets a fixed frame interval of about 30 frames per second. 
		camera = Picamera2()
		config = camera.create_video_configuration(
			main={"size": (1920, 1080)},
			controls={"FrameDurationLimits": (33333, 33333)},
		)
		camera.configure(config)

                #Encode video using H.264 at a target bitrate of 10 Mbps. 
		encoder = H264Encoder(bitrate=10_000_000)

		logging.info("Security system is armed, starting recording.")

                #Start capturing video and write it to the temporary file. 
		camera.start_recording(
		encoder,
		PyavOutput(str(video_path)),
		)
		recording_started = True

                #Record mono audio at 48 kHz using ALSA's arecord utility.
                #The duration is passed to arecord so audio capture stops automatically after the configured recording interval. 
		microphone = subprocess.Popen([
            		"/usr/bin/arecord",
            		"-D", AUDIO_DEVICE,
            		"-f", "S16_LE",
            		"-r", "48000",
            		"-c", "1",
            		"-d", str(RECORD_LEN),
           		str(audio_path),
       		])

                #Keep video capture running for the same interval as audio. 
		time.sleep(RECORD_LEN)

        #Log the full exception details. 
	except Exception:
		logging.exception("Camera recording failed")
		raise

        #Stop video capture before closing the camera. Only attempt to stop recording if the camera successfully started it. 
	finally:
		if recording_started and camera is not None:
			try:
				camera.stop_recording()
				logging.info("Video capture stopped")
			except Exception:
				logging.exception("Failed to stop the camera")

                #Release camera resources even if recording failed. 
		if camera is not None: camera.close()

                #Ensure audio process has exited, if it hangs request termination so it does not record indefinitely. 
		if microphone is not None:
			try:
				return_code = microphone.wait(timeout=10)
				if return_code != 0:
					logging.error(
						"Audio recording failed exit code %s",
						return_code,
					)
			except subprocess.TimeoutExpired:
				microphone.terminate()
				microphone.wait()

        #Verify both temp recordings exist before attempting to combine them. 
	if not video_path.exists() or not audio_path.exists():
		raise RuntimeError("Video or audio file is missing.")

        #Log that files exist and combine video and audio files. 
	logging.info("Combining video and audio into MP4")

	logging.info("Video file exists: %s", video_path.exists())
	logging.info("Audio file exists: %s", audio_path.exists())

        #Log file sizes. 
	if video_path.exists():
    		logging.info("Video size: %d bytes", video_path.stat().st_size)

	if audio_path.exists():
    		logging.info("Audio size: %d bytes", audio_path.stat().st_size)

        #Copy the existing H.264 video stream without re-encoding, encode audio as AAC, and apply a small offset to compensate for capture lagging. 
	subprocess.run([
		"/usr/bin/ffmpeg",
        	"-y",
        	"-i", str(video_path),
		"-itsoffset", "-0.05",
        	"-i", str(audio_path),
		"-map", "0:v:0",
		"-map", "1:a:0",
        	"-c:v", "copy",
        	"-c:a", "aac",
        	"-b:a", "128k",
		#-t limits output to configured recording length
		"-t", str(RECORD_LEN),
		#moves metadata to beginning of the file
        	"-movflags", "+faststart",
        	str(mp4_path),
    	], check=True)

        #Removes temporary files ONLY after FFmpeg succeeds. If merging failes, og audio and video files remain available for recovery. 
	video_path.unlink()
	audio_path.unlink()

	logging.info("Finished recording: %s", mp4_path)

#Run a recording ONLY when this file is executed directly, rather than when it is imported as a module by another Python script. 
if __name__ == "__main__":
	record_vid()
