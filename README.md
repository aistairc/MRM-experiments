# Comparison of Metadata Representation Models for Knowledge Graph Embedings

This is a framework for evaluating the performance of Metadata Representation Models (MRMs) in Link Prediction using Knowledge Graph Embedding.

## OPTIMIZATION
```shell
MRM_TYPE='rdr' # [rdr, sgprop, rc]
python3 opt.py \
  --walk_target "./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/rdf/train.${MRM_TYPE}.nt" \
  --mrm_type ${MRM_TYPE} \
  --link_prediction_dataset "./data/dataset/ikgrc2023.cleaned/${MRM_TYPE}/tasks/link_prediction/" \
  --study_name ${MRM_TYPE} \

```

## Plot experiment result
```shell
poetry run python3 plot.py optuna_db # optuna_db is a directory including optuna study database
```

### Loss curve
```shell
poetry run python3 plot_loss.py
```

### Best Scores
```shell
poetry run python3 show_best_scores.py
```


## DATASET
LinkPrediction: `data/dataset/ikgrc2023.cleaned/*/tasks/link_prediction/`

## KGE model (RDF-star2Vec<sub>ext</sub>)
https://github.com/aistairc/RDF-star2Vec/tree/qo-_sq-walks
