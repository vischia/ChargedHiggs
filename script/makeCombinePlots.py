#!/usr/bin/env python

# Usual reasons to love python imports
import os
import sys
import array 

from optparse import OptionParser
parser = OptionParser()
#parser.add_option("-f","--file",dest="files",default=[],action="append",help="Add a file")
parser.add_option("-f","--file",dest="file",default="",type="string",help="Input file")
parser.add_option("-l","--label",dest="label",default="",type="string",help="Labels, or none or one for input file")
parser.add_option("-o","--outname",dest="outname",help="Name of output pdf/png/C")
parser.add_option("-v","--verbose",dest="verbose",default=False,action="store_true")
parser.add_option("-b","--batch",dest="batch",default=False,action="store_true")
parser.add_option("-u","--unblind",dest="unblind",default=False,action="store_true",help="Draw observation")
parser.add_option("-x","--xSec",dest="xsec",help="Print limit vs xSec instead of mu",default=False,action="store_true")
parser.add_option("","--xSecName",dest="xsecname",help="extra string to be match in the mc_database",default="ChargedHiggs")
parser.add_option("","--mcdb",dest="mcdb",help="the mc_database",default="aux/mcdb.txt")
parser.add_option(""  ,"--yaxis",help="Y axis range Y1,Y2 [%default]",default="")
parser.add_option(""  ,"--xaxis",help="X axis range X1,X2 [%default]",default="")
parser.add_option("","--exclude",dest="exclude",help="Exclude mh points MH1,MH2,.. [%default]",default="")
(opts,args)=parser.parse_args()

sys.argv=[]
import ROOT

def interpolate(x1,y1,x2,y2,x):
	''' linear interpolation between the points (x1,y1) (x2,y2) evaluated at x'''
	#y = mx +q
	if x1==x2 and y1==y2 and x==x1 : return y1

	m= (y2-y1)/(x2-x1)
	q= y2 - m*x2
	return m*x+q

def EigthTeVGraph():
	''' Produce the 8TeV graph for exclusion limits in pb. CMS-PAS HIG-14-020. exp or obs'''
	median = ROOT.TGraph()
	median.SetName("median8TeV")
	obs = ROOT.TGraph()
	obs.SetName("obs8TeV")

	median.SetPoint( median.GetN() , 180 , 0.408 ) 
	obs.SetPoint(    median.GetN() , 180 , 0.384 ) 

	median.SetPoint( median.GetN() , 190 , 0.358 ) 
	obs.SetPoint(    median.GetN() , 190 , 0.377 ) 

	median.SetPoint( median.GetN() , 200 , 0.291 ) 
	obs.SetPoint(    median.GetN() , 200 , 0.362 ) 

	median.SetPoint( median.GetN() , 220 , 0.221 ) 
	obs.SetPoint(    median.GetN() , 220 , 0.331 ) 

	median.SetPoint( median.GetN() , 250 , 0.159 ) 
	obs.SetPoint(    median.GetN() , 250 , 0.266 ) 

	median.SetPoint( median.GetN() , 300 , 0.096 ) 
	obs.SetPoint(    median.GetN() , 300 , 0.153 ) 

	median.SetPoint( median.GetN() , 400 , 0.050 ) 
	obs.SetPoint(    median.GetN() , 400 , 0.054 ) 

	median.SetPoint( median.GetN() , 500 , 0.036 ) 
	obs.SetPoint(    median.GetN() , 500 , 0.033 ) 

	median.SetPoint( median.GetN() , 600 , 0.030 ) 
	obs.SetPoint(    median.GetN() , 600 , 0.026 ) 

	return (median,obs) 


def GetLimitFromTree(inputFile,xsec=False):
	''' Get Limit Histo from Combine tree'''

	## Make Limit plot
	fInput= ROOT.TFile.Open(inputFile)

	if fInput == None:
		print "**** ERROR ****"
		print " file ",f,"does not exist"
		print "***************"

	limitTree = fInput.Get("limit")
	if limitTree == None:
		print "**** ERROR ****"
		print " limit tree not present in file",f
		print "***************"
	
	#Expected
	obs=ROOT.TGraphAsymmErrors()
	obs.SetName("obs")
	
	exp=ROOT.TGraphAsymmErrors()
	exp.SetName("exp")
	
	oneSigma=ROOT.TGraphAsymmErrors()
	oneSigma.SetName("oneSigma")
	
	twoSigma=ROOT.TGraphAsymmErrors()
	twoSigma.SetName("twoSigma")
	
	data    = []
	median 	= []
	Up 	= []
	Up2 	= []
	Down 	= []
	Down2 	= []
	
	## loop over the entries and figure out if they are median, 1s/2s or observed	
	for iEntry in range(0,limitTree.GetEntries()):
		limitTree.GetEntry(iEntry)
		mh = limitTree.mh
		l  = limitTree.limit
		q  = limitTree.quantileExpected
		type= 0
	
		## TODO OBS
			
		if abs(q-0.5)<1.e-5 : 
			#exp.SetPoint(g.GetN(), mh,l ) 
			median.append(  (mh,l) ) 
		
		if abs(q -0.0250000) <1e-5:  ## 95% 2sDown
			type=-2
			Down2.append( (mh,l) )
		if abs(q-0.1599999) <1e-5 :  ## 68% 1sDown
			type=-1
			Down.append( (mh,l) )
		if abs(q-0.8399999) <1e-5 :  ## 68% 1sUp
			type=1
			Up.append( (mh,l) )
		if abs(q-0.9750000) <1e-5 :  ## 95% 2sUp
			type=2
			Up2.append( (mh,l) )
		if q <-.5: # -1
			data.append( (mh,l) ) 
	
	if len(Up2) != len(Down2) :print "[ERROR] Count 2s"
	if len(Up) != len(Down) :print "[ERROR] Count 1s"
	
	if xsec:
		## if you want the cross section , use the linear interpolation between the mass points
		if opts.verbose: print "-> Looking for basepath"
		basepath = ""
		mypath = os.path.abspath(os.getcwd())
		while mypath != "" and mypath != "/":
			if "ChargedHiggs" in os.path.basename(mypath):
				basepath = os.path.abspath(mypath)
			mypath = os.path.dirname(mypath)
		
		if opts.verbose: print "-> Base Path is " + basepath
		
		sys.path.insert(0,basepath)
		sys.path.insert(0,basepath+"/python/")
		sys.path.insert(0,os.getcwd())
		
		from ParseDat import ReadMCDB
	
		if 'FixQCD' in inputFile:
			print "->Reading from OLD"
			mcdb=ReadMCDB(basepath+"/dat/mc_database.old") 
		mcdb=ReadMCDB(basepath+"/"+opts.mcdb) 
		#R[label] = (dir,sumw,xsec)


	xsections_mcdb=[]
	xsections_interpolated={}

	if xsec:
		# save all the xSec in the mcdb
		for i in range(0,len(median)):
			mh= median[i][0]
			xSec= -1
			labelFound=""
			for label in mcdb:
				#if "M%.0f"%mh in label:
				if 'amcatnlo' not in label : continue
				if opts.xsecname not in label: continue
				if "M-%.0f"%mh in label: #amcatnlo
					labelFound=label[:]
					xSec = mcdb[label][2]
			if xSec <0 :  continue
			print "Found xSec for mh=",mh,"xSec=",xSec, "and label", labelFound
			xsections_mcdb.append(  (mh,xSec) )
		# run over the mass point and eventually interpolate between the xsec
		xsections_mcdb.sort()
		for i in range(0,len(median)):
			mh= median[i][0]
			bin=-1
			for j in range(0,len(xsections_mcdb) -1):
				if mh >= xsections_mcdb[j][0] and mh<  xsections_mcdb[j+1][0]:
					bin = j
				if j ==len(xsections_mcdb)-2 and mh == xsections_mcdb[j+1][0]:
					bin = j  # last bin is closed on both sides
			if bin <0 : 
				print "[ERROR]: unable to find cross section bin for mh=", mh
				print "-----------------------"
				for xsec in xsections_mcdb :
					print "mh=",xsec[0],"xsec=",xsec[1]
				print "-----------------------"
	
	
			xsections_interpolated[mh] = interpolate(xsections_mcdb[bin][0],float(xsections_mcdb[bin][1]),xsections_mcdb[bin+1][0],float(xsections_mcdb[bin+1][1]),mh )
	## sort median, Up Up2 Down Down2 data with mh
	median.sort()
	Up.sort()
	Up2.sort()
	Down.sort()
	Down2.sort()
	data.sort()
	## merge the list into TGraphs.
	for i in range(0,len(median)):
		count= exp.GetN()
	
		mh= median[i][0]
		if mh != Up[i][0] : print "[ERROR]: MH mismatch"
		if mh != Up2[i][0] : print "[ERROR]: MH mismatch"
		if mh != Down[i][0] : print "[ERROR]: MH mismatch"
		if mh != Down2[i][0] : print "[ERROR]: MH mismatch"
		if opts.unblind and mh != data[i][0]: print "[ERROR]: MH mismatch"

		isToExclude=False
		if opts.exclude != "":
			for mtest in opts.exclude.split(','):
				if float(mtest) == mh:
					isToExclude = True
		if isToExclude: 
			print "Excluding MH=",mh,"from the plot"
			continue
		
		if xsec:
			print "mh=",mh,"xSec=",xSec, "median = ",median[i][1]
			xSec =  xsections_interpolated[mh]
			median[i]   = (median[i][0], median[i][1]*xSec )
			Up[i]       = (mh, Up[i][1] * xSec ) 
			Up2[i]      = (mh, Up2[i][1] * xSec )
			Down[i]     = (mh, Down[i][1] * xSec )
			Down2[i]    = (mh, Down2[i][1] * xSec )
			if opts.unblind:
				data[i] = (mh, data[i][1] * xSec) 
	
		exp.SetPoint( count, median[i][0] ,median[i][1])

		oneSigma.SetPoint(count, mh, median[i][1] ) 
		oneSigma.SetPointError(count, 0, 0 , median[i][1] - Down[i][1], Up[i][1]-median[i][1] ) 
		twoSigma.SetPoint(count, mh , median[i][1] ) 
		twoSigma.SetPointError(count, 0, 0 , median[i][1] - Down2[i][1], Up2[i][1]-median[i][1] ) 

		if opts.unblind:obs.SetPoint(count,mh,data[i][1])

	return obs,exp,oneSigma,twoSigma

list_data = []
list_exp = []
list_oneSigma=[]
list_twoSigma=[]

for idx,f in enumerate(opts.file.split(',')):
	obs,exp,oneSigma,twoSigma = GetLimitFromTree(f,opts.xsec)

	if idx == 0 :
		obs.SetMarkerStyle(21)
		obs.SetMarkerSize(0.8)
		obs.SetLineColor(1)
		obs.SetLineWidth(2)
		obs.SetFillStyle(0)
		obs.SetMarkerColor(ROOT.kBlack)
		obs.SetLineColor(ROOT.kBlack)
		
		exp.SetLineColor(1)
		exp.SetLineStyle(2)
		exp.SetFillStyle(0)
		
		oneSigma.SetLineStyle(2)
		twoSigma.SetLineStyle(2)
		
		oneSigma.SetFillColor(ROOT.kGreen+1)
		twoSigma.SetFillColor(ROOT.kOrange)

		### PRINT MORE ##
		if opts.unblind:
			print "**** RESULTS **** "
			for point in range(0,obs.GetN()):
				print "MH=",obs.GetX()[point],"y=",obs.GetY()[point]
				print "exp=",exp.GetY()[point]
			print "***************** "

	else:
		obs.SetMarkerStyle(21+idx)
		obs.SetMarkerSize(0.8)
		obs.SetLineColor(1)
		obs.SetLineWidth(2)
		obs.SetFillStyle(0)
	
		exp.SetLineStyle(7)
		exp.SetFillStyle(0)

		if idx== 1:
			exp.SetLineColor(ROOT.kMagenta)
		elif idx==2:
			exp.SetLineColor(ROOT.kCyan)
		elif idx==3:
			exp.SetLineColor(ROOT.kBlue)
			exp.SetLineStyle(3)
		elif idx==4:
			exp.SetLineColor(ROOT.kViolet+1)
			exp.SetLineStyle(5)
		else:
			exp.SetLineColor(1)


		oneSigma.SetLineStyle(3)
		twoSigma.SetLineStyle(3)
		
		oneSigma.SetLineColor(ROOT.kGreen+2)
		twoSigma.SetLineColor(ROOT.kOrange)

		oneSigma.SetFillStyle(0)
		twoSigma.SetFillStyle(0)


	list_data.append(obs)
	list_exp.append(exp)
	list_oneSigma.append(oneSigma)
	list_twoSigma.append(twoSigma)

#if opts.xsec:
#	exp8TeV, obs8TeV= EigthTeVGraph()
#
#	exp8TeV.SetLineColor(ROOT.kRed+2)
#	exp8TeV.SetLineStyle(7)
#	exp8TeV.SetFillStyle(0)
#
#	obs8TeV.SetMarkerColor(ROOT.kRed+2)
#	obs8TeV.SetLineColor(ROOT.kRed+2)
#	obs8TeV.SetMarkerSize(0.8)
#	obs8TeV.SetMarkerStyle(21)
#	obs8TeV.SetFillStyle(0)

## Start Drawing
c=ROOT.TCanvas()

ROOT.gStyle.SetOptTitle(0)
ROOT.gStyle.SetOptStat(0)

if opts.xaxis != "":
	dummy = ROOT.TH1D("dummy","dummy",100, float(opts.xaxis.split(',')[0]), float(opts.xaxis.split(',')[1]))
	dummy.GetXaxis().SetRangeUser(200,3000)
else:
	dummy = ROOT.TH1D("dummy","dummy",1000, 0, 3000)

dummy.GetYaxis().SetRangeUser(1e2,1e8)

dummy.GetXaxis().SetTitle("m_{H^{+}} [GeV]")
dummy.GetYaxis().SetTitle("#sigma/#sigma_{MSSM}")

if opts.xaxis != "" and float(opts.xaxis.split(',')[1]) <135: ## SM?
	dummy.GetXaxis().SetTitle("m_{H} [GeV]")
	dummy.GetYaxis().SetTitle("#sigma/#sigma_{SM}")
else:
    c.SetLogy()

if opts.xsec:
	dummy.GetYaxis().SetTitle("#sigma [pb]")
	dummy.GetXaxis().SetRangeUser(200,3000)
	dummy.GetYaxis().SetRangeUser(1e-2,1e2)

if opts.yaxis != "":
	dummy.GetYaxis().SetRangeUser( float(opts.yaxis.split(',')[0]), float(opts.yaxis.split(',')[1]) )
if opts.xaxis != "":
	dummy.GetXaxis().SetRangeUser( float(opts.xaxis.split(',')[0]), float(opts.xaxis.split(',')[1]) )

dummy.Draw("AXIS")

line = ROOT.TGraph()
line.SetLineColor(ROOT.kGray)
line.SetPoint(0,0,1)
line.SetPoint(1,1000,1)


#mg = ROOT.TMultiGraph()

for idx in range(0,len(list_exp) ):
	if idx==0:
		#mg.Add(list_twoSigma[idx])
		#mg.Add(list_oneSigma[idx])
		list_twoSigma[idx].Draw("PE3 SAME")
		list_oneSigma[idx].Draw("PE3 SAME")
	#mg.Add(list_exp[idx])
	list_exp[idx].Draw("L SAME")
	if opts.unblind: list_data[idx].Draw("P SAME")

#mg.Draw("3")
#mg.Draw("LPX")

line.Draw("L SAME")

#if opts.xsec:
#	exp8TeV.Draw("L SAME")
#	obs8TeV.Draw("PL SAME")
#	l2= ROOT.TLatex()
#	l2.SetTextSize(0.03)
#	l2.SetTextColor(ROOT.kRed+2)
#	l2.SetTextAlign(22)
#	l2.DrawLatex(600,0.08,"19.7 fb^{-1} (8 TeV)")


dummy.Draw("AXIS SAME")
dummy.Draw("AXIS X+ Y+ SAME")
dummy.Draw("AXIG SAME")

# draw latex
l = ROOT.TLatex()
l.SetNDC()
l.SetTextSize(0.05)
l.SetTextFont(42)
l.SetTextAlign(13)
if opts.unblind:
    l.DrawLatex(0.13,.88,"#bf{CMS}, #scale[0.75]{#it{Preliminary}}")
else:
    l.DrawLatex(0.13,.88,"#bf{CMS}, #scale[0.75]{#it{Simulation}}")
l.SetTextSize(0.03)
l.SetTextAlign(31)
l.DrawLatex(0.89,.91,"35.9 fb^{-1} (13 TeV)")

#draw legend
leg = ROOT.TLegend(0.65,.55,.88,.88)
leg.SetFillStyle(0)
leg.SetBorderSize(0)

for idx in range(0, len(list_exp) ) :
	label = "expected"
	if opts.label !="":
		label = opts.label.split(',')[idx]
	leg.AddEntry(list_exp[idx], label, "L" )
	
	if idx==0:
		leg.AddEntry(list_oneSigma[idx], "1 s.d.","FL") 
		leg.AddEntry(list_twoSigma[idx], "2 s.d.","FL") 

##### PRINT TABLE LATEX
doTable=True
if doTable:
	tex=open(opts.outname +".tex","w")
	print>>tex, "\\begin{tabular}{lcccccc}"
	print>>tex, "\\hlinewd{1.2pt}"
	print>>tex, "\\multirow{2}{*}{$m_\\textup{H}$ [GeV]} & \\multicolumn{5}{c}{Expected Limits} & \multirow{2}{*}{Observed limit} \\\\"
	print>>tex, "\\cline{2-6}"
	print>>tex,"& $-2\\sigma$ & $-1\\sigma$ & median  & $1\\sigma$ & $2\\sigma$ & \\\\"
	print>>tex, "\\hline"
	for i in range(0,list_exp[0].GetN()):
		print>>tex, "%.0f"%list_exp[0].GetX()[i],"&",
		print>>tex, "%.2f"%(list_twoSigma[0].GetY()[i]-list_twoSigma[0].GetEYlow()[i]),
		print>>tex, "&",
		print>>tex, "%.2f"%(list_oneSigma[0].GetY()[i]-list_oneSigma[0].GetEYlow()[i]),
		print>>tex, "&",
		print>>tex, "%.2f"%list_exp[0].GetY()[i], ## median
		print>>tex, "&",
		print>>tex, "%.2f"%(list_oneSigma[0].GetY()[i]+list_oneSigma[0].GetEYhigh()[i]),
		print>>tex, "&",
		print>>tex, "%.2f"%(list_twoSigma[0].GetY()[i]+list_twoSigma[0].GetEYhigh()[i]),
		print>>tex, "&",
		if opts.unblind:
			print>>tex, "%.2f"%list_data[0].GetY()[i], ## data
		else:
			print>>tex, "-", ## nothing
		print>>tex, "\\\\"
	print>>tex, "\\hlinewd{1.2pt}"
	print>>tex, "\\end{tabular}"
########

#if opts.xsec:
#	leg.AddEntry(exp8TeV, "expected (8TeV)","L")
#	leg.AddEntry(obs8TeV, "observed (8TeV)","PL")

leg.Draw()

raw_input("Looks ok?")

c.SaveAs(opts.outname + ".pdf")
c.SaveAs(opts.outname + ".png")
