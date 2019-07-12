# Example protocol for maze training
# Author: Ariel Burman

from mazeprotocols import MazeProtocols
import logging

# Name your protocol FileName and version (One file can have multiple protocol variants, 
PROTOCOL_FILE_NAME = __name__.split('.')[1] # This will return the filename, can be changed to any string
PROTOCOL_FILE_VERSION = '1.3'               # Could be used as an all-protocol file versioning

logger=logging.getLogger(PROTOCOL_FILE_NAME)
logger.info('Protocol File: {a}, Version: {b}'.format(a=PROTOCOL_FILE_NAME,b=PROTOCOL_FILE_VERSION))

# import any module you want to use
import time
import numpy as np

# Global variable and functions

def randomDelay(minor=5,mayor=8):
   time.sleep( minor + (mayor-minor) * np.random.random() )

# 1st stage  Operant   (one day each tone)
# 2nd stage  OperantChoice  (one day each tone)
# 3rd stage  RandomChoice   (until reach 80% )


class RandomChoice (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    """ # Options needed
        multidropNum  integer
        rewardWindow  float
       
        # Stimulus
        toneLeftFrecuency    integer
        toneLeftVolume       float 0.0 to 1.0
        toneLeftDuration     float
        toneRightFrecuency   integer
        toneRightVolume      float 0.0 to 1.0
        toneRightDuration    float
    """
    PROTOCOL_NAME=self.__class__.__name__   # Individual protocol name
    PROTOCOL_VERSION = '1.3'                # Individual protocol version

    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    logger.info('Options readed from configuration file')
    for key in options:
        logger.info('Option {a} = {b}'.format(a=key,b=options[key]))

    self.rewardWindow = options['rewardWindow']
    self.multidropNum = options['multidropNum']
    self.setMultiDrop(self.multidropNum)
    self.state = 'start'
    self.closeGateFast('IUL')
    self.closeGateFast('IUR')
    self.openGateFast('OUL')
    self.openGateFast('OUR')
    self.openGateFast('OBL')
    self.closeGateFast('OBR')
    self.closeGateFast('IBL')
    self.openGateFast('IBR')
    self.trialNum = 0
    self.rewardDone = False
    self.timeInitTraining = 0
    self.trialInit = 0
    self.currentTrial = ''
    self.trialsCount = {'L':0,'R':0}
    self.trialsCorrect = {'L':0,'R':0}
    self.trials = []
    self.addTone(key=1,duration=options['toneLeftDuration'],freq=options['toneLeftFrecuency'],volume=options['toneLeftVolume'])
    self.addTone(key=2,duration=options['toneRightDuration'],freq=options['toneRightFrecuency'],volume=options['toneRightVolume'])
    logger.info('Tone 1 asociated with Left at {a} Hz, Volume {b}'.format(a=options['toneLeftFrecuency'],b=options['toneLeftVolume']))
    logger.info('Tone 2 asociated with Right at {a} Hz, Volume {b}'.format(a=options['toneRightFrecuency'],b=options['toneRightVolume']))
    self.addWhiteNoise(key=3,duration=20.0,volume=1.0)
    logger.info('White Noise, Volume 1.0')
    time.sleep(.1)
    self.myLastSensor = None
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    self.printStats()
    logger.info(self.trials)
    self.endTraining()
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

  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    randomDelay(2,4)

    self.trialNum +=1
    nextTone=round(np.random.random()+1)
    if nextTone == 1:
        self.currentTrial = 'L'
    else:
        self.currentTrial = 'R'

    self.trials.append([self.trialNum, self.currentTrial,0])
    self.setSyncTrial(self.currentTrial)
    self.playSound(nextTone)
    self.trialInit = time.time()
    if self.currentTrial == 'L':
      self.setSyncH([2,7])
    else:
      self.setSyncH([3,8])

    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialsCount[self.currentTrial] +=1

    while self.isSoundPlaying():
      time.sleep(.1)

    if self.currentTrial == 'L':
      self.setSyncL([2,7])
    else:
      self.setSyncL([3,8])

    time.sleep(.2)

    if (self.trialNum % 2):
      self.openGate('IUL')
      self.openGate('IUR')
    else:
      self.openGate('IUR')
      self.openGate('IUL')

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    msg1 = 'Trial Num: {c} | Total time = {a} minutes {b} seconds'.format(a=int(tt/60),b=int(tt)%60,c = self.trialNum)
    msg2 = 'Total trial: {a}/{b} = {c}% | Left: {d}/{e} = {f}% | Right: {g}/{h} = {i}%'.format(
        a = (self.trialsCorrect['L']+self.trialsCorrect['R']),
        b = (self.trialsCount['L']+self.trialsCount['R']),
        c = round(100*(self.trialsCorrect['L']+self.trialsCorrect['R'])/(self.trialsCount['L']+self.trialsCount['R']+0.0001)),
        d = self.trialsCorrect['L'] ,
        e = self.trialsCount['L'] ,
        f = round(100*self.trialsCorrect['L']/(self.trialsCount['L']+0.0001)),
        g = self.trialsCorrect['R'] ,
        h = self.trialsCount['R'] ,
        i = round(100*self.trialsCorrect['R']/(self.trialsCount['R']+0.0001)))
    print (msg1)
    print (msg2)
    logger.info(msg1)
    logger.info(msg2)

  def randomDelay(self,minor=5,mayor=8):

     time.sleep( minor + (mayor-minor) * np.random.random())

  def run(self):
    ''' 
        This is the main loop. It should have a 'while True:' statement
        also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    self.trialNum = 0
    self.timeInitTraining = time.time()
    # waiting to rat to pass the sensor
    while self.myLastSensor is not 'C':
      time.sleep(.1)
      pass

    self.closeGateFast('IBR')
    self.openGateFast('OBR')
    self.startTraining()
    self.timeInitTraining = time.time()
    time.sleep(10)

    self.startTrial()
    while True:
      #self.myFunction(self.state)
      if self.state == 'start':
        self.rewardDone = False

        if self.myLastSensor=='UL':
          logger.info('Rat at {a}'.format(a='UL'))
          #the rat went left
          self.closeGateFast('IUR')
          self.state='going left'
          if self.currentTrial=='R':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='UR':
          logger.info('Rat at {a}'.format(a='UR'))
          #the rat went right
          self.closeGateFast('IUL')
          self.state='going right'
          if self.currentTrial=='L':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='L':
          logger.warning('Reached left without passing through UL')
          self.state='going left'
          self.closeGateFast('IUR')
          if self.currentTrial=='R':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='R':
          logger.warning('Reached right without passing through UR')
          self.state='going right'
          self.closeGateFast('IUL')
          if self.currentTrial=='L':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='C':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'going left':
        if self.myLastSensor=='L':
          logger.info('Rat at {a}'.format(a='L'))
          self.closeGateFast('IUL')
          self.openGateFast('IBL')
          self.state = 'reward left'
          if self.rewardDone == False:
            self.rewardDone = True
            now = time.time()
            if now > (self.trialInit + self.rewardWindow):
              logger.info('Not Giving reward, exceeding window')
            elif self.currentTrial=='R':
              logger.info('Not Giving reward, wrong side')
            else:
              logger.info('Giving reward')
              self.multiDrop('L')
              self.trialsCorrect['L'] += 1
              self.trials[-1][2] = 1
            self.printStats()
        elif self.myLastSensor=='BL':
          logger.warning('Reached Bottom Left without passing through L')
        elif self.myLastSensor=='UL':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'reward left':
        if self.myLastSensor=='BL':
          logger.info('Rat at {a}'.format(a='BL'))
          self.state = 'returning left'
        elif self.myLastSensor=='C':
          logger.warning('Reached Center without passing through BL')
          ## should do the same as returning left
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBL')
          self.stopSound()
          self.state = 'start'
          self.startTrial()
        elif self.myLastSensor=='L' or self.myLastSensor=='UL':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'returning left':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBL')
          self.stopSound()
          self.state = 'start'
          self.startTrial()


      elif self.state == 'going right':
        if self.myLastSensor=='R':
          logger.info('Rat at {a}'.format(a='R'))
          self.closeGateFast('IUR')
          self.openGateFast('IBR')
          self.state = 'reward right'
          if self.rewardDone == False:
            now = time.time()
            self.rewardDone = True
            if now > (self.trialInit + self.rewardWindow):
              logger.info('NOT Giving reward, exceeding window')
            elif self.currentTrial=='L':
              logger.info('Not Giving reward, wrong side')
            else:
              logger.info('Giving reward')
              self.multiDrop('R')
              self.trialsCorrect['R'] += 1
              self.trials[-1][2] = 1
            self.printStats()
        elif self.myLastSensor=='BR':
          logger.warning('Reached Bottom right without passing through R')
        elif self.myLastSensor=='UR':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'reward right':
        if self.myLastSensor=='BR':
          logger.info('Rat at {a}'.format(a='BR'))
          self.state = 'returning right'
        elif self.myLastSensor=='C':
          logger.warning('Reached Center without passing through BR')
          ## should do the same as returning right
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.stopSound()
          self.state = 'start'
          self.startTrial()
        elif self.myLastSensor=='R' or self.myLastSensor=='UR':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'returning right':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.stopSound()
          self.state = 'start'
          self.startTrial()

      time.sleep(.05)



class OperantChoice (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    """ # Options needed
        multidropNum  integer
        rewardWindow  float
        side          Left/Right

        # Stimulus
        toneLeftFrecuency    integer
        toneLeftVolume       float 0.0 to 1.0
        toneLeftDuration     float
        toneRightFrecuency   integer
        toneRightVolume      float 0.0 to 1.0
        toneRightDuration    float
    """
    PROTOCOL_NAME=self.__class__.__name__   # Individual protocol name
    PROTOCOL_VERSION = '1.0'                # Individual protocol version

    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    logger.info('Options readed from configuration file')
    for key in options:
        logger.info('Option {a} = {b}'.format(a=key,b=options[key]))

    self.rewardWindow = options['rewardWindow']
    self.multidropNum = options['multidropNum']
    if options['side']=='Left':
      self.currentTrial = 'L'
    elif options['side']=='Right':
      self.currentTrial = 'R'
    else:
      raise ValueError("Option 'side' should be either 'Left' or 'Right'. side={a}".format(a=options['side']))

    self.setMultiDrop(self.multidropNum)
    self.state = 'start'
    self.closeGateFast('IUL')
    self.closeGateFast('IUR')
    self.openGateFast('OUL')
    self.openGateFast('OUR')
    self.openGateFast('OBL')
    self.closeGateFast('OBR')
    self.closeGateFast('IBL')
    self.openGateFast('IBR')
    self.trialNum = 0
    self.rewardDone = False
    self.timeInitTraining = 0
    self.trialInit = 0
    self.trialsCount = {'L':0,'R':0}
    self.trialsCorrect = {'L':0,'R':0}
    self.trials = []
    self.addTone(key=1,duration=options['toneLeftDuration'],freq=options['toneLeftFrecuency'],volume=options['toneLeftVolume'])
    self.addTone(key=2,duration=options['toneRightDuration'],freq=options['toneRightFrecuency'],volume=options['toneRightVolume'])
    logger.info('Tone 1 asociated with Left at {a} Hz, Volume {b}'.format(a=options['toneLeftFrecuency'],b=options['toneLeftVolume']))
    logger.info('Tone 2 asociated with Right at {a} Hz, Volume {b}'.format(a=options['toneRightFrecuency'],b=options['toneRightVolume']))
    self.addWhiteNoise(key=3,duration=20.0,volume=1.0)
    logger.info('White Noise, Volume 1.0')
    time.sleep(.1)
    self.myLastSensor = None
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    self.printStats()
    logger.info(self.trials)
    self.endTraining()
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

  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    randomDelay(2,4)

    self.trialNum +=1
    if self.currentTrial=='L':
      nextTone = 1
    else:
      nextTone = 2

    self.trials.append([self.trialNum, self.currentTrial,0])
    self.setSyncTrial(self.currentTrial)
    self.playSound(nextTone)
    self.trialInit = time.time()
    if self.currentTrial=='L':
      self.setSyncH([2,7])
    else:
      self.setSyncH([3,8])

    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialsCount[self.currentTrial] +=1

    while self.isSoundPlaying():
      time.sleep(.1)

    if self.currentTrial=='L':
      self.setSyncL([2,7])
    else:
      self.setSyncL([3,8])

    time.sleep(.2)

    if (self.trialNum % 2):
      self.openGate('IUL')
      self.openGate('IUR')
    else:
      self.openGate('IUR')
      self.openGate('IUL')

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    msg1 = 'Trial Num: {c} | Total time = {a} minutes {b} seconds'.format(a=int(tt/60),b=int(tt)%60,c = self.trialNum)
    msg2 = 'Total trial: {a}/{b} = {c}% | Left: {d}/{e} = {f}% | Right: {g}/{h} = {i}%'.format(
        a = (self.trialsCorrect['L']+self.trialsCorrect['R']),
        b = (self.trialsCount['L']+self.trialsCount['R']),
        c = round(100*(self.trialsCorrect['L']+self.trialsCorrect['R'])/(self.trialsCount['L']+self.trialsCount['R']+0.0001)),
        d = self.trialsCorrect['L'] ,
        e = self.trialsCount['L'] ,
        f = round(100*self.trialsCorrect['L']/(self.trialsCount['L']+0.0001)),
        g = self.trialsCorrect['R'] ,
        h = self.trialsCount['R'] ,
        i = round(100*self.trialsCorrect['R']/(self.trialsCount['R']+0.0001)))
    print (msg1)
    print (msg2)
    logger.info(msg1)
    logger.info(msg2)

  def run(self):
    '''
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    '''
    self.trialNum = 0
    self.timeInitTraining = time.time()
    # waiting to rat to pass the sensor
    while self.myLastSensor is not 'C':
      time.sleep(.1)
      pass

    self.closeGateFast('IBR')
    self.openGateFast('OBR')
    self.startTraining()
    self.timeInitTraining = time.time()
    time.sleep(10)

    self.startTrial()
    while True:
      #self.myFunction(self.state)
      if self.state == 'start':
        self.rewardDone = False

        if self.myLastSensor=='UL':
          logger.info('Rat at {a}'.format(a='UL'))
          #the rat went left
          self.closeGateFast('IUR')
          self.state='going left'
          if self.currentTrial=='R':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='UR':
          logger.info('Rat at {a}'.format(a='UR'))
          #the rat went right
          self.closeGateFast('IUL')
          self.state='going right'
          if self.currentTrial=='L':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='L':
          logger.warning('Reached left without passing through UL')
          self.closeGateFast('IUR')
          self.state='going left'
          if self.currentTrial=='R':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='R':
          logger.warning('Reached right without passing through UR')
          self.closeGateFast('IUL')
          self.state='going right'
          if self.currentTrial=='L':
            self.playSound(3)
            logger.info('playing white noise')
        elif self.myLastSensor=='C':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'going left':
        if self.myLastSensor=='L':
          logger.info('Rat at {a}'.format(a='L'))
          self.closeGateFast('IUL')
          self.openGateFast('IBL')
          self.state = 'reward left'
          if self.rewardDone == False:
            self.rewardDone = True
            now = time.time()
            if now > (self.trialInit + self.rewardWindow):
              logger.info('Not Giving reward, exceeding window')
            elif self.currentTrial=='R':
              logger.info('Not Giving reward, wrong side')
            else:
              logger.info('Giving reward')
              self.multiDrop('L')
              self.trialsCorrect['L'] += 1
              self.trials[-1][2] = 1
            self.printStats()
        elif self.myLastSensor=='BL':
          logger.warning('Reached Bottom Left without passing through L')
        elif self.myLastSensor=='UL':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'reward left':
        if self.myLastSensor=='BL':
          logger.info('Rat at {a}'.format(a='BL'))
          self.state = 'returning left'
        elif self.myLastSensor=='C':
          logger.warning('Reached Center without passing through BL')
          ## should do the same as returning left
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBL')
          self.stopSound()
          self.state = 'start'
          self.startTrial()
        elif self.myLastSensor=='L' or self.myLastSensor=='UL':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'returning left':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBL')
          self.stopSound()
          self.state = 'start'
          self.startTrial()


      elif self.state == 'going right':
        if self.myLastSensor=='R':
          logger.info('Rat at {a}'.format(a='R'))
          self.closeGateFast('IUR')
          self.openGateFast('IBR')
          self.state = 'reward right'
          if self.rewardDone == False:
            now = time.time()
            self.rewardDone = True
            if now > (self.trialInit + self.rewardWindow):
              logger.info('NOT Giving reward, exceeding window')
            elif self.currentTrial=='L':
              logger.info('Not Giving reward, wrong side')
            else:
              logger.info('Giving reward')
              self.multiDrop('R')
              self.trialsCorrect['R'] += 1
              self.trials[-1][2] = 1
            self.printStats()
        elif self.myLastSensor=='BR':
          logger.warning('Reached Bottom right without passing through R')
        elif self.myLastSensor=='UR':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'reward right':
        if self.myLastSensor=='BR':
          logger.info('Rat at {a}'.format(a='BR'))
          self.state = 'returning right'
        elif self.myLastSensor=='C':
          logger.warning('Reached Center without passing through BR')
          ## should do the same as returning right
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.stopSound()
          self.startTrial()
          self.state = 'start'
        elif self.myLastSensor=='R' or self.myLastSensor=='UR':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'returning right':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.stopSound()
          self.startTrial()
          self.state = 'start'

      time.sleep(.05)


class Operant (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    """ # Options needed
        multidropNum  integer
        rewardWindow  float
        side          Left/Right

        # Stimulus
        toneLeftFrecuency    integer
        toneLeftVolume       float 0.0 to 1.0
        toneLeftDuration     float
        toneRightFrecuency   integer
        toneRightVolume      float 0.0 to 1.0
        toneRightDuration    float
    """
    PROTOCOL_NAME=self.__class__.__name__   # Individual protocol name
    PROTOCOL_VERSION = '1.0'                # Individual protocol version

    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    logger.info('Options readed from configuration file')
    for key in options:
        logger.info('Option {a} = {b}'.format(a=key,b=options[key]))

    self.rewardWindow = options['rewardWindow']
    self.multidropNum = options['multidropNum']
    if options['side']=='Left':
      self.currentTrial = 'L'
    elif options['side']=='Right':
      self.currentTrial = 'R'
    else:
      raise ValueError("Option 'side' should be either 'Left' or 'Right'. side={a}".format(a=options['side']))

    self.setMultiDrop(self.multidropNum)
    self.state = 'start'
    self.closeGateFast('IUL')
    self.closeGateFast('IUR')
    self.openGateFast('OUL')
    self.openGateFast('OUR')
    self.openGateFast('OBL')
    self.closeGateFast('OBR')
    self.closeGateFast('IBL')
    self.openGateFast('IBR')
    self.trialNum = 0
    self.rewardDone = False
    self.timeInitTraining = 0
    self.trialInit = 0
    self.trialsCount = {'L':0,'R':0}
    self.trialsCorrect = {'L':0,'R':0}
    self.trials = []
    self.addTone(key=1,duration=options['toneLeftDuration'],freq=options['toneLeftFrecuency'],volume=options['toneLeftVolume'])
    self.addTone(key=2,duration=options['toneRightDuration'],freq=options['toneRightFrecuency'],volume=options['toneRightVolume'])
    logger.info('Tone 1 asociated with Left at {a} Hz, Volume {b}'.format(a=options['toneLeftFrecuency'],b=options['toneLeftVolume']))
    logger.info('Tone 2 asociated with Right at {a} Hz, Volume {b}'.format(a=options['toneRightFrecuency'],b=options['toneRightVolume']))
    time.sleep(.1)
    self.myLastSensor = None
    pass # leave this line in case 'init' is empty

  def exit(self):
    # ending protocol. cleanup code. probably loggin stats.
    self.endTraining()
    self.printStats()
    logger.info(self.trials)
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

  def myFunction(self,param):
    logger.debug(param)

  def startTrial(self):
    randomDelay(2,4)

    self.trialNum +=1
    if self.currentTrial=='L':
      nextTone = 1
    else:
      nextTone = 2

    self.trials.append([self.trialNum, self.currentTrial,0])
    self.setSyncTrial(self.currentTrial)
    self.playSound(nextTone)
    self.trialInit = time.time()
    if self.currentTrial=='L':
      self.setSyncH([2,7])
    else:
      self.setSyncH([3,8])

    logger.info('Played tone {a} trialNum {b}'.format(a=nextTone,b=self.trialNum))
    self.trialsCount[self.currentTrial] +=1

    while self.isSoundPlaying():
      time.sleep(.1)

    if self.currentTrial=='L':
      self.setSyncL([2,7])
    else:
      self.setSyncL([3,8])

    time.sleep(.2)

    if self.currentTrial == 'L':
      self.openGate('IUL')
    else:
      self.openGate('IUR')

  def printStats(self):
    tt = time.time() - self.timeInitTraining
    msg1 = 'Trial Num: {c} | Total time = {a} minutes {b} seconds'.format(a=int(tt/60),b=int(tt)%60,c = self.trialNum)
    msg2 = 'Total trial: {a}/{b} = {c}% | Left: {d}/{e} = {f}% | Right: {g}/{h} = {i}%'.format(
        a = (self.trialsCorrect['L']+self.trialsCorrect['R']),
        b = (self.trialsCount['L']+self.trialsCount['R']),
        c = round(100*(self.trialsCorrect['L']+self.trialsCorrect['R'])/(self.trialsCount['L']+self.trialsCount['R']+0.0001)),
        d = self.trialsCorrect['L'] ,
        e = self.trialsCount['L'] ,
        f = round(100*self.trialsCorrect['L']/(self.trialsCount['L']+0.0001)),
        g = self.trialsCorrect['R'] ,
        h = self.trialsCount['R'] ,
        i = round(100*self.trialsCorrect['R']/(self.trialsCount['R']+0.0001)))
    print (msg1)
    print (msg2)
    logger.info(msg1)
    logger.info(msg2)

  def run(self):
    ''' 
    This is the main loop. It should have a 'while True:' statement
    also it is recomended to have a time.slep(.05) or bigger delay
    
    '''
    self.trialNum = 0
    # waiting to rat to pass the sensor
    #while self.getLastSensorActive()!='C':
    while self.myLastSensor is not 'C':
        time.sleep(.1)
        pass

    self.closeGateFast('IBR')
    self.openGateFast('OBR')
    self.startTraining()
    self.timeInitTraining = time.time()
    time.sleep(10)

    self.startTrial()
    while True:
      #self.myFunction(self.state)
      if self.state == 'start':
        self.rewardDone = False

        if self.myLastSensor=='UL':
          logger.info('Rat at {a}'.format(a='UL'))
          #the rat went left
          self.closeGateFast('IUR')
          self.state='going left'
        elif self.myLastSensor=='UR':
          logger.info('Rat at {a}'.format(a='UR'))
          #the rat went right
          self.closeGateFast('IUL')
          self.state='going right'
        elif self.myLastSensor=='L':
          logger.warning('Reached left without passing through UL')
          self.state='going left'
        elif self.myLastSensor=='R':
          logger.warning('Reached right without passing through UR')
          self.state='going right'
        elif self.myLastSensor=='C':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'going left':
        if self.myLastSensor=='L':
          logger.info('Rat at {a}'.format(a='L'))
          self.closeGateFast('IUL')
          self.openGateFast('IBL')
          self.state = 'reward left'
          if self.rewardDone == False:
            self.rewardDone = True
            now = time.time()
            if now > (self.trialInit + self.rewardWindow):
              logger.info('Not Giving reward, exceeding window')
            elif self.currentTrial=='R':
              logger.info('Not Giving reward, wrong side')
            else:
              logger.info('Giving reward')
              self.multiDrop('L')
              self.trialsCorrect['L'] += 1
              self.trials[-1][2] = 1
            self.printStats()
        elif self.myLastSensor=='BL':
          logger.warning('Reached Bottom Left without passing through L')
        elif self.myLastSensor=='UL':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'reward left':
        if self.myLastSensor=='BL':
          logger.info('Rat at {a}'.format(a='BL'))
          self.state = 'returning left'
        elif self.myLastSensor=='C':
          logger.warning('Reached Center without passing through BL')
          ## should do the same as returning left
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBL')
          self.state = 'start'
          self.startTrial()
        elif self.myLastSensor=='L' or self.myLastSensor=='UL':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))


      elif self.state == 'returning left':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBL')
          self.state = 'start'
          self.startTrial()


      elif self.state == 'going right':
        if self.myLastSensor=='R':
          logger.info('Rat at {a}'.format(a='R'))
          self.closeGateFast('IUR')
          self.openGateFast('IBR')
          self.state = 'reward right'
          if self.rewardDone == False:
            now = time.time()
            self.rewardDone = True
            if now > (self.trialInit + self.rewardWindow):
              logger.info('NOT Giving reward, exceeding window')
            elif self.currentTrial=='L':
              logger.info('Not Giving reward, wrong side')
            else:
              logger.info('Giving reward')
              self.multiDrop('R')
              self.trialsCorrect['R'] += 1
              self.trials[-1][2] = 1
            self.printStats()
        elif self.myLastSensor=='BR':
          logger.warning('Reached Bottom right without passing through R')
        elif self.myLastSensor=='UR':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'reward right':
        if self.myLastSensor=='BR':
          logger.info('Rat at {a}'.format(a='BR'))
          self.state = 'returning right'
        elif self.myLastSensor=='C':
          logger.warning('Reached Center without passing through BR')
          ## should do the same as returning right
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.state = 'start'
          self.startTrial()
        elif self.myLastSensor=='R' or self.myLastSensor=='UR':
          pass
        else:
          logger.error('Something went wrong State={a}, Sensor={b}'.format(a=self.state,b=self.myLastSensor))

      elif self.state == 'returning right':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.state = 'start'
          self.startTrial()

      time.sleep(.05)
