import os,sys

## to compute versioning
import hashlib

## Hmm common configuration

class HmmConfig():
    ''' Hmm configuration for scripts. 
        All the scripts except the Analyzer can should take the configuration from here.
    '''
    def __init__(self):
        ## CATEGORIES and MAP ##
        self.muCategories=["BB","BO","BE","OO","OE","EE"]
        #self.procCategories= [ "VBF0","OneB","GF","VBF1","Untag0","Untag1"]
        self.procCategories= [ "VBF0","GF","VBF1","Untag0","Untag1"]
        self.categories=[]
        for muStr in self.muCategories:
              for catStr in self.procCategories:
                  self.categories.append(catStr+"_"+muStr);

        ### FIT ###
        self.xmin = 110
        self.xmax=150
        self.sig_mass_points=[120,125,130]
        self.processes=["GluGlu","VBF","ZH","WPlusH","WMinusH","ttH"]
        self.sigfit_gaussians={}
        #self.sigfit_gaussians[("Untag0_BB","GluGlu")] = 3
        #self.scale ={} #("cat","proc") = mean, sigma

        for p in ["GluGlu","ZH","WPlusH","WMinusH"]: # all except vbf
            self.sigfit_gaussians[("VBF0_EE",p)] = 2  ## 25
            self.sigfit_gaussians[("GF_EE",p)] = 2  ## 26

        self.sigfit_gaussians[("GF_BE","GluGlu")] = 2  ## 11
        self.sigfit_gaussians[("VBF0_OE","GluGlu")] = 2  ## 20
        self.sigfit_gaussians[("VBF0_OE","WMinusH")] = 2  ## 20
        self.sigfit_gaussians[("Untag1_EE","WMinusH")] = 2  ## 29

        self.sigfit_gaussians[("GF_OE","ttH")] = 1  ## 20
        self.sigfit_gaussians[("VBF0_EE","ttH")] = 1  ## 25
        self.sigfit_gaussians[("GF_EE","ttH")] = 1  ## 26
        self.sigfit_gaussians[("VBF1_EE","ttH")] = 1  ## 27
        self.sigfit_gaussians[("Untag0_EE","ttH")] = 1  ## 28
        self.sigfit_gaussians[("Untag1_EE","ttH")] = 1  ## 29

        self.sigfit_scale_unc = {} ## cat, proc -> value or (cat,proc)
        self.sigfit_smear_unc = {}
        
        #self.readScaleUnc()        

        ## DATACARD specific ##

        self.datacard_procs=['BKG','GluGlu','VBF','WPlusH','WMinusH','ttH','ZH']

        ##BKG functions after bias
        self.bkg_functions=[]
    
        self.computeVersioning()

    def SimpleScaleAndSmear(self):
        cat0=0
        proc0='GluGlu'
        for cat in range(0,len(self.categories)):
            for proc in self.processes:
                if cat==cat0 and proc==proc0:
                    self.sigfit_scale_unc[cat,proc]=0.0005
                    self.sigfit_smear_unc[cat,proc]=0.1
                else:
                    self.sigfit_scale_unc[cat,proc]=(cat0,proc0)
                    self.sigfit_smear_unc[cat,proc]=(cat0,proc0)

    def catToStr(self,num):
        return self.categories[num]

    def computeVersioning(self):
        catInputs=",".join(self.categories)
        catInputs+=";"+",".join(self.muCategories)
        catInputs+=";"+",".join(self.procCategories)
        catInputs+=";"+",".join(self.processes)
        self.catVersion=hashlib.md5(catInputs).hexdigest()
        fitInputs=catInputs
        fitInputs+=";"+",".join(["%d"%x for x in self.sig_mass_points])
        fitInputs+=";"+",".join(self.processes);
        fitInputs+=";"+",".join([cat+"_"+proc+"=%d"%self.sigfit_gaussians[(cat,proc)] for cat,proc in self.sigfit_gaussians ])
        #fitInputs += ';' + ",".join(["m%.5f-s%.5f"%self.scale[(cat,proc)] for cat,proc in self.scale])
        fitInputs += ';' + ",".join([str(self.sigfit_scale_unc[(cat,proc)]) for cat,proc in self.sigfit_scale_unc])
        fitInputs += ';' + ",".join([str(self.sigfit_smear_unc[(cat,proc)]) for cat,proc in self.sigfit_smear_unc])
        self.fitVersion=hashlib.md5(fitInputs).hexdigest()

    def Print(self):
        print "--- Hmm Configurator ---"
        print "Name:",self.__class__.__name__
        for x in ["xmin","xmax","muCategories","procCategories","categories","sig_mass_points","processes","datacard_procs","sigfit_scale_unc","sigfit_smear_unc","catVersion","fitVersion","bkg_functions"]:
            print x+"=",eval("self."+x)
        print "------------------------"
        print "125: BR",self.br(125)
        print "   : ggH",self.xsec('ggH',125),"qqH",self.xsec('qqH',125.),'WPlusH',self.xsec('WPlusH',125),"WMinusH",self.xsec("WMinusH",125.),"ZH",self.xsec('ZH',125),"ttH",self.xsec('ttH',125)
        print "------------------------"

    def br(self,mass=125):
        ''' only 125 '''
        brStore={
            "120.00":2.4230E-04,
            "120.50":2.4010E-04,
            "121.00":2.3780E-04,
            "121.50":2.3550E-04,
            "122.00":2.3310E-04,
            "122.50":2.3070E-04,
            "123.00":2.2820E-04,
            "123.50":2.2560E-04,
            "124.00":2.2300E-04,
            "124.10":2.2240E-04,
            "124.20":2.2190E-04,
            "124.30":2.2140E-04,
            "124.40":2.2080E-04,
            "124.50":2.2030E-04,
            "124.60":2.1980E-04,
            "124.70":2.1920E-04,
            "124.80":2.1870E-04,
            "124.90":2.1810E-04,
            "125.00":2.1760E-04,
            "125.09":2.1710E-04,
            "125.10":2.1700E-04,
            "125.20":2.1650E-04,
            "125.30":2.1590E-04,
            "125.40":2.1530E-04,
            "125.50":2.1480E-04,
            "125.60":2.1420E-04,
            "125.70":2.1370E-04,
            "125.80":2.1310E-04,
            "125.90":2.1250E-04,
            "126.00":2.1190E-04,
            "126.50":2.0920E-04,
            "127.00":2.0610E-04,
            "127.50":2.0320E-04,
            "128.00":2.0020E-04,
            "128.50":1.9710E-04,
            "129.00":1.9400E-04,
            "129.50":1.9090E-04,
            "130.00":1.8770E-04,
            }
        if "%.2f"%mass in brStore:
            return brStore["%.2f"%mass]
        else: 
            raise ValueError

    def xsec(self,type,mass=125):
        ''' mass: ggH, VBF,WPlusH,WMinusH,ZH,ttH  '''

        xsecStore = { # mass: ggH, VBF,WPlusH,WMinusH,ZH,ttH
                "120.00":( 5.222E+01,3.935E+00,9.558E-01,6.092E-01,9.939E-01,5.697E-01),
                "120.50":( 5.184E+01,3.919E+00,9.439E-01,6.007E-01,9.829E-01,5.625E-01),
                "121.00":( 5.146E+01,3.904E+00,9.320E-01,5.925E-01,9.705E-01,5.568E-01),
                "121.50":( 5.108E+01,3.888E+00,9.201E-01,5.845E-01,9.591E-01,5.502E-01),
                "122.00":( 5.071E+01,3.873E+00,9.091E-01,5.765E-01,9.485E-01,5.438E-01),
                "122.50":( 5.035E+01,3.858E+00,8.971E-01,5.693E-01,9.371E-01,5.375E-01),
                "123.00":( 4.998E+01,3.842E+00,8.843E-01,5.618E-01,9.266E-01,5.315E-01),
                "123.50":( 4.963E+01,3.827E+00,8.725E-01,5.544E-01,9.157E-01,5.259E-01),
                "124.00":( 4.927E+01,3.812E+00,8.611E-01,5.466E-01,9.051E-01,5.193E-01),
                "124.10":( 4.920E+01,3.809E+00,8.591E-01,5.455E-01,9.037E-01,5.179E-01),
                "124.20":( 4.913E+01,3.806E+00,8.569E-01,5.439E-01,9.008E-01,5.167E-01),
                "124.30":( 4.906E+01,3.803E+00,8.548E-01,5.429E-01,8.988E-01,5.161E-01),
                "124.40":( 4.899E+01,3.800E+00,8.527E-01,5.415E-01,8.964E-01,5.143E-01),
                "124.50":( 4.892E+01,3.797E+00,8.500E-01,5.395E-01,8.943E-01,5.132E-01),
                "124.60":( 4.885E+01,3.794E+00,8.487E-01,5.386E-01,8.923E-01,5.122E-01),
                "124.70":( 4.878E+01,3.791E+00,8.462E-01,5.372E-01,8.902E-01,5.115E-01),
                "124.80":( 4.871E+01,3.788E+00,8.442E-01,5.360E-01,8.884E-01,5.100E-01),
                "124.90":( 4.864E+01,3.785E+00,8.419E-01,5.345E-01,8.858E-01,5.086E-01),
                "125.00":( 4.858E+01,3.782E+00,8.400E-01,5.328E-01,8.839E-01,5.071E-01),
                "125.09":( 4.852E+01,3.779E+00,8.380E-01,5.313E-01,8.824E-01,5.065E-01),
                "125.10":( 4.851E+01,3.779E+00,8.377E-01,5.313E-01,8.819E-01,5.060E-01),
                "125.20":( 4.844E+01,3.776E+00,8.355E-01,5.298E-01,8.800E-01,5.052E-01),
                "125.30":( 4.837E+01,3.773E+00,8.334E-01,5.282E-01,8.783E-01,5.043E-01),
                "125.40":( 4.830E+01,3.770E+00,8.313E-01,5.272E-01,8.767E-01,5.033E-01),
                "125.50":( 4.823E+01,3.767E+00,8.291E-01,5.259E-01,8.744E-01,5.023E-01),
                "125.60":( 4.816E+01,3.764E+00,8.270E-01,5.243E-01,8.728E-01,5.007E-01),
                "125.70":( 4.810E+01,3.761E+00,8.243E-01,5.230E-01,8.703E-01,4.993E-01),
                "125.80":( 4.803E+01,3.758E+00,8.224E-01,5.217E-01,8.690E-01,4.982E-01),
                "125.90":( 4.796E+01,3.755E+00,8.211E-01,5.202E-01,8.668E-01,4.971E-01),
                "126.00":( 4.789E+01,3.752E+00,8.184E-01,5.187E-01,8.649E-01,4.964E-01),
                "126.50":( 4.756E+01,3.738E+00,8.080E-01,5.123E-01,8.549E-01,4.909E-01),
                "127.00":( 4.723E+01,3.723E+00,7.987E-01,5.051E-01,8.446E-01,4.851E-01),
                "127.50":( 4.690E+01,3.708E+00,7.879E-01,4.988E-01,8.350E-01,4.799E-01),
                "128.00":( 4.658E+01,3.694E+00,7.785E-01,4.924E-01,8.255E-01,4.742E-01),
                "128.50":( 4.625E+01,3.680E+00,7.687E-01,4.862E-01,8.161E-01,4.689E-01),
                "129.00":( 4.594E+01,3.665E+00,7.593E-01,4.801E-01,8.073E-01,4.639E-01),
                "129.50":( 4.562E+01,3.651E+00,7.501E-01,4.738E-01,7.980E-01,4.586E-01),
                "130.00":( 4.531E+01,3.637E+00,7.414E-01,4.676E-01,7.899E-01,4.539E-01),
                }
        col=-1
        if type=="VBF" or type == "qqH" : col=1
        elif type == "WH" : col = 23 #return 1.373E+00
        elif type == "ZH": col=4
        elif type == "ggH" or type=="GluGlu": col=0
        elif type == "ttH": col=5
        elif type == "bbH" and mass==125 : return 4.880E-01
        elif type == "WMinusH": col=2
        elif type == "WPlusH": col=3

        if col<0 : raise ValueError

        if "%.2f"%mass in xsecStore:
            if col< 10:
                return xsecStore["%.2f"%mass][col]
            else:
                return xsecStore["%.2f"%mass][2] + xsecStore["%.2f"%mass][3] 

        else: 
            raise ValueError

    def lumi(self):
        return 35867

    #def readScaleUnc(self,f="Hmumu/syst/scale/scales.txt"):
    #    self.scale ={} #("cat","proc") = mean, sigma
    #    txt = open(f)
    #    for line in txt:
    #        info = line.split()[0]
    #        mean = float(line.split()[1])
    #        sigma = float(line.split()[2])
    #        procCat = info.split('_')[0]
    #        muCat   = info.split('_')[1]
    #        proc    = info.split('_')[2]
    #        cat = procCat +"_" + muCat
    #        self.scale[ (cat, proc) ] = (mean, sigma)

hmm=HmmConfig()

class HmmConfigAutoCat(HmmConfig):
    def __init__(self):
        HmmConfig.__init__(self)
        self.categories=[ "cat%d"%x for x in range(0,13)]
        self.procCategories=[]
        self.muCategories=[]
        self.sigfit_gaussians={}
        #self.readScaleUnc()        
        self.SimpleScaleAndSmear()
        self.computeVersioning()

hmmAutoCat =HmmConfigAutoCat()

class HmmConfigTTH(HmmConfigAutoCat):
    def __init__(self):
        HmmConfigAutoCat.__init__(self)
        self.categories=[ "ttHHadr","ttHLep" ]
        self.computeVersioning()

class HmmConfigWithTTH(HmmConfigAutoCat):
    def __init__(self):
        HmmConfigAutoCat.__init__(self)
        self.categories=[ "cat%d"%x for x in range(0,16)]
        self.computeVersioning()
        self.sigfit_gaussians[("cat1","GluGlu")] = 2  ## 11
        self.sigfit_gaussians[("cat14","GluGlu")] = 1  ## 11
        self.sigfit_gaussians[("cat15","GluGlu")] = 1  ## 11
        self.sigfit_gaussians[("cat14","VBF")] = 1  ## 11
        self.sigfit_gaussians[("cat15","VBF")] = 1  ## 11
        self.sigfit_gaussians[("cat14","WPlusH")] = 1  ## 11
        self.sigfit_gaussians[("cat15","WPlusH")] = 1  ## 11
        self.sigfit_gaussians[("cat14","WMinusH")] = 1  ## 11
        self.sigfit_gaussians[("cat15","WMinusH")] = 1  ## 11
        self.sigfit_gaussians[("cat14","ZH")] = 2  ## 11
        self.sigfit_gaussians[("cat15","ZH")] = 1  ## 11
        self.sigfit_gaussians[("cat1","ttH")] = 2  ## 11
        self.sigfit_gaussians[("cat1","ttH")] = 3  ## 11

        self.bkg_functions=["zmod2_cat0_ord5","exp_cat1_ord3","zmod2_cat2_ord5","exp_cat3_ord3","zmod2_cat4_ord5","zmod_cat5_ord1","zmod2_cat6_ord5","zmod2_cat7_ord5","zmod2_cat8_ord5","zmod2_cat9_ord5","zmod_cat10_ord1","zmod_cat11_ord1","zmod2_cat12_ord5","zmod_cat13_ord1","bern2_cat14_ord4","bern2_cat15_ord5"]
        

hmmTTH =HmmConfigTTH()
hmmWithTTH =HmmConfigWithTTH()

if __name__=="__main__":
    hmm.Print()
    hmmAutoCat.Print()
    hmmTTH.Print()

import ROOT
from array import array
class QuantileMapping:
    ''' Compute quantile mapping of h-> cumulative fractions'''
    def __init__(self):
        self.base_=None
        self.nbins=20
        self.xmin=0
        self.xmax=1
        self.boundaries=[]
        self.verbose_=0

    def SetBase(self,base):
        self.base_=base.Clone(base.GetName() + "_CumulativeDistribution")
        nbins_orig=self.base_.GetNbinsX()
        norm= base.Integral(1,nbins_orig)
        for i in range(0,nbins_orig):
            self.base_.SetBinContent(i+1, base.Integral(1,i+1) / norm)

        ## compute bin for quantiles
        self.boundaries=[0] ## bondaries are meant as (i,i+1]
        n=1
        for i in range(0,nbins_orig):
            ibin=i+1
            if self.base_.GetBinContent(ibin) >= float(n)/self.nbins or ibin==nbins_orig:
                self.boundaries.append(ibin)
                n+=1
        ##
        if self.verbose_:
            print " --------- QUANTILE MAPPING DEBUG ----------"
            print "nbins=",self.nbins
            print "nbins_orig=",nbins_orig
            print "xmin=",self.xmin
            print "xmax=",self.xmax
            print "Boundaries: 0 ",
            for i in range(0,self.nbins):
                print self.boundaries[i+1],
            print
            print "NOMINAL   : X ",
            for i in range(0,self.nbins):
                print "%.2f"% ( 1./self.nbins),
            print
            print "CD        : X ",
            for i in range(0,self.nbins):
                print self.base_.GetBinContent(self.boundaries[i+1]),
            print
            print "INTEGRAL  : X ",
            for i in range(0,self.nbins):
                print base.Integral(self.boundaries[i] +1, self.boundaries[i+1]),
            print
            for i in range(0,self.nbins):
                if self.boundaries[i] +1 > self.boundaries[i+1]: print "ERROR in boundaries:",self.boundaries[i], self.boundaries[i+1]
            print " -------------------------------------------"
        ## exit
        return self

    def ConvertHist(self,h ):
        r = ROOT.TH1D( h.GetName() +"_QM",h.GetTitle(),self.nbins,self.xmin,self.xmax)
        for i in range(0,self.nbins):
            ibin=i+1
            #r.SetBinContent(ibin ,h.Integral( self.boundaries[i] +1 , self.boundaries[i+1] ))
            err=array('d',[0.])
            value=h.IntegralAndError(self.boundaries[i] +1 , self.boundaries[i+1],err)
            r.SetBinContent(ibin ,value)
            r.SetBinError(ibin ,err[0])
        for att in ['MarkerColor','LineColor','MarkerStyle','LineStyle','LineWidth','FillColor','FillStyle' ]:
            exec( "r.Set" + att +"( h.Get" + att+ "() )" )
        # axis attributes
        for att in ['Title','TitleOffset','TitleFont','TitleSize','LabelFont','LabelSize' ]:
            exec( "r.GetXaxis().Set" + att +"( h.GetXaxis().Get" + att+ "() )" )
            exec( "r.GetYaxis().Set" + att +"( h.GetYaxis().Get" + att+ "() )" )
        r.GetXaxis().SetRangeUser(0.0001,1-0.0001)
        return r

    def ConvertPoint(self,val):
        b= self.base_.FindBin(val)
        return self.base_.GetBinContent(b)

    def Apply( self,h):
        return self.ConvertHist(h)


class Stack:
    ''' This is a soft version of thstack that usually crash'''
    def __init__(self):
        self.hists_=[]
        self.draw_ =[]
        self.name_="myStack"

    def SetName(self,name):
        self.name_ = name

    def Add(self,h,draw=True):
        if len(self.hists_) == 0:
            self.hists_.append( h.Clone(self.name_ +"_"+h.GetName()) )
        else:
            self.hists_.append( h.Clone(self.name_ +"_"+h.GetName()) )
            self.hists_[-1].Add(self.hists_[-2])
        self.draw_.append(draw)

    def Draw(self,opts=""):
        firstDraw=True
        for idx in reversed(range(0,len(self.hists_))):
            h= self.hists_[idx]
            if not self.draw_[idx]: continue
            if firstDraw or 'SAME' in opts: 
                h.Draw(opts)
                firstDraw=False
            else       : 
                h.Draw(opts +" SAME")
                firstDraw=False
    def GetHist(self):
        return self.hists_[-1]

    def GetFirstHist(self):
        return self.hists_[0]

    def Delete(self):
        for h in self.hists_: h.Delete()
        self.hists_=[]

    def Remap(self,qm):
        hists2=[]
        for h in self.hists_:
            hists2.append(qm.Apply(h) )
        self.hists_ = hists2[:]

    def Print(self):
        print "------",self.name_,"-----------"
        for h in self.hists_:
            print "*",h.GetName()
        print "-------------------------------"



import re
class StringToCpp():
    def __init__(self):
        ## string cut to c-cut
        self.map={'bdt_score':'bdt[0]',
                'dimu_avg_abs_eta':'mu_ave_eta',
                'dimu_max_abs_eta':'mu_max_eta',
                }
        self.operator={'gt':'>=','lt':'<'}
    def parse_(self,string,result={}):
        if string =="" : return result
        op= string.split('_')[0]
        if op not in self.operator:
            opStr= '?'
        else:
            opStr=self.operator[op]
        
        newstring = '_'.join(string.split('_')[1:])
        var="???"
        value=0.00

        for key in self.map:
            if re.match(key,newstring): ## beginning of the line
                var = self.map[key]
                newstring = re.sub('^'+key+'_','',newstring)
                valueStr =newstring.split('_')[0]
                newstring = '_'.join(newstring.split('_')[1:] )
                newValueStr=re.sub('n','-',re.sub('p','.',valueStr))
                #print "DEBUG: converting for",var,opStr,"->",newValueStr
                value = float (newValueStr) 
        if var=='???': raise ValueError 
        if (var,opStr) in result:
            if opStr == '>=' or opStr=='>':
                if value >= result[(var,opStr)]: result[(var,opStr)]=value
            if opStr == '<' or opStr== "<=":
                if value <= result[(var,opStr)]: result[(var,opStr)]=value
        else:
            result[(var,opStr)] = value
        return self.parse_(newstring,result)

    def Parse(self,string):  
        result= self.parse_(string,{}) 
        l = []
        for  var,opStr in result:
            l.append( var +" "+opStr+ " " +"%.3f"%result[(var,opStr)] )
        return "if ( " + ' and '.join(l) + " )"

    def ParseAll(self):
        cat="icat"
        print self.Parse("lt_bdt_score_0p400_lt_bdt_score_0p050_lt_bdt_score_n0p400"),cat,"=",0,";"
        print self.Parse("lt_bdt_score_0p400_gt_bdt_score_0p050_gt_dimu_max_abs_eta_0p900_gt_bdt_score_0p250_gt_dimu_max_abs_eta_1p900"),cat,"=",1,";"
        print self.Parse("lt_bdt_score_0p400_lt_bdt_score_0p050_gt_bdt_score_n0p400_gt_dimu_max_abs_eta_1p900"),cat,"=",2,";"
        print self.Parse("gt_bdt_score_0p400_lt_bdt_score_0p730_lt_bdt_score_0p650_gt_dimu_max_abs_eta_0p900_gt_dimu_max_abs_eta_1p900"),cat,"=",3,";"
        print self.Parse("lt_bdt_score_0p400_gt_bdt_score_0p050_lt_dimu_max_abs_eta_0p900_lt_bdt_score_0p250"),cat,"=",4,";"
        print self.Parse("lt_bdt_score_0p400_gt_bdt_score_0p050_lt_dimu_max_abs_eta_0p900_gt_bdt_score_0p250"),cat,"=",5,";"
        print self.Parse("lt_bdt_score_0p400_gt_bdt_score_0p050_gt_dimu_max_abs_eta_0p900_gt_bdt_score_0p250_lt_dimu_max_abs_eta_1p900"),cat,"=",6,";"
        print self.Parse("lt_bdt_score_0p400_gt_bdt_score_0p050_gt_dimu_max_abs_eta_0p900_lt_bdt_score_0p250"),cat,"=",7,";"
        print self.Parse("lt_bdt_score_0p400_lt_bdt_score_0p050_gt_bdt_score_n0p400_lt_dimu_max_abs_eta_1p900"),cat,"=",8,";"
        print self.Parse("gt_bdt_score_0p400_lt_bdt_score_0p730_gt_bdt_score_0p650"),cat,"=",9,";"
        print self.Parse("gt_bdt_score_0p400_lt_bdt_score_0p730_lt_bdt_score_0p650_gt_dimu_max_abs_eta_0p900_lt_dimu_max_abs_eta_1p900"),cat,"=",10,";"
        print self.Parse("gt_bdt_score_0p400_lt_bdt_score_0p730_lt_bdt_score_0p650_lt_dimu_max_abs_eta_0p900"),cat,"=",11,";"
        print self.Parse("gt_bdt_score_0p400_gt_bdt_score_0p730"),cat,"=",12,";"

        #print self.Parse("gt_bdt_score_0p395_gt_bdt_score_0p727_gt_dimu_avg_abs_eta_1p954"),cat,"=",0,";"
        #print self.Parse("lt_bdt_score_0p395_lt_bdt_score_0p051_lt_bdt_score_n0p399"),cat,"=",1,";"
        #print self.Parse("lt_bdt_score_0p395_gt_bdt_score_0p051_gt_dimu_max_abs_eta_0p915_gt_bdt_score_0p246_gt_dimu_max_abs_eta_1p902"),cat,"=",2,";"
        #print self.Parse("lt_bdt_score_0p395_lt_bdt_score_0p051_gt_bdt_score_n0p399_gt_dimu_max_abs_eta_1p965"),cat,"=",3,";"
        #print self.Parse("gt_bdt_score_0p395_lt_bdt_score_0p727_lt_bdt_score_0p645_gt_dimu_max_abs_eta_0p917_gt_dimu_max_abs_eta_1p787"),cat,"=",4,";"
        #print self.Parse("lt_bdt_score_0p395_lt_bdt_score_0p051_gt_bdt_score_n0p399_lt_dimu_max_abs_eta_1p965_lt_bdt_score_n0p115"),cat,"=",5,";"
        #print self.Parse("lt_bdt_score_0p395_lt_bdt_score_0p051_gt_bdt_score_n0p399_lt_dimu_max_abs_eta_1p965_gt_bdt_score_n0p115"),cat,"=",6,";"
        #print self.Parse("lt_bdt_score_0p395_gt_bdt_score_0p051_lt_dimu_max_abs_eta_0p915_lt_bdt_score_0p261"),cat,"=",7,";"
        #print self.Parse("gt_bdt_score_0p395_lt_bdt_score_0p727_lt_bdt_score_0p645_gt_dimu_max_abs_eta_0p917_lt_dimu_max_abs_eta_1p787_lt_bdt_score_0p527"),cat,"=",8,";"
        #print self.Parse("gt_bdt_score_0p395_lt_bdt_score_0p727_lt_bdt_score_0p645_gt_dimu_max_abs_eta_0p917_lt_dimu_max_abs_eta_1p787_gt_bdt_score_0p527"),cat,"=",9,";"
        #print self.Parse("lt_bdt_score_0p395_gt_bdt_score_0p051_lt_dimu_max_abs_eta_0p915_gt_bdt_score_0p261"),cat,"=",10,";"
        #print self.Parse("lt_bdt_score_0p395_gt_bdt_score_0p051_gt_dimu_max_abs_eta_0p915_gt_bdt_score_0p246_lt_dimu_max_abs_eta_1p902"),cat,"=",11,";"
        #print self.Parse("lt_bdt_score_0p395_gt_bdt_score_0p051_gt_dimu_max_abs_eta_0p915_lt_bdt_score_0p246"),cat,"=",12,";"
        #print self.Parse("gt_bdt_score_0p395_lt_bdt_score_0p727_gt_bdt_score_0p645"),cat,"=",13,";"
        #print self.Parse("gt_bdt_score_0p395_lt_bdt_score_0p727_lt_bdt_score_0p645_lt_dimu_max_abs_eta_0p917"),cat,"=",14,";"
        #print self.Parse("gt_bdt_score_0p395_gt_bdt_score_0p727_lt_dimu_avg_abs_eta_1p954"),cat,"=",15,";"
        return 




