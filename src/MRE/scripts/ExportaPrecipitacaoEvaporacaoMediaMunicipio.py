#coding: utf-8

'''
Created on January 19, 2022

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import traceback
import Constantes
import math

def SalvarPrecipitacaoEvaporacaoMediaMunicipio():

    """
        Calcula a evapotranspiração potencial dos cultivos
        
        Fórmula:
            ETpc = ETo * Kc
               EtO = evaporação de referencia (superfície)
               Kc  = coeficiente do cultivo   (tabela)
    """
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Exportando dados histricos de precipitacacao e evaporacao media por municipio...')
    
    # Cria a tabela de evapotranspiracao potencial por cultivo por municipio
    configurarPrecipitacaoEvaporacaoMediaMunicipio("Historico_Precipitacao_Evaporacao_Media_Por_Municipio")

    nomeAtributoCodigoMunicipioPrecipitacao=''
    nomeAtributoPrecipitacaoMediaPrecipitacao=''
    
    nomeAtributoCodigoMunicipio=''
    nomeAtributoMediaEvapRef=''
    
    try:
        
        ListaCodigoMunicipio=[]
        ListaNomeMunicipio=[]

        # Dados históricos de áreas irrigadas por cultivo e por município (variação por ANO)
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO]
        with arcpy.da.SearchCursor(camadaMunicipios, atributos) as cursorMunicipio:
            for row in cursorMunicipio:
                ListaCodigoMunicipio.append(row[0])
                ListaNomeMunicipio.append(row[1])

        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            for mes in range(1,13):
                
                #Monta nome da camada de precipitação média por município referente ao perído <ano,mes>
                nomeCamadaPrecipitacaoMediaMunicipio = "precipitacao_media_por_municipio_" + str(ano) + "_" + str(mes).zfill(2)
                nomeCamadaPrecipitacaoMediaMunicipio = os.path.join(diretorioSuperficiePrecipitacaoMedia, nomeCamadaPrecipitacaoMediaMunicipio)

                #Monta nome da camada de evaporação de referência média por município referente ao perído <ano,mes>
                nomeCamadaEvapRefMediaMunicipio = "evaporacao_media_municipio__" + str(ano) + "_" + str(mes)
                nomeCamadaEvapRefMediaMunicipio = os.path.join(diretorioSuperficieEvapRefMediaMunicipio, nomeCamadaEvapRefMediaMunicipio)
                
                if arcpy.Exists(nomeCamadaEvapRefMediaMunicipio) and arcpy.Exists(nomeCamadaPrecipitacaoMediaMunicipio):
                    
                    if not nomeAtributoCodigoMunicipioPrecipitacao or not nomeAtributoPrecipitacaoMediaPrecipitacao:
                        for f in arcpy.ListFields(nomeCamadaPrecipitacaoMediaMunicipio):
                            if f.aliasName == Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO:
                                nomeAtributoCodigoMunicipioPrecipitacao = f.name
                                 
                            if f.aliasName == Constantes.NOME_ATRIBUTO_MEDIA_SUPERFICIE:
                                nomeAtributoPrecipitacaoMediaPrecipitacao = f.name
                
                    # Precipitação media por município
                    precipitacaoMediaMunicipio={}
                    atributos = [nomeAtributoCodigoMunicipioPrecipitacao, nomeAtributoPrecipitacaoMediaPrecipitacao]
                    with arcpy.da.SearchCursor(nomeCamadaPrecipitacaoMediaMunicipio, atributos) as cursorPrecipitacaoMedia:
                        for rowPrecipitacaoMedia in cursorPrecipitacaoMedia:
                            codMunicipio = rowPrecipitacaoMedia[0]
                            precipitacaoMediaMunicipio[codMunicipio]  = rowPrecipitacaoMedia[1]  


                    if not nomeAtributoCodigoMunicipio or not nomeAtributoMediaEvapRef:
                        for f in arcpy.ListFields(nomeCamadaEvapRefMediaMunicipio):
                            if f.aliasName == Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO:
                                nomeAtributoCodigoMunicipio = f.name
                                 
                            if f.aliasName == Constantes.NOME_ATRIBUTO_MEDIA_SUPERFICIE:
                                nomeAtributoMediaEvapRef = f.name

                    # Evaporacao de referência
                    EtO={}
                    atributos = [nomeAtributoCodigoMunicipio, nomeAtributoMediaEvapRef]
                    with arcpy.da.SearchCursor(nomeCamadaEvapRefMediaMunicipio, atributos) as cursorEvapRef:
                        for rowEvapRef in cursorEvapRef:
                            codMunicipio = rowEvapRef[0]
                            EvapRef = rowEvapRef[1]
                            
                            if EvapRef:
                                EtO[codMunicipio] = EvapRef 
                   
                    for iMunicipio in range(len(ListaCodigoMunicipio)):
                        
                        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_PRECIP_BRUTA, Constantes.NOME_ATRIBUTO_EVAPORACAO_REF]
                        with arcpy.da.InsertCursor("Historico_Precipitacao_Evaporacao_Media_Por_Municipio", atributos) as cursorDestino:
                            cursorDestino.insertRow((ListaCodigoMunicipio[iMunicipio], ListaNomeMunicipio[iMunicipio], ano, mes, precipitacaoMediaMunicipio[codMunicipio], EtO[codMunicipio]))
                         
        arcpy.AddMessage(time.ctime() + ' - Exportacao finalizada...')

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
        
        if len(pymsg)>0 or len(msgs)>0:
            sys.exit(0)
    
def configurarPrecipitacaoEvaporacaoMediaMunicipio(nomeTabela):
    """
    """   

    pymsg = ""
    msgs = ""
    
    try:
    
        # Exclue a tabela caso exista
        if arcpy.Exists(nomeTabela):
            arcpy.Delete_management(nomeTabela)

        nomeTabela = arcpy.CreateTable_management(arcpy.env.workspace, nomeTabela)

        nomeAtributo = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "TEXT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "TEXT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_ANO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_MES
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_PRECIP_BRUTA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_EVAPORACAO_REF
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

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
        
        if len(pymsg)>0 or len(msgs)>0:
            sys.exit(0)

# Parâmetros
camadaMunicipios = arcpy.GetParameterAsText(0)
diretorioSuperficieEvapRefMediaMunicipio = arcpy.GetParameterAsText(1)
diretorioSuperficiePrecipitacaoMedia = arcpy.GetParameterAsText(2)
anoInicialHistorico = int(arcpy.GetParameterAsText(3))
anoFinalHistorico = int(arcpy.GetParameterAsText(4))
workspace = arcpy.GetParameterAsText(5)

if not arcpy.Exists(diretorioSuperficieEvapRefMediaMunicipio):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSuperficieEvapRefMediaMunicipio) )
    sys.exit(0)

if not arcpy.Exists(diretorioSuperficiePrecipitacaoMedia):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSuperficiePrecipitacaoMedia) )
    sys.exit(0)

if not arcpy.Exists(camadaMunicipios):
    arcpy.AddError("Mapa inexistente: {dir}".format(dir=camadaMunicipios) )
    sys.exit(0)

if not arcpy.Exists(workspace):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=workspace) )
    sys.exit(0)

# Verifica a existencia da licenca da extensao ArcGIS Spatial Analyst 
arcpy.CheckOutExtension("Spatial")

# Define o workspace de processamento 
arcpy.env.workspace = workspace

arcpy.env.overwriteOutput = True

SalvarPrecipitacaoEvaporacaoMediaMunicipio()
