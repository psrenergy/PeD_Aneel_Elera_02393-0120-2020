#coding: utf-8
'''
Created on February 10, 2022

@author: Andre Granville
'''
# Import libraries
import arcpy, sys, time, os

NOME_ATRIBUTO_AREA = 'Area'
NOME_ATRIBUTO_NOME_BACIA = 'PV_NAME'
NOME_ATRIBUTO_NUMERO = 'PV'

def AtributeExiste(camada, atributo):
    listaAtributos = arcpy.ListFields(camada, atributo)

    fieldCount = len(listaAtributos)

    if (fieldCount == 1):
        return True
    else:
        return False
    
def exportarBaciasIncrementais(camadaBacia):
    
    arcpy.AddMessage(time.ctime() + ' Shape de bacias a ser dividido em incrementos de drenagem: {camada}'.format(camada=camadaBacia))

    # Inclui o atributo área na tabela associado ao shapefile
    if not AtributeExiste(camadaBacia, NOME_ATRIBUTO_AREA):
        arcpy.AddField_management(camadaBacia,NOME_ATRIBUTO_AREA,"Double")
        expression1 = "{0}".format("!SHAPE.area@SQUAREKILOMETERS!")        
        arcpy.CalculateField_management(camadaBacia, NOME_ATRIBUTO_AREA, expression1, "PYTHON", )
   
    #Ordena as bacias por área em ordem descendente
    numeroBacia=[]
    nomeBacia=[]
    areaBacia=[]
    atributos = [NOME_ATRIBUTO_AREA, NOME_ATRIBUTO_NUMERO, NOME_ATRIBUTO_NOME_BACIA]
    for rowBacia in sorted(arcpy.da.SearchCursor(camadaBacia, atributos), reverse=True):
        areaBacia.append(rowBacia[0])
        numeroBacia.append(int(rowBacia[1]))
        nomeBacia.append(rowBacia[2])
    
    arcpy.AddMessage(time.ctime() + ' - Exportando cada bacia para uma camada independente. Total de bacias a serem exportadas: {numBacias}'.format(numBacias=len(numeroBacia)))
    
    # Exporta cada bacia para uma camada independente
    camadaBacia_Layer = r"in_memory\camadaBacia_Layer"
    arcpy.MakeFeatureLayer_management(camadaBacia,camadaBacia_Layer)
    
    for iBacia in range(len(numeroBacia)):
        sqlWhere = NOME_ATRIBUTO_NUMERO + " = "  + str(numeroBacia[iBacia]) 
        arcpy.SelectLayerByAttribute_management (camadaBacia_Layer, "NEW_SELECTION", sqlWhere) 
        
        nomeCamadaSubBacia = str(numeroBacia[iBacia]) + '.shp'

        # Exclue a camada caso exista
        if arcpy.Exists(str(numeroBacia[iBacia]) + '.shp'):
            arcpy.Delete_management(str(numeroBacia[iBacia]) + '.shp')

        if arcpy.Exists(str(numeroBacia[iBacia]) + '.dbf'):
            arcpy.Delete_management(str(numeroBacia[iBacia]) + '.dbf')

        arcpy.CopyFeatures_management(camadaBacia_Layer, nomeCamadaSubBacia)

    #libera a memoria utilizada  
    arcpy.Delete_management("in_memory")
    
    arcpy.AddMessage(time.ctime() + ' - Bacias exportadas.')

    arcpy.AddMessage(time.ctime() + ' - Extraindo bacias incrementais...')

    # Erase da bacia de maior áreas com a de área imediatamente inferior
    for iBacia in range(len(numeroBacia)-1):
        baciaASerClipada = str(numeroBacia[iBacia]) + '.shp'
        baciaClip =  str(numeroBacia[iBacia+1]) + '.shp'
        
        baciaIncremental = str(numeroBacia[iBacia]) + '_' + str(numeroBacia[iBacia+1]) + '.shp'
        xy_tolerance = ""

        arcpy.AddMessage(time.ctime() + ' - Erase: [{BaciaClipada}-{baciaClip}]'.format(BaciaClipada = nomeBacia[iBacia], baciaClip=nomeBacia[iBacia+1]))
        
        # Executa o Erase
        arcpy.Erase_analysis(baciaASerClipada, baciaClip, baciaIncremental, "")

    # Merge das bacias incrementais em uma unica camada
    #nomeCamadaSaidaMerge = 'baciasIncrementais.shp'

    # for iBacia in range(len(numeroBacia)-1):
    #
        # if iBacia == 0:
            # incrementoBacia1 = str(numeroBacia[iBacia]) + '.shp'
            # incrementoBacia2 =  str(numeroBacia[iBacia+1]) + '.shp'
        # else:
            # incrementoBacia1 = nomeCamadaSaidaMerge
            # incrementoBacia2 =  str(numeroBacia[iBacia]) + '.shp'
            #
        # arcpy.Merge_management([incrementoBacia1, incrementoBacia2], nomeCamadaSaidaMerge)    
      
    
# Parametros de entrada
camadaBacia  = arcpy.GetParameterAsText(0)

if not arcpy.Exists(camadaBacia):
    arcpy.AddError("Camada inexistente: {arquivo}".format(arquivo=camadaBacia) )
    sys.exit(0)

arcpy.env.workspace = os.path.dirname(camadaBacia)

arcpy.env.overwriteOutput = True

exportarBaciasIncrementais(camadaBacia) 
