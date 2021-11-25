#!/bin/bash 

#STOP HADOOP
sh script/stopHadoop.sh

#STOP OPENSCORING SERVER
pkill -f openscoring-server-executable-2.0.5.jar

#DELETING [opt FOLDER (it's created when chrome security is turned off chrome security -> see runProject.sh)
rm -r \[opt

