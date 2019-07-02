# Author: Ariel Burman

from mazeprotocols import MazeProtocols
import logging

# Name your protocol FileName and version (One file can have multiple protocol variants, 
PROTOCOL_FILE_NAME = __name__.split('.')[1] # This will return the filename, can be changed to any string
PROTOCOL_FILE_VERSION = '1.0'               # Could be used as an all-protocol file versioning

logger=logging.getLogger(PROTOCOL_FILE_NAME)
logger.info('Protocol File: {a}, Version: {b}'.format(a=PROTOCOL_FILE_NAME,b=PROTOCOL_FILE_VERSION))

# import any module you want to use
import time
import numpy as np


def randomInt(minor=5,mayor=8):
   return round(minor + np.floor((mayor-minor+1) * np.random.random()))


def randomDelay(minor=5,mayor=8):
   time.sleep( minor + (mayor-minor) * np.random.random() )

class RewardDrivenRandomBlock (MazeProtocols):
  def init(self,options):
    # initialization
    # put here the code you want to run only once, at first
    """ options needed 
        # Block
        blockMin      integer
        blockMax      integer
        
        # Reward
        multidropNum  integer
        rewardWindow  float
       
        # Stimulus
        toneFrecuency     integer
        toneVolume        float 0.0 to 1.0
        toneDuration      float
    """
    PROTOCOL_NAME = self.__class__.__name__   # Individual protocol name
    PROTOCOL_VERSION = '1.2'                # Individual protocol version

    logger.info('Protocol: {a}, Version: {b}'.format(a=PROTOCOL_NAME,b=PROTOCOL_VERSION))
    logger.info('Options readed from configuration file')
    for key in options:
        logger.info('Option {a} = {b}'.format(a=key,b=options[key]))

    self.blockMin = options['blockMin']
    self.blockMax = options['blockMax']
    self.rewardWindow = options['rewardWindow']
    self.multidropNum = options['multidropNum']
    self.setMultiDrop(self.multidropNum)
    self.addTone(1,duration=options['toneDuration'],freq=options['toneFrecuency'],volume=options['toneVolume'])
    self.state = 'start'
    self.closeGateFast('IUL')
    self.closeGateFast('IUR')
    self.openGateFast('OUL')
    self.openGateFast('OUR')
    self.openGateFast('OBL') # maybe closed
    self.closeGateFast('OBR') # maybe closed
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

  def buttonHandler(self,button):
      ''' If you dont use a handler this function should be commented'''
      print('button pressed {a}'.format(a=button))
      pass

  def sensorHandler(self,sensor):
      ''' If you dont use a handler this function should be commented'''
      logger.info('sensor activated {a}'.format(a=sensor))
      self.myLastSensor = sensor
      pass

  # Write your own methods
  
  def myFunction(self,param):
    logger.debug(param)

  def switchSide(self):
    if self.currentTrial == 'R':
        self.currentTrial = 'L'
    else:
        self.currentTrial = 'R'
    self.blockTrials = randomInt(self.blockMin,self.blockMax)
    logger.info('New Block. Trials Count = {a}, Correct Side = {b}'.format(a=int(self.blockTrials),b=self.currentTrial))
    self.playSound(1)


  def startTrial(self):
    randomDelay(2,3)
    self.trialNum += 1
    self.blockTrials -= 1
    logger.info('Block trials remaining = {a}'.format(a=int(self.blockTrials)))

    self.trials.append([self.trialNum, self.currentTrial,0])
        
    self.trialInit = time.time()
    self.setSyncTrial(self.currentTrial)
    if self.currentTrial == 'L':
      self.setSyncH([2,7])
    else:
      self.setSyncH([3,8])

    self.trialsCount[self.currentTrial] +=1

    if self.currentTrial == 'L':
      self.setSyncL([2,7])
    else:
      self.setSyncL([3,8])
    
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
    # select initial side
    if np.random.random()>0.5:
        self.currentTrial = 'L'
    else:
        self.currentTrial = 'R'
    self.blockTrials = randomInt(self.blockMin,self.blockMax)

    # waiting to rat to pass the sensor
    while self.myLastSensor is not 'C':
      time.sleep(.1)
      pass
    
    self.closeGateFast('IBR')
    self.openGateFast('OBR')
    self.startTraining()
    self.timeInitTraining = time.time()
    time.sleep(10)
    self.switchSide()
    self.startTrial()

    while True:
      self.myFunction(self.state)

      if self.state == 'start':
        self.rewardDone = False

        if self.myLastSensor=='UL':
          logger.info('Rat at {a}'.format(a='UL'))
          #the rat went left
          self.closeGateFast('IUR')
          self.state='going left'
          logger.info('reward on left')
        elif self.myLastSensor=='UR':
          logger.info('Rat at {a}'.format(a='UR'))
          #the rat went right
          self.closeGateFast('IUL')
          self.state='going right'
          # check for reward
          logger.info('reward on right')

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
              time.sleep(1)
            self.printStats()
            if self.blockTrials == 0:
                #play sound
                self.switchSide()

      elif self.state == 'reward left':
        if self.myLastSensor=='BL':
          logger.info('Rat at {a}'.format(a='BL'))
          self.state = 'returning left'

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
              time.sleep(1)
            self.printStats()
            if self.blockTrials == 0:
                #play sound
                self.switchSide()

      elif self.state == 'reward right':
        if self.myLastSensor=='BR':
          logger.info('Rat at {a}'.format(a='BR'))
          self.state = 'returning right'
              
      elif self.state == 'returning right':
        if self.myLastSensor=='C':
          logger.info('Rat at {a}'.format(a='C'))
          self.closeGateFast('IBR')
          self.state = 'start'
          self.startTrial()

      time.sleep(.01)

