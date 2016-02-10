import requests
from Security import Username,Password
import datetime
_token =""


def main():
    LogMessage("this starts realy fast")

    token = GetToken()
    queryUrl = "http://services2.arcgis.com/YDRnp3rdop6mVcUC/arcgis/rest/services/RotatingItems8/FeatureServer/0/query"

    params = {"where":"1=1","returnCountOnly":True, "f":"json","token":token}

    r = requests.post(queryUrl,params)
    
    result = r.json()

    LogMessage(result)


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
