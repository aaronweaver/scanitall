# Import PyCheckMarx
import PyCheckmarx
import json
import stashy
import argparse

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

def scanStash(repoObj, cxURL, baseProject, testRun):
    stash = stashy.connect(repoObj["url"], repoObj["username"], repoObj["password"])
    for project in stash.projects:
    	projectName = project["name"]
    	pk = project_key = project["key"]

    	if scanProject(projectName, repoObj["include"], repoObj["exclude"]):
            print
            print "####################################"
            print "Stash Project: " + projectName
            print "####################################"

            for repo in stash.projects[project_key].repos.list():
            	for url in repo["links"]["clone"]:
                    href = url["href"]
                    if "ssh" in href:
                        print "CX Project Name: " + projectName + " " + repo["name"]
                        if testRun == False:
                            cxResult = pyC.scanProject(baseProject + projectName + " " + repo["name"], href, repoObj["sshkey"])
                            print "Successful: " + str(cxResult.IsSuccesfull)
                            print "Project ID: " + str(cxResult.ProjectID) + ", Scan ID: " + str(cxResult.RunId)
                            print "URL: " + cxURL + "CxWebClient/projectscans.aspx?id=" + str(cxResult.ProjectID)
                            print 

########## Begin ##########
parser = argparse.ArgumentParser()
parser.add_argument('--test', help='Run in test mode to verify settings are correct.')
args = parser.parse_args()

testMode = False

if args.test == "true":
    testMode = True

print "####################################"
print "Running in Test Mode: " + str(testMode)
print "####################################"
print

pyC = PyCheckmarx.PyCheckmarx()

with open(pyC.configPath + "config.json", "r") as outfile:
    repos = json.load(outfile)["repos"]
    for repo in repos:
        if repos[repo]["enabled"] == "True":
        	if repos[repo]["repoType"] == "stash":
        		scanStash(repos[repo], pyC.cxURL, pyC.baseProject, testMode)
        	else:
        		raise Exception("Repo type not supported.")
        else:
            print "Skipping repo: " + repo + " as it is not enabled in config."
