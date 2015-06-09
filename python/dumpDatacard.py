#!env python

import sys,os
from glob import glob
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-v","--verbose",dest="verbose",action='store_true',help="Verbose",default=False)
parser.add_option("-f","--file",dest="file",type='string',help="outputfile",default='datacard.txt')
parser.add_option("-i","--input",dest="input",type='string',help="input root file",default='datacard.txt')

parser.add_option("","--hist",dest="hist",type='string',help="histograms. Comma separated.\n\tonly one for cut&count. ",default='CutFlow')
parser.add_option("","--bin",dest="bin",type='string',help="bins for cut and cout, empty for shape analysis.",default="2")

parser.add_option("","--sig",dest="sig",type='string',help="Signal Labels. Default=%default",default='TBHp_HToTauNu_M-200')
parser.add_option("","--bkg",dest="bkg",type='string',help="Bkg Labels. Default=%default",default='DY,TTJets')

parser.add_option("","--syst",dest="syst",type='string',help="Syst Labels. Default=%default",default='JES,JER')

parser.add_option("-s","--shape",dest="shape",action='store_true',help="Force Shape analysis",default=False)

(opts,args) = parser.parse_args()

datacard = open(opts.file,"w")
dataSyst = ["JES"]
mcSyst = ["JER"]

def PrintSeparator():
	print >>datacard, "----------------------------"

def PrintHeader():
	print >>datacard, "datacard for Charged Higgs"
	print >>datacard, "Autogenerated with dumpDatacard "
	print >>datacard, "run with combine"
	PrintSeparator()	
	print >>datacard, "imax *"
	print >>datacard, "jmax *"
	print >>datacard, "kmax *"
	PrintSeparator()	

def PrintLumiSyst(unc, n):
	print >>datacard, "lumi\tlnN",
	for i in range(0,n):
		print>>datacard, 1+unc,
	print >>datacard,""

def PrintCutAndCount():
	''' Print cut and count datacard '''
	sys.argv=[]
	import ROOT
	ROOT.gROOT.SetBatch()
	
	fROOT = ROOT.TFile.Open(opts.input)

	if len(opts.hist.split(',')) != 1: print "ERROR: More than 1 histogram given for cut and count analysis"

	# PRINT FIRST BIN LINE
	#print "bin cat0_8TeV cat1_8TeV cat2_8TeV" 
	print >> datacard, "bin\t",
	for idx,bin in enumerate( opts.bin.split(',') ):
		print >>datacard , "cat%d"%idx,
	print>>datacard, "" 

	# PRINT OBSERVATION
	#observation     -1 -1 -1 
	hData = fROOT.Get(opts.hist)
	if hData == None: 
		print "Data file not found. Using empty one!"
		hData=ROOT.TH1D("fake","fake",100,0,100);

	print >>datacard,"observation\t",
	for idx,bin in enumerate( opts.bin.split(',') ):
		print >>datacard, "%d"%hData.GetBinContent(int(bin)),
	print>>datacard, "" 

	### SIG AND BKG
	# SECOND BIN LINE
	#bin        cat0  cat0 cat0 cat1
	print >>datacard, "bin\t",
	for idx,bin in enumerate( opts.bin.split(',') ):
		for mc in opts.sig.split(','):
			print >>datacard, "cat%d"%idx,
		for mc in opts.bkg.split(','):
			print >>datacard, "cat%d"%idx,
	print >>datacard, ""
	# FIRST PROCESS LINE
	#process    ggH   qqH  bkg  ggH ...
	print >>datacard, "process\t",
	for idx,bin in enumerate( opts.bin.split(',') ):
		for mc in opts.sig.split(','):
			print >>datacard, mc,
		for mc in opts.bkg.split(','):
			print >>datacard, mc,
	print >>datacard, ""
	# SECOND PROCESS LINE
	#process    0     -1   1    0
	print >>datacard, "process\t",
	for idx,bin in enumerate( opts.bin.split(',') ):
		for idx2,mc in enumerate(opts.sig.split(',')):
			print >>datacard, -idx2,
		for idx3,mc in enumerate(opts.bkg.split(',')):
			print >>datacard, idx3+1,
	print >>datacard, ""
	# RATE LINE
	#rate       x     y    z
	print >>datacard, "rate\t",
	for idx,bin in enumerate( opts.bin.split(',') ):
		for mc in opts.sig.split(','):
			mcH=fROOT.Get( opts.hist + "_" + mc)
			print >>datacard, mcH.GetBinContent(int(bin)),
		for mc in opts.bkg.split(','):
			mcH=fROOT.Get( opts.hist + "_" + mc)
			print >>datacard, mcH.GetBinContent(int(bin)),
	print >>datacard, ""
	PrintSeparator()

	## SYST
	#lumi_8TeV                             lnN   1.026 1.026 - 1.026 1.026 - 1.026 1.026 - 
	#0.994/1.006
	PrintLumiSyst( 0.05, len(opts.sig.split(',')) + len(opts.bkg.split(',') ) )
	for syst in opts.syst.split(','):
		if syst not in dataSyst: continue;
		print >> datacard, syst ,"\tlnN",
		for idx,bin in enumerate( opts.bin.split(',') ):
			hUp = fROOT.Get( opts.hist + "_Data_" + syst + "_UP" )
			hDown = fROOT.Get( opts.hist + "_Data_" + syst + "_DOWN" )
			hNominal = fROOT.Get( opts.hist + "_Data_")
			for mc in opts.sig.split(','):
				print >>datacard, hDown.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin)) + "/" + \
						 hUp.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin)),
			for mc in opts.bkg.split(','):
				print >>datacard, hDown.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin)) + "/" + \
						 hUp.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin)),
		print >>datacard,""

	for syst in opts.syst.split(','):
		if syst not in mcSyst: continue;
		print >> datacard, syst ,"\tlnN",
		for idx,bin in enumerate( opts.bin.split(',') ):
			for mc in opts.sig.split(','):
				hUp = fROOT.Get( opts.hist + "_" + mc + "_" + syst + "_UP" )
				hDown = fROOT.Get( opts.hist + "_" + mc + "_" + syst + "_DOWN" )
				#print "Getting histo:", hDown,"|", opts.hist + "_" + mc + "_" + syst + "_DOWN" 
				hNominal = fROOT.Get( opts.hist + "_"+ mc  )
				#print "Getting histo:", hNominal, "|",opts.hist + "_"+ mc
				print >>datacard, str(hDown.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin))) + "/" + \
						 str(hUp.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin))),
			for mc in opts.bkg.split(','):
				hUp = fROOT.Get( opts.hist + "_" + mc + "_" + syst + "_UP" )
				hDown = fROOT.Get( opts.hist + "_" + mc + "_" + syst + "_DOWN" )
				hNominal = fROOT.Get( opts.hist + "_"+ mc  )
				print >>datacard, str(hDown.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin))) + "/" + \
						 str(hUp.GetBinContent(int(bin))/hNominal.GetBinContent(int(bin))),
		print >>datacard,""

	for syst in opts.syst.split(','):
		if syst in mcSyst: continue;
		if syst in dataSyst: continue;
		print "Unable to deal with syst:", syst,"IGNORING IT!"

######################################## SHAPE ##################################
def PrintTH1ShapeLine(proc, cat, file, histo):
	''' Print One of the shaes lines'''
	## print >>datacard, "shapes PROC CAT file histo syste" 
	## print >>datacard, "shapes PROC CAT file w:histo" 
	print >> datacard, "shapes\t",proc,cat,file,histo,
	print >>datacard, histo + "$PROC_$SYSTEMATIC",
	print >>datacard, ""


def PrintDataShape(nCat):
	''' Print the first bin and observation lines'''
	print>>datacard, "bin\t",
	for cat in range(0,nCat):
		print >>datacard, "cat%d"%cat,
	print >>datacard, ""

	print>>datacard,"observation\t",
	for cat in range(0,nCat):
		print >>datacard, "-1", ## take from file
	print >>datacard, ""

def PrintMCShape(hists,sigs,bkgs):
	nCat=len(hists)	
	mcs = []
	mcs.extend(sigs)
	mcs.extend(bkgs)

	print >>datacard, "bin\t",
	for cat,h in enumerate(hists):
	   for mc in mcs:
	      print>>datacard, "cat%d"%cat,
	print>>datacard,""

	print >>datacard, "process\t",
	for cat,h in enumerate(hists):
	   for mc in mcs:
	      print>>datacard, mc,
	print>>datacard,""

	print >>datacard, "process\t",
	for cat,h in enumerate(hists):
	   for mc in mcs:
	      num=1000
	      if mc in sigs: num = -sigs.index(mc)
	      if mc in bkgs: num = bkgs.index(mc) + 1
	      print>>datacard, num,
	print>>datacard,""

	print >>datacard, "rate\t",
	for cat,h in enumerate(hists):
	   for mc in mcs:
	      print>>datacard, "-1",
	print>>datacard,""

def PrintSystShape(systs,hists,mcs):
	PrintLumiSyst( 0.05, len(opts.sig.split(',')) + len(opts.bkg.split(',') ) )
	for s in systs:	
		print>>datacard,s,"\tshape",
		for cat,h in enumerate(hists):
		   for mc in mcs:
		      print>>datacard, "1",
		print>>datacard,""



def PrintShape():
	''' Print shape analysis datacard'''
	hists = opts.hist.split(',')
	nCat=len(hists)
	mcs = []
	sigs = opts.sig.split(',')
	bkgs = opts.bkg.split(',')
	mcs.extend(opts.sig.split(','))
	mcs.extend(opts.bkg.split(','))

	for mc in mcs:
		for idx, h in enumerate(hists):
			PrintTH1ShapeLine( mc, "cat%d"%idx,opts.input ,h)
	PrintSeparator()
	PrintDataShape(nCat)
	PrintMCShape(hists,sigs,bkgs)
	PrintSeparator()
	PrintSystShape(opts.syst.split(','),hists,mcs)
	PrintSeparator()
	###




###################### MAIN ###############
if __name__ == "__main__":
	PrintHeader()
	if opts.bin >=0 and not opts.shape:
		PrintCutAndCount()
	else:
		PrintShape()