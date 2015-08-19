# Recibe un fichero original con las versiones sin fijar
# Devuelve dependencias fijadas a su versión actual por stdout
# Ej: $ ./fix-version.sh dev-reqs.txt
pip freeze | grep -iF -f $1
