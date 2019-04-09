'''This tool creates service areas around points using ArcGIS Online ServiceAreas service'''

import os
import sys
import time

import arcpy

def import_service(service_name, username="annzhang_MIT", password="Hl173gaz?0914az", ags_connection_file="", token="", referer=""):
    '''Imports the service toolbox based on the specified credentials and returns the toolbox object'''

    #Construct the connection string to import the service toolbox
    if username and password:
        tbx = "http://logistics.arcgis.com/arcgis/services;{0};{1};{2}".format(service_name, username, password)
    elif ags_connection_file:
        tbx = "{0};{1}".format(ags_connection_file, service_name)
    elif token and referer:
        tbx = "http://logistics.arcgis.com/arcgis/services;{0};token={1};{2}".format(service_name, token, referer)
    else:
        raise arcpy.ExecuteError("No valid option specified to connect to the {0} service".format(service_name))

    #Import the service toolbox
    tbx_alias = "agol"
    arcpy.ImportToolbox(tbx, tbx_alias)

    return getattr(arcpy, tbx_alias)

import_service("Network Analysis")


def main():
    '''Program entry point'''

    #Get the name and version of the product used to run the script
    install_info = arcpy.GetInstallInfo()
    product_version = "{0} {1}".format(install_info["ProductName"], install_info["Version"])

    #Use the Stores feature class in a file geodatabase called inputs in the same folder as the script
    cwd = os.path.dirname(os.path.abspath(__file__))
    facilities = os.path.join(cwd, "inputs.gdb", "Stores")

    #Get the credentials from the sigend in user and import the service
    service_name = "World/ServiceAreas"
    credentials = arcpy.GetSigninToken()
    if not credentials:
        raise arcpy.ExecuteError("Please sign into ArcGIS Online")
    token = credentials["token"]
    referer = credentials["referer"]
    service = import_service(service_name, token=token, referer=referer)
    
    #Setup other inputs for the service
    break_values = "2 4 6"
    break_units = "Minutes"
    travel_modes = ["Driving Time", "Walking Time"]
    
    #Store outputs in a file geodatabase called outputs in the same folder as the script
    #Create the file geodatabase if it does not exist
    output_gdb_name = "outputs.gdb"
    output_gdb = os.path.join(cwd, output_gdb_name)
    if not os.path.exists(output_gdb):
        arcpy.management.CreateFileGDB(cwd, output_gdb_name)

    #Call the service for each travel mode
    for travel_mode in travel_modes:
        
        #Call the tool
        arcpy.AddMessage("Generating '{0}' {1} service areas using {2} travel mode with {3}".format(break_values,
                                                                                                    break_units,
                                                                                                    travel_mode,
                                                                                                    product_version))
        result = service.GenerateServiceAreas(facilities, break_values, break_units, Travel_Mode=travel_mode)

        #Check the status of the result object every second until it has a value of 4(succeeded) or greater 
        while result.status < 4:
            time.sleep(1)
        
        #print any warning or error messages returned from the tool
        result_severity = result.maxSeverity
        if result_severity == 2:
            arcpy.AddError(result.getMessages(2))
            raise arcpy.ExecuteError("An error occured when running the tool")
        elif result_severity == 1:
            arcpy.AddMessage("Warnings were returned when running the tool")
            arcpy.AddWarning(result.getMessages(1))
    
        #Get the output service areas and save to a file geodatabase feature class.
        output_service_area_name = u"Online_{0}".format(arcpy.ValidateTableName(travel_mode, output_gdb))
        output_service_areas = os.path.join(output_gdb , output_service_area_name)
        if arcpy.Exists(output_service_areas):
            arcpy.management.Delete(output_service_areas)
        result.getOutput(0).save(output_service_areas)


if __name__ == "__main__":
    try:
        main()
    except Exception as ex:
        print(ex.message)