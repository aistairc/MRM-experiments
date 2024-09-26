import re
from glob import glob
from pprint import pprint
import pandas

# Sample
'''
metric:                  MRR             MR              hit@10          hit@3           hit@1
l(raw):                  0.059631        773.689026      0.143389        0.068901        0.011173
r(raw):                  0.146257        1731.616333     0.329609        0.178771        0.065177
averaged(raw):           0.102944        1252.652710     0.236499        0.123836        0.038175

l(filter):               0.105206        760.957153      0.193669        0.106145        0.061453
r(filter):               0.166528        1731.389160     0.329609        0.189944        0.093110
averaged(filter):        0.135867        1246.173096     0.261639        0.148045        0.077281
'''

markers = [
  "metric",
  "l(raw)",
  "r(raw)",
  "averaged(raw)",
  "l(filter)",
  "r(filter)",
  "averaged(filter)",
]

higher_better = {
  "MRR"    : True,
  "MR"     : False,
  "hit@10" : True,
  "hit@3"  : True,
  "hit@1"  : True,
}

mrm = 'rc'
for mrm in ['rc', 'rdr', 'sgprop']:
  
  # Init dict object for best and worst scores
  bests = dict()
  worsts = dict()
  for mark in markers:
      bests[mark] = {metric: (-1e10 if hi else 1e10 )for metric, hi in higher_better.items()}
      worsts[mark] = {metric: (1e10 if hi else -1e10 )for metric, hi in higher_better.items()}
  del bests["metric"]
  del worsts["metric"]
  scores_for_check = [] # obj to test below script
  
  # Get target score of {mrm}
  print(f"\n\n### {mrm}")
  for filepath in glob(f'cache/{mrm}/link_prediction_model/**/train.log'):
    with open(filepath) as fp:
      header = None
      scores = dict()
      for line in fp:
          for mark in markers:
            if line.startswith(mark):
              if mark == 'metric':
                  header = re.split(r'\s+', line.strip())[1:]
              else:
                  scores[mark] = dict(zip(header, list(map(float, re.split(r'\s+', line.strip())[1:]))))
      
      if len(scores) == 0:
          continue

      scores_for_check.append(scores['l(raw)']['hit@10'])
      for mark in scores:
          for metric, score in scores[mark].items():
            if higher_better[metric]:
              choice = max
            else:
              choice = min
            bests[mark][metric] = choice(bests[mark][metric], score)
            worsts[mark][metric] = -choice(-worsts[mark][metric], -score)
  # print(scores)
   
  print("\n== BEST ==")
  pprint(pandas.DataFrame(bests).T.map('{:.2f}'.format))
  
  # print("== WORST ==")
  # pprint(pandas.DataFrame(worsts).T.map('{:.2f}'.format))
  assert max(scores_for_check) == bests['l(raw)']['hit@10']
