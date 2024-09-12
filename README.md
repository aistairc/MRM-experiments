# OPTIMIZATION
```shell
MRM_TYPE='rdr' # [rdr, sgprop, rc]
python3 opt.py \
  --walk_target "./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/rdf/train.${MRM_TYPE}.nt" \
  --mrm_type ${MRM_TYPE} \
  --link_prediction_dataset "./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/tasks/link_prediction/" \
  --study_name ${MRM_TYPE} \

```

```shell
poetry run python3 plot.py optuna_db # optuna_db is a directory including optuna study database
```

# DATASET
LinkPrediction: `data/dataset/ikgrc2023.cleaned/*/tasks/link_prediction/`
