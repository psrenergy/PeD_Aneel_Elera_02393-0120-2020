#coding: utf-8

'''
Created on February 15, 2022

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import traceback
import Constantes

def configurarTabelaRetiradaAguaIrrigacaoBaciaIncremental(nomeTabela):
    """
    """   

    pymsg = ""
    msgs = ""
    
    try:
    
        # Exclue a tabela caso exista
        if arcpy.Exists(nomeTabela):
            arcpy.Delete_management(nomeTabela)

        nomeTabela = arcpy.CreateTable_management(arcpy.env.workspace, nomeTabela)

        nomeAtributo = Constantes.NOME_ATRIBUTO_NOME_BACIA_INCREMENTAL
        arcpy.AddField_management(nomeTabela, nomeAtributo, "TEXT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "TEXT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_ANO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_MES
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "TEXT", "", "", "50", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG
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


def CalcularNecessidadeIrrigacaoPorBaciaIncremental():
    """
    Computa a retirada de água para irrigação em cada bacia incremental (reservatório)
    
    O cálcula para cada bacia, envolve computar a área irrigada de cada municipio 
    que faz interseção espacial com a bacia. Como esta interseção muitas das vezes
    será parcial à área do municipio, necessário computar a área cultivada que tem
    interseção com aa bacia. A partir desta área, computa-se o percentual da área
    cultivado com relação ao total do município. A partir do rpecentual, computa-se
    a necessidade de água por [cultivo,municpio] 
    
    """
    pymsg = ""
    msgs = ""

    arcpy.AddMessage(time.ctime() + ' - Computando a necessidade de irrigacao por bacia incremental...')

    # Cria a tabela histórica de retirada de água para irrigação, por bacia incremental
    configurarTabelaRetiradaAguaIrrigacaoBaciaIncremental(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL)

    try:

        workspace_tmp = arcpy.env.workspace

        camadaBaciasIncrementais_layer = r"in_memory\camadaBaciasIncrementais_layer"
    
        oid_fieldname = arcpy.Describe(camadaBaciasIncrementais).OIDFieldName
    
        atributos = [oid_fieldname, 'bacia']
        with arcpy.da.SearchCursor(camadaBaciasIncrementais, atributos) as cursorBaciaIncremental:
            for rowBacia in cursorBaciaIncremental:
                baciaId = rowBacia[0]
                nomeBacia = rowBacia[1]
                
                arcpy.AddMessage(time.ctime() + ' - Computando a necessidade de irrigacao da bacia Id: {baciaId}'.format(baciaId=baciaId))
                
                sqlWHhere =oid_fieldname + ' = ' + str(baciaId)
    
                arcpy.MakeFeatureLayer_management(camadaBaciasIncrementais, camadaBaciasIncrementais_layer, sqlWHhere)
                
                camadaMunicipiosClipBacia = r"in_memory\camadaMunicipiosClipBacia"
    
                # Processo: clip da camada de municipios usando o bacia incremental como máscara
                arcpy.Clip_analysis(camadaMunicipios, camadaBaciasIncrementais_layer, camadaMunicipiosClipBacia, "")
                
                for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

                    arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))

                    arcpy.env.workspace = diretorioCamadaCultivoIrrigado
                    
                    wildCard = "*" + str(ano) + "_cultivos_irrigados"
                    camadasCultivoIrrigado = arcpy.ListRasters(wildCard)
                    if camadasCultivoIrrigado: 
                        
                        arcpy.env.workspace= workspace_tmp

                        camadaCultivoIrrigado = camadasCultivoIrrigado[0]
                        camadaCultivoIrrigado = os.path.join(diretorioCamadaCultivoIrrigado, camadaCultivoIrrigado)

                        # Processo: tabulate area 
                        #  >> resultado: tabela contendo, para cada municipio, a área irrigada de cada cultivo
                        atributoCamadaMunicipio="CD_MUN"
                        atributoValueRasterMapBiomas = "Value"
                        tabulatedArea = r"in_memory\tabulatedArea"
                        arcpy.sa.TabulateArea(camadaMunicipiosClipBacia, atributoCamadaMunicipio, camadaCultivoIrrigado, atributoValueRasterMapBiomas, tabulatedArea)
                    
                        # Processa a tabela 
                        atributosOrigem=[Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO]

                        atributosCultivo=[]
                        for f in arcpy.ListFields(tabulatedArea):
                            if f.name.startswith('VALUE_'):
                                atributosCultivo.append(f.name)
                        
                        atributosOrigem.extend(atributosCultivo)
                    
                        with arcpy.da.SearchCursor(tabulatedArea, atributosOrigem) as cursorTabulatedArea:
                            for rowTabulatedArea in cursorTabulatedArea:

                                codigoMunicipio = rowTabulatedArea[0]
                                
                                areaIrrigadaHa = {}    
                                for iAtributo in range(0, len(atributosCultivo)):
                                    
                                    classeCultivo = atributosCultivo[iAtributo][6:8]
                                    
                                    areaIrrigadaM2 = rowTabulatedArea[iAtributo+1]
                                    if areaIrrigadaM2>0:
                                        
                                        # converte de metros quadrados para hectares 
                                        areaIrrigadaHa[classeCultivo] = areaIrrigadaM2 * 1e-4 

                                for mes in range(1,13):
                                
                                    #Compara a area irrigada do polígono recortado (clip) do municipio 
                                    #com a area irrigada do polígono completo do municipio
                                    sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = "  +  "'" + codigoMunicipio + "' AND " + Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes)
                                    
                                    atributos=[Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA, Constantes.NOME_ATRIBUTO_NECES_IRRIG]
                                    with arcpy.da.SearchCursor(tabelaHistoricoNecessidadeIrrigadaPorCultivoPorMunicipio, atributos, sqlWhere) as cursorTabelaNecessidadeIrrigadaMunicipio:
                                        for rowTabelaNecessidadeIrrigadaMunicipio in cursorTabelaNecessidadeIrrigadaMunicipio:
                                            classeCultivo = rowTabelaNecessidadeIrrigadaMunicipio[0]
                                            areaIrrigadaHaMunicipioCompleto = rowTabelaNecessidadeIrrigadaMunicipio[1]
                                            
                                            # Pode existir uma determinada classe de cultivo no polígono completo do municipio,
                                            # e não existir do polígono clipado
                                            if classeCultivo in areaIrrigadaHa:
                                                percentual = areaIrrigadaHa[classeCultivo]/areaIrrigadaHaMunicipioCompleto
                                                
                                                retiradaAguaCultivo = percentual * rowTabelaNecessidadeIrrigadaMunicipio[2]
                                                
                                                atributos = [Constantes.NOME_ATRIBUTO_NOME_BACIA_INCREMENTAL, Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA, Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG]
                                                with arcpy.da.InsertCursor(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL, atributos) as cursorDestino:
                                                    cursorDestino.insertRow((nomeBacia, codigoMunicipio, ano, mes, classeCultivo, areaIrrigadaHa[classeCultivo], retiradaAguaCultivo))
                
        tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview = r"in_memory\tabelaRetiradaAguaIrrigacaoBaciaIncremental_tview"
        arcpy.MakeTableView_management(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL, tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview)

        #Sumariza a retirada de água para irrigação por [bacia,ano,mes,ClasseCultivo]
        tabelaHistoricaRetiradaAguaIrrigacaoSumarizada = Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA_POR_CLASSE_CULTIVO
        nomeAtributoSumarizado = Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG
        estatistica = [[nomeAtributoSumarizado, 'SUM']]  
        atributoAgregador = "NM_BACIA;ano;mes;ClasseCultivo"

        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview, tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, estatistica, atributoAgregador)

        #Sumariza a retirada de água para irrigação por [bacia,ano,mes]
        tabelaHistoricaRetiradaAguaIrrigacaoSumarizada = Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA
        nomeAtributoSumarizado = Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG
        estatistica = [[nomeAtributoSumarizado, 'SUM']]  
        atributoAgregador = "NM_BACIA;ano;mes"

        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview, tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, estatistica, atributoAgregador)

        #Sumariza a retirada de água para irrigação por [bacia,ano]

        tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tableview = r"in_memory\tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tview"
        arcpy.MakeTableView_management(tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tableview)

        tabelaHistoricaRetiradaAguaIrrigacaoSumarizada = Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA_POR_ANO
        nomeAtributoSumarizado = Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG_SUMARIZADA
        estatistica = [[nomeAtributoSumarizado, 'MEAN']]  
        atributoAgregador = "NM_BACIA;ano"

        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tableview, tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, estatistica, atributoAgregador)

        #Sumariza a área irrigada por bacia, tipo de cultura e ano [bacia, culura, area irrigada, ano]
        tabelaHistoricaAreaCultivadaPorBaciaSumarizada = Constantes.TABELA_AREA_CULTIVADA_BACIA_INCREMENTAL_SUMARIZADA_POR_ANO
        nomeAtributoSumarizado = Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA
        estatistica = [[nomeAtributoSumarizado, 'SUM']]  
        atributoAgregador = "NM_BACIA;ano;ClasseCultivo"

        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview, tabelaHistoricaAreaCultivadaPorBaciaSumarizada, estatistica, atributoAgregador)

        #libera a memoria utilizada  
        arcpy.Delete_management("in_memory")

        arcpy.AddMessage(time.ctime() + ' - Necessidade de irrigacao por bacia incremental computado.')

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
tabelaHistoricoNecessidadeIrrigadaPorCultivoPorMunicipio = arcpy.GetParameterAsText(0)
camadaBaciasIncrementais = arcpy.GetParameterAsText(1)
camadaMunicipios = arcpy.GetParameterAsText(2)
diretorioCamadaCultivoIrrigado = arcpy.GetParameterAsText(3)
anoInicialHistorico = int(arcpy.GetParameterAsText(4))
anoFinalHistorico = int(arcpy.GetParameterAsText(5))
workspace = arcpy.GetParameterAsText(6)
  
if not arcpy.Exists(tabelaHistoricoNecessidadeIrrigadaPorCultivoPorMunicipio):
    arcpy.AddError("Tabela inexistente: {dir}".format(dir=tabelaHistoricoNecessidadeIrrigadaPorCultivoPorMunicipio) )
    sys.exit(0)

if not arcpy.Exists(camadaBaciasIncrementais):
    arcpy.AddError("Camada inexistente: {dir}".format(dir=camadaBaciasIncrementais) )
    sys.exit(0)

if not arcpy.Exists(camadaMunicipios):
    arcpy.AddError("Camada inexistente: {dir}".format(dir=camadaMunicipios) )
    sys.exit(0)

if not arcpy.Exists(diretorioCamadaCultivoIrrigado):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioCamadaCultivoIrrigado) )
    sys.exit(0)


# Verifica a existencia da licenca da extensao ArcGIS Spatial Analyst 
arcpy.CheckOutExtension("Spatial")

# Define o workspace de processamento 
arcpy.env.workspace = workspace

arcpy.env.overwriteOutput = True

CalcularNecessidadeIrrigacaoPorBaciaIncremental()

