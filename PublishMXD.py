import arcpy
import requests
import os
import xml.dom.minidom as DOM
from Security import Username,Password


mxdPath = r"D:\Temp\PartnerSessie\RotatingItems.mxd"
serviceName = "RotatingItems8"
serviceSummary = "A Summary"
serviceTags ="TAG1,TAG2"
_token=""

def main():
    
    dir,mxdName = os.path.split(mxdPath)
        
    sdDraftFile = os.path.join(dir,serviceName + "HostedMS.sddraft")
    sdDraftFile2 = os.path.join(dir,serviceName + "HostedMSNew.sddraft")
    serviceDefinitionFile = os.path.join(dir,serviceName + ".sd")


    LogMessage("1. Opening MXD")
    mxd = arcpy.mapping.MapDocument(mxdPath)
    
    LogMessage("2. Creating SD Draft")
    arcpy.mapping.CreateMapSDDraft(mxd, sdDraftFile, serviceName, 'MY_HOSTED_SERVICES', summary=serviceSummary, tags=serviceTags)
    for i in xrange(0, arcpy.GetMessageCount()):
        LogMessage(arcpy.GetMessage(i))

    LogMessage("3. Set SD Draft settings")
    SetSDDraftSettings(sdDraftFile,sdDraftFile2)

    LogMessage("4. StageService")
    try:
        os.remove(serviceDefinitionFile)
    except OSError:
        pass
    arcpy.StageService_server(sdDraftFile2, serviceDefinitionFile)
    for i in xrange(0, arcpy.GetMessageCount()):
        LogMessage(arcpy.GetMessage(i))

    LogMessage("5. Upload ServiceDefinition")
    sdItemid = UploadSD2ArcGISOnline(serviceDefinitionFile,serviceName,serviceSummary,serviceTags)    

    LogMessage("6. Publish Service")
    result = PublishServiceFromDefinition(sdItemid,serviceName)

    print result
    LogMessage("Script complete")

def SetSDDraftSettings( origSDDRaftFile, newSDDraftFile, maxRecordCount=1000):
    LogMessage("SetSDDraftSettings::Start")
    # Read the sddraft xml.
    doc = DOM.parse(origSDDRaftFile)
    # Change service from map service to feature service
    typeNames = doc.getElementsByTagName('TypeName')
    for typeName in typeNames:
        # Get the TypeName we want to disable.
        if typeName.firstChild.data == "MapServer":
            typeName.firstChild.data = "FeatureServer"

    #Turn off caching
    configProps = doc.getElementsByTagName('ConfigurationProperties')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "isCached":
                    # turn on caching
                    keyValue.nextSibling.firstChild.data = "false"

    #set max recordcount
    #propSets =  doc.getElementsByTagName('PropertySetProperty')
    #for propSet in propSets:
    #    keyValues = propSet.childNodes
    #    for keyValue in keyValues:
    #        if keyValue.tagName == 'Key':
    #            if keyValue.firstChild.data == "maxRecordCount":
    #                # turn on caching
    #                keyValue.nextSibling.firstChild.data = maxRecordCount


    #Turn on feature access capabilities
    configProps = doc.getElementsByTagName('Info')[0]
    propArray = configProps.firstChild
    propSets = propArray.childNodes
    for propSet in propSets:
        keyValues = propSet.childNodes
        for keyValue in keyValues:
            if keyValue.tagName == 'Key':
                if keyValue.firstChild.data == "WebCapabilities":
                    # turn on caching
                    keyValue.nextSibling.firstChild.data = "Query,Create,Update,Delete,Uploads,Editing"

    descriptions = doc.getElementsByTagName('Type')
    for desc in descriptions:
        if desc.parentNode.tagName == 'SVCManifest':
            if desc.hasChildNodes():
                desc.firstChild.data = "esriServiceDefinitionType_Replacement"


    f = open(newSDDraftFile, 'w')
    doc.writexml( f )
    f.close()


def UploadSD2ArcGISOnline(sdFile, serviceName, serviceSummary, serviceTags):
    
    updateURL = "http://www.arcgis.com/sharing/rest/content/users/{}/addItem".format(Username)
    
    filesUp = {"file": open(sdFile, 'rb')}

    token = GetToken()
    url = updateURL + "?f=json&token="+token+ \
        "&filename="+sdFile+ \
        "&type=Service Definition"\
        "&title="+serviceName+ \
        "&tags="+serviceTags+\
        "&description="+serviceSummary

    LogMessage("Start uploading {} to Arcgis Online".format(sdFile))
    response = requests.post(url, files=filesUp);
    itemPartJSON = response.json()

    if "success" in itemPartJSON:
        itemPartID = itemPartJSON['id']
        LogMessage("new ID: {}".format(itemPartID))
        return itemPartID
    else:
        LogMessage("\n.sd file not uploaded. Check the errors and try again.\n")
        LogMessage(response.text)
        raise Exception(response.text)

def PublishServiceFromDefinition(sdItemid, serviceName):

    publishURL = 'http://www.arcgis.com/sharing/rest/content/users/{}/publish'.format(Username)

    pubParams ='{"name":"'+serviceName+ '"}'

    query_dict = {'itemID': sdItemid,
                'filetype': 'serviceDefinition',
                'publishParameters':pubParams}
    

    jsonResponse = SendRequest(publishURL, query_dict)

    LogMessage("successfully updated...{}...".format(jsonResponse['services']))

    jobid = jsonResponse["services"][0]["jobId"]
    serviceItemId = jsonResponse["services"][0]["serviceItemId"]

    jobstatus = "processing"

    while jobstatus=="processing":
        response=""
        try:
            url = "http://www.arcgis.com/sharing/rest/content/users/{}/items/{}/status".format(Username,serviceItemId)

            query_dict = {'jobid': jobid,
                      'jobtype': "publish"}

            response = SendRequest(url,query_dict)

            jobstatus =  response["status"]
            
        except Exception as e:
            LogMessage("Error in getting jobstatus {} {}".format(response),e.message )

        LogMessage("Status for service {} - job {} is {}".format(serviceName,jobid,jobstatus))
        if jobstatus!= "completed":
            time.sleep(5)

    returnObject = dict()

    if len(jsonResponse["services"])==1:
        returnObject["featureserviceID"] =serviceItemId
        returnObject["featureserviceUrl"] = jsonResponse["services"][0]["serviceurl"]
    else:
        LogMessage("Featureservice search with name {} does not have 1 result, resultcount = {}".format(featureServiceName,len(jsonResponse["services"])))
    return returnObject



def SendRequest(url, params):
       
        token = GetToken()
        url = url + "?token=" +token+ "&f=json"
        
        r = None
    
        try:
            if params==None:
                r = requests.get(url,timeout=120)
            else:
                r = requests.post(url,params,timeout=120)
            r.raise_for_status()
        except Exception as e:    
            LogMessage("===ERROR Sending Request: {}".format(e))

        return r.json()

def GetToken():
    
    global _token
    if _token == "":
        # Get token
        LogMessage("Getting new token")
        hostname = 'http://www.arcgis.com'
        token_URL = 'https://www.arcgis.com/sharing/generateToken'
        token_params = {'username':Username,'password': Password,'referer': hostname,'f':'json','expiration':60}
        
        r = requests.post(token_URL,token_params)
        token_obj= r.json()
       
        _token = token_obj['token']
        expires = token_obj['expires']

        expireDate = datetime.datetime.fromtimestamp(int(expires)/1000)

        LogMessage("new token: {}".format(_token))
        LogMessage("token expires: {}".format(expireDate))
    return _token
       
def LogMessage(msg):
    fullMsg ="{0} - {1}".format(datetime.datetime.now().strftime('%Y%m%d-%H:%M:%S'),msg) 
    print fullMsg
    

if __name__=="__main__":
    main()
