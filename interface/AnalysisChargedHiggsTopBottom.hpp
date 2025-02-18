#ifndef CHARGEDHIGGSTOPBOTTOM_H
#define CHARGEDHIGGSTOPBOTTOM_H
#include "interface/AnalysisBase.hpp"
#include "interface/CutSelector.hpp"
#include "interface/GetBinning.hpp"
#include <memory>

#include "interface/Output.hpp" // DataStore
#include "TMVA/Reader.h"
#include "TMVA/Tools.h"

class ChargedHiggsTopBottom:  virtual public AnalysisBase
{
public:

    ChargedHiggsTopBottom() : AnalysisBase () {}
    virtual ~ChargedHiggsTopBottom () {}

    bool doSynch = false;
    bool doICHEP = false;
    bool writeTree = false;
    bool doSplit = false;

    // Analysis type
    bool do1lAnalysis=false;
    bool do2lAnalysis=false;
    bool doTaulAnalysis=false;

    // trigger bits
    bool passTriggerMu=true;
    bool passTriggerEle=true;

    bool passTriggerMuEle=true;
    bool passTriggerMuMu=true;
    bool passTriggerEleEle=true;


    void Init() override;

    void SetLeptonCuts(Lepton *l) override ;
    void SetJetCuts(Jet*j) override;
    void SetTauCuts(Tau*t) override;

    void BookCutFlow(string l, string category);
    void BookHisto(string l, string category, string phasespace);
    void BookFlavor(string l, string category, string phasespace, string flavor, string SR);
    void Preselection();

    // function with various plots
    void jetPlot(Event*e, string label, string category, string systname, string jetname);
    void leptonPlot(Event*e, string label, string category, string systname, string phasespace);
    void eventShapePlot(Event*e, string label, string category, string systname, string phasespace);
    void classifyHF(Event*e, string label, string category, string systname, string jetname, string SR);
    void leptonicHiggs(Event*e, string label, string systname, TLorentzVector b1, TLorentzVector b2, TLorentzVector p4W, string combination);

    void computeVar(Event*e);

    void printSynch(Event*e, string category);

    double genInfoForWZ(Event*e);
    int genInfoForBKG(Event*e);
    bool genInfoForSignal(Event*e);

    // function for the mini-tree
    void setTree(Event*e, string label, string  category);

    int analyze(Event*,string systname) override;
    const string name() const override {return "ChargedHiggsTopBottom";}

    // Variables for MVA
    template<class T>
    void SetVariable( string name, T value){ varValues_.Set(name, value); }
    void AddVariable( string name, char type, int r);
    void AddSpectator( string name, char type, int r);

    vector<string> weights;


private:


    std::unique_ptr<GetBinning> binLow_;
    std::unique_ptr<GetBinning> binMedium_;
    std::unique_ptr<GetBinning> binHigh_;

    CutSelector cut;

    enum CutFlow{ Total=0,
                  OneLep,
                  NoSecondLep,
                  NoTau,
                  Met,
                  Mt,
                  NJets,
                  NB,
                  MaxCut
    };

    Lepton* leadLep=NULL;
    Lepton* trailLep=NULL;

    double evt_HT=-1;
    double evt_ST=-1;
    double evt_DRlbmaxPt=-1;

    double evt_minDRbb=-1;
    double evt_minDRbb_invMass=-1;

    double evt_minDRlb_invMass=-1;
    double evt_minDRlb=-1;

    double evt_minMasslb=99999;

    double evt_avDRBB=-1;

    double evt_DEtaMaxBB=-1;
    double evt_DEtaMaxJJ=-1;
    double evt_MJJJmaxPt=-1;
    double evt_AvDRJJJmaxPt=-1;
    double evt_AvCSVPt=0;

    double evt_MT=-1;
    double evt_MT2bb=-1;
    double evt_MT2bb1l=-1;
    double evt_DRl1b1=-1;
    double evt_Ml1b1=-1;

    double evt_DRl1j1=-1;
    double evt_DRl1j2=-1;
    double evt_DRl1j3=-1;

    // these are defined only for 2l
    double evt_DRl2b1=-1;
    double evt_MT2ll=-1;
    double evt_MTmin=-1;
    double evt_MTmax=-1;
    double evt_MTtot=-1;

    double evt_HemiMetOut=0;
    double evt_C=0;
    double evt_FW2=0;

    vector<float> bdt;

    int nGenB = 0 ;
    int genLepSig = 0 ;

    /////
    /////

    GenParticle * bAss=NULL;
    GenParticle * bFromTopH=NULL;
    GenParticle * bFromTopAss=NULL;
    GenParticle * topFromH=NULL;
    GenParticle * bFromH=NULL;
    GenParticle * leptonFromTopH=NULL;
    GenParticle * WFromTopH=NULL;
    GenParticle * WFromTopAss=NULL;
    GenParticle * leptonTopAssH=NULL;

    /////
    /////

    DataStore varValues_;

    //
    //TMVA::Reader *reader_ ;
    vector<TMVA::Reader*> readers_;


};

#endif
// Local Variables:
// mode:c++
// indent-tabs-mode:nil
// tab-width:4
// c-basic-offset:4
// End:
// vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 
