import os
import time
import datetime
import argparse
import uuid
import subprocess
import sys
import tempfile
import getpass
import pwd
import grp
from os.path import expanduser
from DirectoryUtils import cd

def buildDocker( dockername, dirname):
	print "Building docker ... " + dockername + " .. @" + dirname
	with cd(dirname):
		os.system("docker build -t "+ dockername + " .")
	return dockername
	
def runDocker(dockername, prompt=""):
	currentdir = os.path.abspath(os.getcwd())
	uid = os.getuid()
	username = getpass.getuser()
	username = username.split()[0]
	groupid = pwd.getpwnam(username).pw_gid
	groupname = grp.getgrgid(groupid).gr_name
	groupname = groupname.split()[0]
	homedir = expanduser("~")
	print "Running docker " + dockername + " as Userid: " + str(uid) + "(" + username +"), + Group:"+str(groupid) + "("+groupname+") at " + homedir
	dirname = tempfile.mkdtemp()
	wname = os.path.join(dirname,"run.sh")
	fw = open( wname, "w+" )
	fw.write("#!/bin/bash\n")
	fw.write("addgroup --force-badname --gid "+str(groupid)+" " +groupname+"\n")
	fw.write("adduser --force-badname --home " + homedir + " --shell /bin/bash --no-create-home --uid " + str(uid)+ " -gecos '' "+username+" --disabled-password --gid "+str(groupid)+"\n" )
	fw.write("adduser "+username +" sudo\n")
	fw.write("adduser "+username +" docker\n")
	fw.write("echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers\n")
	fw.write("chmod --recursive 0755 /root\n")
	fw.write("export HOME="+homedir+"\n")
        #fw.write("echo $PATH\n")
        #fw.write("export PATH=$PATH:$GOPATH/bin\n")
        #fw.write("echo $PATH\n")
	fw.write("cd "+currentdir+"\n")
	fw.write("dockerd > /dev/null 2>&1 &\n")
	#fw.write("su -m "+username +"\n")
        fw.write("$SHELL\n")
	fw.close()
	os.chmod(wname, 0755)
	if prompt == "":
		hostname = "Docker["+dockername+"]"
	else:
		hostname = prompt
	if homedir in currentdir:
		cmd = "docker run --privileged --hostname " + hostname + " --rm -ti -v " + homedir + ":"+homedir + " -v "+dirname+ ":/tmp/runcommand -w "+homedir + " " + dockername + " /tmp/runcommand/run.sh"
	else:
		cmd = "docker run --privileged --hostname " + hostname + " --rm -ti -v " + homedir + ":"+homedir + " -v "+ currentdir + ":" + currentdir + " -v "+dirname+ ":/tmp/runcommand -w "+homedir + " " + dockername + " /tmp/runcommand/run.sh"
	print "Execute: " + cmd
	os.system(cmd)
	
def findDockers( dockername):
	print "Search for dockers .... "+dockername
	tmpf = tempfile.NamedTemporaryFile()
	tmpfname = tmpf.name; 
	tmpf.close()
	#os.remove(tmpfname)
	dockerimages_all = os.system("docker images > " + tmpfname)
	with open(tmpfname,"r") as dockerimage_file:
		lines = dockerimage_file.readlines()
	os.remove(tmpfname)
	numlines = len(lines)
	matchdockers = []
	for i in range(2,numlines):
		imageinfo = lines[i].split()
		imagename = imageinfo[0]+":"+imageinfo[1]
		if dockername in imagename:
			matchdockers.append(imagename)
	return matchdockers
