# ---
MRM_TYPE='rc'
OUTPUT_ROOT_DIR="./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/rdf/"
mkdir -p ${OUTPUT_ROOT_DIR}
ORG_DATA_DIR='data/dataset/ikgrc2023.cleaned/origin/'
cp ${ORG_DATA_DIR}/train.nt ./
cp ${ORG_DATA_DIR}/test.nt ./
cp ${ORG_DATA_DIR}/valid.nt ./
# ORG_DATA_DIR='./' # 'data/dataset/ikgrc2023.cleaned/origin/'

# cp ${ORG_DATA_DIR}/train.nt ${OUTPUT_ROOT_DIR}/train.rc.nt
# cp ${ORG_DATA_DIR}/valid.nt ${OUTPUT_ROOT_DIR}/valid.rc.nt
# cp ${ORG_DATA_DIR}/test.nt  ${OUTPUT_ROOT_DIR}/test.rc.nt

./tools/apache-jena-5.0.0/bin/sparql --data ${OUTPUT_ROOT_DIR}/train.rc.nt --query tools/sparql/sgprop.sq --results TSV > ${OUTPUT_ROOT_DIR}/train.rc.tsv
./tools/apache-jena-5.0.0/bin/sparql --data ${OUTPUT_ROOT_DIR}/valid.rc.nt --query tools/sparql/sgprop.sq --results TSV > ${OUTPUT_ROOT_DIR}/valid.rc.tsv
./tools/apache-jena-5.0.0/bin/sparql --data ${OUTPUT_ROOT_DIR}/test.rc.nt  --query tools/sparql/sgprop.sq --results TSV > ${OUTPUT_ROOT_DIR}/test.rc.tsv

OUTPUT_DIR="./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/tasks/link_prediction/"
mkdir -p ${OUTPUT_DIR}

rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/train.rc.tsv 10 0 0
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.train.txt
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.train.txt
mv export/train2id.txt    ${OUTPUT_DIR}/train2id.txt


rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/valid.rc.tsv 10 0 0
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.valid.txt
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.valid.txt
mv export/train2id.txt    ${OUTPUT_DIR}/valid2id.txt

rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/test.rc.tsv 10 0 0
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.test.txt
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.test.txt
mv export/train2id.txt    ${OUTPUT_DIR}/test2id.txt
 
python3 adjust.py ${OUTPUT_DIR}


rm ${OUTPUT_DIR}/relation2id.test.txt
rm ${OUTPUT_DIR}/relation2id.valid.txt
mv ${OUTPUT_DIR}/relation2id.train.txt ${OUTPUT_DIR}/relation2id.txt

rm ${OUTPUT_DIR}/entity2id.test.txt
rm ${OUTPUT_DIR}/entity2id.valid.txt
mv ${OUTPUT_DIR}/entity2id.train.txt ${OUTPUT_DIR}/entity2id.txt

CDIR=`pwd`
cd ${OUTPUT_DIR}
python3 ${CDIR}/tools/n-n.py
cd ${CDIR}

# --
MRM_TYPE='rdr'
OUTPUT_ROOT_DIR="./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/rdf/"
mkdir -p ${OUTPUT_ROOT_DIR}
ORG_DATA_DIR='./' # 'data/dataset/ikgrc2023.cleaned/origin/'
# ORG_DATA_DIR='data/dataset/ikgrc2023.cleaned/origin/'

bash run.sh ${ORG_DATA_DIR}/train.nt rdr 1 ${OUTPUT_ROOT_DIR}
bash run.sh ${ORG_DATA_DIR}/valid.nt rdr 1 ${OUTPUT_ROOT_DIR}
bash run.sh ${ORG_DATA_DIR}/test.nt rdr  1 ${OUTPUT_ROOT_DIR}

OUTPUT_DIR="./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/tasks/link_prediction/"
mkdir -p ${OUTPUT_DIR}

rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/train.rdr.tsv 10 0 0
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.train.txt
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.train.txt
mv export/train2id.txt    ${OUTPUT_DIR}/train2id.txt


rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/valid.rdr.tsv 10 0 0
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.valid.txt
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.valid.txt
mv export/train2id.txt    ${OUTPUT_DIR}/valid2id.txt

rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/test.rdr.tsv 10 0 0
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.test.txt
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.test.txt
mv export/train2id.txt    ${OUTPUT_DIR}/test2id.txt
 
python3 adjust.py ${OUTPUT_DIR}


rm ${OUTPUT_DIR}/relation2id.test.txt
rm ${OUTPUT_DIR}/relation2id.valid.txt
mv ${OUTPUT_DIR}/relation2id.train.txt ${OUTPUT_DIR}/relation2id.txt

rm ${OUTPUT_DIR}/entity2id.test.txt
rm ${OUTPUT_DIR}/entity2id.valid.txt
mv ${OUTPUT_DIR}/entity2id.train.txt ${OUTPUT_DIR}/entity2id.txt

CDIR=`pwd`
cd ${OUTPUT_DIR}
python3 ${CDIR}/tools/n-n.py
cd ${CDIR}



# ---
MRM_TYPE='sgprop'
OUTPUT_ROOT_DIR="./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/rdf/"
mkdir -p ${OUTPUT_ROOT_DIR}
# ORG_DATA_DIR='data/dataset/ikgrc2023.cleaned/origin/'
ORG_DATA_DIR='./' # 'data/dataset/ikgrc2023.cleaned/origin/'

bash run.sh ${ORG_DATA_DIR}/train.nt sgprop '' ${OUTPUT_ROOT_DIR} 
bash run.sh ${ORG_DATA_DIR}/valid.nt sgprop '' ${OUTPUT_ROOT_DIR} 
bash run.sh ${ORG_DATA_DIR}/test.nt sgprop  '' ${OUTPUT_ROOT_DIR} 

OUTPUT_DIR="./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/tasks/link_prediction/"
mkdir -p ${OUTPUT_DIR}

rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/train.sgprop.tsv 10 0 0
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.train.txt
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.train.txt
mv export/train2id.txt    ${OUTPUT_DIR}/train2id.txt


rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/valid.sgprop.tsv 10 0 0
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.valid.txt
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.valid.txt
mv export/train2id.txt    ${OUTPUT_DIR}/valid2id.txt

rm export/*
java -jar tools/KGRC-Tools/ToolsforFastTransX/URI2ID.jar ${OUTPUT_ROOT_DIR}/test.sgprop.tsv 10 0 0
mv export/relation2id.txt ${OUTPUT_DIR}/relation2id.test.txt
mv export/entity2id.txt   ${OUTPUT_DIR}/entity2id.test.txt
mv export/train2id.txt    ${OUTPUT_DIR}/test2id.txt
 
python3 adjust.py ${OUTPUT_DIR}


rm ${OUTPUT_DIR}/relation2id.test.txt
rm ${OUTPUT_DIR}/relation2id.valid.txt
mv ${OUTPUT_DIR}/relation2id.train.txt ${OUTPUT_DIR}/relation2id.txt

rm ${OUTPUT_DIR}/entity2id.test.txt
rm ${OUTPUT_DIR}/entity2id.valid.txt
mv ${OUTPUT_DIR}/entity2id.train.txt ${OUTPUT_DIR}/entity2id.txt

CDIR=`pwd`
cd ${OUTPUT_DIR}
python3 ${CDIR}/tools/n-n.py
cd ${CDIR}

