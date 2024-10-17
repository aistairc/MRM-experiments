
# 

SCRIPT_DIR=$(cd $(dirname $0); pwd)
MRMCOMVERTER_PATH=${SCRIPT_DIR}/tools/MRMConverter/
FILEPATH=$1
FILENAME=`basename $FILEPATH`
FILENAME="${FILENAME%.*}"
MRM_TYPE=$2
MRM_OPTION=$3
OUTPUT_DIR=$4

echo $MRMCOMVERTER_PATH
# java -classpath "`find ./target/dependency/*.jar | tr '\n' ':'`:./target/MRMConverter-0.0.1-SNAPSHOT.jar" mrmconverter.MRMConverter `realpath ../../ikgrc2023.nt` rdr 1
java -classpath "`find ${MRMCOMVERTER_PATH}/target/dependency/*.jar | tr '\n' ':'`:${MRMCOMVERTER_PATH}/target/MRMConverter-0.0.1-SNAPSHOT.jar" mrmconverter.MRMConverter $FILEPATH $MRM_TYPE $MRM_OPTION
echo "java -classpath "`find ${MRMCOMVERTER_PATH}/target/dependency/*.jar | tr '\n' ':'`:${MRMCOMVERTER_PATH}/target/MRMConverter-0.0.1-SNAPSHOT.jar" mrmconverter.MRMConverter $FILEPATH $MRM_TYPE $MRM_OPTION"

DIR=`dirname ${FILEPATH}`

if [ $2 = 'rdr' ]; then
  mv rdf-star_ext.nt ${OUTPUT_DIR}/${FILENAME}._rdr.nt
  cat ${OUTPUT_DIR}/${FILENAME}._rdr.nt |  grep -v -E '<http://www.w3.org/2002/07/owl#Nothing> <[^>]+> <http://www.w3.org/2002/07/owl#Nothing>' \
    > ${OUTPUT_DIR}/${FILENAME}.rdr.nt
  ./tools/apache-jena-5.0.0/bin/sparql --data ${OUTPUT_DIR}/${FILENAME}.rdr.nt --query tools/sparql/rdr.sq --results TSV > ${OUTPUT_DIR}/${FILENAME}.rdr.tsv
    
  # rm ${OUTPUT_DIR}/${FILENAME}._rdr.nt

elif [ $2 = 'sgprop' ]; then
  mv sgprop.ttl ${OUTPUT_DIR}/${FILENAME}.sgprop.ttl
  ./tools/apache-jena-5.0.0/bin/riot --formatted=N-Triples ${OUTPUT_DIR}/${FILENAME}.sgprop.ttl > ${OUTPUT_DIR}/${FILENAME}.__sgprop.nt
  TRAIN_FILENAME=`echo ${FILENAME} | sed -E "s/(test|valid)/train/g"`
  cat ${OUTPUT_DIR}/${FILENAME}.__sgprop.nt |  grep -v -E '<http://www.w3.org/2002/07/owl#Nothing> <[^>]+> <http://www.w3.org/2002/07/owl#Nothing>' \
    > ${OUTPUT_DIR}/${FILENAME}._sgprop.nt
  poetry run python3 change_sgprop_id.py ${OUTPUT_DIR}/${TRAIN_FILENAME}._sgprop.nt ${OUTPUT_DIR}/${FILENAME}._sgprop.nt ${OUTPUT_DIR}/${FILENAME}.sgprop.nt
  ./tools/apache-jena-5.0.0/bin/sparql --data ${OUTPUT_DIR}/${FILENAME}.sgprop.nt --query tools/sparql/sgprop.sq --results TSV > ${OUTPUT_DIR}/${FILENAME}.sgprop.tsv

  # rm ${OUTPUT_DIR}/${FILENAME}.__sgprop.nt
  # rm ${OUTPUT_DIR}/${FILENAME}._sgprop.nt
elif [ $2 = 'rc' ]; then
  echo ''
fi
