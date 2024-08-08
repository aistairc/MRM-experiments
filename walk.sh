


while (( $# > 0 ))
do
  case $1 in
    # ...

    --qt2subject )
      qt2subject="$2"
      shift
      ;;
    --qt2object )
      qt2object="$2"
      shift
      ;;
    --subject2qt )
      subject2qt="$2"
      shift
      ;;
    --object2qt )
      object2qt="$2"
      shift
      ;;

    --numberOfWalks )
      numberOfWalks="$2"
      shift
      ;;
    --walkGenerationMode )
      walkGenerationMode="$2"
      shift
      ;;
    --depth )
      depth="$2"
      shift
      ;;

    --input )
      N_TRIPLE_FIILPATH="$2"
      shift
      ;;
    --output )
      OUTPUT_FILEPATH="$2"
      shift
      ;;
    -*)
      echo "invalid option"
      exit 1
      ;;
    *)
      echo "argument $1"
      ;;
    # ...
  esac
  shift
done

while (( $# > 0 ))
do
  case $1 in
    --qt2subject )
      ;;
  esac
  shift
done


if [ "${OUTPUT_FILEPATH}" = "" ]; then
  echo "--output is required";
  exit
fi

DIR=`dirname ${OUTPUT_FILEPATH}`
TIME=`date "+%y%m%d_%H%M%S"`
mkdir -p ${DIR}

# N_TRIPLE_FIILPATH=$1
# OUTPUT_DIR=$2
# DEPTH=$3
# numberOfWalks=$4
# walkGenerationMode=$5
# # qt2subject
# # object2qt 
# # qt2object 
# # subject2qt
# 
# 
# numberOfWalks=500
# 
# DEPTH=8
# # walkGenerationMode='MID_WALKS'
# # walkGenerationMode='RANDOM_WALKS'
# walkGenerationMode='RANDOM_WALKS_DUPLICATE_FREE'
# 
# rm ${TMPDIR}/walk/*.txt
# rm ${TMPDIR}/walk/*.gz
# mkdir -p ${TMPDIR}/walk
# echo java -jar tools/RDF-star2Vec/rdf-star2vec_1.0.0-SNAPSHOT.jar \

java -jar tools/RDF-star2Vec/rdf-star2vec_2.0.0-SNAPSHOT.jar \
	-graph ${N_TRIPLE_FIILPATH} \
	-onlyWalks \
	-walkDir ${TMPDIR}/walk \
	-walkGenerationMode ${walkGenerationMode:-'RANDOM_WALKS'} \
	-depth ${depth:-8} \
	-qt2subject ${qt2subject:-0.5} \
	-qt2object  ${qt2object:-0.5} \
	-object2qt  ${object2qt:-0.5} \
	-subject2qt ${subject2qt:-0.5} \
	-numberOfWalks ${numberOfWalks:-100} \
	> ${DIR}/walk.${TIME}.log \
	2>&1 \

# 
gzip -f -d ${TMPDIR}/walk/walk_file_0.txt.gz

mkdir -p ${DIR}
mv ${TMPDIR}/walk/walk_file_0.txt ${OUTPUT_FILEPATH}
# mv ${TMPDIR}/walk/walk_file_0.txt.gz ${DIR}/
rm ${TMPDIR}/walk/walk_file_0.txt.gz
# # tools/word2vec -train walk/walk_file_0.txt -output v100.txt -type 3 -size 100 -threads 4 -min-count 0 -cap 1
