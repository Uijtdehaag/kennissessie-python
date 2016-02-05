####################################################################
## ARCGIS ONLINE HELPER FUNCTIONS
## SEE REST APIs on https://developers.arcgis.com/documentation/
####################################################################
import urllib
import json
import time
import sys

class AGOLHelper(object):
    """
    ArcGIS Online handler class.
      -Generates and keeps tokens
      -template JSON feature objects for point
    """

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token, self.http, self.expires= self.getToken(username, password)

    def getToken(self, username, password, exp=60):  # expires in 60minutes
        """Generates a token."""
        referer = "http://www.arcgis.com/"
        query_dict = {'username': username,
                      'password': password,
                      'referer': referer}

        query_str = urllib.urlencode(query_dict)
        url = "https://www.arcgis.com/sharing/rest/generateToken"
        token = json.loads(urllib.urlopen(url + "?f=json", query_str).read())

        if "token" not in token:
            print(token['error'])
            sys.exit(1)
        else:
            httpPrefix = "http://www.arcgis.com/sharing/rest"
            if token['ssl'] is True:
                httpPrefix = "https://www.arcgis.com/sharing/rest"
            return token['token'], httpPrefix, token['expires']



    def send_AGOL_Request(self,URL, query_dict, returnType=False):
        """
        Helper function which takes a URL and a dictionary and sends the request.
        returnType values =
             False : make sure the geometry was updated properly
             "JSON" : simply return the raw response from the request, it will be parsed by the calling function
             else (number) : a numeric value will be used to ensure that number of features exist in the response JSON
        """

        query_str = urllib.urlencode(query_dict)

        # send a post message
        jsonResponse = urllib.urlopen(URL, urllib.urlencode(query_dict))
        file = jsonResponse.read()

##    try:
##    except:

        jsonOuput = json.loads(file)


        if returnType == "JSON":
            return jsonOuput

        if not returnType:
            if "error" in jsonOuput:
                print("Error: {0} {}".format(jsonOuput),URL)
                return False

            if "updateResults" in jsonOuput:
                try:
                    for updateItem in jsonOuput['updateResults']:
                        if updateItem['success'] is True:
                            #print("updateResults request submitted successfully")
                            return True
                        if updateItem['success'] is False:
                            print("No results update: {0}\n\n{1}\n\n{2}\n\n".format(updateItem,query_dict,URL))
                except:
                    print("Error: {0} {}".format(jsonOuput),URL)
                    return False

            if "addResults" in jsonOuput:
                try:
                    #print jsonOuput['addResults']
                    for addItem in jsonOuput['addResults']:
                        if addItem['success'] is True:
                            #print("addResults request submitted successfully")
                            return True
                        if addItem['success'] is False:
                            print("No results added: {0}\n\n{1}\n\n{2}\n\n".format(updateItem,query_dict,URL))
                except:
                    print("Error: {0} {1}".format(jsonOuput,URL))
                    return False

            if "deleteResults" in jsonOuput:
                try:
                    for deleteItem in jsonOuput['deleteResults']:
                        if deleteItem['success'] is True:
                            #print("addResults request submitted successfully")
                            return True
                except:
                    print("Error: {0} {1}".format(jsonOuput),URL)
                    return False


        else:  # Check that the proper number of features exist in a layer
            if len(jsonOuput['features']) != returnType:
                print("FS layer needs seed values")
                return False

        return True


    def queryFeatures(self, urlFeatureService,where,layer='0'):

        url = urlFeatureService + "/{}".format(layer)+"/query"

        query_dict = {
            "f": "json",
            "where": where,
            "outFields": "*",
            "token": self.token
        }

        # Check 1 point exists in the point layer (0), if not, add a value
        return self.send_AGOL_Request(url, query_dict,"JSON")



    def addFeatures(self, urlFeatureService, features,layer='0'):
        """Use a URL and features values to add Features."""

        url = urlFeatureService + "/{}".format(layer)+"/addFeatures"
        try:
            # Always updates point #1.
            submitData = {
                "features": features,
                "f": "json",
                "token": self.token
            }

            bOK = self.send_AGOL_Request(url, submitData)

        except:
            print("couldn't add features")
            return False

        return bOK

    def updateFeatures(self, urlFeatureService, features,layer='0'):
        """Use a URL and features values to update an existing point."""
        url = urlFeatureService + "/{}".format(layer)+"/updateFeatures"

        try:
            #print "XXX "+features+ "XXX"
            # Always updates point #1.
            submitData = {
                "features": features,
                "f": "json",
                "token": self.token
            }

            bOK = self.send_AGOL_Request(url, submitData)

        except:
            print("couldn't update features")
            return False

        return bOK

    def deleteFeatures(self, urlFeatureService,where,layer='0'):
        #try:
        url = urlFeatureService + "/{}".format(layer)+"/deleteFeatures"
        ptData = {
            "where": where,
            "f": "json",
            "token": self.token
        }

        bOK =self.send_AGOL_Request(url, ptData)

       # except:
         #   print("could not delete features")
         #   return False


        return bOK