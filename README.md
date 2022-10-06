# Módulo HydroCheck

O módulo HydroCheck tem o objetivo de identificar possíveis inconsistências nos dados históricos de vazões afluentes que tenham sido fornecidos. Para isso, ele calcula as seguintes métricas para cada usina:

* Média de Longo Prazo: Média dos valores anuais médios de afluência para todos os anos. A falta de dados para determinado ano de uma estação fará com que esse ano seja desconsiderado para evitar a introdução de desvios.
* Coeficiente de Variação da média anual (CV Méd. Anual): Medida adimensional calculada a partir da razão entre o desvio padrão das afluências anuais médias de cada usina e sua média. Valores altos para o CV das médias anuais de afluência de uma determinada usina podem indicar a existência de afluências irreais. Costumeiramente, os CVs reduzem com o aumento da afluência média, já que vazões maiores estão associadas a maiores áreas de escoamento, que resultam da soma de vazões afluentes de várias sub-bacias hidrográficas, cujas variabilidades individuais se cancelam ao se juntarem à bacia maior.
* Teste de KPSS: Testa a hipótese de que a série temporal de vazões é estacionária ao redor de sua média. Quanto mais baixo o valor, mais estacionária é a série.
* Teste de Tendência: É uma medida adimensional simplificada da tendência da série temporal, isto é, se as vazões aumentaram ou reduziram com o tempo. Valores positivos significam um aumento nas afluências, enquanto valores negativos indicam que as afluências reduziram para a usina analisada. 

No diretório `HydroCheck1.1`, em `src`, está disponível o programa compilado e código fonte do módulo.

# Reconhecimento de Áreas Irrigadas e seus Respectivos Cultivos para análise de Extração de Água da Bacia do Rio São Francisco

## Apêndice 

### Diretório do Google Earth Engine

https://code.earthengine.google.com/?accept_repo=users/rodrigobenoliel/water_crops_est

Contém:

* `irrigacao_sent2`: código de reconhecimento de áreas de baixo estresse hídrico.
* `classificador_tf_uni_prepoc`: código de preprocessamento de dados para treinamento do modelo.
* `tf_uni_test`: código de validação do modelo e visualização.
* `visualization`: visualização de classificação sobre Bacia do Rio São Francisco.

### Notebooks de Google Colab

* Preprocessamento, treinamento, EEfication e exportação do modelo para a Google AI Platform: https://colab.research.google.com/drive/1KDfBen-KGxY3K1gPnya9Nz84EJeV95el?usp=sharing
* Avaliação da Bacia de São Francisco Completa e Exportação para o Google Earth Engine: https://colab.research.google.com/drive/1SKql_37rHBAcvhTv1KdqD0PW4UJcaGyl?usp=sharing

### Scripts de ArcGIS

Na pasta `flowEstimator`,em `src`, estão disponíveis também arquivos de código Python utilizados como módulos para rotinas de geoprocessamento em ArcGIS.

---
## Resumo
Este repositório apresenta o resultado da pesquisa por uma metodologia para melhorar a gestão da água
considerando o nexo água-alimentos-energia ao quantificar as retiradas d’água em bacias hidrográficas. Um
estudo de caso para a bacia do Rio São Francisco será apresentado. A metodologia utiliza uma rede neural sobre
uma série temporal imagens de satélites.  As informações sobre o estágio de desenvolvimento desses cultivos é então
combinada com informações climáticas regionalizadas, como precipitação e temperatura, para avaliar a retirada
de água por irrigação. Uma abordagem bottom-up agrega resultados locais em grandes áreas para avaliar o
impacto final da agricultura irrigada sobre o balanço hídrico sobre as usinas hidrelétricas, como no caso de
Sobradinho. Uma comparação entre os resultados obtidos e dados oficiais utilizados por ANA e ONS permite
uma avaliação sobre as implicações desta diferença ao planejamento da operação do setor elétrico.

Inclui-se aqui links para os ambientes Google Earth Engine e Google Colab, além de scripts que utilizam framework de ArcGIS. Alguns destes demandam credenciais próprias e licenças de determinados serviços para serem utilizados.

---
## Introdução

A bacia hidrográfica do rio São Francisco possui uma grande multiplicidade de usos para consumo. A ANA
(Agência Nacional de Águas) vem desenvolvendo estudos de longo prazo que permitem a diversos setores da
economia e comitês de bacia determinar projeções de captação, consumo e retorno. Em 2019, ela consolidou
dados históricos e realizou projeções sobre demandas hídricas totais e setoriais por município brasileiro para
cada usina hidrelétrica do SIN (Sistema Interligado Nacional) de 1931 até 2030.

Nesses estudos, nota-se a importância do setor agrícola para o desenvolvimento econômico da região. Em 2016,
o faturamento do setor agrícola na BHSF foi de R$ 24 bilhões (INOVAGRI, 2017)), sendo responsável pela captação da maior parcela d’água nessa bacia. A maior parte desse montante decorre da produção de duas sub-
bacias do São Francisco com maior remuneração por produção principalmente devido a altos níveis de produção de café, milho e soja (Alto São Francisco) e de cana-de-açúcar, milho, soja e uva (Médio São Francisco).

A expansão da agricultura irrigada tem sido um importante fator de desenvolvimento econômico do país. É
preciso haver uma gestão do uso d’água, principalmente nas regiões mais secas do país, para garantir que não
haja um uso excessivo da água subterrânea (acima da capacidade de reposição natural pelas chuvas). É
igualmente importante avaliar como este avanço da agricultura irrigada impacta a disponibilidade hídrica de
outras atividades econômicas, como no caso da produção hidrelétrica, responsável por cerca de 70% da
eletricidade produzida no país se a captação d’água (superficial ou subterrânea reduzir a vazão afluente às
usinas hidrelétricas.

Cabe destacar que historicamente os usos consuntivos d’água eram parcelas bem pequenos no balanço hídrico
de rios importantes, como o São Francisco. Os resultados do trabalho indicam que esta premissa, ainda que
considerada válida por muitos, vem se tornando progressivamente inadequada com o rápido crescimento de lavouras irrigadas no Oeste da Bahia e outras áreas. Entretanto, recentes crises de escassez hídrica na bacia do
rio São Francisco, vem chamando a atenção para certo desequilíbrio entre disponibilidade hídrica (decrescente)
e as demandas da água (crescente, principalmente impulsionadas pela expansão da fronteira agrícola irrigada).

Neste projeto apresentaremos a metodologia para calcular os usos consuntivos da água para irrigação. Para essa
avaliação, como se verá mais à frente, é fundamental definir as áreas efetivamente irrigadas e os tipos de
cultivo, pois alguns requerem mais água que outros para se desenvolverem, como o caso da cana de açúcar.
Muitos investimentos vêm sendo feitos recentemente para a implantação de sistemas de irrigação que
garantam maior segurança de produção ante as condições climáticas e retorno sobre os investimentos. Para
essa estimativa a Agência Nacional de Águas – ANA utiliza os dados dos censos agropecuários do IBGE,
informações essas autodeclaradas, que por este motivo podem trazer inconsistências. O trabalho apresenta
uma abordagem alternativa baseada na interpretação dessas imagens e aplicação de algoritmos de machine
learning.

---
## Dados

O projeto em questão demandou uso de três bases de dados principais oriundas de sensoriamento remoto, são estas:

* Sentinel 2: Imagens multi-espectrais;
* Landsat 8: Imagens multi-espectrais;
* MapBiomas: Mapa de uso do solo;
* GPM: Mapa de reconhecimento de chuva;

A aplicação de cada um desses conjuntos estará sendo desenvolvida ao longo da metodologia do projeto. Além das bases mencionadas, disponíveis online, serão utilizados dados de campo coletados especialmente para esta pesquisa.

---
## Metodologia

### Identificação de áreas de baixo estresse hídrico

O primeiro estágio do processo consiste no reconhecimento de áreas rurais de baixo estresse hídrico. A metodologia proposta usou imagens do período seco de cada ano. Essa premissa foi adotada a fim de determinar que, se uma área que deveria estar seca e com alto estresse hídrico não estiver, seria muito provável haja um fluxo externo de água, ou seja, uma irrigação. Adotou-se um método baseado em três índices:

* `NDVI` (_Normalized Difference Vegetation Index_);
* `NDWI` (_Normalized Difference Water Index_);
* `SWIR` (_Short Wave Infra Red_);

Os três indicadores apresentados são capazes de, para determinadas faixas de valores, indicar presença de vegetação e humidade. Cada um dos índices foi calculado ou obtido diretamente de valores de reflectância providenciados pelas imagens do Sentinel 2. Realizou-se uma sobreposição de todas as imagens produzidas pela aplicação de cada um dos indicadores sobre o mapa, e guardou-se os pontos na qual todos os índices estivessem dentro dos limites estipulados. Tais pontos foram considerados como de baixo estresse hídrico e, portanto, com grandes chances de serem irrigados.

Sobre essas imagens, realizou-se um pós processamento visando filtrar áreas que poderiam ser falsos positivos. Este critério foi realizado com base no mapa de chuva (GPM) e de uso do solo (MapBiomas), na qual se eliminou áreas na qual foi identificado eventuais chuvas ou que não atendiam a determinadas categorias de cultivos.

No próximo estágio do projeto, será desenvolvido um modelo capaz de reconhecer tais cultivos sob baixo estresse hídrico diretamente, além de categorias adicionais observadas em campo.

### Pré-processamento dos dados para treinamento do modelo de reconhecimento de cultivos irrigados

Esta etapa consistiu em organizar as coleções isoladas em uma única estrutura que armazenava ambas as informações de entrada e saída em um formato que o modelo fosse capaz de usar para seu treinamento. Primeiramente, foi feito o processamento dos dados de entrada. Uma vez que o mapa de irrigação é um compilado quinzenal, optou-se por reduzir a escala temporal das imagens de satélite para esse mesmo grau. Assim, foi feito um recorte deste dentro do período de estudo, e aplicou-se um método para calcular a mediana de cada pixel dentro dessa janela, eliminando aqueles que apresentavam alto nível de nebulosidade. Por fim, selecionou-se as bandas relevantes para o reconhecimento, são estas as do espectro visível e infravermelho, listadas a seguir.

Sentinel 2:

* `B2`: Azul.
* `B3`: Verde.
* `B4`: Vermelho.
* `B5`: Próximo de infravermelho 1.
* `B6`: Próximo de infravermelho 2.
* `B7`: Próximo de infravermelho 3.
* `B8`: NIR.
* `B8A`: Próximo de infravermelho 4.
* `B11`: Infravermelho de bandas curtas 1.
* `B12`: Infravermelho de bandas curtas 2.

Em seguida, aplicou-se nas imagens os filtros dos mapas de cultivos e irrigação, para que apenas restassem áreas de interesse (agricultura irrigada). Assim, todo pixel das imagens que estivesse incluído nas regiões irrigadas, e ao mesmo também fizesse parte de uma das quatro categorias de cultura mencionadas, recebeu um rótulo do respectivo cultivo. Caso contrário, foi classificado como “vazio”.

Além dos dados já mencionados, como dito anteriormente, adquiriu-se também dados de cultivo através de pesquisa de campo. Esses dados foram utilizados para balizar as informações de uso do solo disponíveis até então, além de para permitir o reconhecimento de novas classes de cultivos não presentes no escopo do MapBiomas. Aos dados de campo foram adicionados novos pontos resultantes de comparação visual com imagens de satélite de alta resolução, disponíveis para visualização somente.

Novas áreas definidas visualmente e pela pesquisa de campo para o treinamento do modelo podem ser visualizadas abaixo, de uva (roxo e azul), manga (laranja) e coco ou banana (branco).

![Dados de campo e visuais](/assets/dados_campo_vis.png "Dados de campo e visuais")

O resultado deste processo pode ser visualizado nas imagens a seguir. Esquerda: imagem do LandSat 8 em região de cana de açúcar em cores reais. Centro: áreas de cana-de-açúcar indicadas pelo MapBiomas (laranja), áreas reconhecidas como irrigadas (azul) e pertencem a ambos os grupos (cana-de-açúcar irrigada, marrom). Direita: Polígonos selecionados para treinamento (laranja são pixels de cana irrigados e vermelho “vazios”, ou seja, não é cana).

![Comparacao preproc](/assets/comp_preproc.png "Comparacao preproc")

### Definição e treinamento do modelo de reconhecimento de cultivos irrigados

Pela necessidade de maior esforço computacional, migrou-se do uso de modelos nativos do Google EE para Redes Neurais Artificiais (ANN) da TensorFlow Keras API, modelos que possuem integração com o Google Cloud e Google EE. A mudança de ambiente permitiu o aumento na quantidade de dados usados para treinamento, devido a menores limitações de memória.

O desenvolvimento do modelo foi dividido em dois estágios: o primeiro consistiu no treinamento e validação somente com as categorias básicas disponíveis pelo mapa de uso do solo, e o segundo, com esses mesmos dados mais aqueles coletados em campo.

O resultado do primeiro estágio está exposto na tabela a seguir.

| Dados | Precisão (%) | Perda (Entropia Cruzada Categórica) |
|---|---|---|
|Treinamento|96,1%|0,150|
|Validação|87,2%|0,456|
|Teste|85,9%|0,454|


![Resultados Petrolina e Juazeiro](/assets/results_petr.png "Resultados Petrolina e Juazeiro")

A imagem acima exibe uma visualização da classificação (esquerda) comparada ao mapa de uso do solo (direita). A cor laranja indica áreas irrigadas de cana-de açúcar, e verde de outras culturas perenes. Resquícios de outras cores na imagem da classificação do modelo são resultado de reconhecimento incorreto de outros cultivos.

Em seguida, treinou-se mais uma vez o modelo, dessa vez tanto com dados do MapBiomas, quanto coletados em campo e definidos visualmente por comparação. Os resultados estão exibidos na abaixo.

![Resultados Petrolina e Juazeiro](/assets/results_petr_2.png "Resultados Petrolina e Juazeiro")

A esquerda: áreas de cultivo irrigado reconhecidas pelo modelo em Petrolina, de uva (roxo), manga (laranja), coco ou banana (branco), cana (azul), herbáceas (vermelho) e café (rosa). A direita: áreas identificadas como irrigadas na mesma região. Nota-se forte presença de manga, uva e cana. Os dois primeiros estão completamente de acordo com o esperado, já a cana, apesar de não ser o que se imaginava, ainda é um cultivo possível nessa região. Em geral, o modelo manifesta a tendência esperada de acordo com a viagem de campo.