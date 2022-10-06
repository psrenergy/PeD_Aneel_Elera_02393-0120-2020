#coding: utf-8
'''
Created on Nov 8, 2021Historico_Evaporacao_Real_Por_Cultivo_Por_Municipio

@author: andre
'''

# camada do histórico de feiçoes (poligonos) das masssas d'água artificiais identificadas
ARQUIVO_MASSA_DAGUA_AGREGADO='Massa_Dagua_Identificado_Agregado'

# camadas 
ARQUIVO_MAIOR_MASSA_DAGUA_AGREGADO='Massa_DAgua_Maior_Area_Agregado'
ARQUIVO_MAIOR_MASSA_DAGUA_AGREGADO_BUFFER_1KM='Massa_DAgua_Maior_Area_Buff_1km_Agregado'
ARQUIVO_MAIOR_MASSA_DAGUA_AGREGADO_DISSOLVE='Massa_DAgua_Maior_Area_Dissolve_Agregado'
ARQUIVO_MAIOR_MASSA_DAGUA_AGREGADO_SIMPLIFY='Massa_DAgua_Maior_Area_Simplify_Agregado'
ARQUIVO_MAIOR_MASSA_DAGUA_PONTOS_MARGEM_AGREGADO='Massas_DAgua_Maior_Area_Pontos_Margem_Agregado'

# tabelas
TABELA_HISTORICO_ETREAL_EVAPREF_KC_MEDIO_MASSA_DAGUA = 'Historico_EtReal_EvapRef_Kc_Medio_Massa_Dagua'
TABELA_KC_MENSAL_MASSA_DAGUA = 'Kc_Mensal_Massa_Dagua'
TABELA_HISTORICA_EVAPREF_MEDIO_POR_ESTACAO = 'Historico_EvapRef_Medio_Estacao'
TABELA_HISTORICO_ETREAL = 'Historico_EtReal'
TABELA_HISTORICO_EVAPREF = 'Historico_EvapRef'

# camada do histórico das feições de massas dagua
ARQUIVO_HISTORICO_MASSA_DAGUA_AGREGADO_SIMPLIFY='Historico_Massa_DAgua_Simplify_Agregado'
ARQUIVO_HISTORICO_MASSA_DAGUA_PONTOS_MARGEM_AGREGADO= 'Historico_Massas_DAgua_Pontos_Margem_Agregado'

#tabelas
TABELA_HISTORICO_EVAPREF_MEDIO_MASSA_DAGUA = 'Historico_EvapRef_Medio_Massa_Dagua'
TABELA_HISTORICO_ETLIQUIDA_MEDIO_MASSA_DAGUA = 'Historico_EVliquida_Media_Massa_Dagua'

# atributos
NOME_ATRIBUTO_AREA='poly_area'
NOME_ATRIBUTO_MASSA_DAGUA = 'nmoriginal'
NOME_ATRIBUTO_ID_MASSA_DAGUA = 'gid'
NOME_ATRIBUTO_ETREAL = 'EtReal'
NOME_ATRIBUTO_ETREAL_MEDIO = 'EtRealMedio'
NOME_ATRIBUTO_EVAPREF = 'EvapRef'
NOME_ATRIBUTO_EVAPREF_MEDIO = 'EvapRefMedio'
NOME_ATRIBUTO_KC = "Kc"
NOME_ATRIBUTO_KC_MEDIO = 'KcMedio'
NOME_ATRIBUTO_ANO = "Ano"
NOME_ATRIBUTO_MES = "Mes"
NOME_ATRIBUTO_ESTACAO = "Estacao"
NOME_ATRIBUTO_PRECIP = 'Precip'
NOME_ATRIBUTO_PRECIP_EFETIVA = 'PrecipEfetiva'
NOME_ATRIBUTO_EFIC_APLICACAO = 'EficAplicacao'
NOME_ATRIBUTO_ETPOTENCIAL = 'EtPotencial'
NOME_ATRIBUTO_MEDIA_SUPERFICIE = 'MEAN'
################### AREAS IRRIGADAS ###################################

#tabelas
TABELA_HISTORICO_AREA_IRRIGADA_POR_MUNICIPIO = "Historico_Area_Irrigada_Municipio"
TABELA_HISTORICO_AREA_IRRIGADA_POR_CULTIPO_POR_MUNICIPIO = "Historico_Area_Irrigada_Por_Cultivo_Por_Municipio"
TABELA_LOG_INCONSISTENCIA_HISTORICO_AREA_IRRIGADA_POR_MUNICIPIO = "Log_Inconsistencia_Historico_Area_Irrigada_Municipio"
TABELA_NECESSIDADE_IRRIGACAO_POR_CULTIPO_POR_MUNICIPIO =  "Historico_Necessidade_Irrigacao_Por_Cultivo_Por_Municipio"
TABELA_EVAPOTRANSPIRACAO_POTENCIAL_POR_CULTIVO =  "Historico_Evaporacao_Potencial_Por_Cultivo_Por_Municipio"
TABELA_PRECIPITACAO_EFETIVA_POR_CULTIVO = 'Historico_Precipitacao_Efetiva_Por_Cultivo_Por_Municipio'
TABELA_FATOR_DISPONIBILIDADE_AGUA_POR_CULTIVO = 'Historico_Fator_Disp_Agua_Por_Cultivo_Por_Municipio'
TABELA_CAPACIDADE_TOTAL_ARMAZENAMENTO_POR_CULTIVO = 'Historico_Capacidade_Total_Armazenamento_Por_Culivo'
TABELA_LAMINA_DAGUA_CULTIVO = 'Historico_Lamina_DAgua_Por_Cultivo_Por_Municipio'
TABELA_COEF_UMIDADE_SOLO ='Historico_Coeficiente_Umidade_Solo_Por_Cultivo_Por_Municipio'
TABELA_EVAPOTRANSPIRACAO_REAL_POR_CULTIVO = 'Historico_Evaporacao_Real_Por_Cultivo_Por_Municipio'        
TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL  = 'Historico_Retirada_Agua_Irrigacao_Por_Municipio_Por_Cultivo_Por_Bacia_Incremental'
TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA_POR_CLASSE_CULTIVO  = 'Historico_Retirada_Agua_Irrigacao_Sumarizada_Por_Classe_Cultivo_Por_Bacia_Incremental'
TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA = 'Historico_Retirada_Agua_Irrigacao_Sumarizada_Por_Bacia_Incremental'
TABELA_RETIRADA_AGUA_IRRIGACAO_BACIA_INCREMENTAL_SUMARIZADA_POR_ANO = 'Historico_Retirada_Agua_Irrigacao_Sumarizada_Por_Bacia_Incremental_Por_Ano'
TABELA_AREA_CULTIVADA_BACIA_INCREMENTAL_SUMARIZADA_POR_ANO = 'Historico_Area_Cultivada_Irrigacao_Sumarizada_Por_Bacia_Incremental_Por_Ano'

#atributos
NOME_ATRIBUTO_CODIGO_MUNICIPIO = "CD_MUN"
NOME_ATRIBUTO_NOME_MUNICIPIO = "NM_MUN"
NOME_ATRIBUTO_AREA_TABELA_ESTATISTICA='Area'
AREA_KM2 = 'AREA_KM2'
NOME_ATRIBUTO_AREA_MUNICIPIO_HA = 'AreaMunHa'
NOME_ATRIBUTO_AREA_IRRIG_HA = 'AreaIrrigHa'
NOME_ATRIBUTO_AREA_IRRIG_PERC = 'AreaIrrigPerc'
NOME_ATRIBUTO_CLASSE_CULTIVO = 'ClasseCultivo'
                              

NOME_ATRIBUTO_AREA_CULTIVO_HA = 'AreaCultivoHa'
NOME_ATRIBUTO_NECES_IRRIG = 'NecesIrrig'
MES1='Mes_1'
MES2='Mes_2'
MES3='Mes_3'
MES4='Mes_4'
MES5='Mes_5'
MES6='Mes_6'
MES7='Mes_7'
MES8='Mes_8'
MES9='Mes_9'
MES10='Mes_10'
MES11='Mes_11'
MES12='Mes_12'
NOME_ATRIBUTO_FAT_DSP_AGUA = 'FAT_DSP_AGUA'
NOME_ATRIBUTO_FAT_DSP_AGUA_REF = 'f0'
NOME_ATRIBUTO_CAP_TOTAL_ARM = 'CTA'
NOME_ATRIBUTO_TOTAL_AD = 'Total_AD'
NOME_ATRIBUTO_PROF_RAIZ_CULTIVO = 'Z'
NOME_ATRIBUTO_LAMINA_DAGUA = 'LAA'
NOME_ATRIBUTO_COEF_UMIDADE_SOLO = 'Ks'
NOME_ATRIBUTO_ETREAL = 'ETrc'
NOME_ATRIBUTO_NOME_BACIA_INCREMENTAL = 'NM_BACIA'
NOME_ATRIBUTO_RETIRADA_IRRIG = 'RETIRADA_IRRIG'
NOME_ATRIBUTO_RETIRADA_IRRIG_SUMARIZADA = 'SUM_RETIRADA_IRRIG'



