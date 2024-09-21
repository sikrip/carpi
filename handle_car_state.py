# adjust screen brightness based on input from the car lights
# shutdown when the GPIO17 goes low for 5 seconds
import RPi.GPIO as GPIO
import time
import subprocess
import requests
import json
from datetime import datetime
from pathlib import Path

GPIO.setwarnings(False)
GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

CAR_LIGHT_PIN = 4 # input from the car lights
GPIO.setup(CAR_LIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

SHUTDOWN_PIN = 17 # input form the key on relay
GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

logFilesPath = '/home/pi'
dropboxApiKey = ''

def dropboxUpload(file):
    time = datetime.now()
    
    dropboxUploadArg = {
    "path": "/{folder}/{fileName}".format(folder=time.strftime("%Y-%m-%d"), fileName=file.name),
    "mode": "overwrite",
    "strict_conflict": False
    }
    
    headers = {
        'Authorization': 'Bearer {apiKey}'.format(apiKey=dropboxApiKey),
        'Dropbox-API-Arg': json.dumps(dropboxUploadArg),
        'Content-Type': 'application/octet-stream'
    }

    with open(file, "rb") as f:
        data = f.read()
        response = requests.post('https://content.dropboxapi.com/2/files/upload', headers=headers, data=data)
        print(response)
        f.close()
    return response.status_code

def applyBrightness(b):
	global brightness
	brightness = b
	file = open("/sys/class/backlight/rpi_backlight/brightness","w")
	file.write(str(b))
	file.close()

def uploadLogs():
	try:
		output = subprocess.call('ping -c 2 www.dropbox.com', timeout=10, shell=True)
		if(output==0):
			print('\nUploading logs to dropbox...\n')
			logFiles = Path(logFilesPath).glob('*.csv')
			for logFile in logFiles:
				try:
					print("Uploading {logFilePath}".format(logFilePath=logFile))
					if(dropboxUpload(logFile)==200):
					    print("Removing {logFilePath}".format(logFilePath=logFile))
					    subprocess.call("rm {logFilePath}".format(logFilePath=logFile), shell=True)
				except subprocess.TimeoutExpired:
					print("\nFailed to upload {logFilePath}".format(logFilePath=logFile))
	except subprocess.TimeoutExpired:
		print('\nNo internet connection')


brightnessHigh = 200
brightnessLow = 50
brightness = brightnessHigh # current brightness

shutdownCounter = 0
shutdownWaitTime = 5 # seconds to wait before shutting down after key off
initialWaitTime = 10 # seconds to wait on startup in order to not interupt powertune boot

time.sleep(initialWaitTime);

while(True):
	if (shutdownCounter >= shutdownWaitTime):
		uploadLogs()
		print('Shuting down...')
		subprocess.call(['shutdown', '-h','now'])
	shutdownState = GPIO.input(SHUTDOWN_PIN)
	lightState = GPIO.input(CAR_LIGHT_PIN)

	# Advance the shoutdown counter by 1 each second the
	# shoutdown pin goes low
	if (shutdownState == True):
		shutdownCounter = 0
	else:
		shutdownCounter += 1

	if lightState == True and brightness == brightnessHigh:
		applyBrightness(brightnessLow)
	elif lightState == False and brightness == brightnessLow:
		applyBrightness(brightnessHigh)
	time.sleep(1)
