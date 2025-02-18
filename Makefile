GCC=g++
CXXFLAGS=`root-config --libs --cflags` -O2 -fPIC -I../  -I./
## to use BareObjects
RPATH= -Wl,-rpath=$(PWD)/../NeroProducer/Core/bin
CXXFLAGS += -L$(PWD)/../NeroProducer/Core/bin -lBare  -ggdb -lTMVA -l RooFit -l RooFitCore  -l Physics
SOFLAGS=-shared

SRCDIR=src
BINDIR=bin
HPPDIR=interface
AUXDIR=aux

SRC=$(wildcard $(SRCDIR)/*.cpp)
OBJ=$(patsubst $(SRCDIR)/%.cpp, $(BINDIR)/%.o , $(SRC)  )
HPPLINKDEF=$(patsubst $(SRCDIR)/%.cpp, ../interface/%.hpp , $(SRC)  )

.PHONY: all
all:
	$(info, "--- Full compilation --- ")	
	$(info, "-> if you want just to recompile something use 'make fast' ")	
	$(info, "------------------------ ")	
	$(MAKE) clean
	$(MAKE) libChargedHiggs.so
	$(MAKE) libChargedHiggs.0.so

.PHONY: fast
fast:
	$(MAKE) libChargedHiggs.so
	$(MAKE) libChargedHiggs.0.so

.PHONY: core
core:
	cd ../NeroProducer/Core && $(MAKE) 

# check if CMSSW is defined
ifndef CMSSW_BASE
$(info No CMSSSW !!!!)
$(info I ll sleep 3s to let you acknowledge it)
$(shell sleep 3s)
CXXFLAGS += -I/usr/include/python2.7 -lpython2.7
else
$(info CMSSW found: $(CMSSW_BASE) )
COMBINELIBFILE = $(wildcard $(CMSSW_BASE)/lib/$(SCRAM_ARCH)/libHiggsAnalysisCombinedLimit.so)
COMBINELIB = HiggsAnalysisCombinedLimit
COMBINELIBDIR = $(CMSSW_BASE)/lib/$(SCRAM_ARCH)/
CXXFLAGS += -I"/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/external/python/2.7.11-mlhled/include/python2.7"
CXXFLAGS += -D HAVE_PYTHIA -I/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/external/pythia8/219/include -L/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/external/pythia8/219/lib  -lpythia8
#-I/cvmfs/cms.cern.ch/$(SCRAM_ARCH)/external/clhep/2.2.0.4-kpegke/include
#"-lpythia8 -lclhep "
endif

# check if Combine is present and compiled 
ifeq ("$(COMBINELIBFILE)", "") 
$(info No Combine Package found)
else
$(info Using combine: $(COMBINELIB))
CXXFLAGS += -L$(ROOFITSYS)/lib -lRooFit -lRooFitCore -I$(ROOFITSYS)/include
CXXFLAGS += -D HAVE_COMBINE -L$(COMBINELIBDIR) -l$(COMBINELIB) 
RPATH += -Wl,-rpath=$(COMBINELIBDIR)
endif

libChargedHiggs.so: $(OBJ) Dict | $(BINDIR)
	$(GCC) $(CXXFLAGS) $(RPATH) $(SOFLAGS) -o $(BINDIR)/$@ $(OBJ) $(BINDIR)/dict.o

libChargedHiggs.0.so: $(OBJ) Dict | $(BINDIR)
	$(GCC) $(CXXFLAGS) $(SOFLAGS) -o $(BINDIR)/$@ $(OBJ) $(BINDIR)/dict.o

$(OBJ) : $(BINDIR)/%.o : $(SRCDIR)/%.cpp interface/%.hpp | $(BINDIR)
	$(GCC) $(CXXFLAGS) $(RPATH) -c -o $(BINDIR)/$*.o $<

.PHONY: Dict
Dict: $(BINDIR)/dict.o

$(BINDIR)/dict.o: $(SRC) | $(BINDIR)
	genreflex $(SRCDIR)/classes.h -s $(SRCDIR)/classes_def.xml -o $(BINDIR)/dict.cc --deep --fail_on_warnings --rootmap=$(BINDIR)/dict.rootmap --rootmap-lib=libChargedHiggs.so -I interface/ -I../
	$(GCC) -c -o $(BINDIR)/dict.o $(CXXFLAGS) $(RPATH) -I interface $(BINDIR)/dict.cc
	#cd $(BINDIR) && rootcint -v4 -f dict.cc -c -I../../ -I../  $(HPPLINKDEF)  ../interface/LinkDef.hpp 
	#cd $(BINDIR) && $(GCC) -c -o dict.o $(CXXFLAGS) $(RPATH) -I../../ dict.cc

$(BINDIR):
	mkdir -p $(BINDIR)
	mkdir -p $(AUXDIR)

.PHONY: clean
clean:
	-rm $(OBJ)
	-rm $(BINDIR)/dict*
	-rm $(BINDIR)/libChargedHiggs.so
	-rmdir $(BINDIR)
