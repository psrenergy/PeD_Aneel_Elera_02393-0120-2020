#coding: utf-8
'''
Created on Jun 23, 2021

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, os, time
import traceback
from Util import File 
import csv

def criaTabelaMedicaoMeteorologica(workspace, nomeTabela):
    """
    Cria uma tabela vazia para armazenar o histórico de 
    dados meteorológicos, associados à estações de medição
    
    :param str workspace: diretório de trabalho 
    :param str nomeTabela: nome da tabela 
    
    :return: a tabela criada
    """   
    
    if arcpy.Exists(workspace + "\\" + nomeTabela):
        arcpy.Delete_management(workspace + "\\" + nomeTabela)
    
    nomeTabela = arcpy.CreateTable_management(workspace, nomeTabela)
    
    nomeAtributo = "Codigo"
    arcpy.AddField_management(nomeTabela, nomeAtributo, "LONG", "", "", "", "", "", "REQUIRED")

    nomeAtributo = "Ref_Ano"
    arcpy.AddField_management(nomeTabela, nomeAtributo, "LONG", "", "", "", "", "", "REQUIRED")
    
    nomeAtributo = "Ref_Mes"
    arcpy.AddField_management(nomeTabela, nomeAtributo, "LONG", "", "", "", "", "", "REQUIRED")

    nomeAtributo = "Medicao"
    arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
  
    return nomeTabela

# input parameters 
arquivoCSVMedicaoMeteorologica = arcpy.GetParameterAsText(0)
anoInicialHistorico = arcpy.GetParameterAsText(1)
anoFinalHistorico = arcpy.GetParameterAsText(2)
saidaDbfMedicaoMeteorologica = arcpy.GetParameterAsText(3)

if File.existFile(arquivoCSVMedicaoMeteorologica):

    arcpy.AddMessage(time.ctime() + " Lendo dados historicos de medicoes meteorologicas do arquivo: {file}...".format(file = os.path.basename(arquivoCSVMedicaoMeteorologica)))

    workspace = os.path.dirname(saidaDbfMedicaoMeteorologica)
    DbfMedicaoMeteorologica = os.path.basename(saidaDbfMedicaoMeteorologica)
    
    arcpy.env.overwriteOutput = True

    pymsg = ""
    msgs = ""
    
    registro=""
    cursor=""
    
    try:

        DbfMedicaoMeteorologica = criaTabelaMedicaoMeteorologica(workspace, DbfMedicaoMeteorologica)

        codigoEstacoes=[]
        col_header_length = 2
        with open(arquivoCSVMedicaoMeteorologica) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            cont_linha = 0

            atributos = ['Codigo', 'Ref_Ano', 'Ref_Mes', 'Medicao']
            cursor = arcpy.da.InsertCursor(DbfMedicaoMeteorologica, atributos)
            
            for linha in csv_reader:
                
                #header
                if cont_linha == 0:
                    numColunas = len(linha)
                    for iColuna in range(col_header_length, numColunas):
                        codigoEstacoes.append(linha[iColuna])
                else:
                    
                    year = linha[0]
                    month = linha[1]
                    
                    if anoInicialHistorico <= year <= anoFinalHistorico:
                        
                        for iColumn in range(col_header_length, numColunas):
                            cursor.insertRow((codigoEstacoes[iColumn-col_header_length], year, month, linha[iColumn]))
                    
                cont_linha += 1

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
        if registro:
            del registro
        if cursor:
            del cursor

        if len(pymsg)>0 or len(msgs)>0:
            sys.exit(0)

