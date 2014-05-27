#!/usr/bin/env python

from Subsets import k_subsets
from TrainMVA_HZG import TrainMva
import shutil
import os
import sys

def VarOptimizer():
  varList = ['smallTheta', 'bigTheta', 'comPhi', 'threeBodyPtOM', 'GEta', 'l1Eta', 'l2Eta']
#varList = ['bigTheta', 'l2Eta']
  varNames = ['cos(#theta)', 'cos(#Theta)', '#phi', 'pT_{ll#gamma}/m_{ll#gamma}', '#eta_{#gamma}', '#eta_{l1}', '#eta_{l2}']
  varDict = dict(zip(varList,varNames))

  selectionList = ['mumuGamma', 'eeGamma']
  sampleSuffix = '05-24-14_PhoMVA'
  bgName = 'allBG'
#selection = 'mumuGamma'

  for selection in selectionList:
    logFile = open('mvaeff.out','w')
    logFile.write('--- ==================================================================================================\n')
    logFile.write('--- Cuts                          Classifier   (  #signal, #backgr.)  Optimal-cut  S/sqrt(S+B)      NSig      NBkg   EffSig   EffBkg\n')
    logFile.write('--- --------------------------------------------------------------------------------------------------\n')
    logFile.close()

    for subsetSize in range(2, len(varList)+1):
      for subVarList in k_subsets(varList,subsetSize):
        print list(subVarList)
        TrainMva(subVarList,varDict,sampleSuffix,doGui = False, log='mvaeff.out',_selection = selection)

    headDir = '_'.join([sampleSuffix,bgName,'ggM123'])
    outputDir = '/'.join([headDir,selection])

    shutil.copy('mvaeff.out',outputDir)
    os.remove('mvaeff.out')

def Gui():
  varList_mu = ['smallTheta', 'bigTheta', 'threeBodyPtOM', 'l1Eta', 'l2Eta']
  varNames_mu = ['cos(#theta)', 'cos(#Theta)', 'pT_{ll#gamma}/m_{ll#gamma}', '#eta_{l1}', '#eta_{l2}']
  varList_el = ['threeBodyPtOM', 'l2Eta', 'GEta', 'bigTheta', 'smallTheta', 'l1Eta']
  varNames_el = ['pT_{ll#gamma}/m_{ll#gamma}', '#eta_{l2}', '#eta_{#gamma}', 'cos(#Theta)', 'cos(#theta)', '#eta_{l1}']

  varDict_mu = dict(zip(varList_mu,varNames_mu))
  varDict_el = dict(zip(varList_el,varNames_el))

  sampleSuffix = '05-24-14_PhoMVA'
  bgName = 'allBG'

  TrainMva(varList_mu,varDict_mu,sampleSuffix,_selection = 'mumuGamma',doGui = True)
  TrainMva(varList_el,varDict_el,sampleSuffix,_selection = 'eeGamma', doGui = True)

if __name__ == "__main__":
  def Wrong():
    print 'specify either "opt" or "gui"'

  if len(sys.argv) != 2: Wrong()
  if sys.argv[1] == 'opt': VarOptimizer()
  elif sys.argv[1] == 'gui': Gui()
  else: Wrong()

