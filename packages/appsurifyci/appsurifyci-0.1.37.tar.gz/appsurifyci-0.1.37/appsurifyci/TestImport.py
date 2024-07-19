import requests
import logging
import os
from http.client import HTTPConnection  # py3
import sys
import argparse
from urllib.parse import quote

importtype = "junit"

def urlencode(name):
    return quote(name, safe="")

parser = argparse.ArgumentParser(description='Sync a number of commits before a specific commit')

parser.add_argument('--url', type=str, required=False,
                    help='Enter your organization url')
parser.add_argument('--project', type=str, required=False,
                    help='Enter project name')
parser.add_argument('--apikey', type=str, required=False,
                    help='The API key to communicate with API')
parser.add_argument('--commit', type=str, required=False,
                    help='Enter the commit that would be the starter')
parser.add_argument('--report', type=str, required=False,
                    help='Enter the report.  Currently only supports a single file')
parser.add_argument('--branch', type=str, required=False,
                    help='Enter the explicity branch to process commit')
parser.add_argument('--testsuite', type=str, required=False,
                    help='Enter the testsuite')
parser.add_argument('--importtype', type=str, required=False,
                    help='Enter the import type junit or trx')
parser.add_argument('--vstestlocation', type=str, required=False,
                    help='Enter the import type junit or trx')
parser.add_argument('--vstestsearch', type=str, required=False, default='',
                    help='Enter the import type junit or trx')
parser.add_argument('--dll', type=str, required=False,
                    help='Enter the import type junit or trx')
parser.add_argument('--repo_name', type=str, required=False, default='',
                    help='Define repository name')


args = parser.parse_args()
#url = args.url.rstrip('/')
#project = args.project
#apikey = args.apikey
#commit = args.commit
#branch = args.branch
#filepath = args.report
#repository = args.repo_name
#testsuite = args.testsuite
#importtype = args.importtype
vstestlocation = args.vstestlocation
dll = args.dll
vstestsearch = args.vstestsearch

#testsuiteencoded = urlencode(testsuite)
#projectencoded = urlencode(project)
#testsuiteencoded = testsuite
#projectencoded = project



def testimport():

    
    cwd = os.getcwd()
    try:
        print("vs test location = ")

        if vstestsearch != "":
            os.chdir(vstestsearch)
            directories = os.listdir(os.getcwd())
            print(directories)
            directories.sort(reverse=True)
            print(directories)
            temploc = os.path.join(vstestsearch, directories[0])
            print(temploc)
            vstestlocation = os.path.join(temploc, "x64")
            
            print(vstestlocation)


        print(vstestlocation)
        #runcommand("cd\\")
        os.chdir(vstestlocation)
        #runcommand("cd "+vstestlocation)
        #runcommand("dir")
        print(os.listdir(os.getcwd()))
        commandToRun = (
            
            "vstest.console "
            + dll
            + " /ListFullyQualifiedTests /ListTestsTargetPath:testlist.txt"
        )
        
        runcommand(commandToRun)
        print("completed v1")
        commandToRun = (
            "vstest.console.exe "
            + dll
            + " /ListFullyQualifiedTests /ListTestsTargetPath:testlist.txt"
        )
        runcommand(commandToRun)
        print("completed v2")
    except Exception as e:
        print(e)
    os.chdir(cwd)
    print(os.listdir(os.getcwd()))

    #if vstestlocation.endswith('"'):
    #    vstestlocation = vstestlocation[:-1]
    #if not vstestlocation.endswith("\\"):
    #    if vstestlocation != "":
    #        vstestlocation = vstestlocation + "\\"
    #vstestlocation = '"' + vstestlocation + 'vstest.console"'
    #if vstestlocation == '"vstest.console"':
    #    vstestlocation = "vstest.console"
    #commandToRun = (
    #    vstestlocation
    #    + " "
    #    + dll
    #    + " /ListFullyQualifiedTests /ListTestsTargetPath:testlist.txt"
    #)
    #runcommand(commandToRun)

def runcommand(command, stream="false"):
    print("Running command " + command)
    print("platform = " + sys.platform)
    try:
        if stream == "true":
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                encoding="utf-8",
            )
            output = ""
            while True:
                # returns None while subprocess is running
                retcode = process.poll()
                line = process.stdout.readline()
                output = output + line
                print(line, end="")
                # yield line
                if retcode is not None:
                    break
            return output
        if stream == "false":
            result = subprocess.run(command, shell=True, capture_output=True)
            # subprocess.run(['ls', '-l'])stdout=subprocess.PIPE,
            print((result.stdout.decode("utf-8")))
            print((result.stderr.decode("utf-8")))
            return result.stdout.decode("utf-8")
    except Exception as ex:
        print(ex)



def testimportold():

    log = logging.getLogger('urllib3')
    log.setLevel(logging.DEBUG)

    # logging from urllib3 to console
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    log.addHandler(ch)

    # print statements from `http.client.HTTPConnection` to console/stdout
    HTTPConnection.debuglevel = 1
    print("importing results")
    print(filepath)

    sizeOfFile = os.path.getsize(filepath)

    apiurl = url + "/api/external/import/"

    payload = {
        "type": importtype,
        "commit": commit,
        "project_name": projectencoded,
        "test_suite_name": testsuiteencoded,
        "repo": repository,
        "import_type": "prioritized",
    }

    files = {
        "file": open(filepath, "rb"),
    }

    headers = {
        "token": apikey,
    }

    print(headers)
    print(payload)
    print(apiurl)

    response = requests.post(apiurl, headers=headers, data=payload, files=files)

    print("file import sent")
    if response.status_code >= 500:
        print(
            (
                "[!] [{0}] Server Error {1}".format(
                    response.status_code, response.content.decode("utf-8")
                )
            )
        )
    elif response.status_code == 404:
        print(("[!] [{0}] URL not found: []".format(response.status_code)))
    elif response.status_code == 401:
        print(("[!] [{0}] Authentication Failed".format(response.status_code)))
    elif response.status_code == 400:
        print(("[!] [{0}] Bad Request: Content: {1}".format(response.status_code, response.content)))
    elif response.status_code >= 300:
        print(("[!] [{0}] Unexpected Redirect".format(response.status_code)))
    elif response.status_code == 200 or response.status_code == 201:
        print("success")
    else:
        print(
            (
                "[?] Unexpected Error: [HTTP {0}]: Content: {1}".format(
                    response.status_code, response.content
                )
            )
        )

if __name__ == '__main__':
    testimport()