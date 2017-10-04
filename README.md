# Scanitall!

A python client to import all stash projects to Checkmarx SAST and will then begin immediately scanning those projects.

## Installation

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```
## Usage
Edit config/config.json.sample and save as config.json. Enter your Checkmarx server, credentials and then configure your stash server. For the Stash configuration there are two options to specify the projects to scan. If you enter a "*" for the include option then all projects will be scanned. You can additionally specify a project or projects to excluded by defining the project that you wish to exclude. For example: exclude="test,lab". Each include or exclude is a comma delimited list.

Once you have configured config.json then run the script in test mode.

```
python scanit.py --test=true
```

If you are satisfied with the results then run it again as follows:

```
python scanit.py
```

The results will look like this:
```
####################################
Running in Test Mode: False
####################################

Configuration Path: config/
http://cxweb/cxwebinterface/SDK/CxSDKWebService.asmx

####################################
Stash Project: Android
####################################
CX Project Name: Android App1
Successful: True
Project ID: 77, Scan ID: 346
URL: http://cxweb/CxWebClient/projectscans.aspx?id=77

CX Project Name: Android App2
Successful: True
Project ID: 78, Scan ID: 347
URL: http://cxweb/CxWebClient/projectscans.aspx?id=78
```
