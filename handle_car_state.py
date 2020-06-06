# adjust screen brightness based on input from the car lights
# upload logs to dropbox
# shutdown when the GPIO17 goes low for 5 seconds
import RPi.GPIO as GPIO
import time
import subprocess

GPIO.setwarnings(False)
GPIO.cleanup()

GPIO.setmode(GPIO.BCM)

CAR_LIGHT_PIN = 4 # input from the car lights
GPIO.setup(CAR_LIGHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

SHUTDOWN_PIN = 17 # input form the key on relay
GPIO.setup(SHUTDOWN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def applyBrightness(b):
	global brightness
	brightness = b
	file = open("/sys/class/backlight/rpi_backlight/brightness","w")
	file.write(str(b))
	file.close()

def uploadLogs():
	try:
        	output = subprocess.call('ping -c 2 www.dropbox.com', shell=True)
        	if(output==0):
                	print('Uploading to dropbox...')
                	subprocess.call('/home/pi/scripts/dropbox_uploader.sh -s upload ~/*.csv /', timeout=120, shell=True)
                	subprocess.call('rm ~/*.csv', shell=True)
	except subprocess.TimeoutExpired:
        	print('\nDropbox upload timeout occurred...')


brightnessHigh = 200
brightnessLow = 50
brightness = brightnessHigh # current brightness

shutdownCounter = 0
shutdownWaitTime = 5 # seconds to wait before shutting down after key off
initialWaitTime = 10 # seconds to wait on startup in order to not interrupt PowerTune boot

time.sleep(initialWaitTime)

while(True):
	if (shutdownCounter >= shutdownWaitTime):
		uploadLogs()
		print('Shuting down...')
		subprocess.call(['shutdown', '-h','now'])
		#sys.exit("shutdown")
	shutdownState = GPIO.input(SHUTDOWN_PIN)
	lightState = GPIO.input(CAR_LIGHT_PIN)
	
	# Advance the shoutdown counter by 1 each second the
	# shoutdown pin goes low
	if (shutdownState == True):
		shutdownCounter = 0
	else:
		shutdownCounter += 1
	# Handle brightness
	if lightState == True and brightness == brightnessHigh:
		applyBrightness(brightnessLow)
	elif lightState == False and brightness == brightnessLow:
		applyBrightness(brightnessHigh)
	time.sleep(1)
