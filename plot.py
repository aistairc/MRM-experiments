# coding: utf-8
import optuna
from collections import defaultdict
from matplotlib import pyplot
import os
import sys
import json

# mrms = ['rc', 'rdr', 'sgprop']
mrms = ['rc', 'rdr']

path = os.path.relpath(sys.argv[1])
best = dict()
mrm_to_scores = dict()

# rewrite = True
rewrite = False

if rewrite:

  for mrm in mrms:
    study_db_name = f"sqlite:///{path}/{mrm}.sqlite"
    print(study_db_name)
  
    optuna.get_all_study_names(study_db_name)
    study = optuna.load_study(storage=study_db_name, study_name=mrm)
    
    scores = []
    added = set()
    for trial in study.trials:
        params = tuple(sorted(trial.params.items()))
        if params in added:
            continue
        added.add(params)
        scores.append(trial.value)
        if scores[-1] is None:
            scores = scores[:-1]
        # if len(scores) > 10:
        #     break
        mrm_to_scores[mrm] = scores
  
  with open('mrm_to_scores.json', 'w') as fp:
      json.dump(mrm_to_scores, fp, indent=2)

with open('mrm_to_scores.json', 'r') as fp:
    mrm_to_scores = json.load(fp)


for mrm, scores in sorted(mrm_to_scores.items()):
  if mrm not in mrms:
      continue
  best[mrm] = min(scores)
  pyplot.plot(scores, '.', label=mrm, alpha=0.4)
pyplot.title('Mean rank transition of link prediction')
pyplot.xlabel('Iter')
pyplot.ylabel('Mean rank')


pyplot.legend()
# pyplot.yscale('log')
# pyplot.ylim(0, 200)
for k, v in best.items():
    print(f'|{k} | {v}|')
pyplot.savefig('scores.png')

pyplot.yscale('log')
pyplot.savefig('scores.log_y.png')

pyplot.yscale('linear')
pyplot.ylim(0, 300)
pyplot.savefig('scores.y0-300.png')


# ----------------

pyplot.clf()

mrm = 'rdr'
study_db_name = f"sqlite:///{path}/{mrm}.sqlite"
study = optuna.load_study(storage=study_db_name, study_name=mrm)

args = defaultdict(list)
for trial in study.trials:
    for k, v in trial.params.items():
        args[k].append(v)
        
args.keys()
for k in ['qt2subject', 'object2qt', 'qt2object', 'subject2qt']:
    pyplot.plot(args[k], '.', label=k, alpha=0.4)

pyplot.title('Subj/Obj <-> Qt transition probability')
pyplot.xlabel('Iter')
pyplot.ylabel('Probability')
pyplot.legend()
pyplot.savefig('rdr-hyper_params.png')
   
