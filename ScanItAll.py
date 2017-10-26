#!/usr/bin/env python

"""ScanItAll.py: Imports specified repos from Stash, Bitbucket, Github into Checkmarx."""

__author__      = "Aaron Weaver"
__copyright__   = "Copyright 2017, Aaron Weaver"

import PyCheckmarx
import PyBitBucket
import json
import stashy
import argparse
from github import Github

#### Helper Functions ######
def scanProject(currentProject, includes, excludes):
	scanIt = False

	for include in includes.split(','):
		if currentProject == include or include == "*":
			scanIt = True
			#Check for any excludes
			for exclude in excludes.split(','):
				if exclude == currentProject:
					scanIt = False
					break
			break

	return scanIt

def checkmarxProject(cxURL, projectName, repoLink, sshkey, testRun):
	print
	print "####################################"
	print "Project: " + projectName
	print "####################################\n"
	print "CX Project Name: " + projectName + " " + repoLink

	if testRun == False:
		cxResult = pyC.scanProject(projectName, repoLink, sshkey)
		print "Successful: " + str(cxResult.IsSuccesfull)
		print "Project ID: " + str(cxResult.ProjectID) + ", Scan ID: " + str(cxResult.RunId)
		print "URL: " + cxURL + "CxWebClient/projectscans.aspx?id=" + str(cxResult.ProjectID)
		print "Repo: " + repoLink
		print

#### Repo Specific Implementations ######
def scanStash(repoObj, cxURL, baseProject, testRun):
    stash = stashy.connect(repoObj["url"], repoObj["username"], repoObj["password"])
    for project in stash.projects:
    	projectName = project["name"]
    	pk = project_key = project["key"]

    	if scanProject(projectName, repoObj["include"], repoObj["exclude"]):

            for repo in stash.projects[project_key].repos.list():
            	for url in repo["links"]["clone"]:
                    href = url["href"]
                    if "ssh" in href:
                        #Call Checkmarx and create or update the project
						checkmarxProject(cxURL, projectName + " " + repo["name"], href, repoObj["sshkey"], testRun)

def scanBitBucket(repoObj, cxURL, baseProject, testRun):
	bitbucket = PyBitBucket.PyBitBucket(repoObj["username"], repoObj["password"], debug=False)

	repos = None
	#Loop through the user repos
	for user in repoObj["usernames"]:
		repos = bitbucket.get_all_repos(repoObj["usernames"][user])

	for page in repos:
		for repo in repos[page]["values"]:
			projectName = repo["name"]

			if scanProject(projectName, repoObj["include"], repoObj["exclude"]):
				for link in repo["links"]["clone"]:
					if link["name"] == "ssh":
						repoLink = link["href"]

				#Call Checkmarx and create or update the project
				checkmarxProject(cxURL, repoObj["username"] + " " + projectName, repoLink, repoObj["sshkey"], testRun)

def scanGithub(repoObj, cxURL, baseProject, testRun):
	g = Github(repoObj["username"], repoObj["password"])

	# User repos
	for repo in g.get_user().get_repos():
		if scanProject(repo.name, repoObj["include"], repoObj["exclude"]):
			#Call Checkmarx and create or update the project
			checkmarxProject(cxURL, repo.name, repo.ssh_url, repoObj["sshkey"], testRun)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--test', help='Run in test mode to verify settings are correct.')
	args = parser.parse_args()

	msg = "Creating and/or Modifying Projects in Checkmarx."
	testMode = False

	if args.test == "true":
		testMode = True
		msg = "Running in  Test Mode. Projects won't be created in Checkmarx"

	print "################################################################"
	print msg
	print "################################################################"
	print

	pyC = PyCheckmarx.PyCheckmarx()

	with open(pyC.configPath + "config.json", "r") as outfile:
	    repos = json.load(outfile)["repos"]
	    for repo in repos:
	        if repos[repo]["enabled"] == "True":
				if repos[repo]["repoType"] == "stash":
					scanStash(repos[repo], pyC.cxURL, pyC.baseProject, testMode)
				elif repos[repo]["repoType"] == "bitbucket":
					scanBitBucket(repos[repo], pyC.cxURL, pyC.baseProject, testMode)
				elif repos[repo]["repoType"] == "github":
					scanGithub(repos[repo], pyC.cxURL, pyC.baseProject, testMode)
				else:
					print "Unsupported Repo: " + repos[repo]["repoType"]
	        else:
	            print "Skipping Repo: " + repo + " as it is not enabled in config.\n"
