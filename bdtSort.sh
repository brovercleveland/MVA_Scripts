#! /usr/bin/env sh


inputDir=05-24-14_PhoMVA_allBG_ggM123/mumuGamma 
cat $inputDir/mvaeff.out | awk 'NR<4{print $0;next}{print $0| "sort -k8n"}' > $inputDir/mvaeffsorted.out 
inputDir=05-24-14_PhoMVA_allBG_ggM123/eeGamma 
cat $inputDir/mvaeff.out | awk 'NR<4{print $0;next}{print $0| "sort -k8n"}' > $inputDir/mvaeffsorted.out 
