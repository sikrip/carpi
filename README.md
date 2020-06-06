# carpi
Python script for integrating a Raspberry Pi in a car.

## Features
 * adjust screen brightness based on input from the car lights (connect dashlights to GPIO4)
 * when the GPIO17 goes low for 5 seconds, will upload all csv files on home directory to dropbox (see https://github.com/andreafabrizi/Dropbox-Uploader)
   and then will shutdown the Rasberry Pi.
