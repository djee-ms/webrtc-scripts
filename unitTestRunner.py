import os
import time
import subprocess

import config
from logger import Logger
from utility import Utility
from settings import Settings
import errors
from errors import error_codes, NO_ERROR

class UnitTestRunner:
  @classmethod
  def init(cls):
    """
      Initiates logger object.
    """
    cls.logger = Logger.getLogger('Unit tests')

  @classmethod
  def run(cls, targetName, platform, cpu, configuration, builderWorkingPath = None):
    """
      Start target building process.
      :param targetName: Name of the main target (ortc or webrtc)
      :param platform: Platform name
      :param cpu: Target CPU
      :param builderWorkingPath: Path where generated projects for specified target.
      :return: NO_ERROR if build was successfull. Otherwise returns error code
    """
    start_time = time.time()
    ret = NO_ERROR
    cls.failedTestsCounter = 0
    cls.logger.info('Running unit tests for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration)

    #If path with generated projects is not specified generate path from input arguments
    if builderWorkingPath == None:
      builderWorkingPath = Settings.getGnOutputPath(config.GN_OUTPUT_PATH, targetName, platform, cpu, configuration)

    workingDir = os.path.join(Settings.webrtcPath,builderWorkingPath)

    #If folder for specified target and platform doesn't exist, stop further execution
    if not os.path.exists(workingDir):
      cls.logger.error('Output folder at ' + workingDir + ' doesn\'t exist. It looks like prepare is not executed. Please run prepare action.')
      return errors.ERROR_UNIT_TESTS_WORKING_FOLDER_NOT_EXIST

    #Change current working directory to one with generated projects
    Utility.pushd(workingDir)

    cls.unitTestFailuresLog = open('UnitTestFailures.txt','w')

    for unitTest in Settings.unitTests:
      cls.executeUnitTest(unitTest)
    
    cls.unitTestFailuresLog.close()
    
    if cls.failedTestsCounter > 0:
      cls.logger.warning('Some unit tests has failed. You can see the details in file ' + os.path.abspath(cls.unitTestFailuresLog))

    #Switch to previously working directory
    Utility.popd()

    if ret == NO_ERROR:
      cls.logger.info('Running build for target: ' + targetName + '; platform: ' + platform + '; cpu: ' + cpu + '; configuration: ' + configuration + ', finished successfully!')
    end_time = time.time()
    cls.executionTime = end_time - start_time
    return ret

  @classmethod
  def executeUnitTest(cls, unittest):
    """
    """
    ret = NO_ERROR

    listOfTests = config.AVAILABLE_UNIT_TESTS[unittest]
    cmdLine = unittest
    testsToRunSeparately = ''
    filter = '--gtest_filter='
    outputFile = unittest + '.txt'
    if '*' in listOfTests:
      if len(listOfTests) > 1:
        for testName in listOfTests[1:]:
          testsToRunSeparately += testName + ':'
        cmdLine += ' ' + filter + '-' + testsToRunSeparately
        ret = cls.runUnitTestSubprocess(cmdLine, outputFile)
        if ret == NO_ERROR:
          cmdLine += ' ' + filter + testsToRunSeparately
          ret = cls.runUnitTestSubprocess(cmdLine, outputFile, True)
        else:
          cls.logger.error('Failed running unit test ' + unittest)
      else:
        ret = cls.runUnitTestSubprocess(cmdLine, outputFile)
    else:
      for testName in listOfTests:
        testsToRunSeparately += testName + ':'
      cmdLine += ' ' + filter + testsToRunSeparately
      ret = cls.runUnitTestSubprocess(cmdLine, outputFile)
    
    cls.parseResults(unittest, outputFile)
    return ret

  @classmethod
  def parseResults(cls, unitTestName, outputFile):

    with open(outputFile, 'r') as fileToParse:
      fileContent = fileToParse.read()

    unitTests = fileContent.split(config.UNIT_TESTS_LOG_SEPARATOR)

    for unitTest in unitTests:
      testResults = unitTest.split(config.UNIT_TEST_RESULTS_SEPARATOR)
      testResult = testResults[-1]
      if 'FAILED' in testResult:
        cls.unitTestFailuresLog.write(unitTestName)
        cls.unitTestFailuresLog.write('==============')
        for line in testResult.split('\n'):
          if 'FAILED' in line:
            cls.failedTestsCounter += 1
            cls.unitTestFailuresLog.write(line)
        cls.unitTestFailuresLog.write('==============')
        cls.unitTestFailuresLog.flush()
    return True

  @classmethod
  def runUnitTestSubprocess(cls, unittest, logToFile = '', appendToFile = False):
    """
      Runs provided command line as subprocess.
      :param commands: List of commands to execute.
      :param shouldLog: Flag if subprocess stdout should be logged or not
      :return result: NO_ERROR if subprocess is executed successfully. Otherwise error or subprocess returncode
    """
    result = NO_ERROR
    logFile = None
    commandToExecute = ''

    try:
      if len(logToFile) > 0:
        if appendToFile:
          logFile = open(logToFile, 'a')
        else:
          logFile = open(logToFile, 'w')

      #Execute command
      cls.logger.debug('\n Running unit test: ' + unittest + '\n')
      process = subprocess.Popen(unittest, shell=False, stdin=subprocess.PIPE, stdout=logFile, stderr=subprocess.PIPE)
   
      #Enable showing subprocess output and responsiveness on keyboard actions (terminating script on user action) 
      stdout, stderr = process.communicate()

      if process.returncode != 0:
        if stderr != '':
          cls.logger.warning(str(stderr))

    except Exception as error:
      result = errors.ERROR_UNIT_TESTS_EXECUTION_FAILED
      cls.logger.error(str(error))
    finally:
      if process != None:
        process.terminate()
      if logFile != None:
        logFile.write(config.UNIT_TESTS_LOG_SEPARATOR)
        logFile.flush()

    if result != NO_ERROR:
      cls.logger.error(error_codes[result])

    return result