##Imports necesarry libraries/modules
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json

##identifies the app as a FastAPI application
app = FastAPI()

##identfies that the "static" folder in the directory contains static files needed at runtime
app.mount("/static", StaticFiles(directory="static"), name="static")

##ifentifies that the index.html found in the "templates" folder are the templates we want linked together with this application
templates = Jinja2Templates(directory="templates")

##basic folder creation function with a check for overwrite conflicts
def folderCreator(path):
    if os.path.isdir(path):
        return path
    else:
        os.mkdir(path)
        return path

##basic function to generate a set base folder path for each mission by linking all URL parameters in one string with "_" in between each parameter
def missionDirectory(basePath,paramList):
    missionDirectoryPath = os.path.join(basePath,'_'.join(paramList))
    folderCreator(missionDirectoryPath)
    return missionDirectoryPath

##function that never got created, the idea was to create another endpoint that allowed the user to push up a .json file (MissionCraft.json) with edits, and given the right permissions, push a personalized, edited version of the json file to an AWS repo. This would have led to the need for another function and endpoint that others could go to,
##enter a unique ID for that json file, and have the app reach out to the AWS bucket, use that ID to find that json file, and overwrite the MissionCraft.json file on their own local machine (essentially a way to modify and share modifications to tailor the application more easily)
def syncJson(basePath):
    return

##function to take a folder code (3 digit number) and generate a series of variables needed by utiliizing the MissionCraft.json, simplifying/automating the process to only require on URL parameter to generate a wider set of data variables
def parseFolderCode(folderCode):
    missionTypeId = str(folderCode[0])
    craftTypeId = str(folderCode[1:])
    with open('MissionCrafts.json') as f:
        data = json.load(f)
    missionType = data[missionTypeId]["title"]
    missionTypeShort = data[missionTypeId]["abbr"]
    craftPassDict = {}
    for craft in data[missionTypeId]["crafts"]:
        craftPassDict.update({data[missionTypeId]["crafts"][craft]["name"]:[str(missionTypeId)+str(craft),data[missionTypeId]["crafts"][craft]["name"],data[missionTypeId]["crafts"][craft]["shortName"]]})
    craftType = data[missionTypeId]["crafts"][craftTypeId]["name"]
    craftTypeShort = data[missionTypeId]["crafts"][craftTypeId]["shortName"]
    return missionType,missionTypeShort,craftType,craftTypeShort,craftPassDict

##function to identify the current mission's directory. Each mission creates a folder, and each flight for each mission creates a folder in that mission folder. To ensure that each folder is unique, this function generates the next sequential flight number and appends it to the folder name for that flight folder
def findFlights(missionDirectoryPath):
    folderList = []
    maxFlight = 0
    for folder in os.listdir(missionDirectoryPath):
        if os.path.isdir(os.path.join(missionDirectoryPath, folder)):
            if folder[0] and folder[3]:
                folderList.append(folder)
                flightNum = int(folder[6:8])
                if flightNum > maxFlight:
                    maxFlight = flightNum
    maxFlight += 1
    return str(maxFlight).zfill(2)

##first endpoint of the FastAPI application. takes a series of URL parameters and runs through the functions listed above and below to generate MISSION folders in the C:/DSAR_data folder 
@app.get("/mission", response_class=HTMLResponse)
async def folderize(request: Request, incident:str='NaN',team:str='NaN',mission:str='0000',squad:str='00',folderCode:str='000',missionGlobalId:str='00000000-0000-0000-0000-000000000000'):
    basePath = folderCreator(r"C:\DSAR_Data")
    missionType,missionTypeShort,craftType,craftTypeShort,craftPassDict = parseFolderCode(folderCode)
    paramList = [incident,team,"Mission-"+mission,"Squad-"+squad,missionTypeShort]
    missionDirectoryPath = missionDirectory(basePath,paramList)
    initialFlight = findFlights(missionDirectoryPath)

    ##returns the template html file as a "landing page" for the application
    return templates.TemplateResponse(
        request=request, name="item.html", context={
            "missionDirectoryPath":missionDirectoryPath,
            "folderCode":folderCode,
            "initialFlight":initialFlight,
            "missionType":missionType,
            "craftType":craftType,
            "craftTypeShort": craftTypeShort,
            "craftPassDict":craftPassDict,
            "missionGlobalId":missionGlobalId})

##function to parse the folderCode paramter to generate a list of subfolders that the application can then go and create
def parseFolderCode_POST(folderCode):   
    missionTypeId = str(folderCode[0])
    craftTypeId = str(folderCode[1:])
    with open('MissionCrafts.json') as f:
        data = json.load(f)
    if missionTypeId == "4":
        if data[missionTypeId]["crafts"][craftTypeId]["processingFlag"] == 'Y':
            subFolders = data[missionTypeId]["folders"]
        else:
            subFolders = data[missionTypeId]["folders"][1:]
    else:
        subFolders = data[missionTypeId]["folders"]
    return subFolders

##second endpoint that uses the findFlights function to find the next sequential flight number and uses variables generated to define the flight subfolder structure to generate the folder structure specific to that's mission's flight.
@app.post("/newFlight")
async def newFlight(request: Request):
    body = await request.json()
    missionDirectoryPath = body["missionDirectoryPath"].replace('"','')
    folderCode = body["folderCode"].replace('"','')
    craftShortName = body["craftTypeShort"].replace('"','')
    maxFlight = findFlights(missionDirectoryPath)
    flightFolder = folderCreator(os.path.join(missionDirectoryPath,"Flight"+maxFlight+"_"+craftShortName).replace('"',''))
    subFolders = parseFolderCode_POST(folderCode)
    for folder in subFolders:
        folderCreator(os.path.join(flightFolder,folder))
    return JSONResponse(content={'nextFlight':str(int(maxFlight)+1).zfill(2)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False, log_config=None)
