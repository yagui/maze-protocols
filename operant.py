# Example protocol for maze training
# Author: Ariel Burman


from mazeprotocols import MazeProtocols
import time

import logging
logger=logging.getLogger(__name__)


import numpy as np

PROTOCOL_NAME= 'Operant'
PROTOCOL_VERSION = '1.1'

class OperantLeft (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    # trainType should be 'L' of 'R'
    trainType = 'L'
    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    self.rewardWindow = 8.0
    logger.info('Training Type: {a}, Window size: {b}'.format(a=trainType,b=self.rewardWindow))
    self.state = 'start'
    self.closeGateFast('IUL')
    self.closeGateFast('IUR')
    self.openGateFast('OUL')
    self.openGateFast('OUR')
    self.openGateFast('OBL') # maybe closed
    self.openGateFast('OBR') # maybe closed
    self.closeGateFast('IBL')
    self.closeGateFast('IBR')
    self.multidropNum = 3
    self.setMultiDrop(self.multidropNum)
    logger.info('set multidrop to {a}'.format(a=self.multidropNum))
    self.trialNum = 0
    self.rewardDone = False
    self.timeInitTraining = 0
    self.trainingType = trainType
    self.trialInit = 0
    self.trialCorrect = 0
    self.addTone(1,duration=1.0,freq=1000,volume=0.7)
    self.addTone(2,duration=1.0,freq=8000,volume=1.0)
    logger.info('Tone 1 asociated with Left 1 kHz')
    logger.info('Tone 2 asociated with Right 8 kHz')
    time.sleep(.1)
    self.myLastSensor = None
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    self.printStats()
    print('bye bye')
    pass # leave this line in case 'exit' is empty

#  def buttonHandler(obj,button):
#      ''' If you dont use a handler this function should be commented'''
#      pass
#
#  def sensorHandler(self,sensor):
#      ''' If you dont use a handler this function should be commented'''
#      print('sensor activated {a}'.format(a=sensor))
#      print(id(self))
#      print(dir(self))
#      self.trialNum +=1
#      self.myLastSensor = sensor
#      pass

  # Write your own methods
  
  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    self.trialNum +=1
    if self.trainingType == 'L':
        nextTone = 1
    else:
        nextTone = 2
    self.playSound(nextTone)
    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialInit = time.time()
    time.sleep(1.2)
    if (self.trialNum % 2):
      self.openGate('IUL')
      self.openGate('IUR')
    else:
      self.openGate('IUR')
      self.openGate('IUL')

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    msg1 = 'Total trial: {a}/{b} = {c}% | Total time = {d} minutes {e} seconds'.format(d=int(tt/60),e=int(tt)%60,b = self.trialNum,a=self.trialCorrect,c=round(100*self.trialCorrect/self.trialNum))
    print (msg1)
    logger.info(msg1)

  def run(self):
    ''' 
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    try:
      self.trialNum = 0
      # waiting to rat to pass the sensor
      #while self.getLastSensorActive()!='C':
      while self.isSensorActive('C')==False:
          pass
      self.timeInitTraining = time.time()
      self.startTrial()
      while True:
        self.myFunction(self.state)
        if self.state == 'start':
          self.rewardDone = False

          #if self.myLastSensor=='UL':
          if self.isSensorActive('UL')==True:
            logger.info('Rat at {a}'.format(a='UL'))
            #the rat went left
            self.closeGateFast('IBL')
            self.closeGateFast('IBR')
            self.closeGateFast('IUR')
            self.openGateFast('OBL')
            self.state='going left'
            logger.info('reward on left')
          #elif self.myLastSensor=='UR':
          elif self.isSensorActive('UR')==True:
            logger.info('Rat at {a}'.format(a='UR'))
            #the rat went right
            self.closeGateFast('IBL')
            self.closeGateFast('IBR')
            self.closeGateFast('IUL')
            self.openGateFast('OBR')
            self.state='going right'
            # check for reward
            logger.info('reward on right')

        elif self.state == 'going left':
          #if self.myLastSensor=='L':
          if self.isSensorActive('L')==True:
            logger.info('Rat at {a}'.format(a='L'))
            self.closeGateFast('IUL')
            self.openGateFast('IBL')
            self.state = 'reward left'
            if self.rewardDone == False:
              self.rewardDone = True
              now = time.time()
              if now > (self.trialInit + self.rewardWindow):
                logger.info('Not Giving reward, exceeding window')
              elif self.trainingType == 'R':
                logger.info('Not Giving reward, wrong side')
              else:
                logger.info('Giving reward')
                self.multiDrop('L')
                self.trialCorrect += 1
              self.printStats()

        elif self.state == 'reward left':
          #if self.myLastSensor=='BL':
          if self.isSensorActive('BL')==True:
            logger.info('Rat at {a}'.format(a='BL'))
            self.closeGateFast('OUL')
            self.state = 'returning left'

          #if self.myLastSensor=='L':
          if self.isSensorActive('L')==True:
            logger.info('Rat at {a}'.format(a='L'))

        elif self.state == 'returning left':
          #if self.myLastSensor=='C':
          if self.isSensorActive('C')==True:
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGateFast('OBL')
            self.openGateFast('OUL')
            self.openGateFast('OUR')
            self.state = 'start'
            self.startTrial()


        elif self.state == 'going right':
          #if self.getLastSensorActive()=='R':
          if self.isSensorActive('R')==True:
            logger.info('Rat at {a}'.format(a='R'))
            self.closeGateFast('IUR')
            self.openGateFast('IBR')
            self.state = 'reward right'
            if self.rewardDone == False:
              now = time.time()
              self.rewardDone = True
              if now > (self.trialInit + self.rewardWindow):
                logger.info('NOT Giving reward, exceeding window')
              elif self.trainingType=='L':
                logger.info('Not Giving reward, wrong side')
              else:
                logger.info('Giving reward')
                self.multiDrop('R')
                self.trialCorrect += 1
              self.printStats()

        elif self.state == 'reward right':
          #if self.getLastSensorActive()=='BR':
          if self.isSensorActive('BR')==True:
            logger.info('Rat at {a}'.format(a='BR'))
            self.closeGateFast('OUR')

            self.state = 'returning right'

          #if self.getLastSensorActive()=='R':
          if self.isSensorActive('R')==True:
            logger.info('Rat at {a}'.format(a='R'))
                
        elif self.state == 'returning right':
          #if self.getLastSensorActive()=='C':
          if self.isSensorActive('C')==True:
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGateFast('OBR')
            self.openGateFast('OUL')
            self.openGateFast('OUR')
            self.state = 'start'
            self.startTrial()

        time.sleep(.01)

    except Exception as e:
      logger.error(e)
      print(e)

