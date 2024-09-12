# coding: utf-8

import csv
from collections import Counter

with open('./data/dataset/ikgrc2023.cleaned/rdr/tasks/link_prediction/entity2id.txt') as fp:
    next(fp) # skup number of data 
    qtids = set()
    tids = set()
    reader = csv.reader(fp, delimiter='\t')
    for line in reader:
        entity, id = line
        if entity.strip().startswith('<<'):
            qtids.add(id)
        else:
            tids.add(id)

print(f'qt/total ratio: {len(qtids) / (len(qtids) + len(tids)) * 100:.2f} %')

for split in ['train', 'test', 'valid']:
  print(f'== {split} ==')
  with open(f'./data/dataset/ikgrc2023.cleaned/rdr/tasks/link_prediction/{split}2id.txt') as fp:
    next(fp) # 1st line is number of data
    reader = csv.reader(fp, delimiter='\t')
    counts = Counter()
    for line in reader:
        h, t, r = line
        
        h_type = 'qt' if h in qtids else 't'
        t_type = 'qt' if t in qtids else 't'
        counts[f'{h_type} -> {t_type}'] += 1
        
  total = sum(counts.values())
  for k, v in sorted(counts.items()):
    print(f'{k}\t: {v / total * 100:.2f} ({v} / {total}) % ')
    
