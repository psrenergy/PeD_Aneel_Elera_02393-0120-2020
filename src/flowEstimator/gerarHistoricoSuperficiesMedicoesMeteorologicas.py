#coding: utf-8
'''
Created on November 1, 2021

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import traceback
from Util import File 
import Constantes

EVAPORACAO_REFERENCIA = 1
PRECIPITACAO_MEDIA =2

def criarSuperficieInterpolada(ano, mes, tabelaMedicaoMeteorologica, nomeSuperficie):
    
    # Cria feature layer do shape das estações de medição
    camadaEstacoesINMET_Layer = r"in_memory\camadaEstacoesINMET_lyr"
    arcpy.MakeFeatureLayer_management(shapeFileEstacaosInMet, camadaEstacoesINMET_Layer)

    # Processo: Join dos atributos da tabela de medição meteorologica com o layer das estações de medicao
    nomeAtributoJoinTabelaOrigem="Codigo"
    nomeAtributoJoinTabelaDestino="Codigo"
    arcpy.AddJoin_management(camadaEstacoesINMET_Layer, nomeAtributoJoinTabelaOrigem, tabelaMedicaoMeteorologica, nomeAtributoJoinTabelaDestino, "KEEP_ALL")

    # Processo: Criando superficie, usando o algortimo de interpolação IDW (Inverse Distance Weighted)
    arcpy.env.extent = shapeFileMunicipiosSaoFrancisco
    atributoValorZ = "medicao_media_por_estacao.Medicao"
    superficie = r"in_memory\superficie"
    arcpy.Idw_3d(camadaEstacoesINMET_Layer, atributoValorZ, superficie, resolucaoEspacialSuperficie, "2", "VARIABLE 3", "")
    
    # Processo: Extract by Mask (usando o shape dos municípios do São Francisco como máscara)
    arcpy.gp.ExtractByMask_sa(superficie, shapeFileMunicipiosSaoFrancisco, nomeSuperficie)

    # Processo: Computa a média da medição meteorologica por Município.
    zoneField="CD_MUN"
    statistic = "MEAN"
    tabelaMediaMedicao = r"in_memory\tabelaMediaMedicao" 
    arcpy.gp.ZonalStatisticsAsTable_sa(shapeFileMunicipiosSaoFrancisco, zoneField, nomeSuperficie, tabelaMediaMedicao, "DATA", statistic)

    # Cria feature layer do shape dos municipios
    camadaMunicipios_Layer = r"in_memory\camadaMunicipios_lyr"
    arcpy.MakeFeatureLayer_management(shapeFileMunicipiosSaoFrancisco, camadaMunicipios_Layer)

    # Processo: Join dos atributos da tabela de municipios com a tabela de estatistica da media de medição meteorologica 
    nomeAtributoJoinTabelaOrigem="CD_MUN"
    nomeAtributoJoinTabelaDestino="CD_MUN"
    arcpy.AddJoin_management(camadaMunicipios_Layer, nomeAtributoJoinTabelaOrigem, tabelaMediaMedicao, nomeAtributoJoinTabelaDestino, "KEEP_ALL")

    # Processo: Exporta o layers de municipio para uma camada 
    nomeCamadaMunicipioMediaMedicao = prefixo_nome_medicao + "_por_municipio_" + str(ano) + "_" + str(mes).zfill(2)
    arcpy.Select_analysis(camadaMunicipios_Layer, nomeCamadaMunicipioMediaMedicao)
    
    #Processo: Converte o shape de municipios (polígono) para o formato Raster
    valueField = "tabelaMediaMedicao_MEAN"
    nomeSuperficiePorMunicipio="superficie_" + nomeCamadaMunicipioMediaMedicao
    arcpy.PolygonToRaster_conversion(nomeCamadaMunicipioMediaMedicao, valueField, nomeSuperficiePorMunicipio, "MAXIMUM_AREA", "NONE", resolucaoEspacialSuperficie)

    
#Parâmetros de entrada    
tipoMedicaoMeteorologica= int(arcpy.GetParameterAsText(0)[0])
shapeFileEstacaosInMet = arcpy.GetParameterAsText(1)
tabelaHistoricoMedicaoMeteorologica = arcpy.GetParameterAsText(2)
anoInicialHistorico = int(arcpy.GetParameterAsText(3))
anoFinalHistorico = int(arcpy.GetParameterAsText(4))
resolucaoEspacialSuperficie = int(arcpy.GetParameterAsText(5))
shapeFileMunicipiosSaoFrancisco = arcpy.GetParameterAsText(6)
diretorioSaidaSuperficie = arcpy.GetParameterAsText(7)

if not File.existFile(diretorioSaidaSuperficie):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSaidaSuperficie) )
    sys.exit(0)

if not File.existFile(tabelaHistoricoMedicaoMeteorologica):
    arcpy.AddError("Tabela inexistente: {arquivo}".format(dir=tabelaHistoricoMedicaoMeteorologica) )
    sys.exit(0)

if not File.existFile(shapeFileEstacaosInMet):
    arcpy.AddError("Shapefile inexistente: {arquivo}".format(dir=shapeFileEstacaosInMet) )
    sys.exit(0)

if not File.existFile(shapeFileMunicipiosSaoFrancisco):
    arcpy.AddError("Shapefile inexistente: {arquivo}".format(dir=shapeFileMunicipiosSaoFrancisco) )
    sys.exit(0)

# Verifica a existencia da licenca da extensao ArcGIS Spatial Analyst 
arcpy.CheckOutExtension("Spatial")

# Define o workspace de processamento 
arcpy.env.workspace = diretorioSaidaSuperficie

arcpy.env.overwriteOutput = True

# Tipo da medição meteorologica associada à superficie interpolada send criada
if tipoMedicaoMeteorologica == EVAPORACAO_REFERENCIA:
    prefixo_nome_medicao = "evaporacao_referencia"
elif tipoMedicaoMeteorologica == PRECIPITACAO_MEDIA:   
    prefixo_nome_medicao = "precipitacao_media"
else:
    prefixo_nome_medicao = "temperatura_media"

arcpy.AddMessage(time.ctime() + " Gerando superficies interpoladas a partir dos dados de medicao das estacoes do INMET....")

numTotSuperficies = ((anoFinalHistorico-anoInicialHistorico)+1) * 12
arcpy.SetProgressor("step", "Numero de superficies interpoladas a criar: " + str(numTotSuperficies), 0, int(numTotSuperficies), 1)
time.sleep(2)

# Gera superficie interpolada para cada <ano,mes> do histórico
iSuperficie = 0
for ano in range(anoInicialHistorico, anoFinalHistorico + 1):
    for mes in range (1,13):

        arcpy.AddMessage(time.ctime() + " Gerando superficie interpolada: {Ano}/{Mes}".format(Ano=ano, Mes=mes))
        
        iSuperficie +=1
        arcpy.SetProgressorLabel("Gerando superficie: " + str(iSuperficie) + "/" + str(numTotSuperficies))
        arcpy.SetProgressorPosition()
    
        sqlWhere = "Ref_Ano = " + str(ano) + " AND Ref_Mes = " + str(mes)
    
        # filtra tabela histórica de medições para o <ano,mes> 
        tabelaMedicaoMeteorologicaEmMemoria = "in_memory\medicao_media_por_estacao"
        arcpy.TableSelect_analysis(tabelaHistoricoMedicaoMeteorologica, tabelaMedicaoMeteorologicaEmMemoria, sqlWhere)
        
        nomeSuperficie = "superficie_" + prefixo_nome_medicao + str(ano) + "_" + str(mes).zfill(2)
        criarSuperficieInterpolada(ano, mes, tabelaMedicaoMeteorologicaEmMemoria, nomeSuperficie)
        
        #libera a memoria utilizada  
        arcpy.Delete_management("in_memory")

arcpy.ResetProgressor()

