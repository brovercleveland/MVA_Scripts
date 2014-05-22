#! /usr/bin/env sh


cat 05-07-14_PhoMVA_allBG_ggM123/mumuGamma/mvaeff.out | awk 'NR<4{print $0;next}{print $0| "sort -k8n"}' > mvaeffsorted.out 
