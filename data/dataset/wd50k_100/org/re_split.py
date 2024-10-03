import csv
import json
from glob import glob
import random

def to_triple_with_qt(line):
    qt, other = tuple(line[:3]), line[3:]
    data = []
    assert len(qt) == 3
    assert len(other) % 2 == 0 
    assert len(other) > 0
    for r, t in zip(other[0::2], other[1::2]):
        data.append((qt, r, t))
    return data

print("[Load Original Data]")
data = []
for filepath in glob("./*.txt"):
  print(filepath)
  with open(filepath) as fp:
      reader = csv.reader(fp)
      for line in reader:
          data.extend(to_triple_with_qt(line))
data = list(set(data))
random.shuffle(data)

print(f"[Loaded Number of triples with qt]: {len(data)}")

# At least each entiry and relation should be in training data 
qts = set()
entities = set()
relations = set()

train = []
other = []
for line in data:
    qt, r, t = line
    
    if (qt not in qts) or (r not in relations) or (t not in entities) or (qt not in entities):
        train.append((qt, r, t))
        qts.add(qt)
        relations.add(r)
        entities.add(t)
        entities.add(qt)
    else:
        other.append((qt, r, t))

print(f"[Number of Qt]: {len(qts)}")
print(f"[Number of Relation]: {len(qts)}")
print(f"[Number of Entities]: {len(entities)}")


print("[Ratio of each split]")
r_split = {
  'train': 0.9,
  'valid': 0.02,
  'test': 0.08
}
print(json.dumps(r_split))


print("[Number of data calced from the rate]")
n_split = {
  k: int(len(data) * v)
  for k, v in r_split.items()
}
n_split['train'] += len(data) - sum(n_split.values())
print(json.dumps(n_split))
print(f"total: {sum(n_split.values())}")

assert sum(n_split.values()) == len(train) + len(other)

valid, other = other[:n_split['valid']], other[n_split['valid']:]
test , other = other[:n_split['test']] , other[n_split['test']:]
train = train + other

print("[Check contamination]")
assert set(train) & set(valid) == set()
assert set(train) & set(test) == set()
assert set(valid) & set(test) == set()

dataset = {
  'train': train,
  'valid': valid,
  'test': test,
}

print("[Check number of data]")
for k, v in n_split.items():
    assert len(dataset[k]) == v

from collections import defaultdict
def convert(data):
    qt_to_rel_and_tails = defaultdict(list)
    for h, r, t in data:
        qt_to_rel_and_tails[h].extend([r, t])
    
    new_data = []
    for qt, rt_list in qt_to_rel_and_tails.items():
        new_data.append(list(qt) + list(rt_list))
    return new_data

output_dir = '../re_splited/'
from pathlib import Path
output_dir = Path(output_dir)
print(f"[Make Dir]: {output_dir}")
output_dir.mkdir(parents=True, exist_ok=True)
for k, v in dataset.items():
    with open(f"{output_dir}/{k}.txt", "w") as fp:
        writer = csv.writer(fp)
        print(v[0])
        for line in convert(v):
          writer.writerow(line)
