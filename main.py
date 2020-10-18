#!/bin/python3

### BEGIN INIT INFO
# Provides:          myservice
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Automatic Hot Beverage Machine
# Description:       Put a long description of the service here
### END INIT INFO

import RPi.GPIO as GPIO
import logging
import json
from time import sleep

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('/home/pi/AHBM/AHBM.log'),
        logging.StreamHandler()
    ]    
)

GPIO.setmode(GPIO.BOARD)

pins = {
    'LED': {
        'RED': 21,
        'GRN': 23,
    },
    'input': {
        'LFT': 19,
        'MOD': 15,
        'SEL': 13,
        'RGT': 11,
    },
    'stepper': {
        'ENA': 8,
        'DIR': 10,
        'PUL': 12,
    },
}
with open('/home/pi/AHBM/settings.json', 'r') as f:
    settings = json.load(f)
for group in pins:
    for pin in pins[group]:
        if group is 'input':
            GPIO.setup(pins[group][pin], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        else:
            GPIO.setup(pins[group][pin], GPIO.OUT)

def inputHandler(pin, string):
    def wrap(func):
        def wrappedFunc(*args):
            if GPIO.input(pin):
                GPIO.output(pins['LED']['RED'], 1)
                logging.info(string)
                func(*args)
                sleep(0.3)
        return wrappedFunc
    return wrap

@inputHandler(pins['input']['RGT'], 'Right')
def right():
    GPIO.output(pins['LED']['GRN'], 1)
    GPIO.output(pins['stepper']['DIR'], 1)

@inputHandler(pins['input']['LFT'], 'Left')
def left():
    logging.info('Actual Delay: {:f}'.format(settings['delay']))
    GPIO.output(pins['LED']['GRN'], 0)
    GPIO.output(pins['stepper']['DIR'], 0)

@inputHandler(pins['input']['SEL'], 'Select')
def select():
    for i in range(int(settings['stepsRev']/8)):
        GPIO.output(pins['stepper']['PUL'], 1)
        sleep(settings['delay'])
        GPIO.output(pins['stepper']['PUL'], 0)
        sleep(settings['delay'])

@inputHandler(pins['input']['MOD'], 'Mode')
def mode():
    global settings
    with open('/home/pi/AHBM/settings.json') as f:
        settings = json.load(f)
    logging.info('Delay: {:f}'.format(settings['delay']))

startupNo = 1
logging.info('AHBM: START UP...')
for i in range(3):
    GPIO.output(pins['LED']['GRN'], 1 if startupNo else 0)
    GPIO.output(pins['LED']['RED'], 0 if startupNo else 1)
    startupNo = 0 if startupNo else 1
    sleep(0.5)
logging.info('AHBM: READY')

GPIO.output(pins['stepper']['ENA'], 0)
while True:
    try:
        GPIO.output(pins['LED']['RED'], 0)
        left()
        right()
        select()
        mode()
    except KeyboardInterrupt:
        break

for pin in pins['LED']:
    GPIO.output(pins['LED'][pin], 0)
GPIO.cleanup()
