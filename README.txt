Uso de Script para extraccion, generacion y etiquetado de un corpus para el entrenamiento de herramientas de analisis de sentimiento aplicadas a la 
ingeniería de software en Latinoamérica (Ecuador, Colombia, Argentina y Mexico)

1. Despues de clonar el repositorio en los archivos: Generar_corpus.py y Repositorios.py se debe agregar un token para el acceso al API de GitHub.
2. Se debe ejecutar en orden primero: Repositorios.py, el cual generara una lista de 120 repositorios (30 por pais) compatibles con los parametros de 
busqueda detallados en el script.
3. Posteriormente sin cambiar de directorio se debe ejecutar: Generar_corpus.py el cual extraera: commits, issues, pr's y readme de los respositorios
los cuales quedaran a disposicion.
4. Por ultimo con el archivo Entrenamiento.ipynb compatible con jupyter, se podra: extraer del corpus previamente generado los commits e issues (se 
puede modificar para la extraccion de los demas elementos presentes en el corpus), realizar una normalizacion basica y avanzada del corpus, realizar 
el etiquetado del corpus con VADER, realizar el entramiento de SVM, RL y RF, obtener las metricas (modificables) MCC, F1-Score Macro, Recall Macro y 
Accuracy y por ultimo generar cuadros comparativos de las metricas obtenidas.

