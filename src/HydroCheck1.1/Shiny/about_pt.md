## Módulo HydroCheck

Esse módulo foi criado no âmbito do P&D 02393-0120/2020 de "Investigação dos fatores que interferem na performance do MRE".

Seu objetivo é identificar, a partir de indicadores estatísticos e de séries temporais, dados históricos incorretos de vazões afluentes que tenham sido fornecidos. A verificação da qualidade dos dados é essencial para garantir que resultados confiáveis sejam gerados pelos modelos de otimização/simulação, como NEWAVE e SDDP.


### Analisando os resultados

Esse módulo calcula as seguintes métricas para todas as usinas fornecidas:

***
1. Média de longo prazo : Média dos valores anuais médios de afluência para todos os anos.

2. CV Méd. Anual : Razão entre o desvio padrão de uma variável e sua média. Nesse caso, calcula-se o coeficiente de variação (CV) das vazões médias anuais. O CV é uma medida adimensional.

  Valores altos para o CV das médias anuais de afluência de uma determinada usina podem indicar a existência de afluências irreais. Valores de vazão tendem a mostrar pequenas variações ao longo dos anos, mas têm uma mais clara correlação com sua localização. Além disso, usinas com baixos valores de afluência tendem a apresentar maior variação, enquanto rios maiores têm um comportamento mais estável.

3. Teste Constante de KPSS: Testa a hipótese de que a série temporal de vazões é estacionária ao redor de sua média. Quanto mais baixo o valor, mais estacionária é a série.

  Assume-se em estudos hidrológicos que séries de vazão são estacionárias. O SDDP considera a mesma hipótese para construir cenários futuros. Portanto, o teste KPSS indica o nível de acuracidade dessa hipótese de estacionariedade e alerta para possíveis valores incorretos nas vazões históricas.

  As usinas que tiverem valores do teste KPSS acima de determinado limite aparecerão na tabela de avisos. Nesse módulo, o limite definido é 1,2 vezes o valor do 95º percentil do conjunto de resultados do teste KPSS para todas as usinas consideradas.


4. Teste de Tendência: ([Média da 2ª metade da série] / [Média da 1ª metade da série] - 1)*100%

  É uma medida adimensional simplificada da tendência da série temporal, isto é, se as vazões aumentaram ou reduziram com o tempo. Valores positivos significam um aumento nas afluências, enquanto valores negativos indicam que as afluências reduziram para a usina analisada.

*** 


### Sugestões
O usuário pode decidir quais valores serão analisados para validar os dados inseridos. Contudo, sugestões são feitas como configuração default para facilitar a visualização.

Para a variável do eixo X, o CV da média anual é selecionado por default, já que se espera mostrar somente resultados positivos. Valores maiores aparecerão na direita do gráfico. Esses valores são considerados como mais suspeitos, já que mostram maior variação do que outras usinas.

O default do eixo Y é o indicador do teste de tendência. O usuário identificará intuitivamente afluências crescentes e decrescentes, já que afluências crescentes são positivas e decrescentes são negativas no gráfico.

A variável selecionada para a escala de cores é o Teste Constante KPSS. Séries temporais altamente não-estacionárias serão destacadas em vermelho, alertando que podem causar problemas.

A opção de escala de tamanho está desabilitada por default. Devido à considerável variabilidade de afluências entre usinas, selecionar o checkbox pode causar problemas de escala, já que pontos com baixos valores podem estar muito pequenos em comparação com os outros. Assim, recomenda-se que o usuário analise cada ponto sem a escala de tamanho antes de habilitá-la.

Por default, a variável de escala de tamanho é a média de longo prazo. O usuário pode identificar intuitivamente usinas com afluências mais altas ao comparar o tamanho do ponto. Já que essas usinas são mais relevantes para o sistema, é aceitável que essas estejam mais destacadas do que outras.

Consulte o manual do usuário para uma descrição mais detalhada desse módulo.