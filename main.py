from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

def folderCreator(path):
    if os.path.isdir(path):
        return path
    else:
        os.mkdir(path)
        return path
    
def missionDirectory(basePath,paramList):
    missionDirectoryPath = os.path.join(basePath,'_'.join(paramList))
    folderCreator(missionDirectoryPath)
    return missionDirectoryPath

def syncJson(basePath):
    return

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
    return missionType,missionTypeShort,craftType,craftTypeShort, craftPassDict

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

@app.get("/mission", response_class=HTMLResponse)
async def folderize(request: Request, incident:str='NaN',team:str='NaN',mission:str='0000',squad:str='00',folderCode:str='000',missionGlobalId:str='00000000-0000-0000-0000-000000000000'):
    basePath = folderCreator(r"C:\DSAR_Data")
    missionType,missionTypeShort,craftType,craftTypeShort,craftPassDict = parseFolderCode(folderCode)
    paramList = [incident,team,"Mission-"+mission,"Squad-"+squad,missionTypeShort]
    missionDirectoryPath = missionDirectory(basePath,paramList)
    initialFlight = findFlights(missionDirectoryPath)


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