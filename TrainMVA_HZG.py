#!/usr/bin/env python

import ROOT


inputFilesDir = '../HiggsZGAnalyzer/mvaFiles/'
outputWeightsDir = ''

USE_SEPARATE_TRAIN_TEST_FILES = True
# if selecting training and testing events from the same file
# one has to enter specify the number of events

def TrainMva(myMethodList = '', _signalName, _bgName, _numSignalTrain = 0, _numBgTrain = 0, _numSignalTest = 0, _numBgTest = 0, _weightsSubDir = ''):

  print '==> Starting TrainMva '
  # subdirectory where output weights for classifiers will go
  outputWeightsDir += _weightsSubDir


  # Common weights for the entire sample
  # use with event weights that do not account for x-section,
  # or with fullWeight to avoid too small weights due to small sample scale factors (if such issues occur)
  signalWeight = 1.0
  backgroundWeight = 1.0

  sigFileName_train = ''
  sigFileName_test = ''

  bgFileName_train = ''
  bgFileName_test = ''

  # signal names are hzzXXX
  # bgName: zz, ttbar, dymm,.... see below
  # this is for individual training.
  # When bg's are combined we use a variation of  allBg.
  # For the case when the gamma+jet sample was used for DY
  # the name is allBgPhoton.
  #  Define bg's inputs as needed

  # CHECK THE FILENAMES BELOW AGAIN!!!

  if (_bgName == 'zz'):
    bgFileName_train = inputFilesDir + 'zz_train.root'
    bgFileName_test = inputFilesDir + 'zz_test.root'
    bgFileName = inputFilesDir + 'zz.root' # when it is common.
  elif (_bgName == 'ttbar'):
    bgFileName_train = inputFilesDir + 'ttbar_train.root'
    bgFileName_test = inputFilesDir + 'ttbar_test.root'
    bgFileName = inputFilesDir + 'ttbar.root' # when it is common.
  else:
    print 'Unknown background',_bgName,'Check Input!'
    return


  if (_signalName == 'hzz125'):
    sigFileName_train = inputFilesDir + 'hzz125_train.root'
    sigFileName_test = inputFilesDir + 'hzz125_test.root'
    sigFileName = inputFilesDir + 'hzz125.root'
  else if (_signalName == 'hzz200'):
    sigFileName_train = inputFilesDir + 'hzz200_train.root'
    sigFileName_test = inputFilesDir + 'hzz200_test.root'
    sigFileName = inputFilesDir + 'hzz200.root'
  else:
    print 'Unknown signal',_signalName,'Check Input!'
    return

  #   used for the filenames of the MVA weights xml files, etc.
  sampleNames =  _bgName+'_'+_signalName+'_'

  # contains the performance histograms from the training
  # and the input variables
  outFileName = sampleNames + 'TMVA.root'

  #-----------------------------------------------------------

  ROOT.TMVA.Tools.Instance()

  # Default MVA methods to be trained + tested
  Use = {}

  # See available methods below.
  # If the list of methods passed to TrainMva is empty (=''), the switches below determine what methods are used
  # else they are ignored.

  # --- Cut optimisation
  Use['Cuts'] = 0
  Use['CutsD'] = 0
  Use['CutsPCA'] = 0
  Use['CutsGA'] = 0
  Use['CutsSA'] = 0
  #
  # --- 1-dimensional likelihood ('naive Bayes estimator')
  Use['Likelihood'] = 0
  Use['LikelihoodD'] = 0
  Use['LikelihoodPCA'] = 0
  Use['LikelihoodKDE'] = 0
  Use['LikelihoodMIX'] = 0
  #
  # --- Mutidimensional likelihood and Nearest-Neighbour methods
  Use['PDERS'] = 0
  Use['PDERSD'] = 0
  Use['PDERSPCA'] = 0
  Use['PDEFoam'] = 0
  Use['PDEFoamBoost'] = 0
  Use['KNN'] = 0
  #
  # --- Linear Discriminant Analysis
  Use['LD'] = 0
  Use['Fisher'] = 0
  Use['FisherG'] = 0
  Use['BoostedFisher'] = 0
  Use['HMatrix'] = 0
  #
  # --- Function Discriminant analysis
  Use['FDA_GA'] = 0
  Use['FDA_SA'] = 0
  Use['FDA_MC'] = 0
  Use['FDA_MT'] = 0
  Use['FDA_GAMT'] = 0
  Use['FDA_MCMT'] = 0
  #
  # --- Neural Networks (all are feed-forward Multilayer Perceptrons)
  Use['MLP'] = 0 # Recommended ANN
  Use['MLPBFGS'] = 0 # Recommended ANN with optional training method
  Use['MLPBNN'] = 1 # Recommended ANN with BFGS training method and bayesian regulator
  Use['CFMlpANN'] = 0 # Depreciated ANN from ALEPH
  Use['TMlpANN'] = 0 # ROOT's own ANN
  #
  # --- Support Vector Machine
  Use['SVM'] = 0
  #
  # --- Boosted Decision Trees
  Use['BDT'] = 1 # uses Adaptive Boost
  Use['BDTG'] = 0 # uses Gradient Boost
  Use['BDTB'] = 0 # uses Bagging
  Use['BDTD'] = 0 # decorrelation + Adaptive Boost
  Use['BDTF'] = 0 # allow usage of fisher discriminant for node splitting
  #
  # --- Friedman's RuleFit method, ie, an optimised series of cuts ('rules')
  Use['RuleFit'] = 0 # problem with DY (AA)
  # ---------------------------------------------------------------

  print
  print '==> Start TrainMva'

  # --- Here the preparation phase begins

  # Create a ROOT output file where TMVA will store ntuples, histograms, etc.
  outputFile = ROOT.TFile.Open(outFileName, 'RECREATE')
  classificationBaseName = 'discr_' + sampleNames + '_'

  factory = ROOT.TMVA.Factory(classificationBaseName, outputFile,
      '!V:!Silent:Color:DrawProgressBar:Transformations=ID;P;G,D:AnalysisType=Classification');

  (TMVA.gConfig().GetIONames()).fWeightFileDir = outputWeightsDir

  # Define the input variables that shall be used for the MVA training


  factory.AddVariable('medisc','-log(Pb/(Ps+Pb))', '', 'F')
  factory.AddVariable('smallTheta','cos(#theta)','','F')
  factory.AddVariable('bigTheta','cos(#Theta)','','F')
  factory.AddVariable('comPhi','#phi','rad','F')


  if (!USE_SEPARATE_TRAIN_TEST_FILES):
    sigFile = ROOT.TFile.Open(sigFileName)
    bgFile = ROOT.TFile.Open(bgFileName)
    print '--- TrainMva       : Using input files:',sigFile.GetName(),'and',bgFile.GetName()
    # --- Register the training and test trees
    signal = sigFile.Get('varMVA')
    background = bgFile.Get('varMVA')

    # You can add an arbitrary number of signal or background trees
    factory.AddSignalTree(signal, signalWeight)
    factory.AddBackgroundTree(background, backgroundWeight)
  else:
    sigFile_train = ROOT.TFile.Open(sigFileName_train)
    bgFile_train = ROOT.TFile.Open(bgFileName_train)
    sigFile_test = ROOT.TFile.Open(sigFileName_test)
    bgFile_test = ROOT.TFile.Open(bgFileName_test)

    print '--- TrainMva       : Using input files:',sigFile_train.GetName(), 'and', bgFile_train.GetName()
    print sigFile_test.GetName(), 'and', bgFile_test.GetName()

    signal_train =  sigFile_train.Get('varMVA')
    background_train =  bgFile_train.Get('varMVA')
    signal_test = sigFile_test.Get('varMVA')
    background_test = bgFile_test.Get('varMVA')

    factory.AddSignalTree(signal_train, signalWeight * 2, 'Training')
    factory.AddBackgroundTree(background_train, backgroundWeight * 2, 'Training')
    factory.AddSignalTree(signal_test, signalWeight * 2, 'Test')
    factory.AddBackgroundTree(background_test, backgroundWeight * 2, 'Test')
  }

  # Weights stored in the input ntuples to be used for event weighting.
  # For mixed bg samples these will contain scaling factors that ensure the
  # different components are mixed according to the xsections.
  # Vertex multiplicity weighting (where applicable) should also be included.

  factory.SetSignalWeightExpression('scaleFactor')
  factory.SetBackgroundWeightExpression('scaleFactor')

  if (!USE_SEPARATE_TRAIN_TEST_FILES) {
    factory.PrepareTrainingAndTestTree(addCutsSig, addCutsBg,
        'nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V') # I used this one when reading train/test from same file
  } else {
    # I prefer using separate files for training/testing, so this is just for completeness.

    # note that here the signal and the bg cuts are the same, so we can use this form
    factory.PrepareTrainingAndTestTree(addCutsSig,
        _numSignalTrain, _numBgTrain, _numSignalTest, _numBgTest,
        'SplitMode=Random:NormMode=NumEvents:!V')
  }


  std::cout << '==> Booking the methods ' << std::endl
  # ---- Book MVA methods
  #
  # Please lookup the various method configuration options in the corresponding cxx files, eg:
  # src/MethoCuts.cxx, etc, or here: http:#tmva.sourceforge.net/optionRef.html
  # it is possible to preset ranges in the option string in which the cut optimisation should be done:
  # '...:CutRangeMin[2]=-1:CutRangeMax[2]=1'...', where [2] is the third input variable



