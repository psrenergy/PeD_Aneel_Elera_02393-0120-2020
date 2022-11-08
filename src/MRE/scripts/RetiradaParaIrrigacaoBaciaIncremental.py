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


def CalcularRetiradaIrrigacaoPorBaciaIncremental():
    """
    Computa a retirada de água para irrigação em cada bacia incremental (reservatório)
    
    O cálcula para cada bacia, envolve computar a área irrigada de cada municipio 
    que faz interseção espacial com a bacia. Como esta interseção muitas das vezes
    será parcial à área do municipio, necessário computar a área cultivada que tem
    interseção com aa bacia. A partir desta área, computa-se o percentual da área
    cultivado com relação ao total do município. A partir do rpecentual, computa-se
    a Retirada de água por [cultivo,municpio] 
    
    """
    pymsg = ""
    msgs = ""

    arcpy.AddMessage(time.ctime() + ' - Computando a retirada de agua para irrigacao por bacia incremental...')

    # Cria a tabela histórica de retirada de água para irrigação, por bacia incremental
    configurarTabelaRetiradaAguaIrrigacaoBaciaIncremental(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL)

    atributosTabRetiradaIrrigacao=[]
    for eficAplicacao in listaEficAplicao:
        nomeColunaRetiradaIrrigacao = Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG + "_" + eficAplicacao.replace(".","")
        arcpy.AddField_management(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL, nomeColunaRetiradaIrrigacao, "DOUBLE", "", "", "", "", "", "REQUIRED")

        atributosTabRetiradaIrrigacao.append(nomeColunaRetiradaIrrigacao)    

    try:

        workspace_tmp = arcpy.env.workspace

        camadaBaciasIncrementais_layer = r"in_memory\camadaBaciasIncrementais_layer"
    
        oid_fieldname = arcpy.Describe(camadaBaciasIncrementais).OIDFieldName
    
        atributos = [oid_fieldname, 'bacia']
        with arcpy.da.SearchCursor(camadaBaciasIncrementais, atributos) as cursorBaciaIncremental:
            for rowBacia in cursorBaciaIncremental:
                baciaId = rowBacia[0]
                nomeBacia = rowBacia[1]
                
                arcpy.AddMessage(time.ctime() + ' - Computando a retirada de agua para irrigacao da bacia Id: {baciaId}'.format(baciaId=baciaId))
                
                sqlWHhere =oid_fieldname + ' = ' + str(baciaId)
    
                arcpy.MakeFeatureLayer_management(camadaBaciasIncrementais, camadaBaciasIncrementais_layer, sqlWHhere)
                
                camadaMunicipiosClipBacia = r"in_memory\camadaMunicipiosClipBacia"
    
                # Processo: clip da camada de municipios usando o bacia incremental como máscara
                arcpy.Clip_analysis(camadaMunicipios, camadaBaciasIncrementais_layer, camadaMunicipiosClipBacia, "")
                
                for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

                    arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))

                    arcpy.env.workspace = diretorioCamadaCultivoIrrigado
                    
                    wildCard = "*" + str(ano) + "_cultivos_irrigados*"
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
                                    
                                    atributos=[Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA]
                                    atributos.extend(atributosTabRetiradaIrrigacao)
                                    with arcpy.da.SearchCursor(tabelaHistoricoRetiradaIrrigadaPorCultivoPorMunicipio, atributos, sqlWhere) as cursorTabelaRetiradaIrrigadaMunicipio:
                                        for rowTabelaRetiradaIrrigadaMunicipio in cursorTabelaRetiradaIrrigadaMunicipio:
                                            classeCultivo = rowTabelaRetiradaIrrigadaMunicipio[0]
                                            areaIrrigadaHaMunicipioCompleto = rowTabelaRetiradaIrrigadaMunicipio[1]
                                            
                                            # Pode existir uma determinada classe de cultivo no polígono completo do municipio,
                                            # e não existir do polígono clipado
                                            if classeCultivo in areaIrrigadaHa:
                                                percentual = areaIrrigadaHa[classeCultivo]/areaIrrigadaHaMunicipioCompleto
                                                
                                                #Para cada coluna de retirada de agua associada a um fator de efieciencia de irrigacao
                                                listaRetiradaAguaCultivo=[]
                                                indice = 1
                                                for atributo in atributosTabRetiradaIrrigacao:
                                                    indice +=1
                                                    retiradaAguaCultivo = percentual * rowTabelaRetiradaIrrigadaMunicipio[indice]
                                                
                                                    listaRetiradaAguaCultivo.append(retiradaAguaCultivo)
                                                
                                                atributos = [Constantes.NOME_ATRIBUTO_NOME_BACIA_INCREMENTAL, Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA]
                                                atributos.extend(atributosTabRetiradaIrrigacao)

                                                cursorDestino = arcpy.InsertCursor(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL, atributos)
                                                row = cursorDestino.newRow()
                                                row.setValue(atributos[0], nomeBacia)
                                                row.setValue(atributos[1], codigoMunicipio)
                                                row.setValue(atributos[2], ano)
                                                row.setValue(atributos[3], mes)
                                                row.setValue(atributos[4], classeCultivo)
                                                row.setValue(atributos[5], areaIrrigadaHa[classeCultivo])

                                                indice=5
                                                for retiradaAguaCultivo in listaRetiradaAguaCultivo:
                                                    indice+=1
                                                    row.setValue(atributos[indice], retiradaAguaCultivo)
                                                
                                                cursorDestino.insertRow(row)
                
        #adicionando um intervalo de tempo para garantir que a tabela Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL, populado no passo anterior, esteja disponivel.
        # erro que estava sendo gerado: ERROR 000732: Input Table: Dataset Historico_Retirada_Agua_Irrigacao_Por_Municipio_Por_Cultivo_Por_Bacia_Incremental does not exist or is not supported  
        time.sleep(10)
        
        estatisticaSUM = []
        for eficAplicacao in listaEficAplicao:
            nomeAtributo = Constantes.NOME_ATRIBUTO_RETIRADA_IRRIG + "_" + eficAplicacao.replace(".","")
            estatisticaSUM.append([nomeAtributo, "SUM"] )

        tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview = r"in_memory\tabelaRetiradaAguaIrrigacaoBaciaIncremental_tview"
        arcpy.MakeTableView_management(Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL, tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview)

        #Sumariza a retirada de água para irrigação por [bacia,ano,mes,classecultivo]
        tabelaHistoricaRetiradaAguaIrrigacaoSumarizada = Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA_POR_CLASSE_CULTIVO
        estatistica = estatisticaSUM  
        atributoAgregador = "NM_BACIA;ano;mes;ClasseCultivo"
        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview, tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, estatistica, atributoAgregador)

        #Sumariza a retirada de água para irrigação por [bacia,ano,mes]
        tabelaHistoricaRetiradaAguaIrrigacaoSumarizada = Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA
        estatistica = estatisticaSUM  
        atributoAgregador = "NM_BACIA;ano;mes"
        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview, tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, estatistica, atributoAgregador)

        #Sumariza a retirada de água para irrigação por [bacia,ano]
        estatisticaMEAN = []
        for atributoSumarizado in atributosTabRetiradaIrrigacao:
            nomeAtributo = 'SUM_' + atributoSumarizado
            estatisticaMEAN.append([nomeAtributo, "MEAN"] )
        
        tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tableview = r"in_memory\tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tview"
        arcpy.MakeTableView_management(tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tableview)

        tabelaHistoricaRetiradaAguaIrrigacaoSumarizada = Constantes.TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA_POR_ANO
        estatistica = estatisticaMEAN
        atributoAgregador = "NM_BACIA;ano"
        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncrementalSumarizada_tableview, tabelaHistoricaRetiradaAguaIrrigacaoSumarizada, estatistica, atributoAgregador)

        #Sumariza a área irrigada por bacia, municipio, ano e tipo de cultura [bacia, ano, classecultivo, area cultivada]
        tabelaHistoricaAreaCultivadaPorBaciaSumarizada = Constantes.TABELA_AREA_CULTIVADA_MUNICIPIO_SUMARIZADA_POR_ANO
        nomeAtributoSumarizado = Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA
        estatistica = [[nomeAtributoSumarizado, 'MEAN']]  
        atributoAgregador = "NM_BACIA;CD_MUN;ano;ClasseCultivo"
        
        arcpy.Statistics_analysis(tabelaRetiradaAguaIrrigacaoBaciaIncremental_tableview, tabelaHistoricaAreaCultivadaPorBaciaSumarizada, estatistica, atributoAgregador)

        #libera a memoria utilizada  
        arcpy.Delete_management("in_memory")

        arcpy.AddMessage(time.ctime() + ' - Retirada de agua para irrigacao por bacia incremental computado.')

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
tabelaHistoricoRetiradaIrrigadaPorCultivoPorMunicipio = arcpy.GetParameterAsText(0)
camadaBaciasIncrementais = arcpy.GetParameterAsText(1)
camadaMunicipios = arcpy.GetParameterAsText(2)
diretorioCamadaCultivoIrrigado = arcpy.GetParameterAsText(3)
anoInicialHistorico = int(arcpy.GetParameterAsText(4))
anoFinalHistorico = int(arcpy.GetParameterAsText(5))
eficAplicacao = arcpy.GetParameterAsText(6)    
workspace = arcpy.GetParameterAsText(7)

# Nonme das colunas de retirada de agua, associadas ao parametro de eficiencia de irrigacao
listaEficAplicao= eficAplicacao.split(";")
  
if not arcpy.Exists(tabelaHistoricoRetiradaIrrigadaPorCultivoPorMunicipio):
    arcpy.AddError("Tabela inexistente: {dir}".format(dir=tabelaHistoricoRetiradaIrrigadaPorCultivoPorMunicipio) )
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

CalcularRetiradaIrrigacaoPorBaciaIncremental()

