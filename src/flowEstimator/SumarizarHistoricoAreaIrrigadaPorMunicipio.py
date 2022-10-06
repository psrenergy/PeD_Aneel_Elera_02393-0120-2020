#coding: utf-8
'''
Created on December 8, 2021

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import traceback
import Constantes
import re

def configurarTabelaLogInconsistenciasDadosHistoricosIrrigacao(nomeTabela):
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

        arcpy.AddField_management(nomeTabela, "Ano_1", "SHORT", "", "", "", "", "", "REQUIRED")
        arcpy.AddField_management(nomeTabela, "Ano_2", "SHORT", "", "", "", "", "", "REQUIRED")
        arcpy.AddField_management(nomeTabela, "ValAno_1", "DOUBLE", "", "", "", "", "", "REQUIRED")
        arcpy.AddField_management(nomeTabela, "ValAno_2", "DOUBLE", "", "", "", "", "", "REQUIRED")

        arcpy.AddField_management(nomeTabela, "Dif_Perc", "DOUBLE", "", "", "", "", "", "REQUIRED")

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

def configurarTabelaAreaIrrigadaPorCultivoPorMunicipio(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_ANO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_PERC
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

def configurarTabelaAreaIrrigadaHistoricaPorMunicipio(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_ANO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_PERC
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
    
def logarInconsistenciaDadoHistoricosIrrigacao(nomeTabelaLogInconsistencia, codigoMunicipio, NomeMunicipio, nomeAtributoAno1, nomeAtributoAno2, valAno1, valAno2, difPerc):
    """
    """   

    pymsg = ""
    msgs = ""
    
    try:

        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, "Ano_1", "Ano_2", "ValAno_1", "ValAno_2", "Dif_Perc"]
      
        with arcpy.da.InsertCursor(nomeTabelaLogInconsistencia, atributos) as cursor:
            cursor.insertRow((codigoMunicipio, NomeMunicipio, nomeAtributoAno1, nomeAtributoAno2, valAno1, valAno2, difPerc))

     
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
    
def extraiAnoDeNomeTabelaEstatistica(nomeTabela):
    numeros = [int(s) for s in re.findall(r'\d+', nomeTabela)]
    if numeros:
        for numero in numeros:
            if len(str(numero)) == 4:
                return numero
    
    
# input parameters
workspaceTabelasEstatisticaAreaIrrigada = arcpy.GetParameterAsText(0)
camadaMunicipiosSaoFrancisco  = arcpy.GetParameterAsText(1)

if not arcpy.Exists(workspaceTabelasEstatisticaAreaIrrigada):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=workspaceTabelasEstatisticaAreaIrrigada) )
    sys.exit(0)
                  
arcpy.AddMessage(time.ctime() + " - Sumarizando o historico das areas irrigadas por municipio...")

# Define o workspace de processamento 
arcpy.env.workspace = workspaceTabelasEstatisticaAreaIrrigada

tabelas = arcpy.ListTables("TabulateArea_*")
if tabelas: 
    
    # Tabela de áreas irrigadas totais por Municipio
    configurarTabelaAreaIrrigadaHistoricaPorMunicipio(Constantes.TABELA_HISTORICO_AREA_IRRIGADA_POR_MUNICIPIO)

    # Tabela de áreas irrigadas por cultivo por Municipio
    configurarTabelaAreaIrrigadaPorCultivoPorMunicipio(Constantes.TABELA_HISTORICO_AREA_IRRIGADA_POR_CULTIPO_POR_MUNICIPIO)
    
for tabela in tabelas:
    
    ano = extraiAnoDeNomeTabelaEstatistica(tabela)
    if ano:
        
        atributosOrigem=[Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO]
        
        atributosCultivo=[]
        for f in arcpy.ListFields(tabela):
            if f.name.startswith('VALUE_'):
                atributosCultivo.append(f.name)
        
        atributosOrigem.extend(atributosCultivo)
        
        with arcpy.da.SearchCursor(tabela, atributosOrigem) as cursorOrigem:
            for rowOrigem in cursorOrigem:
            
                sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = "  +  "'" + rowOrigem[0] + "'" 
                
                atributosMunicipio = [Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.AREA_KM2]
                with arcpy.da.SearchCursor(camadaMunicipiosSaoFrancisco, atributosMunicipio, sqlWhere) as cursorMunicipio:
                    for rowMunicipio in cursorMunicipio:
                        nomeMunicipio = rowMunicipio[0]
                        areaMunicipioKm2 = rowMunicipio[1] 
                        areaMunicipioHa = areaMunicipioKm2 * 100 #converte de Km2 para hectares 
                        
                        # Inclusão na tabela áreas irrigadas totais por Municipio
                        atributosDestinoAreaIrrigadaTotal = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA, Constantes.NOME_ATRIBUTO_AREA_IRRIG_PERC]
                        with arcpy.da.InsertCursor(Constantes.TABELA_HISTORICO_AREA_IRRIGADA_POR_MUNICIPIO, atributosDestinoAreaIrrigadaTotal) as cursorDestino:
                            
                            areaIrrigadaM2 = 0
                            for iAtributo in range(1, len(atributosCultivo)+1):
                                areaIrrigadaM2 += rowOrigem[iAtributo]
                            
                            areaIrrigadaHa = areaIrrigadaM2 * 1e-4 # convertendo de metros quadrados para hectares 
                            
                            percentualAreaIrrigada = (areaIrrigadaHa/areaMunicipioHa) * 100
                            percentualAreaIrrigada= '{0:.3g}'.format(percentualAreaIrrigada) 
                            
                            cursorDestino.insertRow((rowOrigem[0], nomeMunicipio, areaMunicipioHa, ano, areaIrrigadaHa, percentualAreaIrrigada))

                        # Inclusão na tabela áreas irrigadas por cultivo por Municipio
                        atributosDestinoAreaIrrigadaPorCultivo = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA, Constantes.NOME_ATRIBUTO_AREA_IRRIG_PERC]
                        with arcpy.da.InsertCursor(Constantes.TABELA_HISTORICO_AREA_IRRIGADA_POR_CULTIPO_POR_MUNICIPIO, atributosDestinoAreaIrrigadaPorCultivo) as cursorDestino:
                            
                            for iAtributo in range(0, len(atributosCultivo)):
                                
                                classeCultivo = atributosCultivo[iAtributo][6:8]
                                
                                areaIrrigadaM2 = rowOrigem[iAtributo+1]
                            
                                if areaIrrigadaM2>0:
                                
                                    areaIrrigadaHa = areaIrrigadaM2 * 1e-4 # convertendo de metros quadrados para hectares 
                                    
                                    percentualAreaIrrigada = (areaIrrigadaHa/areaMunicipioHa) * 100
                                    percentualAreaIrrigada= '{0:.3g}'.format(percentualAreaIrrigada) 
                                    
                                    cursorDestino.insertRow((rowOrigem[0], nomeMunicipio, areaMunicipioHa, ano, classeCultivo, areaIrrigadaHa, percentualAreaIrrigada))

# Cria um indice para a tabela Constantes.TABELA_HISTORICO_AREA_IRRIGADA_POR_CULTIPO_POR_MUNICIPIO
atributos = [Constantes.NOME_ATRIBUTO_ANO]
nomeIndice = "indice"
arcpy.AddIndex_management(Constantes.TABELA_HISTORICO_AREA_IRRIGADA_POR_CULTIPO_POR_MUNICIPIO, atributos, nomeIndice, "NON_UNIQUE", "ASCENDING")

arcpy.AddMessage(time.ctime() + ' - Processo finalizado.')

