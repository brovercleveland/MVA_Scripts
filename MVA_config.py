#!/usr/bin/env python

from Subsets import k_subsets
from TrainMVA_HZG import TrainMva

varList = ['smallTheta', 'bigTheta', 'comPhi', 'threeBodyPtOM', 'GEta', 'l1Eta', 'l2Eta']
varNames = ['cos(#theta)', 'cos(#Theta)', '#phi', 'pT_{ll#gamma}/m_{ll#gamma}', '#eta_{#gamma}', '#eta_{l1}', '#eta_{l2}']
varDict = dict(zip(varList,varNames))

selectionList = ['mumuGamma', 'eeGamma']
sampleSuffix = '05-07-14_PhoMVA'

for subsetSize in range(2, len(varList)+1):
  for subVarList in k_subsets(varList,subsetSize):
    print list(subVarList)
    if len(subVarList) == 7:
      TrainMva(subVarList,varDict,sampleSuffix)

