'''
Created on Sep 14, 2021

@author: andre
'''
import arcpy, sys, time, os
import traceback
from Util import File 
import csv
import datetime


listaPrefixoNomeArquivoLandsatInconsistentes = [  'Espelhos_SF_1984_Chuva', 
                                                  'Espelhos_SF_1985_Chuva',
                                                  'Espelhos_SF_1986_Seca',
                                                  'Espelhos_SF_1989_Chuva',
                                                  'Espelhos_SF_1997_Chuva',
                                                  'Espelhos_SF_1998_Chuva',
                                                  'Espelhos_SF_2002_Seca',
                                                  'Espelhos_SF_2003_Chuva',
                                                  'Espelhos_SF_2012_Seca',
                                                  'Espelhos_SF_2021_Chuva'
                                               ]

def createWaterBodyInconsistentAreaTable(workspace, inDbfName):
    '''
    Creates an empty dbf table to log the size inconsistencies of the the water bodies 
    mapped in the drought and humid landsat images
    
    Input:
       workspace - Working directory of file geodatabase 
       inDbfName - Name of the dbf table
    
    Output:
       the dbf table
    
    '''
    if arcpy.Exists(workspace + "\\" + inDbfName):
        arcpy.Delete_management(workspace + "\\" + inDbfName)
    
    inDbfName = arcpy.CreateTable_management(workspace, inDbfName)
    
    nomeAtributo = "ImgSeca"
    arcpy.AddField_management(inDbfName, nomeAtributo, "TEXT", "", "", 50, "", "", "REQUIRED")

    nomeAtributo = "ImgChuva"
    arcpy.AddField_management(inDbfName, nomeAtributo, "TEXT", "", "", 50, "", "", "REQUIRED")
    
    nomeAtributo = "nomeMassaDagua"
    arcpy.AddField_management(inDbfName, nomeAtributo, "TEXT", "", "", 50, "", "", "REQUIRED")

    nomeAtributo = "AreaSeca"
    arcpy.AddField_management(inDbfName, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

    nomeAtributo = "AreaChuva"
    arcpy.AddField_management(inDbfName, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
  
    return inDbfName

def logarInconsistencia():


def logarArquivoNaoExiste(nomeArquivo):
    

def executarAnaliseConsistenciaArquivos(nomeArquivoSeco, nomeArquivoUmido):
    
    fcLandsatSeco = nomeArquivoSeco
    fcLandsatUmido = nomeArquivoUmido
    
    for massaDagua in arcpy.SearchCursor(fcLandsatSeco, ["nmoriginal", "POLY_AREA"]):
        nomeMassaDguaSeco = massaDagua[0]
        areaMassaDaguaSeco= massaDagua[1]
        
        
        
        SE nomeMassaDgua <> NULL ENTAO 'Se foi identificado'
            MassaDaguaUmida = Query camada nomeArquivoUmido (nomeFeciao = nomeMassaDgua)
            SE AREA(MassDaguaSEca) > AREA(MassaDaguaUmida) ENTAO
                logarInconsistencia
                Substituir massa
                
    
# Parametros de entrada 
inDiretorioFcSatelite = arcpy.GetParameterAsText(0)
inAnoHistoricoInicial=arcpy.GetParameterAsText(1)
inAnoHistoricoFinal=arcpy.GetParameterAsText(2)
inPrefixoNomeArquivoFcSatelite=arcpy.GetParameterAsText(3)
inSufixoNomeArquivoFcSateliteUmido=arcpy.GetParameterAsText(4)
inSufixoNomeArquivoFcSateliteSeco=arcpy.GetParameterAsText(5)
outNomeArquivoLog=arcpy.GetParameterAsText(6)

for ano in range(int(inAnoHistoricoInicial), int(inAnoHistoricoFinal)):
    nomeArquivoUmido = inPrefixoNomeArquivoFcSatelite + str(ano) + inSufixoNomeArquivoFcSateliteUmido
    nomeArquivoSeco = inPrefixoNomeArquivoFcSatelite + str(ano) + inSufixoNomeArquivoFcSateliteSeco
    
    if not File.existFile(inDiretorioFcSatelite + "\\" + nomeArquivoUmido):
        logarArquivoNaoExiste(inDiretorioFcSatelite + "\\" + nomeArquivoUmido)
          
    if not File.existFile(inDiretorioFcSatelite + "\\" + nomeArquivoSeco):
        logarArquivoNaoExiste(inDiretorioFcSatelite + "\\" + nomeArquivoSeco)
    
    executarAnaliseConsistenciaArquivos(inDiretorioFcSatelite + "\\" + nomeArquivoUmido, inDiretorioFcSatelite + "\\" + nomeArquivoSeco)