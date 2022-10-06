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

NUMERO_DIAS_MES = 30
NUMERO_SEGUNDOS_DIA = 86400

def CalcularEvapotranspiracaoPotencialCultivo():
    """
        Calcula a evapotranspiração potencial dos cultivos
        
        Fórmula:
            ETpc = ETo * Kc
               EtO = evaporação de referencia (superfície)
               Kc  = coeficiente do cultivo   (tabela)
    """
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Computando a evapotranspiracao potencial por cultivo...')
    
    # Cria a tabela de evapotranspiracao potencial por cultivo por municipio
    configurarTabelaEvapotranspiracaoPotencialCultivoPorMunicipio(Constantes.TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO)
    
    nomeAtributoCodigoMunicipio=''
    nomeAtributoMediaEvapRef=''
    
    try:
        
        # Preenche estrutura de dados dos coeficientes de cultivo mensais de cada cultivo
        Kc={}
        atributos = ['ClasseCult', Constantes.MES1,Constantes.MES2,Constantes.MES3,Constantes.MES4,Constantes.MES5,Constantes.MES6,Constantes.MES7,Constantes.MES8,Constantes.MES9,Constantes.MES10,Constantes.MES11,Constantes.MES12]
        with arcpy.da.SearchCursor(tabelaCoefCultivo, atributos) as cursorCoefCultivo:
            for rowCoefCultivo in cursorCoefCultivo:
                
                classeCultivo = rowCoefCultivo[0]
                
                listaValoresMensais=[]
                for mes in range(1,13):
                    listaValoresMensais.append(rowCoefCultivo[mes])
                
                Kc[classeCultivo] = listaValoresMensais
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            #Popula as estruturas de dados com os dados das áreas irrigadas por cultivo e por municipio referente ao ano <ano>
            ListaCodigoMunicipio=[]
            ListaNomeMunicipio=[]
            ListaAreaMunicipio=[]
            ListaClasseCultivo=[]
            ListaAreaIrrigadaCultivo=[]

            arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))

            # Dados históricos de áreas irrigadas por cultivo e por município (variação por ANO)
            sqlWhere = Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) 
            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA]
            with arcpy.da.SearchCursor(tabelaHistoricoAreaIrrigadaPorCultivoPorMunicipio, atributos, sqlWhere) as cursorAreaIrrigCultivoMunicipio:
                for rowAreaIrrigCultivoMunicipio in cursorAreaIrrigCultivoMunicipio:
                    ListaCodigoMunicipio.append(rowAreaIrrigCultivoMunicipio[0])
                    ListaNomeMunicipio.append(rowAreaIrrigCultivoMunicipio[1])
                    ListaAreaMunicipio.append(rowAreaIrrigCultivoMunicipio[2])
                    ListaClasseCultivo.append(rowAreaIrrigCultivoMunicipio[4])
                    ListaAreaIrrigadaCultivo.append(rowAreaIrrigCultivoMunicipio[5])

            # se existem dados para o ano <ano>...
            if len(ListaCodigoMunicipio)>0:
                
                for mes in range(1,13):
                    
                    arcpy.AddMessage(time.ctime() + ' - mes {mes}'.format(mes=mes))

                    #Evaporação de referência por município, na etapa <ano,mes> 
                    
                    #Monta nome da camada de evaporação de referência média por município referente ao perído <ano,mes>
                    nomeCamadaEvapRefMediaMunicipio = "evaporacao_media_municipio__" + str(ano) + "_" + str(mes)
                    nomeCamadaEvapRefMediaMunicipio = os.path.join(diretorioSuperficieEvapRefMediaMunicipio, nomeCamadaEvapRefMediaMunicipio)
                    
                    if arcpy.Exists(nomeCamadaEvapRefMediaMunicipio):

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
                            
                            # Inclusao da Evaporação Potencial do Cultivo
                            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA , Constantes.NOME_ATRIBUTO_ETPOTENCIAL]
                            with arcpy.da.InsertCursor(Constantes.TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO, atributos) as cursorDestino:
                                
                                codMunicipio = ListaCodigoMunicipio[iMunicipio]
                                
                                if codMunicipio in EtO:
                                    nomeMunicipio = ListaNomeMunicipio[iMunicipio]
                                    areaMunicipio = ListaAreaMunicipio[iMunicipio]
                                    classeCultivo = ListaClasseCultivo[iMunicipio]
                                    areaIrrigadaCultivo = ListaAreaIrrigadaCultivo[iMunicipio]

                                    coefCultivo = Kc[classeCultivo][mes-1]
                                    EtPC = EtO[codMunicipio] * coefCultivo 
                                
                                    cursorDestino.insertRow((codMunicipio, nomeMunicipio, areaMunicipio, ano, mes, classeCultivo, areaIrrigadaCultivo, EtPC))

        # Cria um indice para a tabela Constantes.TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO
        atributos = [Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES]
        nomeIndice = "indice"
        arcpy.AddIndex_management(Constantes.TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO, atributos, nomeIndice, "NON_UNIQUE", "ASCENDING")
                         
        arcpy.AddMessage(time.ctime() + ' - Computo da evapotranspiracao potencial por cultivo finalizado...')

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
    

def CalcularFatorDisponibilidadeAguaCultivo():
    """
        Calcula o fator de disponibilidade de água (f) por cultura e por mês
        
        Fórmula:
        
        f = f0 +0,04(5 -ETrc) 
        
            f0  : fator fixo por cultivo
            ETrc: Evapotranspiração real do cultivo 
                    (Observação: Em razão de referência circular nas fórmulas, vamos usar o ETpc calculado anteriormente no fluxo)
        
    """
    
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Computando o fator de disponibilidade de agua por cultivo...')
    
    # Cria a tabela de fator de disponibilidade de água (f) por cultura e por mês
    configurarTabelaFatorDisponibilidadeAguaCultivo(Constantes.TABELA_FATOR_DISPONIBILIDADE_AGUA_POR_CULTIVO)
    
    try:

        # Preenche a estrutura de dados dos fatores de referencia de disponibilidade de agua  
        f0={}
        atributos = ['ClasseCult', Constantes.NOME_ATRIBUTO_FAT_DSP_AGUA_REF]
        with arcpy.da.SearchCursor(tabelaFatorDispAguaRefPorCultivo, atributos) as cursorFatorDisponibilidadeRef:
            for rowFatorDisponibilidadeRef in cursorFatorDisponibilidadeRef:
                
                classeCultivo = rowFatorDisponibilidadeRef[0]
                f0[classeCultivo] = rowFatorDisponibilidadeRef[1]
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))

            for mes in range(1,13):

                arcpy.AddMessage(time.ctime() + ' - mes {mes}'.format(mes=mes))

                # Evaporação Potencial por Cultivo
                sqlWhere = Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes) 
                atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_ETPOTENCIAL]
                with arcpy.da.SearchCursor(Constantes.TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO, atributos, sqlWhere) as cursorETPt:
                    for rowETPt in cursorETPt:
                        codigoMunicipio = rowETPt[0]
                        nomeMunicipio   = rowETPt[1]
                        classeCultivo   = rowETPt[2]
                        EtPt            = rowETPt[3]
                        
                        if EtPt:
                            f = f0[classeCultivo] + 0.04 * (5 - EtPt) 
                        else:
                            f=0
                            
                        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_FAT_DSP_AGUA]
                        with arcpy.da.InsertCursor(Constantes.TABELA_FATOR_DISPONIBILIDADE_AGUA_POR_CULTIVO, atributos) as cursorDestino:
                            cursorDestino.insertRow((codigoMunicipio, nomeMunicipio, ano, mes, classeCultivo, f))
    
        # Cria um indice para a tabela Constantes.TABELA_FATOR_DISPONIBILIDADE_AGUA_POR_CULTIVO
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES]
        nomeIndice = "indice"
        arcpy.AddIndex_management(Constantes.TABELA_FATOR_DISPONIBILIDADE_AGUA_POR_CULTIVO, atributos, nomeIndice, "NON_UNIQUE", "ASCENDING")

        arcpy.AddMessage(time.ctime() + ' - Fator de disponibilidade de agua por cultivo computado.')

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
    
def CalcularKs():
    """
        Fórmula:
        
        Ks = (1 + log(LAA+1)/log(CTA+1))/2
             LAA = lamina atual de dagua (mm)           
             CTA = Capacidade total de armazenamento (mm)
               
    """
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Computando o coeficiente de umidade do solo por cultivo (Ks) ...')
    
    # Cria a tabela para armazenasa o histórico de coefiecientes de umidade do solo por cultivo e por município (Ks)
    configurarTabelaCoefUmidadeSolo(Constantes.TABELA_COEF_UMIDADE_SOLO)
    
    try:
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            #Popula as estruturas de dados com a capacidade total de armazenamento por cultivo e por municipio referente ao ano <ano>
            ListaCodigoMunicipio=[]
            ListaNomeMunicipio=[]
            ListaClasseCultivo=[]
            ListaCTA=[]

            arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))

            # Dados históricos de capacidade total de armazenamento por cultivo e por município (variação por ANO)
            sqlWhere = Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) 
            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_CAP_TOTAL_ARM]
            with arcpy.da.SearchCursor(Constantes.TABELA_CAPACIDADE_TOTAL_ARMAZENAMENTO_POR_CULTIVO, atributos, sqlWhere) as cursorCTA:
                for rowCTA in cursorCTA:
                    ListaCodigoMunicipio.append(rowCTA[0])
                    ListaNomeMunicipio.append(rowCTA[1])
                    ListaClasseCultivo.append(rowCTA[3])
                    ListaCTA.append(rowCTA[4])

            # se existem dados para o ano <ano>...
            if len(ListaCodigoMunicipio) > 0:

                for mes in range(1,13):

                    arcpy.AddMessage(time.ctime() + ' - Mes {mes}'.format(mes=mes))
                     
                    for iMunicipio in range(len(ListaCodigoMunicipio)):
                        
                        LaminaDagua={}
                        sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = " + "'" + ListaCodigoMunicipio[iMunicipio]  + "' AND " + Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes) 
                        atributos = [Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_LAMINA_DAGUA]
                        with arcpy.da.SearchCursor(Constantes.TABELA_LAMINA_DAGUA_CULTIVO, atributos, sqlWhere) as cursorLaminaDAgua:
                            for rowLaminaDAgua in cursorLaminaDAgua:
                                
                                classeCultivo = rowLaminaDAgua[0]
                                LaminaDagua[classeCultivo] = rowLaminaDAgua[1]
                        
                        if LaminaDagua:
                            
                            LAA = LaminaDagua[ListaClasseCultivo[iMunicipio]]
                            CTA = ListaCTA[iMunicipio] 
                            
                            Ks = (1 + math.log(LAA+1)/math.log(CTA+1) ) /2
                            
                            # Inclusao do Coeficiente de umidade do solo por Cultivo por Municipio
                            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_COEF_UMIDADE_SOLO]
                            with arcpy.da.InsertCursor(Constantes.TABELA_COEF_UMIDADE_SOLO, atributos) as cursorDestino:
                                cursorDestino.insertRow((ListaCodigoMunicipio[iMunicipio], ListaNomeMunicipio[iMunicipio], ano, mes, ListaClasseCultivo[iMunicipio], Ks))
                     
        # Cria um indice para a tabela Constantes.TABELA_COEF_UMIDADE_SOLO
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO]
        nomeIndice = "indice"
        arcpy.AddIndex_management(Constantes.TABELA_COEF_UMIDADE_SOLO, atributos, nomeIndice, "UNIQUE", "ASCENDING")

        arcpy.AddMessage(time.ctime() + ' - Coeficiente de umidade do solo por cultivo (Ks) computado')

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
    
def CalcularLaminaAtualAgua():
    """
        Fórmula:
        
        LAA = CTA * f
              LAA = Lamina atual de água (mm)
              CTA = Capacidade total de armazenamento (mm)           
                f = Fator de disponibilidade de água quando ainda não estresse hídrico
               
    """
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Computando a lamina atual de agua por cultivo (LAA) ...')
    
    # Cria a tabela de lamina dagua por cultivo e por município (LAA)
    configurarTabelaLaminaDAgua(Constantes.TABELA_LAMINA_DAGUA_CULTIVO)
    
    try:
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            #Popula as estruturas de dados com a capacidade total de armazenamento por cultivo e por municipio referente ao ano <ano>
            ListaCodigoMunicipio=[]
            ListaNomeMunicipio=[]
            ListaClasseCultivo=[]
            ListaCTA=[]

            arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))

            # Dados históricos de áreas irrigadas por cultivo e por município (variação por ANO)
            sqlWhere = Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) 
            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_CAP_TOTAL_ARM]
            with arcpy.da.SearchCursor(Constantes.TABELA_CAPACIDADE_TOTAL_ARMAZENAMENTO_POR_CULTIVO, atributos, sqlWhere) as cursorCTA:
                for rowCTA in cursorCTA:
                    ListaCodigoMunicipio.append(rowCTA[0])
                    ListaNomeMunicipio.append(rowCTA[1])
                    ListaClasseCultivo.append(rowCTA[3])
                    ListaCTA.append(rowCTA[4])

            # se existem dados para o ano <ano>...
            if len(ListaCodigoMunicipio) > 0:

                for mes in range(1,13):

                    arcpy.AddMessage(time.ctime() + ' - Mes {mes}'.format(mes=mes))
                     
                    for iMunicipio in range(len(ListaCodigoMunicipio)):

                        f={}
                        sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = " + "'" + ListaCodigoMunicipio[iMunicipio]  + "' AND " + Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes) 
                        atributos = [Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_FAT_DSP_AGUA]
                        with arcpy.da.SearchCursor(Constantes.TABELA_FATOR_DISPONIBILIDADE_AGUA_POR_CULTIVO, atributos, sqlWhere) as cursorFatorDspAgua:
                            for rowFatorDspAgua in cursorFatorDspAgua:
                                classeCultivo = rowFatorDspAgua[0]
                                f[classeCultivo] = rowFatorDspAgua[1]
                        
                        if f:
                            
                            LAA = ListaCTA[iMunicipio] * f[ListaClasseCultivo[iMunicipio]]
                            
                            # Inclusao da Lâmina DÁgua por Cultivo por Municipio
                            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_LAMINA_DAGUA]
                            with arcpy.da.InsertCursor(Constantes.TABELA_LAMINA_DAGUA_CULTIVO, atributos) as cursorDestino:
                                cursorDestino.insertRow((ListaCodigoMunicipio[iMunicipio], ListaNomeMunicipio[iMunicipio], ano, mes, ListaClasseCultivo[iMunicipio], LAA))
                     

        # Cria um indice para a tabela Constantes.TABELA_LAMINA_DAGUA_CULTIVO
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES]
        nomeIndice = "indice"
        arcpy.AddIndex_management(Constantes.TABELA_LAMINA_DAGUA_CULTIVO, atributos, nomeIndice, "NON_UNIQUE", "ASCENDING")
                    
        arcpy.AddMessage(time.ctime() + ' - Lamina atual de agua computado.')
            
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

def CalcularCapacidadeTotalArmazenamento():
    """
        Fórmula:
        
        CTA = CAD * Z
              CTA = Capacidade total de armazenamento (mm)                     (obs: ao multiplica mm/cm por cm, cota-se o cm)
              CAD = Capacidade de água disponível (mm/cm)                      (Camada de disponibildiade de água da EMBRAPA)
               Z  = Profundidade efetiva do sistema radicular da cultura (cm)  (valor fixo por cultura)
    """
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Computando a capacidade total de armazenamento por cultivo (CTA) ...')
    
    # Cria a tabela de capacidade total de armazenamento por cultura (CTA)
    configurarTabelaCapacidadeTotalArmazenamento(Constantes.TABELA_CAPACIDADE_TOTAL_ARMAZENAMENTO_POR_CULTIVO)
    
    try:
        
        # Preenche a estrutura de dados da profundidade efetiva do sistema radicular da cultura  
        z={}
        atributos = ['ClasseCult', Constantes.NOME_ATRIBUTO_PROF_RAIZ_CULTIVO]
        with arcpy.da.SearchCursor(tabelaProfSistemaRadicularPorCultivo, atributos) as cursorZ:
            for rowZ in cursorZ:
                classeCultivo = rowZ[0]
                z[classeCultivo] = rowZ[1]

        workspace_tmp = arcpy.env.workspace 

        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))
            
            arcpy.env.workspace = diretorioCamadaCultivoIrrigado
            
            wildCard = "*" + str(ano) + "_cultivos_irrigados"
            camadasCultivoIrrigado = arcpy.ListRasters(wildCard)
            if camadasCultivoIrrigado: 
                
                arcpy.env.workspace= workspace_tmp
                
                camadaCultivoIrrigado = camadasCultivoIrrigado[0]
                camadaCultivoIrrigado = os.path.join(diretorioCamadaCultivoIrrigado, camadaCultivoIrrigado)
                
                # Processo: Raster to Point (conversao do formato raster para pontos)
                CamadaPontosMapBiomas = camadaCultivoIrrigado + "_points" 
                CamadaPontosMapBiomas = os.path.join(diretorioCamadaCultivoIrrigado, CamadaPontosMapBiomas)

                arcpy.RasterToPoint_conversion(camadaCultivoIrrigado, CamadaPontosMapBiomas, "Value")
                
                # Processo: Polygon to Raster (converte a camada de disponibilidade de água do formato de polígono para Raster)
                diretorioEmbrapa = os.path.dirname(camadaEmbrapaAguaDispSolo)
                nomeRasterEmbrapaAguaDispSolo = "Brasil_AD_solos_v5_sao_francisco_albers.tif"
                nomeRasterEmbrapaAguaDispSolo = os.path.join(diretorioEmbrapa, nomeRasterEmbrapaAguaDispSolo)
                
                valueField = "Total_AD"
                cellsize = 100
                arcpy.PolygonToRaster_conversion(camadaEmbrapaAguaDispSolo, valueField, nomeRasterEmbrapaAguaDispSolo, "CELL_CENTER", "NONE", cellsize)
                
                # Processo: Extract value to points (exporta os valores de disponibilidade de água do raster da Embrapa, nas coordenadas definidas pelos pontos da camada de Mapbiomas )
                CamadaPontosMapBiomasAD = CamadaPontosMapBiomas + "_AD" 
                CamadaPontosMapBiomasAD = os.path.join(diretorioCamadaCultivoIrrigado, CamadaPontosMapBiomasAD)

                arcpy.gp.ExtractValuesToPoints_sa(CamadaPontosMapBiomas, nomeRasterEmbrapaAguaDispSolo, CamadaPontosMapBiomasAD, "NONE", "VALUE_ONLY")
                
                # Processo: Spatial Join (join entre as camadas de Municipios com e de culturas irrigadas com informação de disponibilidade de água)
                targetFeatures = CamadaPontosMapBiomasAD
                joinFeatures = camadaMunicipios
                CamadaJoinMunicipioMapBiomasAD = CamadaPontosMapBiomasAD + "_Municipio"
                CamadaJoinMunicipioMapBiomasAD = os.path.join(diretorioCamadaCultivoIrrigado, CamadaJoinMunicipioMapBiomasAD)
                
                fieldmappings = arcpy.FieldMappings()
                fieldmappings.addTable(targetFeatures)
                fieldmappings.addTable(joinFeatures)
                
                # renomeia atributo que identifica a classe de cultivo
                classeCultivoFieldIndex = fieldmappings.findFieldMapIndex("grid_code")
                fieldmap = fieldmappings.getFieldMap(classeCultivoFieldIndex)
                field = fieldmap.outputField
                field.name = "ClasseCultivo"
                field.aliasName = "ClasseCultivo"
                fieldmap.outputField = field
                fieldmappings.replaceFieldMap(classeCultivoFieldIndex, fieldmap)
                
                # renomeia atributo que identifica a disponibilidae de agua no solo
                ADFieldIndex = fieldmappings.findFieldMapIndex("RASTERVALU")
                fieldmap = fieldmappings.getFieldMap(ADFieldIndex)
                field = fieldmap.outputField
                field.name = "Total_AD"
                field.aliasName = "Total_AD"
                fieldmap.outputField = field
                fieldmappings.replaceFieldMap(ADFieldIndex, fieldmap)
                
                arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, CamadaJoinMunicipioMapBiomasAD, "JOIN_ONE_TO_ONE", "KEEP_ALL", fieldmappings)
                
                #Calcula a disponibilidade média de água por [Município, Cultivo] no Ano
                tabelaADPorCultivoPorMunicipio = "tabela_AD_{ano}_Medio_Por_Cultivo_Por_Municipio".format(ano=ano)
                tabelaADPorCultivoPorMunicipio = os.path.join(diretorioCamadaCultivoIrrigado, tabelaADPorCultivoPorMunicipio)

                nomeAtributoEstatistica = Constantes.NOME_ATRIBUTO_TOTAL_AD
                estatistica = [[nomeAtributoEstatistica, 'MEAN']]  
                atributoAgregador = "CD_MUN;NM_MUN;ClasseCultivo"
                
                arcpy.Statistics_analysis(CamadaJoinMunicipioMapBiomasAD, tabelaADPorCultivoPorMunicipio, estatistica, atributoAgregador)

                #Calcula do CTA por [Municipio, Cultivo] do Ano = Ano
                atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, 'MEAN_Total_AD']
                with arcpy.da.SearchCursor(tabelaADPorCultivoPorMunicipio, atributos) as cursorOrigem:
                    
                    for rowOrigem in cursorOrigem:
                        codigoMunicipio = rowOrigem[0]
                        nomeMunicipio   = rowOrigem[1]
                        classeCultivo   = rowOrigem[2]
                        ADMedio         = rowOrigem[3]
                        
                        if ADMedio:
                            CTA = ADMedio * z[classeCultivo]
                        
                            # Inclusão na tabela Capacidade total de armazenamento
                            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_CAP_TOTAL_ARM]
                            with arcpy.da.InsertCursor(Constantes.TABELA_CAPACIDADE_TOTAL_ARMAZENAMENTO_POR_CULTIVO, atributos) as cursorDestino:
                                cursorDestino.insertRow((codigoMunicipio, nomeMunicipio, ano, classeCultivo, CTA))
        
        arcpy.AddMessage(time.ctime() + ' - CTA Computado com sucesso.')
            
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

def CalcularETrc():
    """
        Calcula a evapotranspiração real dos cultivos
        
        Fórmula:
            ETrc = ETpc * Ks
               ETrc = evapotranspiração real do cultivo
               ETpc = evapotranspiração potencial do cultivo
               Ks   = coeficiente umidade do solo
               
    """
    pymsg = ""
    msgs = ""
    
    arcpy.AddMessage(time.ctime() + ' - Computando a evapotranspiracao real por cultivo (ETrc) ...')
    
    # Cria a tabela para armazena o histórico da evapotranspiracao real por cultivo e por município (ETrc)
    configurarTabelaEvapotranspiracaoRealCultivo(Constantes.TABELA_EVAPOTRANSPIRACAO_REAL_POR_CULTIVO)
    
    try:
        
        # Evapotranspiracao Potencial
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA, Constantes.NOME_ATRIBUTO_ETPOTENCIAL]
        with arcpy.da.SearchCursor(Constantes.TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO, atributos) as cursorETpc:
            for rowETpc in cursorETpc:
                codigoMunicipio = rowETpc[0]
                nomeMunicipio = rowETpc[1]
                areaMunicipio = rowETpc[2]
                ano = rowETpc[3]
                mes = rowETpc[4]
                classeCultivo = rowETpc[5]
                areaIrrigCultivo = rowETpc[6]
                ETpc = rowETpc[7]
                 
                sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = " + "'" + codigoMunicipio  + "' AND " + Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes) + " AND " + Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO + " = "  + str(classeCultivo)
                atributos = [Constantes.NOME_ATRIBUTO_COEF_UMIDADE_SOLO]
                with arcpy.da.SearchCursor(Constantes.TABELA_COEF_UMIDADE_SOLO, atributos, sqlWhere) as cursorCoefUmidadeSolo:
                    for rowCoefUmidadeSolo in cursorCoefUmidadeSolo:
                        ETrc = ETpc * rowCoefUmidadeSolo[0]
                        
                        # Insere na tabela de Evapotranspiracao Real
                        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA, Constantes.NOME_ATRIBUTO_ETREAL]
                        with arcpy.da.InsertCursor(Constantes.TABELA_EVAPOTRANSPIRACAO_REAL_POR_CULTIVO, atributos) as cursorDestino:
                            cursorDestino.insertRow((codigoMunicipio, nomeMunicipio, areaMunicipio, ano, mes, classeCultivo, areaIrrigCultivo, ETrc))

                        
        arcpy.AddMessage(time.ctime() + ' - Evapotranspiracao real por cultivo computado.')

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
        
def CalcularCoeficienteUmidadeSolo():
    """
        Calcula o coeficiente de umidade do solo (Ks)
        
        Fórmula:
        
        Ks = ( 1 + log(LAA+1)/log(CTA+1) )/2
             CTA = CAD * Z
             LAA = CTA * f
             
             LAA = lâmina atual de água (mm)
             CTA = Capacidade total de armazenamento (mm)
             CAD = Capacidade de água disponível (mm/cm) : vem da camada da EMBRAPA
             Z   = Profundidade efetiva do sistema radicular da cultura (cm)
                    (valor fixo por cultura)
             f   = Fator de disponibilidade de água quando ainda não há estresse hídrico (adimensional) 
                    (depende da cultura. Valor mensal)
                  
    """
    #Cálculo Capacidade total de armazenamento (CTA)
    CalcularCapacidadeTotalArmazenamento()
    
    # Cálculo do Fator f
    CalcularFatorDisponibilidadeAguaCultivo()
    
    #Cálculo da lâmina atual de água (LAA)
    CalcularLaminaAtualAgua()
    
    #Cálculo do coeficiente de umidade do solo (Ks)
    CalcularKs()
    
    
def CalcularEvapotranspiracaoRealCultivo():
    """
        Calcula a evapotranspiração real dos cultivos
        
        Fórmula:
            ETrc = ETpc * Ks
               ETrc = evapotranspiração real do cultivo
               ETpc = evapotranspiração potencial do cultivo
               Ks   = coeficiente umidade do solo
               
            ETpc = ETo * Kc
            Ks ....
    """

    # Cálculo do ETpc
    CalcularEvapotranspiracaoPotencialCultivo()
    
    # Cálculo do Ks
    CalcularCoeficienteUmidadeSolo()
    
    # Cálculo da Evapotranspiracao Real do Cultivo
    CalcularETrc()
    
def CalcularPrecipitacaoEfetiva():
    """
        Calcula a precipitação efetiva média mensal por cultivo, por municipio

        Fórmula:
            Pe = SF(0,70917 * Pt**0,82416 - 0,11556) * (10**(0,02426 * ETrc) ) 
               Pt   = Precipitação média mensal (mm) 
               ETrc = Evapotranspiração média mensal da cultura (igual à evpotranspiração real) 
               SF   = fator de armazenamento de água no solo (=1)
        
    """
    pymsg = ""
    msgs = ""

    nomeAtributoCodigoMunicipio=''
    nomeAtributoPrecipitacaoMedia=''
    
    arcpy.AddMessage(time.ctime() + ' - Computando a precipitacao efetiva media por cultivo...')
    
    # Cria a tabela de precipitação efetiva média por cultivo por municipio
    configurarTabelaPrecpitacaoEfetivaCultivoPorMunicipio(Constantes.TABELA_PRECIPITACAO_EFETIVA_POR_CULTIVO)

    try:
        
        for ano in range(anoInicialHistorico, anoFinalHistorico + 1):

            #Popula as estruturas de dados com os dados das áreas irrigadas por cultivo e por municipio referente ao ano <ano>
            ListaCodigoMunicipio=[]
            ListaNomeMunicipio=[]
            ListaClasseCultivo=[]
            ListaAreaIrrigadaCultivo=[]

            arcpy.AddMessage(time.ctime() + ' - Ano {ano}'.format(ano=ano))
            
            # Dados históricos de áreas irrigadas por cultivo e por município (variação por ANO)
            sqlWhere = Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) 
            atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA]
            with arcpy.da.SearchCursor(tabelaHistoricoAreaIrrigadaPorCultivoPorMunicipio, atributos, sqlWhere) as cursorAreaIrrigCultivoMunicipio:
                for rowAreaIrrigCultivoMunicipio in cursorAreaIrrigCultivoMunicipio:
                    ListaCodigoMunicipio.append(rowAreaIrrigCultivoMunicipio[0])
                    ListaNomeMunicipio.append(rowAreaIrrigCultivoMunicipio[1])
                    ListaClasseCultivo.append(rowAreaIrrigCultivoMunicipio[3])
                    ListaAreaIrrigadaCultivo.append(rowAreaIrrigCultivoMunicipio[4])
    
            if len(ListaCodigoMunicipio)>0:
                
                for mes in range(1,13):
                    
                    arcpy.AddMessage(time.ctime() + ' - mes {mes}'.format(mes=mes))

                    #Monta nome da camada de precipitação média por município referente ao perído <ano,mes>
                    nomeCamadaPrecipitacaoMediaMunicipio = "precipitacao_media_por_municipio_" + str(ano) + "_" + str(mes).zfill(2)
                    nomeCamadaPrecipitacaoMediaMunicipio = os.path.join(diretorioSuperficiePrecipitacaoMedia, nomeCamadaPrecipitacaoMediaMunicipio)
                    
                    if arcpy.Exists(nomeCamadaPrecipitacaoMediaMunicipio):
    
                        if not nomeAtributoCodigoMunicipio or not nomeAtributoPrecipitacaoMedia:
                            
                            for f in arcpy.ListFields(nomeCamadaPrecipitacaoMediaMunicipio):
                                if f.aliasName == Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO:
                                    nomeAtributoCodigoMunicipio = f.name
                                     
                                if f.aliasName == Constantes.NOME_ATRIBUTO_MEDIA_SUPERFICIE:
                                    nomeAtributoPrecipitacaoMedia = f.name
                
                        # Precipitação media por município
                        precipitacaoMediaMunicipio={}
                        atributos = [nomeAtributoCodigoMunicipio, nomeAtributoPrecipitacaoMedia]
                        with arcpy.da.SearchCursor(nomeCamadaPrecipitacaoMediaMunicipio, atributos) as cursorPrecipitacaoMedia:
                            for rowPrecipitacaoMedia in cursorPrecipitacaoMedia:
                                codMunicipio = rowPrecipitacaoMedia[0]
                                precipitacaoMedia = rowPrecipitacaoMedia[1] 
                                precipitacaoMediaMunicipio[codMunicipio]  = precipitacaoMedia 
                                    
                        for iMunicipio in range(len(ListaCodigoMunicipio)):

                            # Cáclulo da precipitação efetiva media
    
                            sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = " + "'" + ListaCodigoMunicipio[iMunicipio]  + "' AND " + Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes) + " AND " + Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO + " = "  + str(ListaClasseCultivo[iMunicipio])
                            atributos = [Constantes.NOME_ATRIBUTO_ETREAL]
                            with arcpy.da.SearchCursor(Constantes.TABELA_EVAPOTRANSPIRACAO_REAL_POR_CULTIVO, atributos, sqlWhere) as cursorETrc:
                                for rowETRc in cursorETrc:
                                    ETrc = rowETRc[0] 
                                    PrecipitacaoEfetiva = (0.70917 * math.pow(precipitacaoMediaMunicipio[codMunicipio],0.82416) - 0.11556) * (math.pow(10, 0.02426 * ETrc))
                                    
                                    if PrecipitacaoEfetiva <0:
                                        PrecipitacaoEfetiva = 0
                                        
                                    # Inclusao da Precipitacao Media por Cultivo por Municipio
                                    atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA , Constantes.NOME_ATRIBUTO_PRECIP_EFETIVA]
                                    with arcpy.da.InsertCursor(Constantes.TABELA_PRECIPITACAO_EFETIVA_POR_CULTIVO, atributos) as cursorDestino:
                                        cursorDestino.insertRow((ListaCodigoMunicipio[iMunicipio], ListaNomeMunicipio[iMunicipio], ano, mes, ListaClasseCultivo[iMunicipio], ListaAreaIrrigadaCultivo[iMunicipio], PrecipitacaoEfetiva))
                            
        # Cria um indice para a tabela Constantes.TABELA_PRECIPITACAO_EFETIVA_POR_CULTIVO
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO]
        nomeIndice = "indice"
        arcpy.AddIndex_management(Constantes.TABELA_PRECIPITACAO_EFETIVA_POR_CULTIVO, atributos, nomeIndice, "UNIQUE", "ASCENDING")

        arcpy.AddMessage(time.ctime() + ' - Computo da precipitacao efetiva por cultivo finalizado...')

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

def CalcularNecessidadeIrrigacao():
    """
       Calcula o volume de água total necessário para a irrigação dos cultivos.
       O resultado será agregado por <ano, mes, cultivo, municipio>
       
       Formula: 
          In = ((ETrc - Pe) * área cultivo)) / eficiência aplicação
               In           = Necessidade de irrgiação (m3/s)
               ETrc         = Evapotranspiração real da cultura 
               Pe           = Precipitação efetiva
               Área cultivo = em hectares
               Eficiência aplicação: [0.6..0.9]. Por hora, adotar 0.7 como padrão
               
       Regras de conversão de unidades:
          1 mm = 10m3/ha        
            
    """

    pymsg = ""
    msgs = ""

    arcpy.AddMessage(time.ctime() + ' - Computando a necessidade de irrigacao por cultivo e por municipio...')

    # ETrc
    CalcularEvapotranspiracaoRealCultivo()
    
    # Pe
    CalcularPrecipitacaoEfetiva()
    
    try:

        # Cria a tabela de necessidade de irrigação por cultivo, por municipio
        configurarTabelaNecessidadeIrrigacaoPorCultivoPorMunicipio(Constantes.TABELA_NECESSIDADE_IRRIGACAO_POR_CULTIPO_POR_MUNICIPIO)
        
        # Tabela de evapotranspiracao real 
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA, Constantes.NOME_ATRIBUTO_ETREAL]
        with arcpy.da.SearchCursor(Constantes.TABELA_EVAPOTRANSPIRACAO_REAL_POR_CULTIVO, atributos) as cursorETrc:
            for rowETrc in cursorETrc:
                codigoMunicipio= rowETrc[0]
                nomeMunicipio= rowETrc[1]
                areaMunicipio = rowETrc[2]
                ano = rowETrc[3]
                mes =  rowETrc[4]
                classeCultivo = rowETrc[5]
                areaIrrigadaCultivo = rowETrc[6]
                ETrc = rowETrc[7]
                 
                # Tabela de Precipitacao Efetiva
                sqlWhere = Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO + " = " + "'" + codigoMunicipio  + "' AND " + Constantes.NOME_ATRIBUTO_ANO + " = "  + str(ano) + " AND " + Constantes.NOME_ATRIBUTO_MES + " = "  + str(mes) + " AND " + Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO + " = "  + str(classeCultivo)
                atributos = [Constantes.NOME_ATRIBUTO_PRECIP_EFETIVA]
                with arcpy.da.SearchCursor(Constantes.TABELA_PRECIPITACAO_EFETIVA_POR_CULTIVO, atributos, sqlWhere) as cursorPe:
                    for rowPe in cursorPe:
                        precipitacaoEfetiva = rowPe[0]
                        
                        #Por hora, aplica-se o fator default de 0.6 para a eficiencia da aplicao 
                        eficAplicacao = 0.6

                        # Converte a evapotranspiração de valores médios mensais para total mensal. 
                        # (obs: A precipitação já está expressa em milimiteros por mês no CSV de origem)
                        ETrc = ETrc * NUMERO_DIAS_MES

                        # Para tranformar mm/ha em m3/ha, multiplica-se 10 
                        necessidadeIrrigacao = ((ETrc-precipitacaoEfetiva) * (areaIrrigadaCultivo * 10) ) / eficAplicacao
                        
                        # converte de m3/mês para m3/s
                        necessidadeIrrigacao = (necessidadeIrrigacao/NUMERO_DIAS_MES)/NUMERO_SEGUNDOS_DIA
                        
                        if necessidadeIrrigacao<0:
                            necessidadeIrrigacao = 0
                        
                        # Inclusao na tabela de necessidade de irrigacao
                        #atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA , Constantes.NOME_ATRIBUTO_PRECIP_EFETIVA, Constantes.NOME_ATRIBUTO_ETREAL, Constantes.NOME_ATRIBUTO_EFIC_APLICACAO, Constantes.NOME_ATRIBUTO_NECES_IRRIG]
                        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_NOME_MUNICIPIO, Constantes.NOME_ATRIBUTO_AREA_MUNICIPIO_HA, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES, Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO, Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA , Constantes.NOME_ATRIBUTO_PRECIP_EFETIVA, Constantes.NOME_ATRIBUTO_ETREAL, Constantes.NOME_ATRIBUTO_EFIC_APLICACAO, Constantes.NOME_ATRIBUTO_NECES_IRRIG]
                        with arcpy.da.InsertCursor(Constantes.TABELA_NECESSIDADE_IRRIGACAO_POR_CULTIPO_POR_MUNICIPIO, atributos) as cursorDestino:
                            cursorDestino.insertRow((codigoMunicipio, nomeMunicipio, areaMunicipio, ano, mes, classeCultivo, areaIrrigadaCultivo, precipitacaoEfetiva, ETrc, eficAplicacao, necessidadeIrrigacao))
                        
        # Cria um indice para a tabela Constantes.TABELA_NECESSIDADE_IRRIGACAO_POR_CULTIPO_POR_MUNICIPIO
        atributos = [Constantes.NOME_ATRIBUTO_CODIGO_MUNICIPIO, Constantes.NOME_ATRIBUTO_ANO, Constantes.NOME_ATRIBUTO_MES]
        nomeIndice = "indice"
        arcpy.AddIndex_management(Constantes.TABELA_NECESSIDADE_IRRIGACAO_POR_CULTIPO_POR_MUNICIPIO, atributos, nomeIndice, "NON_UNIQUE", "ASCENDING")
        
        arcpy.AddMessage(time.ctime() + ' - Necessidade de irrigacao por cultivo, por municpio computado.')

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

def configurarTabelaCoefUmidadeSolo(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")
     
        nomeAtributo = Constantes.NOME_ATRIBUTO_COEF_UMIDADE_SOLO
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
    
def configurarTabelaLaminaDAgua(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")
     
        nomeAtributo = Constantes.NOME_ATRIBUTO_LAMINA_DAGUA
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
    
def configurarTabelaCapacidadeTotalArmazenamento(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")
     
        nomeAtributo = Constantes.NOME_ATRIBUTO_CAP_TOTAL_ARM
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
    
def configurarTabelaFatorDisponibilidadeAguaCultivo(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_FAT_DSP_AGUA
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

def configurarTabelaNecessidadeIrrigacaoPorCultivoPorMunicipio(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_MES
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "TEXT", "", "", "50", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_CULTIVO_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_PRECIP_EFETIVA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_ETREAL
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_EFIC_APLICACAO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_NECES_IRRIG
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

def configurarTabelaEvapotranspiracaoRealCultivo(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_MES
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_ETREAL
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

def configurarTabelaEvapotranspiracaoPotencialCultivoPorMunicipio(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_MES
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_ETPOTENCIAL
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

def configurarTabelaPrecpitacaoEfetivaCultivoPorMunicipio(nomeTabela):
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

        nomeAtributo = Constantes.NOME_ATRIBUTO_CLASSE_CULTIVO
        arcpy.AddField_management(nomeTabela, nomeAtributo, "SHORT", "", "", "50", "", "", "REQUIRED")

        nomeAtributo = Constantes.NOME_ATRIBUTO_AREA_IRRIG_HA
        arcpy.AddField_management(nomeTabela, nomeAtributo, "DOUBLE", "", "", "", "", "", "REQUIRED")
        
        nomeAtributo = Constantes.NOME_ATRIBUTO_PRECIP_EFETIVA
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
tabelaHistoricoAreaIrrigadaPorCultivoPorMunicipio = arcpy.GetParameterAsText(0)
tabelaCoefCultivo = arcpy.GetParameterAsText(1)
tabelaFatorDispAguaRefPorCultivo = arcpy.GetParameterAsText(2)
tabelaProfSistemaRadicularPorCultivo = arcpy.GetParameterAsText(3)
diretorioSuperficieEvapRefMediaMunicipio = arcpy.GetParameterAsText(4)
diretorioSuperficiePrecipitacaoMedia = arcpy.GetParameterAsText(5)
diretorioCamadaCultivoIrrigado = arcpy.GetParameterAsText(6)
camadaEmbrapaAguaDispSolo = arcpy.GetParameterAsText(7)
camadaMunicipios = arcpy.GetParameterAsText(8)
anoInicialHistorico = int(arcpy.GetParameterAsText(9))
anoFinalHistorico = int(arcpy.GetParameterAsText(10))
workspace = arcpy.GetParameterAsText(11)
  
if not arcpy.Exists(tabelaHistoricoAreaIrrigadaPorCultivoPorMunicipio):
    arcpy.AddError("Tabela inexistente: {dir}".format(dir=tabelaHistoricoAreaIrrigadaPorCultivoPorMunicipio) )
    sys.exit(0)

if not arcpy.Exists(tabelaCoefCultivo):
    arcpy.AddError("Tabela inexistente: {dir}".format(dir=tabelaCoefCultivo) )
    sys.exit(0)

if not arcpy.Exists(tabelaFatorDispAguaRefPorCultivo):
    arcpy.AddError("Tabela inexistente: {dir}".format(dir=tabelaFatorDispAguaRefPorCultivo) )
    sys.exit(0)

if not arcpy.Exists(tabelaProfSistemaRadicularPorCultivo):
    arcpy.AddError("Tabela inexistente: {dir}".format(dir=tabelaProfSistemaRadicularPorCultivo) )
    sys.exit(0)

if not arcpy.Exists(diretorioSuperficieEvapRefMediaMunicipio):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSuperficieEvapRefMediaMunicipio) )
    sys.exit(0)

if not arcpy.Exists(diretorioSuperficiePrecipitacaoMedia):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioSuperficiePrecipitacaoMedia) )
    sys.exit(0)

if not arcpy.Exists(diretorioCamadaCultivoIrrigado):
    arcpy.AddError("Diretorio inexistente: {dir}".format(dir=diretorioCamadaCultivoIrrigado) )
    sys.exit(0)

if not arcpy.Exists(camadaEmbrapaAguaDispSolo):
    arcpy.AddError("Mapa inexistente: {dir}".format(dir=camadaEmbrapaAguaDispSolo) )
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

CalcularNecessidadeIrrigacao()
