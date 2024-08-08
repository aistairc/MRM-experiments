while (( $# > 0 ))
do
  case $1 in
    # ...

    --input )
      INPUT_FILEPATH="$2"
      shift
      ;;
    --output )
      OUTPUT_FILEPATH="$2"
      shift
      ;;
    --type )
      TYPE="$2"
      shift
      ;;
    --size )
      SIZE="$2"
      shift
      ;;
    --window )
      WINDOW="$2"
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


# OUTPUT_FILEPATH=v100.txt
# INPUT_FILEPATH=walk/walk_file_0.txt
# TYPE=3
# SIZE=100
DIR=`dirname ${OUTPUT_FILEPATH}`
TIME=`date "+%y%m%d_%H%M%S"`
mkdir -p ${DIR}
tools/word2vec -train ${INPUT_FILEPATH} \
	-output ${OUTPUT_FILEPATH} \
	-type ${TYPE} \
	-size ${SIZE} \
	-window ${WINDOW} \
	-threads 4 \
	-min-count 0 \
	-cap 1 \
	> ${DIR}/train.${TIME}.log \
	2>&1 \
