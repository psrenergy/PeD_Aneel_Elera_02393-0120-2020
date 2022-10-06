'''
Created on Jun 23, 2021

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import EstacaoMedicao
import traceback
from Util import File 
import csv

def createStationWeatherMeasurementTable(workspace, inDbfName):
    '''
    Creates an empty dbf table to hold the rainfall index 
    of each weather station in given year/month
    
    Input:
       workspace - Working directory of file geodatabase 
       inDbfName - Name of the dbf table
    
    Output:
       the dbf table
    
    '''
    if arcpy.Exists(workspace + "\\" + inDbfName):
        arcpy.Delete_management(workspace + "\\" + inDbfName)
    
    inDbfName = arcpy.CreateTable_management(workspace, inDbfName)
    
    nomeAtributo = "Codigo"
    arcpy.AddField_management(inDbfName, nomeAtributo, "LONG", "", "", "", "", "", "REQUIRED")

    nomeAtributo = "Ref_Ano"
    arcpy.AddField_management(inDbfName, nomeAtributo, "LONG", "", "", "", "", "", "REQUIRED")
    
    nomeAtributo = "Ref_Mes"
    arcpy.AddField_management(inDbfName, nomeAtributo, "LONG", "", "", "", "", "", "REQUIRED")

    nomeAtributo = "Medicao"
    arcpy.AddField_management(inDbfName, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
  
    return inDbfName

# input parameters 
inWorkspace = arcpy.GetParameterAsText(0)
inCSVFileWeatherStationHistoricalData = arcpy.GetParameterAsText(1)
anoReferencia = arcpy.GetParameterAsText(2)
mesReferencia = arcpy.GetParameterAsText(3)
outDbfWeatherStation = arcpy.GetParameterAsText(4)

if File.existFile(inCSVFileWeatherStationHistoricalData):

    DbfWeatherName = os.path.basename(outDbfWeatherStation)
    
    arcpy.env.overwriteOutput = True

    pymsg = ""
    msgs = ""
    
    try:

        outDbfWeatherName = createStationWeatherMeasurementTable(inWorkspace, DbfWeatherName)

        arcpy.AddMessage("Reading the historical weather data from {file}...".format(file = os.path.basename(inCSVFileWeatherStationHistoricalData) ))

        #
        stations = []
        col_header_length = 2
        with open(inCSVFileWeatherStationHistoricalData) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                
                #header
                if line_count == 0:
                    x = 0
                    y = 0
                    numCols = len(row)
                    for iColumn in range(col_header_length, numCols):
                        station = EstacaoMedicao.Estacao(row[iColumn], x, y) 
                        stations.append(station)
                        
                else:
                    
                    year = row[0]
                    month = row[1]
                    
                    sDateKey = str(month).zfill(2) + "/" + str(year)
                      
                    #precipitation data 
                    for iColumn in range(col_header_length, numCols):
                        station = stations[iColumn - col_header_length]
                        station.historicalMeasures.measures[sDateKey] = row[iColumn]
                        
                        if line_count == 1:
                            station.historicalMeasures.horizon.initialDate=time.strptime("1/1/" + str(year), "%d/%m/%Y")
                        else:    
                            station.historicalMeasures.horizon.finallDate=time.strptime("30/12/" + str(year), "%d/%m/%Y")
                        
                    
                line_count += 1

        cursor = arcpy.InsertCursor(outDbfWeatherName)

        for station in stations:

            sDateKey = str(mesReferencia).zfill(2) + '/' + str(anoReferencia)
            if sDateKey not in station.historicalMeasures.measures:
                arcpy.AddError("Nao existem dados historicos associada a data: {mes}/{ano} ".format(mes = mesReferencia, ano=anoReferencia))
                sys.exit(0)
            else:
                
                row = cursor.newRow()
                
                row.setValue("Codigo", station.site.code)
                row.setValue("Ref_Ano", anoReferencia)
                row.setValue("Ref_Mes", mesReferencia)
                row.setValue("Medicao", station.historicalMeasures.measures[sDateKey])
                
                cursor.insertRow(row)
                
    except:
        
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        
        # Concatenate error information into message string
        pymsg = 'PYTHON ERRORS:\nTraceback info:\n{0}\nError Info:\n{1}'\
              .format(tbinfo, str(sys.exc_info()[1]))
        
        msgs = 'ArcPy ERRORS:\n {0}\n'.format(arcpy.GetMessages(2))
      
        # Return python error messages for script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

    finally:
    
        # Delete cursor objects to remove locks on the data 
        if row:
            del row
        if cursor:
            del cursor

        if len(pymsg)>0 or len(msgs)>0:
            sys.exit(0)

