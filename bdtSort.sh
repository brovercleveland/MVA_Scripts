#! /usr/bin/env sh


inputDir=07-6-14_PhoMVA_allBG_ggM123/mumuGamma 
cat $inputDir/mvaeff.out | awk 'NR<4{print $0;next}{print $0| "sort -k8n"}' > $inputDir/sorted_mvaeff.out 
inputDir=07-6-14_PhoMVA_allBG_ggM123/eeGamma 
cat $inputDir/mvaeff.out | awk 'NR<4{print $0;next}{print $0| "sort -k8n"}' > $inputDir/sorted_mvaeff.out 
