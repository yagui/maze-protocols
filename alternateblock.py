# Example protocol for maze training
# Author: Ariel Burman


from mazeprotocols import MazeProtocols
import time

import logging
logger=logging.getLogger(__name__)

PROTOCOL_NAME= 'AlternateBlock'
PROTOCOL_VERSION = '1.3'

import numpy as np

class AlternateBlock (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    """ options needed 
        blockSize:    integer  
        multidropNum: integer
       
        # Stimulus
        toneLeft             integer
        toneLeftFrecuency    integer
        toneLeftVolume       float 0.0 to 1.0
        toneLeftDuration     float
        toneRight            integer
        toneRightFrecuency   integer
        toneRightVolume      float 0.0 to 1.0
        toneRightDuration    float
    """
    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    self.blockSize = options['blockSize']
    logger.info('Block Size: {a}'.format(a=self.blockSize))
    self.multidropNum = options['multidropNum']
    logger.info('set multidrop to {a}'.format(a=self.multidropNum))
    self.setMultiDrop(self.multidropNum)
    self.state = 'start'
    self.openGate('IUL')
    self.openGate('IUR')
    self.openGate('OUL')
    self.openGate('OUR')
    self.openGate('OBL') # maybe closed
    self.openGate('OBR') # maybe closed
    self.closeGate('IBL')
    self.closeGate('IBR')
    self.toneDone = False
    self.trialNum = 0
    self.rewardDone = False
    self.addTone(options['toneLeft'],duration=options['toneLeftDuration'],freq=options['toneLeftFrecuency'],volume=options['toneLeftVolume'])
    self.addTone(options['toneRight'],duration=options['toneRightDuration'],freq=options['toneRightFrecuency'],volume=options['toneRightVolume'])
    logger.info('Tone {a} asociated with Left at {b} Hz, Volume {c}'.format(a=options['toneLeft'],b=options['toneLeftFrecuency'],c=options['toneLeftVolume']))
    logger.info('Tone {a} asociated with Right at {b} Hz, Volume {c}'.format(a=options['toneRight'],b=options['toneRightFrecuency'],c=options['toneRightVolume']))
    time.sleep(1)
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    print('bye bye')
    pass # leave this line in case 'exit' is empty

#  def buttonHandler(obj,button):
#      ''' If you dont use a handler this function should be commented'''
#      pass
#

  def sensorHandler(self,sensor):
      ''' If you dont use a handler this function should be commented'''
      logger.info('sensor activated {a}'.format(a=sensor))
      self.myLastSensor = sensor
      pass

  # Write your own methods

  
  def chooseNextTone(self,count):
    return int((count-1)/self.blockSize) % 2 + 1

  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    self.trialNum +=1
    nextTone=self.chooseNextTone(self.trialNum)
    self.playSound(nextTone)
    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialInit = time.time()
    self.printStats()

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    print ('Trial Num: {c} | Total time = {a} minutes {b} seconds'.format(a=int(tt/60),b=int(tt)%60),c = self.trialNum)

  def run(self):
    ''' 
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    try:
      self.trialNum = 0
      self.closeGate('IUR')
      # waiting to rat to pass the sensor
      while self.myLastSensor is not 'C':
          time.sleep(.1)
          pass
      self.startTrial()
      self.timeInitTraining = time.time()
      while True:
        self.myFunction(self.state)
        if self.state == 'start':
          #if self.lastSensorActive()=='UL':
          self.rewardDone = False

          if self.myLastSensor=='UL':
            logger.info('Rat at {a}'.format(a='UL'))
            #the rat went left
            self.closeGate('IBL')
            self.closeGate('IBR')
            self.openGate('OBL')
            self.state='going left'
            logger.info('reward on left')
          elif self.myLastSensor=='UR':
            logger.info('Rat at {a}'.format(a='UR'))
            #the rat went right
            self.closeGate('IBL')
            self.closeGate('IBR')
            self.openGate('OBR')
            self.state='going right'
            # check for reward
            logger.info('reward on right')

        elif self.state == 'going left':
          if self.myLastSensor=='L':
            logger.info('Rat at {a}'.format(a='L'))
            self.closeGate('IUL')
            self.openGate('IBL')
            self.state = 'reward left'
            if self.rewardDone == False:
              logger.info('Giving reward')
              self.multiDrop('L')
              self.rewardDone = True

        elif self.state == 'reward left':
          if self.myLastSensor=='BL':
            logger.info('Rat at {a}'.format(a='BL'))
            self.closeGate('OUL')

            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('IUL')
            else:
                self.openGate('IUR')
            self.state = 'returning left'

          if self.isSensorActive('L')==True:
            logger.info('Rat at {a}'.format(a='L'))

        elif self.state == 'returning left':
          if self.myLastSensor=='C':
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGate('OBL')
            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('OUL')
            else:
                self.openGate('OUR')
            self.state = 'start'
            self.startTrial()


        elif self.state == 'going right':
          if self.myLastSensor=='R':
            logger.info('Rat at {a}'.format(a='R'))
            self.closeGate('IUR')
            self.openGate('IBR')
            self.state = 'reward right'
            if self.rewardDone == False:
              logger.info('Giving reward')
              self.multiDrop('R')
              self.rewardDone = True

        elif self.state == 'reward right':
          if self.myLastSensor=='BR':
            logger.info('Rat at {a}'.format(a='BR'))
            self.closeGate('OUR')

            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('IUL')
            else:
                self.openGate('IUR')

            self.state = 'returning right'

          if self.isSensorActive('R')==True:
            logger.info('Rat at {a}'.format(a='R'))
                
        elif self.state == 'returning right':
          if self.myLastSensor=='C':
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGate('OBR')
            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('OUL')
            else:
                self.openGate('OUR')
            self.state = 'start'
            self.startTrial()

        time.sleep(.01)

    except Exception as e:
      logger.error(e)
      print(e)






class AlternateBlockWindow (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    """ options needed 
        blockSize     integer  
        multidropNum  integer
        rewardWindow  float
       
        # Stimulus
        toneLeft             integer
        toneLeftFrecuency    integer
        toneLeftVolume       float 0.0 to 1.0
        toneLeftDuration     float
        toneRight            integer
        toneRightFrecuency   integer
        toneRightVolume      float 0.0 to 1.0
        toneRightDuration    float
    """
    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    self.blockSize = options['blockSize']
    self.rewardWindow = options['rewardWindow']
    logger.info('Block Size: {a}'.format(a=self.blockSize))
    logger.info('Reward Window: {a}'.format(a=self.rewardWindow))
    self.multidropNum = options['multidropNum']
    logger.info('set multidrop to {a}'.format(a=self.multidropNum))
    self.setMultiDrop(self.multidropNum)
    self.state = 'start'
    self.openGate('IUL')
    self.openGate('IUR')
    self.openGate('OUL')
    self.openGate('OUR')
    self.openGate('OBL') # maybe closed
    self.openGate('OBR') # maybe closed
    self.closeGate('IBL')
    self.closeGate('IBR')
    self.toneDone = False
    self.trialNum = 0
    self.rewardDone = False
    self.timeInitTraining = 0
    self.trialInit = 0
    self.addTone(options['toneLeft'],duration=options['toneLeftDuration'],freq=options['toneLeftFrecuency'],volume=options['toneLeftVolume'])
    self.addTone(options['toneRight'],duration=options['toneRightDuration'],freq=options['toneRightFrecuency'],volume=options['toneRightVolume'])
    logger.info('Tone {a} asociated with Left at {b} Hz, Volume {c}'.format(a=options['toneLeft'],b=options['toneLeftFrecuency'],c=options['toneLeftVolume']))
    logger.info('Tone {a} asociated with Right at {b} Hz, Volume {c}'.format(a=options['toneRight'],b=options['toneRightFrecuency'],c=options['toneRightVolume']))
    time.sleep(1)
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    print('bye bye')
    pass # leave this line in case 'exit' is empty

#  def buttonHandler(obj,button):
#      ''' If you dont use a handler this function should be commented'''
#      pass
#

  def sensorHandler(self,sensor):
      ''' If you dont use a handler this function should be commented'''
      logger.info('sensor activated {a}'.format(a=sensor))
      self.myLastSensor = sensor
      pass

  # Write your own methods

  
  def chooseNextTone(self,count):
    return int((count-1)/self.blockSize) % 2 + 1

  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    self.trialNum +=1
    nextTone=self.chooseNextTone(self.trialNum)
    self.playSound(nextTone)
    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialInit = time.time()
    self.printStats()

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    print ('Trial Num: {c} | Total time = {a} minutes {b} seconds'.format(a=int(tt/60),b=int(tt)%60,c = self.trialNum))

  def run(self):
    ''' 
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    try:
      self.trialNum = 0
      self.closeGate('IUR')
      # waiting to rat to pass the sensor
      while self.myLastSensor is not 'C':
          time.sleep(.1)
          pass
      self.timeInitTraining = time.time()
      self.startTrial()
      while True:
        self.myFunction(self.state)
        if self.state == 'start':
          self.rewardDone = False

          if self.myLastSensor=='UL':
            logger.info('Rat at {a}'.format(a='UL'))
            #the rat went left
            self.closeGate('IBL')
            self.closeGate('IBR')
            self.openGate('OBL')
            self.state='going left'
            logger.info('reward on left')
          elif self.myLastSensor=='UR':
            logger.info('Rat at {a}'.format(a='UR'))
            #the rat went right
            self.closeGate('IBL')
            self.closeGate('IBR')
            self.openGate('OBR')
            self.state='going right'
            # check for reward
            logger.info('reward on right')

        elif self.state == 'going left':
          if self.myLastSensor=='L':
            logger.info('Rat at {a}'.format(a='L'))
            self.closeGate('IUL')
            self.openGate('IBL')
            self.state = 'reward left'
            if self.rewardDone == False:
              now = time.time()
              if now > (self.trialInit + self.window):
                logger.info('Not Giving reward, exceeding window')
              else:
                  logger.info('Giving reward')
                  self.multiDrop('L')
                  self.rewardDone = True

        elif self.state == 'reward left':
          if self.myLastSensor=='BL':
            logger.info('Rat at {a}'.format(a='BL'))
            self.closeGate('OUL')

            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('IUL')
            else:
                self.openGate('IUR')
            self.state = 'returning left'

          if self.isSensorActive('L')==True:
            logger.info('Rat at {a}'.format(a='L'))

        elif self.state == 'returning left':
          if self.myLastSensor=='C':
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGate('OBL')
            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('OUL')
            else:
                self.openGate('OUR')
            self.state = 'start'
            self.startTrial()


        elif self.state == 'going right':
          if self.myLastSensor=='R':
            logger.info('Rat at {a}'.format(a='R'))
            self.closeGate('IUR')
            self.openGate('IBR')
            self.state = 'reward right'
            if self.rewardDone == False:
              now = time.time()
              if now > (self.trialInit + self.window):
                logger.info('NOT Giving reward, exceeding window')
              else:
                  logger.info('Giving reward')
                  self.multiDrop('R')
                  self.rewardDone = True

        elif self.state == 'reward right':
          if self.myLastSensor=='BR':
            logger.info('Rat at {a}'.format(a='BR'))
            self.closeGate('OUR')

            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('IUL')
            else:
                self.openGate('IUR')

            self.state = 'returning right'

          if self.isSensorActive('R')==True:
            logger.info('Rat at {a}'.format(a='R'))
                
        elif self.state == 'returning right':
          if self.myLastSensor=='C':
            logger.info('Rat at {a}'.format(a='C'))
            self.closeGate('OBR')
            nextTone = self.chooseNextTone(self.trialNum+1)
            if nextTone == 1:
                self.openGate('OUL')
            else:
                self.openGate('OUR')
            self.state = 'start'
            self.startTrial()

        time.sleep(.01)

    except Exception as e:
      logger.error(e)
      print(e)

