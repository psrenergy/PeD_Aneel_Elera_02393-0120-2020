#coding: utf-8
'''
Created on November 1, 2021

@author: Andre Granville
'''
# Import libraries
import arcpy, sys,  os, time
import traceback
import Constantes
from Util import File 
from arcpy import env
import re 

def agregarShapefile(workspace, arquivoShapeOrigem, arquivoShapeDestino):
    
    pymsg = ""
    msgs = ""

    try:
    
        # busca o ano dentro da string do nome do arquivo
        numeros = [int(s) for s in re.findall(r'\d+', arquivoShapeOrigem)]
        if numeros:
            ano = numeros[0]
        if arquivoShapeOrigem.lower().find('chuva') > 0:
            estacao = 'Chuva'
        else:
            estacao = 'Seco'
            
        atributosOrigem = [Constantes.NOME_ATRIBUTO_ID_MASSA_DAGUA, Constantes.NOME_ATRIBUTO_MASSA_DAGUA, Constantes.NOME_ATRIBUTO_AREA, 'SHAPE@']
        atributosDestino = [Constantes.NOME_ATRIBUTO_ID_MASSA_DAGUA, Constantes.NOME_ATRIBUTO_MASSA_DAGUA, Constantes.NOME_ATRIBUTO_AREA, 'SHAPE@',Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_ESTACAO]
        
        with arcpy.da.SearchCursor(os.path.join(workspace, arquivoShapeOrigem), atributosOrigem) as cursorOrigem:
            with arcpy.da.InsertCursor(arquivoShapeDestino,atributosDestino) as cursorDestino:
                for row in cursorOrigem:
                    cursorDestino.insertRow((row[0], row[1], row[2], row[3], ano, estacao))
            
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
            if cursorOrigem:
                del cursorOrigem
            if cursorDestino:
                del cursorDestino
    
            if len(pymsg)>0 or len(msgs)>0:
                sys.exit(0)
                
def configurarShapeFilesMassaDAguaLandSatAgregado(workspace, nomeArquivoShapeFileMassasDAguaAgregado):
    """
    Cria um shapefile para armazenar todas as massas d'agua identificadas na imagem Landsat
    
    :param str workspace: diretório de trabalho 
    :param str arquivoShapeFileMassasDAguaAgregado: nome do shapefile que sera criado
    
    """   

    pymsg = ""
    msgs = ""
    
    try:
        
        # Exclue o arquivo caso exista
        if arcpy.Exists(os.path.join(workspace, nomeArquivoShapeFileMassasDAguaAgregado)):
            arcpy.Delete_management(os.path.join(workspace, nomeArquivoShapeFileMassasDAguaAgregado))
    
        has_m = "DISABLED"
        has_z = "DISABLED"
        
        arquivoShapeFileMassasDAguaAgregado = arcpy.CreateFeatureclass_management(workspace, nomeArquivoShapeFileMassasDAguaAgregado, "POLYGON", "", has_m, has_z)

        nomeAtributo = Constantes.NOME_ATRIBUTO_ID_MASSA_DAGUA
        arcpy.AddField_management(arquivoShapeFileMassasDAguaAgregado, nomeAtributo, "long", "", "", "", "", "", "REQUIRED")
      
        nomeAtributo = Constantes.NOME_ATRIBUTO_MASSA_DAGUA
        arcpy.AddField_management(arquivoShapeFileMassasDAguaAgregado, nomeAtributo, "TEXT", "", "", "100", "", "", "REQUIRED")
    
        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA
        arcpy.AddField_management(arquivoShapeFileMassasDAguaAgregado, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_ANO
        arcpy.AddField_management(arquivoShapeFileMassasDAguaAgregado, nomeAtributo, "long", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_ESTACAO
        arcpy.AddField_management(arquivoShapeFileMassasDAguaAgregado, nomeAtributo, "TEXT", "", "", "10", "", "", "REQUIRED")
        
        return arquivoShapeFileMassasDAguaAgregado
    
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

# paremetros de entrada
diretorioShapeFilesMassaDAguaLandSat = arcpy.GetParameterAsText(0)
diretorioSaida = arcpy.GetParameterAsText(1)

if not File.existFile(diretorioSaida):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSaida) )
    sys.exit(0)
                  
if os.path.isdir(diretorioShapeFilesMassaDAguaLandSat):
   
    # Define o workspace de processamento 
    arcpy.env.workspace = diretorioSaida
 
    nomeArquivoShapeFileMassasDAguaAgregado = Constantes.ARQUIVO_MASSA_DAGUA_AGREGADO
        
    arcpy.AddMessage(time.ctime() + " - Agregandos as Massas DAgua de cada imagem Landsat em uma unica camada: {file}...".format(file = nomeArquivoShapeFileMassasDAguaAgregado))
    
    cont = 0
    
    for nomeArquivoLandsat in os.listdir(diretorioShapeFilesMassaDAguaLandSat):
        if nomeArquivoLandsat.endswith("dissolve.shp"):
            
            cont =cont+1
            if cont == 1:
                desc = arcpy.Describe(os.path.join(diretorioShapeFilesMassaDAguaLandSat, nomeArquivoLandsat))
                sistema_coordenadas = desc.spatialReference
                env.overwriteOutput = True
                env.outputCoordinateSystem=sistema_coordenadas
                
                arquivoShapeFileMassasDAguaAgregado= configurarShapeFilesMassaDAguaLandSatAgregado(diretorioSaida, nomeArquivoShapeFileMassasDAguaAgregado)
                
            agregarShapefile(diretorioShapeFilesMassaDAguaLandSat, nomeArquivoLandsat, arquivoShapeFileMassasDAguaAgregado)
        
        else:
            continue

    arcpy.AddMessage(time.ctime() + " - Foram agregados as Massas DAgua de {total} arquivos".format(total = cont))
