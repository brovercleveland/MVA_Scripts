#!/usr/bin/env python

from Subsets import k_subsets
from TrainMVA_HZG import TrainMva
import shutil
import os

varList = ['smallTheta', 'bigTheta', 'comPhi', 'threeBodyPtOM', 'GEta', 'l1Eta', 'l2Eta']
varNames = ['cos(#theta)', 'cos(#Theta)', '#phi', 'pT_{ll#gamma}/m_{ll#gamma}', '#eta_{#gamma}', '#eta_{l1}', '#eta_{l2}']
varDict = dict(zip(varList,varNames))

selectionList = ['mumuGamma', 'eeGamma']
sampleSuffix = '05-07-14_PhoMVA'
bgName = 'allBG'
selection = 'mumuGamma'

logFile = open('mvaeff.out','w')
logFile.write('--- ==================================================================================================\n')
logFile.write('--- Cuts                          Classifier   (  #signal, #backgr.)  Optimal-cut  S/sqrt(S+B)      NSig      NBkg   EffSig   EffBkg\n')
logFile.write('--- --------------------------------------------------------------------------------------------------\n')
logFile.close()

for subsetSize in range(2, len(varList)+1):
  for subVarList in k_subsets(varList,subsetSize):
    print list(subVarList)
    TrainMva(subVarList,varDict,sampleSuffix,log='mvaeff.out')

headDir = '_'.join([sampleSuffix,bgName,'ggM123'])
outputDir = '/'.join([headDir,selection])

shutil.copy('mvaeff.out',outputDir)
os.remove('mvaeff.out')


