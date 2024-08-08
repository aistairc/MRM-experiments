# java -jar rdf-star2vec_1.0.0-SNAPSHOT.jar \
# 	-graph rdf-star_ext_ikgrc2023.nt \
# 	-onlyWalks \
# 	-walkDir experiment/ \
# 	-walkGenerationMode STAR_MID_WALKS_DUPLICATE_FREE \
# 	-depth 8 \
# 	-qt2subject 0.5 \
# 	-object2qt 0.5

# # ../../data/dataset/ikgrc2023/train.nt \
# java -jar rdf-star2vec_1.0.0-SNAPSHOT.jar \
# 	-graph ../../data/sgprop.tsv \
# 	-onlyWalks \
# 	-walkDir experiment/ \
# 	-walkGenerationMode STAR_MID_WALKS_DUPLICATE_FREE \
# 	-depth 8 \
# 	-qt2subject 0.5 \
# 	-object2qt 0.5 \

# singleton property, reification の場合は walkGenerationMode に jRDF2Vec にあるモードを指定しないと動かない

DATA_FILEPATH=$1
# DATA_FILEPATH=../../data/dataset/ikgrc2023/train.nt \
WALK_GENERATION_MODE='RANDOM_WALKS'
# WALK_GENERATION_MODE='STAR_MID_WALKS'
java -jar rdf-star2vec_1.0.0-SNAPSHOT.jar \
	-graph ${DATA_FILEPATH} \
	-onlyWalks \
	-walkDir experiment/ \
	-walkGenerationMode ${WALK_GENERATION_MODE} \
	-depth 8 \
	-qt2subject 0.5 \
	-object2qt 0.5 \

gzip -f -d experiment/walk_file_0.txt.gz
DIM=100
../word2vec -train experiment/walk_file_0.txt -output v${DIM}.txt -type 3 -size ${DIM} -threads 4 -min-count 0 -cap 1
