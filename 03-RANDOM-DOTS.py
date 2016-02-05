############################################################################
# publish data to ArcGIS Online hosted feature service sample
#
# Author: Antoon Uijtdehaag, Esri Nederland bv
#
# Get your free developement en testing account at
# http://developers.arcgis.com
####################################################################
# Required python modules
import urllib, json, time, sys, os.path, datetime, random
import agol as ago

# Main program starts here
def addSomeRandomDots(username,password,fs_url):
    #create a list in case we add more then one feature
    addFeatureList= []

    # Initialize the AGOLHandler for token and feature service JSON templates
    con = ago.AGOLHelper(username, password)

    # Add new feature
    addFeature = {
                "attributes": {
                    "SHOUTOUT":"Hi there"
                },
                "geometry": {
                    "x": random.uniform(-180, 180),
                    "y": random.uniform(-90, 90),
                    "spatialReference" : {"wkid" : 4326}
                }
            }

    # add feature to the list
    addFeatureList.append(addFeature)

    # add all features to feature service
    if len(addFeatureList) > 0 and con.addFeatures(fs_url, json.dumps(addFeatureList)):
        print  "add {} features".format(len(addFeatureList) )


if __name__ == '__main__':
 # Add your credentials here
    username = ""
    password = ""
    fs_url = "http://services.arcgis.com/emS4w7iyWEQiulAb/arcgis/rest/services/RANDOMDOTS/FeatureServer"

    addSomeRandomDots(username,password,fs_url)