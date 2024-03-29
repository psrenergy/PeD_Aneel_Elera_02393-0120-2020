#coding: utf-8
'''
Created on January 17, 2022

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os
import traceback
from Util import File 

def filtrarCulturasIrrigadas(anoInicialHistorico, anoFinalHistorico):
    """
    Filtra das camadas de satelite, contendo o mapeamento dos cultivos irrigados, as areas
    que tenham intersecao espacial com as camadas do Mapbiomas.
    """
    pymsg=''
    msgs =''

    try:
        
        arcpy.AddMessage('Filtrando os cultivos irrigados das imagens de satelite, tomando como mascara de filtro, o mapeamento do Mapbioas...')
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            #Monta nome do raster do Mapbiomas referente ao ano <ano>
            nomeRasterMapBiomas = "mapbiomas_brazil_collection_60_" + str(ano) + "_Albers_clip_reclass_con.tif"
            nomeRasterMapBiomas = os.path.join(diretorioMapBiomas, nomeRasterMapBiomas)

            #Monta nome do raster de áreas irrigadas
            nomeImgSateliteIrrigacao = "sentinel_" + str(ano) + "_cultivos_irrigados.tif"
            nomeImgSateliteIrrigacao = os.path.join(diretorioImgSateliteAreasIrrigadas, nomeImgSateliteIrrigacao)

            nomeRasterFiltrado = "sentinel_" + str(ano) + "_cultivos_irrigados_filtrado_mapbiomas"

            if arcpy.Exists(nomeRasterMapBiomas) and arcpy.Exists(nomeImgSateliteIrrigacao):

                arcpy.AddMessage('Filtrando imagem de satelite: {Satelite}'.format(Satelite = os.path.basename(nomeImgSateliteIrrigacao)))
        
                # Processo: Extract by Mask
                rasterEntrada = nomeImgSateliteIrrigacao
                rasterMascara = nomeRasterMapBiomas
                rasterResultado = nomeRasterFiltrado
                
                nomeRasterFiltrado = arcpy.sa.ExtractByMask(rasterEntrada, rasterMascara)
                nomeRasterFiltrado.save(rasterResultado)

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
diretorioImgSateliteAreasIrrigadas = arcpy.GetParameterAsText(1)
anoInicialHistorico = int(arcpy.GetParameterAsText(2))
anoFinalHistorico = int(arcpy.GetParameterAsText(3))
diretorioSaida= arcpy.GetParameterAsText(4)

if not arcpy.Exists(diretorioMapBiomas):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioMapBiomas) )
    sys.exit(0)

if not arcpy.Exists(diretorioImgSateliteAreasIrrigadas):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioImgSateliteAreasIrrigadas) )
    sys.exit(0)

if not arcpy.Exists(diretorioSaida):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSaida) )
    sys.exit(0)


# Verifica a existencia da licenca da extensao ArcGIS Spatial Analyst 
arcpy.CheckOutExtension("Spatial")

# Define o workspace de processamento 
arcpy.env.workspace = diretorioSaida

arcpy.env.overwriteOutput = True

filtrarCulturasIrrigadas(anoInicialHistorico, anoFinalHistorico)
