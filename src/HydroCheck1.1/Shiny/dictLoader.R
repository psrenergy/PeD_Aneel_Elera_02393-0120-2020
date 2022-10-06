dict <- read.table(file='dict.csv',header=T, sep=',')

# tentar fazer setNames('pt', key) para receber o idioma como parâmetro
dicTranslateCurrent <- with(dict,setNames(pt, key))
