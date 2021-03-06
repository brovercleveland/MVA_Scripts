#!/usr/bin/env python
import sys
import os
import shutil
import atexit


import ROOT


# if selecting training and testing events from the same file
# one has to enter specify the number of events

def TrainMva(varList, varDict, sampleSuffix, myMethodList = '', _signalName = 'ggM123', _bgName = 'allBG', _selection = 'mumuGamma', _numSignalTrain = 0, _numBgTrain = 0, _numSignalTest = 0, _numBgTest = 0, doGui = False, log = None):


  ROOT.gROOT.ProcessLine('.L '+os.getenv('ROOTSYS')+'/tmva/test/TMVAGui.C')
  inputFilesDir = 'testTrainDir/'

  USE_SEPARATE_TRAIN_TEST_FILES = True

  print '==> Starting TrainMva '
  # subdirectory where output weights and plots for classifiers will go

  headDir = '_'.join([sampleSuffix,_bgName,_signalName])
  outputDir = '/'.join([headDir,_selection,'_'.join(varList)])
  outputWeightsDir = outputDir + '/weights'
  if not os.path.exists(outputWeightsDir):
    os.makedirs(outputWeightsDir)

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

  fileSel = ''
  if _selection == 'mumuGamma':
    fileSel = 'MuMu'
  elif _selection == 'eeGamma':
    fileSel = 'EE'
  if (_bgName == 'allBG'):
    bgFileName_train = inputFilesDir + '_'.join(['higgsTraining',fileSel+'2012ABCD',sampleSuffix,'bg.root'])
    bgFileName_test = inputFilesDir + '_'.join(['higgsSample',fileSel+'2012ABCD',sampleSuffix,'bg.root'])
    bgFileName = inputFilesDir + 'zz.root' # when it is common.
  else:
    print 'Unknown background',_bgName,'Check Input!'
    return


  sigFileName_train = inputFilesDir + '_'.join(['higgsTraining',fileSel+'2012ABCD',sampleSuffix,'signal.root'])
  sigFileName_test = inputFilesDir + '_'.join(['higgsSample',fileSel+'2012ABCD',sampleSuffix,'signal.root'])
  sigFileName = inputFilesDir + 'hzz125.root'

  #   used for the filenames of the MVA weights xml files, etc.
  sampleNames =  '_'.join([_selection,_bgName,_signalName,sampleSuffix])

  # contains the performance histograms from the training
  # and the input variables
  outFileName = outputDir+'/'+sampleNames + '_TMVA.root'

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
  Use['MLPBNN'] = 0 # Recommended ANN with BFGS training method and bayesian regulator
  Use['CFMlpANN'] = 0 # Depreciated ANN from ALEPH
  Use['TMlpANN'] = 0 # ROOT's own ANN
  #
  # --- Support Vector Machine
  Use['SVM'] = 0
  #
  # --- Boosted Decision Trees
  Use['BDT'] = 0 # uses Adaptive Boost
  Use['BDTG'] = 1 # uses Gradient Boost
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

  #factory = ROOT.TMVA.Factory(classificationBaseName, outputFile, '!V:!Silent:Color:DrawProgressBar:Transformations=ID;P;G,D:AnalysisType=Classification');
  factory = ROOT.TMVA.Factory(classificationBaseName, outputFile, '!V:!Silent:Color:DrawProgressBar:Transformations=I;D;P;G,D:AnalysisType=Classification');

  (ROOT.TMVA.gConfig().GetIONames()).fWeightFileDir = outputWeightsDir

  # Define the input variables that shall be used for the MVA training


  for var in varList:
    factory.AddVariable(var,varDict[var],'','F')

  factory.AddSpectator('threeBodyMass','m_{ll#gamma}','GeV')


  if not USE_SEPARATE_TRAIN_TEST_FILES:
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

    factory.AddSignalTree(signal_train, signalWeight, 'Training')
    factory.AddBackgroundTree(background_train, backgroundWeight, 'Training')
    factory.AddSignalTree(signal_test, signalWeight, 'Test')
    factory.AddBackgroundTree(background_test, backgroundWeight, 'Test')

  # Weights stored in the input ntuples to be used for event weighting.
  # For mixed bg samples these will contain scaling factors that ensure the
  # different components are mixed according to the xsections.
  # Vertex multiplicity weighting (where applicable) should also be included.

  factory.SetSignalWeightExpression('scaleFactor')
  factory.SetBackgroundWeightExpression('scaleFactor')

  if not USE_SEPARATE_TRAIN_TEST_FILES:
    factory.PrepareTrainingAndTestTree('', '',
        'nTrain_Signal=0:nTrain_Background=0:SplitMode=Random:NormMode=NumEvents:!V') # I used this one when reading train/test from same file
  else:
    # I prefer using separate files for training/testing, so this is just for completeness.
    # note that here the signal and the bg cuts are the same, so we can use this form
    #_numSignalTrain = signal_train.GetEntries()
    #_numBgTrain = background_train.GetEntries()
    #_numSignalTest = signal_test.GetEntries()
    #_numBgTest = background_test.GetEntries()
    _numSignalTrain = 0
    _numBgTrain = 0
    _numSignalTest = 0
    _numBgTest = 0
    myCut = ROOT.TCut('threeBodyMass>115')
    factory.PrepareTrainingAndTestTree(myCut,
        _numSignalTrain, _numBgTrain, _numSignalTest, _numBgTest,
        'SplitMode=Random:NormMode=NumEvents:!V')


  print '==> Booking the methods'
  # ---- Book MVA methods
  #
  # Please lookup the various method configuration options in the corresponding cxx files, eg:
  # src/MethoCuts.cxx, etc, or here: http:#tmva.sourceforge.net/optionRef.html
  # it is possible to preset ranges in the option string in which the cut optimisation should be done:
  # '...:CutRangeMin[2]=-1:CutRangeMax[2]=1'...', where [2] is the third input variable

  # Cut optimisation
  if (Use['Cuts']):
    factory.BookMethod(ROOT.TMVA.Types.kCuts, 'Cuts',
        '!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart')

  if (Use['CutsD']):
    factory.BookMethod(ROOT.TMVA.Types.kCuts, 'CutsD',
        '!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart:VarTransform=Decorrelate')

  if (Use['CutsPCA']):
    factory.BookMethod(ROOT.TMVA.Types.kCuts, 'CutsPCA',
        '!H:!V:FitMethod=MC:EffSel:SampleSize=200000:VarProp=FSmart:VarTransform=PCA')

  if (Use['CutsGA']):
    factory.BookMethod(ROOT.TMVA.Types.kCuts, 'CutsGA',
        'H:!V:FitMethod=GA:CutRangeMin[0]=-10:CutRangeMax[0]=10:VarProp[1]=FMax:EffSel:Steps=30:Cycles=3:PopSize=400:SC_steps=10:SC_rate=5:SC_factor=0.95')

  if (Use['CutsSA']):
    factory.BookMethod(ROOT.TMVA.Types.kCuts, 'CutsSA',
        '!H:!V:FitMethod=SA:EffSel:MaxCalls=150000:KernelTemp=IncAdaptive:InitialTemp=1e+6:MinTemp=1e-6:Eps=1e-10:UseDefaultScale')

  # Likelihood ('naive Bayes estimator')
  if (Use['Likelihood']):
    factory.BookMethod(ROOT.TMVA.Types.kLikelihood, 'Likelihood',
        'H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmoothBkg[1]=10:NSmooth=1:NAvEvtPerBin=50')

  # Decorrelated likelihood
  if (Use['LikelihoodD']):
    factory.BookMethod(ROOT.TMVA.Types.kLikelihood, 'LikelihoodD',
        '!H:!V:TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=Decorrelate')

  # PCA-transformed likelihood
  if (Use['LikelihoodPCA']):
    factory.BookMethod(ROOT.TMVA.Types.kLikelihood, 'LikelihoodPCA',
        '!H:!V:!TransformOutput:PDFInterpol=Spline2:NSmoothSig[0]=20:NSmoothBkg[0]=20:NSmooth=5:NAvEvtPerBin=50:VarTransform=PCA')

  # Use a kernel density estimator to approximate the PDFs
  if (Use['LikelihoodKDE']):
    factory.BookMethod(ROOT.TMVA.Types.kLikelihood, 'LikelihoodKDE',
        '!H:!V:!TransformOutput:PDFInterpol=KDE:KDEtype=Gauss:KDEiter=Adaptive:KDEFineFactor=0.3:KDEborder=None:NAvEvtPerBin=50')

  # Use a variable-dependent mix of splines and kernel density estimator
  if (Use['LikelihoodMIX']):
    factory.BookMethod(ROOT.TMVA.Types.kLikelihood, 'LikelihoodMIX',
        '!H:!V:!TransformOutput:PDFInterpolSig[0]=KDE:PDFInterpolBkg[0]=KDE:PDFInterpolSig[1]=KDE:PDFInterpolBkg[1]=KDE:PDFInterpolSig[2]=Spline2:PDFInterpolBkg[2]=Spline2:PDFInterpolSig[3]=Spline2:PDFInterpolBkg[3]=Spline2:KDEtype=Gauss:KDEiter=Nonadaptive:KDEborder=None:NAvEvtPerBin=50')

  # Test the multi-dimensional probability density estimator
  # here are the options strings for the MinMax and RMS methods, respectively:
  #      '!H:!V:VolumeRangeMode=MinMax:DeltaFrac=0.2:KernelEstimator=Gauss:GaussSigma=0.3' )
  #      '!H:!V:VolumeRangeMode=RMS:DeltaFrac=3:KernelEstimator=Gauss:GaussSigma=0.3' )
  if (Use['PDERS']):
    factory.BookMethod(ROOT.TMVA.Types.kPDERS, 'PDERS',
        '!H:!V:NormTree=T:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600')

  if (Use['PDERSD']):
    factory.BookMethod(ROOT.TMVA.Types.kPDERS, 'PDERSD',
        '!H:!V:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600:VarTransform=Decorrelate')

  if (Use['PDERSPCA']):
    factory.BookMethod(ROOT.TMVA.Types.kPDERS, 'PDERSPCA',
        '!H:!V:VolumeRangeMode=Adaptive:KernelEstimator=Gauss:GaussSigma=0.3:NEventsMin=400:NEventsMax=600:VarTransform=PCA')

  # Multi-dimensional likelihood estimator using self-adapting phase-space binning
  if (Use['PDEFoam']):
    factory.BookMethod(ROOT.TMVA.Types.kPDEFoam, 'PDEFoam',
        '!H:!V:SigBgSeparate=F:TailCut=0.001:VolFrac=0.0666:nActiveCells=500:nSampl=2000:nBin=5:Nmin=100:Kernel=None:Compress=T')

  if (Use['PDEFoamBoost']):
    factory.BookMethod(ROOT.TMVA.Types.kPDEFoam, 'PDEFoamBoost',
        '!H:!V:Boost_Num=30:Boost_Transform=linear:SigBgSeparate=F:MaxDepth=4:UseYesNoCell=T:DTLogic=MisClassificationError:FillFoamWithOrigWeights=F:TailCut=0:nActiveCells=500:nBin=20:Nmin=400:Kernel=None:Compress=T')

  # K-Nearest Neighbour classifier (KNN)
  if (Use['KNN']):
    factory.BookMethod(ROOT.TMVA.Types.kKNN, 'KNN',
        'H:nkNN=20:ScaleFrac=0.8:SigmaFact=1.0:Kernel=Gaus:UseKernel=F:UseWeight=T:!Trim')

  # H-Matrix (chi2-squared) method
  if (Use['HMatrix']):
    factory.BookMethod(ROOT.TMVA.Types.kHMatrix, 'HMatrix', '!H:!V:VarTransform=None')

  # Linear discriminant (same as Fisher discriminant)
  if (Use['LD']):
    factory.BookMethod(ROOT.TMVA.Types.kLD, 'LD', 'H:!V:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10')

  # Fisher discriminant (same as LD)
  if (Use['Fisher']):
    factory.BookMethod(ROOT.TMVA.Types.kFisher, 'Fisher', 'H:!V:Fisher:VarTransform=None:CreateMVAPdfs:PDFInterpolMVAPdf=Spline2:NbinsMVAPdf=50:NsmoothMVAPdf=10')

  # Fisher with Gauss-transformed input variables
  if (Use['FisherG']):
    factory.BookMethod(ROOT.TMVA.Types.kFisher, 'FisherG', 'H:!V:VarTransform=Gauss')

  # Composite classifier: ensemble (tree) of boosted Fisher classifiers
  if (Use['BoostedFisher']):
    factory.BookMethod(ROOT.TMVA.Types.kFisher, 'BoostedFisher',
        'H:!V:Boost_Num=20:Boost_Transform=log:Boost_Type=AdaBoost:Boost_AdaBoostBeta=0.2:!Boost_DetailedMonitoring')

  # Function discrimination analysis (FDA) -- test of various fitters - the recommended one is Minuit (or GA or SA)
  if (Use['FDA_MC']):
    factory.BookMethod(ROOT.TMVA.Types.kFDA, 'FDA_MC',
        'H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1)(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MC:SampleSize=100000:Sigma=0.1');

  if (Use['FDA_GA']): # can also use Simulated Annealing (SA) algorithm (see Cuts_SA options])
    factory.BookMethod(ROOT.TMVA.Types.kFDA, 'FDA_GA',
        'H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1)(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:PopSize=300:Cycles=3:Steps=20:Trim=True:SaveBestGen=1');

  if (Use['FDA_SA']): # can also use Simulated Annealing (SA) algorithm (see Cuts_SA options])
    factory.BookMethod(ROOT.TMVA.Types.kFDA, 'FDA_SA',
        'H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1)(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=SA:MaxCalls=15000:KernelTemp=IncAdaptive:InitialTemp=1e+6:MinTemp=1e-6:Eps=1e-10:UseDefaultScale');

  if (Use['FDA_MT']):
    factory.BookMethod(ROOT.TMVA.Types.kFDA, 'FDA_MT',
        'H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1)(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=2:UseImprove:UseMinos:SetBatch');

  if (Use['FDA_GAMT']):
    factory.BookMethod(ROOT.TMVA.Types.kFDA, 'FDA_GAMT',
        'H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1)(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=GA:Converger=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=0:!UseImprove:!UseMinos:SetBatch:Cycles=1:PopSize=5:Steps=5:Trim');

  if (Use['FDA_MCMT']):
    factory.BookMethod(ROOT.TMVA.Types.kFDA, 'FDA_MCMT',
        'H:!V:Formula=(0)+(1)*x0+(2)*x1+(3)*x2+(4)*x3:ParRanges=(-1,1)(-10,10);(-10,10);(-10,10);(-10,10):FitMethod=MC:Converger=MINUIT:ErrorLevel=1:PrintLevel=-1:FitStrategy=0:!UseImprove:!UseMinos:SetBatch:SampleSize=20');

  # TMVA ANN: MLP (recommended ANN) -- all ANNs in TMVA are Multilayer Perceptrons
  if (Use['MLP']):
    factory.BookMethod(ROOT.TMVA.Types.kMLP, 'MLP', '!H:!V:NeuronType=tanh:VarTransform=N:NCycles=500:HiddenLayers=N:TestRate=10')

  if (Use['MLPBFGS']):
    factory.BookMethod(ROOT.TMVA.Types.kMLP, 'MLPBFGS', 'H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:!UseRegulator')

  if (Use['MLPBNN']):
    factory.BookMethod(ROOT.TMVA.Types.kMLP, 'MLPBNN', 'H:!V:NeuronType=tanh:VarTransform=N:NCycles=600:HiddenLayers=N+5:TestRate=5:TrainingMethod=BFGS:UseRegulator') # BFGS training with bayesian regulators
  # reduced epochs from 600 (AA)


  # CF(Clermont-Ferrand)ANN
  if (Use['CFMlpANN']):
    factory.BookMethod(ROOT.TMVA.Types.kCFMlpANN, 'CFMlpANN', '!H:!V:NCycles=2000:HiddenLayers=N+1,N') # n_cycles:#nodes:#nodes:...

  # Tmlp(Root)ANN
  if (Use['TMlpANN']):
    factory.BookMethod(ROOT.TMVA.Types.kTMlpANN, 'TMlpANN', '!H:!V:NCycles=200:HiddenLayers=N+1,N:LearningMethod=BFGS:ValidationFraction=0.3') # n_cycles:#nodes:#nodes:...

  # Support Vector Machine
  if (Use['SVM']):
    factory.BookMethod(ROOT.TMVA.Types.kSVM, 'SVM', 'Gamma=0.25:Tol=0.001:VarTransform=Norm')

  # Boosted Decision Trees - DEFAULT
  #    if (Use['BDTG']): # Gradient Boost . Default parameters
  #        factory.BookMethod(ROOT.TMVA.Types.kBDT, 'BDTG',
  #            '!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedGrad:GradBaggingFraction=0.5:nCuts=20:NNodesMax=5')


  # here is a version with modified parameters
  if (Use['BDTG']): # Gradient Boost
    factory.BookMethod(ROOT.TMVA.Types.kBDT, 'BDTG',
        #'!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.10:UseBaggedGrad:GradBaggingFraction=0.5:nCuts=20:NNodesMax=8:nEventsMin=30')
        '!H:!V:NTrees=1200:BoostType=Grad:Shrinkage=0.10:UseBaggedGrad:GradBaggingFraction=0.7:nCuts=5000:NNodesMax=4:IgnoreNegWeights:nEventsMin=100')
        #'!H:V:NTrees=2000:BoostType=Grad:Shrinkage=0.05:nCuts=20:NNodesMax=10:UseBaggedGrad:GradBaggingFraction=0.50:IgnoreNegWeights')
    factory.PrintHelpMessage("BDTG")


  if (Use['BDT']): # Adaptive Boost
    factory.BookMethod(ROOT.TMVA.Types.kBDT, 'BDT',
        '!H:!V:NTrees=400:nEventsMin=40:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=1:SeparationType=GiniIndex:nCuts=20')


  if (Use['BDTB']): # Bagging
    factory.BookMethod(ROOT.TMVA.Types.kBDT, 'BDTB',
        '!H:!V:NTrees=400:BoostType=Bagging:SeparationType=GiniIndex:nCuts=20:PruneMethod=NoPruning')

  if (Use['BDTD']): # Decorrelation + Adaptive Boost
    factory.BookMethod(ROOT.TMVA.Types.kBDT, 'BDTD',
        '!H:!V:NTrees=400:nEventsMin=400:MaxDepth=3:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=20:PruneMethod=NoPruning:VarTransform=Decorrelate')

  if (Use['BDTF']): # Allow Using Fisher discriminant in node splitting for (strong) linearly correlated variables
    factory.BookMethod(ROOT.TMVA.Types.kBDT, 'BDTMitFisher',
        '!H:!V:NTrees=50:nEventsMin=150:UseFisherCuts:MaxDepth=3:BoostType=AdaBoost:AdaBoostBeta=0.5:SeparationType=GiniIndex:nCuts=20:PruneMethod=NoPruning')

  # RuleFit -- TMVA implementation of Friedman's method
  if (Use['RuleFit']):
    factory.BookMethod(ROOT.TMVA.Types.kRuleFit, 'RuleFit',
        'H:!V:RuleFitModule=RFTMVA:Model=ModRuleLinear:MinImp=0.001:RuleMinDist=0.001:NTrees=20:fEventsMin=0.01:fEventsMax=0.5:GDTau=-1.0:GDTauPrec=0.01:GDStep=0.01:GDNSteps=10000:GDErrScale=1.02')

  # For an example of the category classifier usage, see: TMVAClassificationCategory

  # --------------------------------------------------------------------------------------------------

  # ---- Now you can optimize the setting (configuration) of the MVAs using the set of training events

  # factory.OptimizeAllMethods('SigEffAt001','Scan')
  # factory.OptimizeAllMethods('ROCIntegral','GA')

  # --------------------------------------------------------------------------------------------------

  # ---- Now you can tell the factory to train, test, and evaluate the MVAs

  # Train MVAs using the set of training events
  factory.TrainAllMethods()

  # ---- Evaluate all MVAs using the set of test events
  factory.TestAllMethods()

  # ----- Evaluate and compare performance of all configured MVAs
  factory.EvaluateAllMethods()

  # --------------------------------------------------------------

  # Save the output
  outputFile.Close()
  sigFile_train.Close()
  sigFile_test.Close()
  bgFile_train.Close()
  bgFile_test.Close()

  print '==> Wrote root file:', outputFile.GetName()
  print '==> TrainMva is done!'

  # Launch the GUI for the root macro
  # make it lightweight for batch jobs and skip loading this script . for interactive include
  # TMVAGui.C which is currently commented out.

  if not doGui:
    #ROOT.gROOT.ProcessLine('.x '+os.getenv('ROOTSYS')+'/tmva/test/mvaeffs.C("'+outFileName+'","'+log+'","'+'_'.join(varList)+'")')
    ROOT.gROOT.ProcessLine('.x mvaeffs_v2.C("'+outFileName+'","'+log+'","'+'_'.join(varList)+'")')
    #ROOT.gApplication.SetReturnFromRun(True)
    #ROOT.gApplication.Terminate(0)
  else:
    ROOT.TMVAGui(outFileName)
    ROOT.gApplication.Run()

  if os.path.exists('plots'):
    if not os.path.exists(outputDir+'/plots'):
      shutil.move('plots',outputDir+'/plots')
    else:
      for plot in os.listdir('plots'):
        shutil.copy('plots/'+plot,outputDir+'/plots')
      shutil.rmtree('plots')


if __name__=="__main__":
  TrainMva(_selection='mumuGamma')
  #TrainMva()



