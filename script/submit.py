#!env python

import os,sys
from glob import glob
from subprocess import call, check_output
import re

from optparse import OptionParser, OptionGroup

usage = "usage: %prog [options]"
parser=OptionParser(usage=usage)
parser.add_option("-i","--input" ,dest='input',type='string',help="Input Configuration file",default="")
parser.add_option("-d","--dir" ,dest='dir',type='string',help="Directory where to write the configuration",default="submit")
parser.add_option("-v","--debug" ,dest='debug',type='int',help="Debug Verbosity. From 0-3. Default=%default",default=0)
parser.add_option("-n","--njobs" ,dest='njobs',type='int',help="Number of Job to submit",default=50)
parser.add_option("-q","--queue" ,dest='queue',type='string',help="Queue",default="1nh")

job_opts= OptionGroup(parser,"Job options:","these options modify the job specific")
job_opts.add_option("-t","--no-tar" ,dest='tar',action='store_false',help="Do not Make Tar",default=True)
job_opts.add_option("","--dryrun" ,dest='dryrun',action='store_true',help="Do not Submit",default=False)
job_opts.add_option("","--no-compress" ,dest='compress',action='store_false',help="Don't compress",default=True)
job_opts.add_option("","--compress"    ,dest='compress',action='store_true',help="Compress stdout/err")
job_opts.add_option("-m","--mount-eos" ,dest='mount',action='store_true',help="Mount eos file system.",default=False)
job_opts.add_option("","--hadoop" ,dest='hadoop',action='store_true',help="Use Hadhoop and MIT-T3",default=False)
job_opts.add_option("-c","--cp" ,dest='cp',action='store_true',help="cp Eos file locally. Do not use xrootd. ",default=False)
job_opts.add_option("","--nosyst" ,dest='nosyst',action='store_true',help="Do not Run Systematics",default=False)
job_opts.add_option("","--config" ,dest='config',action='append',type="string",help="add line in configuration",default=[])

hadd_opts=OptionGroup(parser,"Hadd options","these options modify the behaviour of hadd")
hadd_opts.add_option("","--hadd" ,dest='hadd',action='store_true',help="Hadd Directory.",default=False)
hadd_opts.add_option("","--clear" ,dest='clear',action='store_true',help="Clear Directory (used with hadd).",default=False)
hadd_opts.add_option("","--nocheck" ,dest='nocheck',action='store_true',help="Skip checking of log files in hadd. 'zcat log*.txt.gz| grei -i error' ",default=False)

summary= OptionGroup(parser,"Summary","these options are used in case of summary is wanted")
summary.add_option("-s","--status",dest="status", action='store_true', help = "Display status information for a submission. (Can be use with hadoop option)", default=False)
summary.add_option("","--resubmit",dest="resubmit", action='store_true', help = "Resubmit failed jobs. (no hadoop)", default=False)
summary.add_option("-j","--joblist",dest="joblist", type='string', help = "Resubmit this job list. '' or 'fail' will submit the failed jobs. 'run' will submit the running jobs. Job list = 3,5,6-10", default="")

parser.add_option_group(job_opts)
parser.add_option_group(hadd_opts)
parser.add_option_group(summary)

(opts,args)=parser.parse_args()

EOS='/afs/cern.ch/project/eos/installation/0.3.15/bin/eos.select'

if 'CMSSW_BASE' not in os.environ:
	print "-> Use a CMSSW environment: cmsenv"
	exit(0)

print "inserting in path cwd"
sys.path.insert(0,os.getcwd())
print "inserting in path cwd/python"
sys.path.insert(0,os.getcwd()+'/python')

## bash color string
red="\033[01;31m"
green = "\033[01;32m"
yellow = "\033[01;33m"
cyan = "\033[01;36m"
white = "\033[00m"

def PrintLine(list):
	''' convert list in list of int number, sort and compress consecutive numbers. Then print the result:
	4,5,8,3 -> 3-5,8
	'''
	nums = [ int(s) for s in list ]
	nums.sort()
	compress = []
	last = None
	blockinit = None

	for n in nums:
		#first if it is not consecutive
		if last == None: ## INIT
			blockinit = n

		elif last != n-1:
			#close a block and open a new one
			if last != blockinit:
				compress.append( str(blockinit) + "-" + str(last) ) 
			else:
				compress.append( str(last) ) 
			blockinit = n

		last = n

	#consider also the last number
	#close a block and open a new one
	if last != blockinit:
		compress.append( str(blockinit) + "-" + str(last) ) 
	else:
		compress.append( str(last) ) 

	return ",".join(compress)

def Print_ (done, run, fail, pend):
	'''Internal'''
	tot = len(run) + len(fail) + len(done) + len(pend)

	color = red
	if len(run) > len(fail) and len(run) >len(pend)  : color= yellow
	if len(pend) > len(run) and len(pend) >len(fail): color= cyan
	if len(done) == tot and tot >0 : color = green
	
	print " ----  Directory "+ color+opts.dir+white+" --------"
	print " Pend: " + cyan   + "%3d"%len(pend) + " / " + str(tot) + white + " : " + PrintLine(pend)  ###
	print " Run : " + yellow + "%3d"%len(run) + " / "  + str(tot) + white + " : " + PrintLine(run)  ### + ",".join(run)  + "|" 
	print " Fail: " + red    + "%3d"%len(fail) + " / " + str(tot) + white + " : " + PrintLine(fail) ### + ",".join(fail) + "|" 
	print " Done: " + green  + "%3d"%len(done) + " / " + str(tot) + white + " : " + PrintLine(done) ### + ",".join(done) + "|" 
	print " -------------------------------------"

def PrintSummary(dir, doPrint=True):
	''' Print summary informations for dir'''
	run  = glob(dir + "/*run")
	fail = glob(dir + "/*fail")
	done = glob(dir + "/*done")
	pend = glob(dir + "/*pend")

	run = [ re.sub('\.run','' , re.sub('.*/sub','', r) ) for r in run ] 	
	fail = [ re.sub('\.fail','' , re.sub('.*/sub','', r) ) for r in fail ] 	
	done = [ re.sub('\.done','' , re.sub('.*/sub','', r) ) for r in done ] 	
	pend = [ re.sub('\.pend','' , re.sub('.*/sub','', r) ) for r in pend ] 	

	if doPrint:
		Print_(done,run,fail,pend)

	return ( done, run, fail, pend)

def PrintHadhoop(dir, doPrint = True):
	log = glob ( dir + "/test.*.log" )
	done=[]
	run =[]
	fail=[]
	pend=[]
	for l in log:
		iJob = re.sub('.*/test\.','', re.sub("\.log","" , l ) )
		status = call( "cat %s | grep 'Job executing on host' >& /dev/null"%(l) , shell=True)
		if status != 0 :
			pend.append(iJob)
			continue
		status = call( "cat %s | grep 'Job terminated.' >& /dev/null"%(l) , shell=True)
		if status != 0:
			run.append(iJob)
			continue
		status = call( "cat %s | grep 'return value 0' >& /dev/null"%(l) , shell=True)
		if status != 0:
			fail.append(iJob)
			continue
		outlist = glob(dir +"/*_%s.root"%iJob)
		if len(outlist) != 1:
			print "unable to find outfile in:",outlist
			fail.append(iJob)
			continue
		outname=outlist[0]
		if os.stat(outname).st_size == 0:
			fail.append(iJob)
			continue
		done.append(iJob)
	
	if doPrint:
		Print_(done,run,fail,pend)
	return ( done, run, fail)

if opts.status:
	if opts.hadoop:
		PrintHadhoop(opts.dir,doPrint=True)
	else:
		( done, run, fail, pend) = PrintSummary(opts.dir,doPrint=True)
		cpu=[]
		termcpu=re.compile("TERM_CPULIMIT")
		for iJob in fail + run:
		    try:
		        log = open(opts.dir + "/log"+iJob+".txt")
		    except IOError: 
		        continue
		    if re.search("TERM_CPULIMIT",log.read() ) != None : cpu.append(iJob)
		    log.close()
		if len(cpu) >0 :
		    print " CPU LIMIT",PrintLine(cpu)
		    print " -------------------------------------"
		#if opts.fullstatus:
		notRunning=[]
		bjobs = check_output("bjobs -w",shell=True)
		for iJob in run+pend:
		    #test/Hmumu/Hmumu_2017_04_05_Bdt/Job_76
		    if not re.search( re.sub('//','/','%s/Job_%d\s'%(opts.dir,int(iJob))),bjobs):notRunning.append( iJob)
		    #cmd = "bjobs -w | grep '%s/Job_%d\>'"%(opts.dir,int(iJob))
		    #status = call(cmd,shell=True)
		    #if status != 0: notRunning.append( iJob)
		if len(notRunning) >0 :
		    print " NOT RUNNING! ",PrintLine(notRunning)
		    print " -------------------------------------"
	exit(0)

if opts.resubmit:
	( done, run, fail, pend) = PrintSummary(opts.dir,False)

	if opts.joblist == '' or opts.joblist.lower() == 'fail':
		joblist = fail
	elif opts.joblist.lower() =='run':
		joblist = run
	elif opts.joblist.lower() == 'pend' :
		joblist = pend
	elif opts.joblist.lower() == 'done' :
		joblist = done
	elif opts.joblist.lower() == 'all' :
		joblist = pend + run + fail + done
	else:
		joblist = opts.joblist.split(',')

	for job in joblist:
		if '-' in job: 
		   iBegin= int(job.split('-')[0])
		   iEnd = int(job.split('-')[1])
		else: 
		   iBegin= int(job)
		   iEnd = int(job)
	   	for iJob in range(iBegin,iEnd+1):
			#iJob= int(job)
			basedir = os.environ['PWD'] + "/" + opts.dir
			touch = "touch " + basedir + "/sub%d.pend"%iJob
			call(touch,shell=True)
			cmd = "rm " + basedir + "/sub%d.fail"%iJob + " 2>&1 >/dev/null"
			call(cmd,shell=True)
			cmd = "rm " + basedir + "/sub%d.run"%iJob + " 2>&1 >/dev/null"
			call(cmd,shell=True)
			cmd = "rm " + basedir + "/log%d.txt"%iJob + " 2>&1 >/dev/null"
			call(cmd,shell=True)
			cmdline = "bsub -q " + opts.queue + " -o %s/log%d.txt"%(basedir,iJob) + " -J " + "%s/Job_%d"%(opts.dir,iJob) + " %s/sub%d.sh"%(basedir,iJob)
			print cmdline
			call (cmdline,shell=True)
	exit(0)

if opts.hadd:
	filelist = glob(opts.dir + "/*.root")
	if opts.dir[-1] == '/':dir = opts.dir[:-1]
	else: dir  = opts.dir[:]

	if not opts.nocheck:
		cmd = "zcat %s/log*.txt.gz | grep -i error | sort | uniq -c "%dir
		st=call(cmd,shell=True)

		cmd = "zcat %s/log*.txt.gz | grep -i '\[error\]' > /dev/null "%dir
		st=call(cmd,shell=True)
		if st == 0 and opts.clear:
			print "-> Errors have been found. Refusing to clear"
			opts.clear = False
		cmd = "zcat %s/log*.txt.gz | grep -i warning | sort | uniq -c "%dir
		call(cmd,shell=True)

	name = re.sub('.*/','',dir)
	cmd = "[ -f %s%s.root ] && rm -v %s/%s.root"%(opts.dir,name,opts.dir,name) ## remove the file in oredr not to double count
	call(cmd,shell=True)
	cmd = "hadd -f %s/%s.root "%(opts.dir, name ) + " ".join(filelist)
	st=call(cmd,shell=True)

	if st !=0 :
		print "-> Unsuccessfull hadd. (in case refuse to clear). Removing created file."
		cmd="rm -v %s/%s.root "%(opts.dir, name )
		call(cmd,shell=True)
		opts.clear = False

	if opts.clear: 
		filelist = glob(opts.dir + "/*")
		rmlist = [ f for f in filelist if  re.sub('^.*/','',f) != name + ".root"]
		keeplist = [ f for f in filelist if re.sub('^.*/','',f) == name + ".root"]
		rmcmd = "rm " + " ".join(rmlist)
		#for i in rmlist:
		#	print i, "'"+re.sub('^.*/','',f) + "'", "'" + name + ".root'"
		print " I will keep = '",keeplist
		call(rmcmd,shell=True)
	exit(0)

# import Parser
from ParseDat import *
config=ParseDat(opts.input)

call("[ -d %s ] && rm -r %s"%(opts.dir,opts.dir),shell=True)
call("mkdir -p %s"%opts.dir,shell=True)
cmdFile=open("%s/submit_cmd.sh"%opts.dir,"w")
cmdFile.write("##Commands used to submit on batch. Automatic written by python/submit.py script\n")

if opts.tar:
	cmd=["tar","-czf","%s/package.tar.gz"%opts.dir]
	if True: ## copy also the bare library in the tar. for grid submission
		cmdBare = "mkdir -p ./bin/bare"
		call(cmdBare,shell=True)
		cmdBare = "cp " +os.environ["CMSSW_BASE"] + "/src/NeroProducer/Core/bin/libBare.so ./bin/bare/"
		call(cmdBare,shell=True)
		cmdBare = "cp " +os.environ["CMSSW_BASE"] + "/src/NeroProducer/Core/bin/dict_rdict.pcm ./bin/bare/"
		call(cmdBare,shell=True)
		## run time libraries needs also the .h files :(
		cmdBare = "mkdir -p ./bin/interface"
		call(cmdBare,shell=True)
		cmdBare = "cp " + os.environ["CMSSW_BASE"] + "/src/NeroProducer/Core/interface/*hpp ./bin/interface/"
		call(cmdBare,shell=True);
		### this file is produced by make
		#cmdBare = "cp bin/libChargedHiggs.so bin/libChargedHiggs.0.so"
		#call(cmdBare,shell=True)
		#cmdBare = "/afs/cern.ch/user/a/amarini/public/patchelf --set-rpath '' bin/libChargedHiggs.0.so"
		#call(cmdBare,shell=True)
	cmd.extend( glob("bin/bare/*" ) )
	cmd.extend( glob("bin/interface/*" ) )
	cmd.extend( glob("bin/*so" ) )
	cmd.extend( glob("bin/dict*" ) )
	#cmd.extend( glob("bin/tag.txt" ) )
	#cmd.extend( glob("dat/*dat" ) )
	#cmd.extend( glob("dat/*txt" ) )
	cmd.extend( glob("dat/*" ) )
	cmd.extend( glob("aux/*" ) )
	cmd.extend( glob("python/*py") )
	#cmd.extend( glob("test/*") )
	cmd.extend( glob("test/*py") )
	cmd.extend( glob("test/*C") )
	cmd.extend( glob("test/*.hpp") )
	cmd.extend( glob("test/*.cpp") )
	cmd.extend( glob("test/*.o") )
	cmd.extend( glob("test/*.so") )
	cmd.extend( glob("test/*.exe") )
	cmd.extend( glob("interface/*hpp" ) ) ## who is the genius that in ROOT6 need these at run time ? 
	tarCmdline = " ".join(cmd)
	print tarCmdline
	call(cmd)

	tarInfo = open("%s/tar.txt"%opts.dir,"w")
	print >> tarInfo, tarCmdline
	tarInfo.close()
	cmd="git rev-parse HEAD > %s/tag.txt" %opts.dir
	call(cmd,shell=True)
	cmd="git describe --tags >> %s/tag.txt" %opts.dir
	call(cmd,shell=True)
	cmd="git diff HEAD > %s/patch.txt" %opts.dir
	call(cmd,shell=True)

## expand *
if True:
	fileList=[]
	for f in config['Files']:
		list=[]
		if '/store/' or '/eos/user' in f:
			if opts.hadoop:
				list = FindHadoop( f ) 
			elif opts.mount:
				list =  FindEOS(f, "%%MOUNTPOINT%%/eos")
			else:
				list =  FindEOS(f)
		else :
			list=glob(f)
			if list == []: ### maybe remote ?
				list=f
		if len(list)==0:
			print "<*> Error in File list from",f,"-- No File Found"
			raise IOError
		fileList.extend(list)
	config['Files']=fileList
	splittedInput=chunkIt(config['Files'],opts.njobs )

if opts.hadoop:
   if len(fileList) ==0:
	print "filelist has 0 len: Nothing to be done"
	exit(0)
   redirect = ">&2"
   run= open("%s/run.sh"%opts.dir,"w")
   run.write("#!/bin/bash\n")
   run.write("JOBID=$1\n")
   run.write("source /cvmfs/cms.cern.ch/cmsset_default.sh\n")
   # if x509 proxy is copied to the workspace
   # export X509_USER_PROXY=x509up_u$(id -u)
   #use_x509userproxy = true
   run.write("scram p CMSSW %s\n"%os.environ['CMSSW_VERSION'])
   run.write("cd %s/src\n"%os.environ['CMSSW_VERSION'])
   run.write("eval `scram runtime -sh`\n")
   run.write("tar xzf ../../package.tar.gz\n")
   run.write("mkdir -p ../NeroProducer/Core/bin\n")
   run.write("cp -v bin/bare/* ../NeroProducer/Core/bin\n") 
   run.write("mkdir -p ../NeroProducer/Core/interface\n")
   run.write("cp -v bin/interface/* ../NeroProducer/Core/interface\n") 
   run.write('LD_LIBRARY_PATH=./:./bin/:$LD_LIBRARY_PATH\n')
   run.write("echo --- ENV ---- %s\n"%redirect)
   run.write("env | sed 's/^/ENV ---/' %s \n"%redirect)
   run.write("echo --- LS ---- %s\n"%redirect)
   run.write("ls -l | sed 's/^/LS ---/' %s\n"%redirect)
   #cmsRun cfg.py jobId=$JOBID
   run.write("python python/Loop.py -v -d ../../input${JOBID}.dat %s\n"%redirect)
   run.write('EXITCODE=$?\n')
   run.write("echo Finished At: %s\n"%redirect)
   run.write("date %s\n"%redirect)
   run.write("echo EXITCODE is $EXITCODE %s\n"%redirect)
   run.write("exit $EXITCODE\n")
   run.close()
   
   inputLs =[]
   subdir="."
   for iJob in range(0,opts.njobs):
        if len(splittedInput[iJob]) == 0 : 
             print "No file to run on for job "+ str(iJob)+"," + red + " will not send it!" + white
             continue
	outname = re.sub('.root','_%d.root'%iJob,config['Output'])
	dat=open("%s/input%d.dat"%(opts.dir,iJob),"w")
	inputLs.append("%s/input%d.dat"%(subdir,iJob))
	dat.write("include=%s\n"%opts.input)
	dat.write('Files=%s\n'%( ','.join(splittedInput[iJob]) ) )
	dat.write('Output=%s/%s\n'%(subdir,outname) )
	if opts.nosyst:
		dat.write("Smear=NONE\n")
	for l in opts.config:
		dat.write(l+"\n")
	dat.close()
   # create condor.jdl
   outname = re.sub('.root','_$(Process).root',config['Output'])
   condor=open("%s/condor.jdl"%opts.dir,"w")
   condor.write("executable = %s/run.sh\n"%subdir)
   condor.write("should_transfer_files = YES\n")
   condor.write("when_to_transfer_output = ON_EXIT\n")
   condor.write("transfer_input_files = %(dir)s/package.tar.gz,%(input)s\n"%{"dir":subdir,"input": ",".join(inputLs)})
   condor.write("universe = vanilla\n")
   condor.write("log = test.$(Process).log\n")
   condor.write("output = %s\n"%outname)
   condor.write("error = test.$(Process).err\n")
   condor.write("requirements = Arch == \"X86_64\" && OpSysAndVer == \"SL6\" && HasFileTransfer\n")
   condor.write("arguments = $(Process)\n")
   condor.write("use_x509userproxy = true\n") ## X509 should work
   condor.write("queue %d\n"%(len(inputLs)))
   condor.close()
   cmdFile.write("cd %s\n"%opts.dir)
   cmdFile.write("condor_submit condor.jdl\n")
   cmd ="cd %s && condor_submit condor.jdl"%opts.dir
   if not opts.dryrun: 
	status = call(cmd,shell=True)
	if status !=0:
		print "unable to submit,",cmd
   else:
	print cmd
		
##################### WRITE BATCH ###########################
if not opts.hadoop:
   for iJob in range(0,opts.njobs):
	sh=open("%s/sub%d.sh"%(opts.dir,iJob),"w")
	basedir=opts.dir
	if basedir[0] != '/': basedir=os.environ['PWD'] + "/" + opts.dir
	
	sh.write('#!/bin/bash\n')
	sh.write('[ "$WORKDIR" == "" ] && export WORKDIR="/tmp/%s/" \n'%(os.environ['USER']))
	sh.write('cd %s\n'%(os.getcwd() ) )
	sh.write('LD_LIBRARY_PATH=%s:$LD_LIBRARY_PATH\n'%os.getcwd())
	sh.write('eval `scramv1 runtime -sh`\n') # cmsenv

	if opts.tar:
		sh.write("mkdir -p $WORKDIR/%s_%d\n"%(opts.dir,iJob))
		sh.write("cd $WORKDIR\n")
		sh.write("ln -s %s_%d/interface ./"%(opts.dir,iJob))
		sh.write("cd $WORKDIR/%s_%d\n"%(opts.dir,iJob))
		#sh.write('LD_LIBRARY_PATH=${PWD}:${PWD}/bin:$LD_LIBRARY_PATH\n') ## TODO: test
		sh.write("tar -xzf %s/package.tar.gz\n"%(basedir ))
		sh.write("mkdir -p %s\n"%opts.dir)
		sh.write("cp %s/*dat %s/\n"%(basedir,opts.dir))

	touch = "touch " + basedir + "/sub%d.pend"%iJob
	call(touch,shell=True)
	cmd = "rm " + basedir + "/sub%d.run 2>&1 >/dev/null"%iJob + " 2>&1 >/dev/null"
	call(cmd,shell=True)
	cmd = "rm " + basedir + "/sub%d.done 2>&1 >/dev/null"%iJob + " 2>&1 >/dev/null"
	call(cmd,shell=True)
	cmd = "rm " + basedir + "/sub%d.fail 2>&1 >/dev/null"%iJob + " 2>&1 >/dev/null"
	call(cmd,shell=True)

	sh.write('date > %s/sub%d.run\n'%(basedir,iJob))
	sh.write('rm %s/sub%d.done 2>&1 >/dev/null\n'%(basedir,iJob))
	sh.write('rm %s/sub%d.pend 2>&1 >/dev/null\n'%(basedir,iJob))
	sh.write('rm %s/sub%d.fail 2>&1 >/dev/null\n'%(basedir,iJob))

	if opts.mount:
		#mountpoint = "~/eos"
		mountpoint = "$WORKDIR/%s_%d/eos"%(opts.dir,iJob)
		sh.write('%s -b fuse mount %s\n'% (EOS,mountpoint))

	if opts.cp:
		sh.write("mkdir cp\n")
		for idx,file in enumerate(splittedInput[iJob]):
			if 'root://eoscms//' in file: file = re.sub('root://eoscms//','', file)
			# -1 = filename , -2 = dirname
			filename = file.split('/')[-1] ## remove all directories
			dir = file.split('/')[-2]
			sh.write("mkdir ./cp/%s\n"%dir)
			sh.write('cmsStage %s ./cp/%s/\n'%(file,dir))
			splittedInput[iJob][idx] = "./cp/" + dir + "/" + filename


	if opts.debug>1:
		# after CD in the WORKDIR and mount
		sh.write('echo "-------- ENV -------"\n')
		sh.write("env \n") # print run time environment
		sh.write('echo "--------------------"\n')
		sh.write('echo "-------- LS -------"\n')
		sh.write("ls -lR\n")
		sh.write('echo "--------------------"\n')



	if opts.compress:
		compressString="2>&1 | gzip > %s/log%d.txt.gz"%(opts.dir,iJob)
	else: compressString =""

	sh.write('python python/Loop.py -v -d %s/input%d.dat %s\n'%(opts.dir,iJob,compressString))

	if opts.compress:
		sh.write('EXITCODE=${PIPESTATUS[0]}\n')
	else:
		sh.write('EXITCODE=$?\n')
	sh.write('rm %s/sub%d.run 2>&1 >/dev/null\n'%(basedir,iJob))
	sh.write('[ $EXITCODE == 0 ] && touch %s/sub%d.done\n'%(basedir,iJob))
	sh.write('[ $EXITCODE != 0 ] && echo $EXITCODE > %s/sub%d.fail\n'%(basedir,iJob))

	if opts.mount:
		sh.write('%s -b fuse umount %s\n'% (EOS,mountpoint))

	outname = re.sub('.root','_%d.root'%iJob,config['Output'])

	if opts.tar:
		if basedir != opts.dir : 
			sh.write("[ $EXITCODE == 0 ] && mv -v %s/%s %s/ || { echo TRANSFER > %s/sub%d.fail; rm %s/sub%d.done; }  \n"%(opts.dir,outname,basedir,basedir,iJob,basedir,iJob))
		if opts.compress:
			sh.write("mv %s/log%d.txt.gz %s/log%d.txt.gz\n"%(opts.dir,iJob,basedir,iJob) )
	sh.write('echo "Finished At:"\n')
	sh.write("date\n")
	
	dat=open("%s/input%d.dat"%(opts.dir,iJob),"w")
	dat.write("include=%s\n"%opts.input)
	dat.write(re.sub('%%MOUNTPOINT%%',"./", 'Files=%s\n'%( ','.join(splittedInput[iJob]) ) ))
	dat.write('Output=%s/%s\n'%(opts.dir,outname) )
	if opts.nosyst:
		dat.write("Smear=NONE\n")
	for l in opts.config:
		dat.write(l+"\n")

	## make the sh file executable	
	call(["chmod","u+x","%s/sub%d.sh"%(opts.dir,iJob)])

	## submit
	#sh.write('#$-N %s/Job_%d\n'%(opts.dir,iJob))
	cmdline = "bsub -q " + opts.queue + " -o %s/log%d.txt"%(basedir,iJob) + " -J " + "%s/Job_%d"%(opts.dir,iJob) + " %s/sub%d.sh"%(basedir,iJob)
	print cmdline
	cmdFile.write(cmdline+"\n")

	if len(splittedInput[iJob]) == 0 : 
		print "No file to run on for job "+ str(iJob)+"," + red + " will not send it!" + white
		continue
	if not opts.dryrun: 
		call(cmdline,shell=True)

