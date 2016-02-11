import arcpy,os

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [Tool]

class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
       	# First parameter
    	param0 = arcpy.Parameter(
        displayName="Input Features",
        name="in_features",
        datatype="GPFeatureLayer",
        parameterType="Required",
        direction="Input")

        param1 = arcpy.Parameter(
        displayName="Output Name",
        name="out_feature_class",
        datatype="GPString",
        parameterType="Required",
        direction="Output")

        params = [param0,param1]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        arcpy.Buffer_analysis(in_features=parameters[0], out_feature_class=parameters[1],
                                buffer_distance_or_field="500 Meters",
                                line_side="FULL",
                                line_end_type="ROUND",
                                dissolve_option="NONE",
                                dissolve_field="",
                                method="PLANAR")

        return

#############################################
## main function
## Purpose: TESTING in Pyscripter
#############################################
def main():

    if (os.path.basename(sys.executable).lower() != 'python.exe'):
        return

    myTool = Tool()
    parameters = myTool.getParameterInfo()
    parameters[0] = r"D:\Projecten\ArcPy - Python\Samples\GTFS\GTFS.gdb/Stops"
    parameters[1] = r"D:\Projecten\ArcPy - Python\Samples\GTFS\GTFS.gdb/Stops_Buffer"

    myTool.execute(parameters,None)

if __name__ == '__main__':
    main()

