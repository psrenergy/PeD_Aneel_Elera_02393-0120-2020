## Módulo HydroCheck

Este módulo fue creado como parte del I&D 02393-0120/2020 de "Investigación de factores que interfieren con el desempeño del MRE".

Su propósito es identificar, a partir de indicadores estadísticos y de series de tiempo, datos históricos inconsistentes de caudales. La verificación de la calidad de estos datos es esencial para garantizar que los modelos de optimización/simulación, como NEWAVE y SDDP, generen resultados fiables.


### Analizando los resultados

Este módulo calcula las siguientes métricas para todas las centrales hidroeléctricas suministradas:

***
1. Promedio a largo plazo: Promedio de los valores anuales de caudales para todos los años.

2. CV Promedio Anual: Relación entre la desviación típica de una variable y su promedio. En este módulo, el coeficiente de variación (CV) fue calculado para el promedio anual de los caudales. El CV es una medida adimensional.

  Valores elevados de CV de caudales anuales pueden indicar la existencia de problemas con estos caudales. Los valores de caudales tienden a presentar pequeñas variaciones a lo largo de los años, pero tienen una clara correlación con su ubicación. Además, las centrales con bajos valores de caudales usualmente presentan mayor variación, mientras que los ríos más grandes tienen un comportamiento más estable.


3. Prueba constante de KPSS: Prueba la hipótesis de que la serie de caudales es estacionaria alrededor de su promedio. Cuanto menor sea el valor, más estacionaria será la serie.
  
  En los estudios hidrológicos se asume estacionariedad en las series de caudales. SDDP considera la misma hipótesis para construir escenarios futuros. Por tanto, la prueba KPSS indica el nivel de confianza de esta hipótesis y advierte sobre posibles valores incorrectos en los caudales históricos.

  Las centrales con resultados de la prueba de KPSS por encima de un límite definido se mostrarán en la tabla de avisos. En este módulo, el límite definido es 1,2 veces el valor del 95% percentil del conjunto de resultados de la prueba de KPSS para todas las centrales consideradas.


4. Prueba de tendencia: ([Promedio de 2ª mitad de la serie] / [Promedio de 1ª mitad de la serie] - 1)*100%
  
  Es una medida adimensional simplificada de la tendencia de la serie temporal. Los valores positivos significan un aumento en los caudales y los valores negativos una reducción de estos para la estación analizada.

***

### Sugerencias
El usuario puede decidir qué valores se analizarán para validar los datos ingresados. Sin embargo, se ofrecen sugerencias como configuración predeterminada para facilitar la visualización.

Para la variable del eje X, el CV de promedios anuales se selecciona por estándar, ya que se espera que muestre solo resultados positivos. Los valores más grandes aparecerán a la derecha del gráfico. Estos valores pueden indicar problemas con los datos de caudales, ya que muestran una mayor variación que otras centrales.

El valor predeterminado del eje Y es el indicador de la prueba de tendencia. El usuario identificará intuitivamente los caudales crecientes y decrecientes, ya que los caudales crecientes son positivos y los decrecientes son negativos en el gráfico.

La variable seleccionada para la escala de colores es la prueba constante KPSS. Las series de tiempo no-estacionarias se resaltarán en rojo, advirtiendo que pueden causar problemas.

La opción de escala de tamaño está deshabilitada de forma predeterminada. Debido a la considerable variabilidad de los caudales entre estaciones, seleccionar la casilla de verificación puede causar problemas de escala, ya que los puntos con valores bajos pueden ser muy pequeños en comparación con los demás. Por lo tanto, se recomienda que el usuario analice cada punto sin la escala de tamaño antes de habilitarlo.

De forma predeterminada, la variable de escala de tamaño es el promedio a largo plazo. El usuario puede identificar intuitivamente las estaciones con mayores caudales al comparar el tamaño del punto. Dado que estas estaciones son más relevantes para el sistema, es aceptable que sean más prominentes que otras.

Consulte el Manual del usuario para obtener una descripción más detallada de ese módulo. 