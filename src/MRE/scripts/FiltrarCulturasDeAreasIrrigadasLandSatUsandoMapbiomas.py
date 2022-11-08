#coding: utf-8
'''
Created on January 17, 2022

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import traceback
from Util import File 

def validarAreasIrrigadasLandSat(anoInicialHistorico, anoFinalHistorico):
    """
    Valida o levantamento das áreas irrigadas LandSat, filtrando as áreas que correspondam à culturas do Mapbiomas
    """
    
    pymsg=''
    msgs =''
    
    try:
        
        arcpy.AddMessage('Filtrando as areas irrigadas LandSat que tem intersecao com as culturas mapeadas pelo MapBiomas...')
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            #Monta nome do raster do LandSat de áreas irrigadas
            nomeRasterLandSatIrrigacao = "Areas_Irrigadas_SF_" + str(ano) + "_setnull.tif"
            nomeRasterLandSatIrrigacao = os.path.join(diretorioLandSatAreasIrrigadas, nomeRasterLandSatIrrigacao)

            #Monta nome do raster do Mapbiomas referente ao ano <ano>
            nomeRasterMapBiomas = "mapbiomas_brazil-collection_60_" + str(ano) + "_Albers_clip_reclass_con.tif    "
            nomeRasterMapBiomas = os.path.join(diretorioMapBiomas, nomeRasterMapBiomas)
            
            nomeRasterLandSatIrrigacaoValidado = "Areas_Irrigadas_SF_" + str(ano) + "_validado_mapbiomas" 

            if arcpy.Exists(nomeRasterMapBiomas) and arcpy.Exists(nomeRasterLandSatIrrigacao):

                arcpy.AddMessage('Filtrando as areas irrigadas do arquivo LandSat: {LandSat}'.format(LandSat = os.path.basename(nomeRasterLandSatIrrigacao)))
        
                # Processo: Extract by Mask
                rasterEntrada = nomeRasterLandSatIrrigacao
                rasterMascara = nomeRasterMapBiomas
                rasterResultado = nomeRasterLandSatIrrigacaoValidado
                
                arcpy.gp.ExtractByMask_sa(rasterEntrada, rasterMascara, rasterResultado)

        arcpy.AddMessage('Processo finalizado.')

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

# Parâmetros de entrada
diretorioMapBiomas = arcpy.GetParameterAsText(0)
diretorioLandSatAreasIrrigadas = arcpy.GetParameterAsText(1)
anoInicialHistorico = int(arcpy.GetParameterAsText(2))
anoFinalHistorico = int(arcpy.GetParameterAsText(3))
diretorioSaida= arcpy.GetParameterAsText(4)

if not File.existFile(diretorioMapBiomas):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioMapBiomas) )
    sys.exit(0)

if not File.existFile(diretorioLandSatAreasIrrigadas):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioLandSatAreasIrrigadas) )
    sys.exit(0)

if not File.existFile(diretorioSaida):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSaida) )
    sys.exit(0)

# Verifica a existencia da licenca da extensao ArcGIS Spatial Analyst 
arcpy.CheckOutExtension("Spatial")

# Define o workspace de processamento 
arcpy.env.workspace = diretorioSaida

arcpy.env.overwriteOutput = True

validarAreasIrrigadasLandSat(anoInicialHistorico, anoFinalHistorico)
