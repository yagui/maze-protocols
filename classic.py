# Example protocol for maze training
# Author: Ariel Burman


from mazeprotocols import MazeProtocols
import time

import logging
logger=logging.getLogger(__name__)

PROTOCOL_NAME= 'Classic'
PROTOCOL_VERSION = '1.1'

import numpy as np


class Classic (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    self.time = 0
    self.state = 'start'
    self.openGate('IUL')
    self.openGate('IUR')
    self.openGate('OUL')
    self.openGate('OUR')
    self.openGate('OBL') # maybe closed
    self.openGate('OBR') # maybe closed
    self.closeGate('IBL')
    self.closeGate('IBR')
    self.multidone = False
    self.toneDone = False
    self.setMultiDrop(5)
    self.nextTone = 0
    self.addTone(1,duration=1.0,freq=1000,volume=1.0)
    self.addTone(2,duration=1.0,freq=8000,volume=1.0)
    logger.info('set multidrop to 5')
    time.sleep(2)
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    print('bye bye')
    pass # leave this line in case 'exit' is empty

#  def buttonHandler(obj,button):
#      ''' If you dont use a handler this function should be commented'''
#      pass
#
#  def sensorHandler(obj,sensor):
#      ''' If you dont use a handler this function should be commented'''
#      pass

  # Write your own methods

  def chooseNextTone(self):
    a = np.random.random()
    if a>0.5:
        self.nextTone = 2
    else:
        self.nextTone = 1

  def myFunction(self,param):
    logger.debug(param)


  def run(self):
    ''' 
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    try:
      while True:
        self.myFunction(self.state)
        if self.state == 'start':
          #if self.lastSensorActive()=='UL':
          self.multidone = False
          if self.isSensorActive('C')==True:
            if self.toneDone == False:
              self.chooseNextTone()
              self.playSound(self.nextTone)
              logger.info('Played tone {a}'.format(a=self.nextTone))
              self.toneDone = True

          if self.isSensorActive('UL')==True:
            self.closeGate('IBL')
            self.closeGate('IBR')
            self.closeGate('IUR')
            self.openGate('OBL')
            #the rat went left
            self.state='going left'
            # check for reward
            self.drop('L')
            self.toneDone = False
            logger.info('reward on left')
          #elif self.lastSensorActive()=='UR':
          elif self.isSensorActive('UR')==True:
            #the rat went left
            self.closeGate('IBL')
            self.closeGate('IBR')
            self.closeGate('IUL')
            self.openGate('OBR')
            self.state='going right'
            self.toneDone = False
            # check for reward
            self.drop('R')
            logger.info('reward on right')

        elif self.state == 'going left':
          #if self.lastSensorActive()=='L':
          if self.isSensorActive('L')==True:
            self.closeGate('IUL')
            self.openGate('IBL')
            self.state = 'reward left'

        elif self.state == 'reward left':
          #if self.lastSensorActive()=='BL':
          if self.isSensorActive('BL')==True:
            self.closeGate('OUL')
            self.openGate('IUL')
            self.openGate('IUR')
            self.state = 'returning left'

          if self.isSensorActive('L')==True:
            if self.multidone == False:
              self.multiDrop('L')
              self.multidone = True

        elif self.state == 'returning left':
          #if self.lastSensorActive()=='C':
          if self.isSensorActive('C')==True:
            self.closeGate('OBL')
            self.openGate('OUL')
            self.openGate('OUR')
            self.state = 'start'
            self.chooseNextTone()
            self.playSound(self.nextTone)
            logger.info('Played tone {a}'.format(a=self.nextTone))
            self.toneDone = True


        elif self.state == 'going right':
          #if self.lastSensorActive()=='R':
          if self.isSensorActive('R')==True:
            self.closeGate('IUR')
            self.openGate('IBR')
            self.state = 'reward right'

        elif self.state == 'reward right':
          #if self.lastSensorActive()=='BR':
          if self.isSensorActive('BR')==True:
            self.closeGate('OUR')
            self.openGate('IUL')
            self.openGate('IUR')
            self.state = 'returning right'

          if self.isSensorActive('R')==True:
            if self.multidone == False:
              self.multiDrop('R')
              self.multidone = True
                
        elif self.state == 'returning right':
          #if self.lastSensorActive()=='C':
          if self.isSensorActive('C')==True:
            self.closeGate('OBR')
            self.openGate('OUL')
            self.openGate('OUR')
            self.state = 'start'
            self.chooseNextTone()
            self.playSound(self.nextTone)
            logger.info('Played tone {a}'.format(a=self.nextTone))
            self.toneDone = True

        time.sleep(.025)

    except Exception as e:
      logger.error(e)
      print(e)
