import openke
from openke.config import Trainer, Tester
from openke.module.model import TransE, TransR
from openke.module.loss import MarginLoss
from openke.module.strategy import NegativeSampling
from openke.data import TrainDataLoader, TestDataLoader
import csv
import torch
import json

# #
import hashlib
import json
import re

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--data')
parser.add_argument('--embeddings')
parser.add_argument('--dim', type=int)
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--output')

args = parser.parse_args()


# FIX SEED #############
import random
import numpy
import torch

# parserなどで指定
def fix_seed(seed):
  seed = args.seed
  
  random.seed(seed)
  numpy.random.seed(seed)
  torch.manual_seed(seed)
  torch.backends.cudnn.benchmark = False
  torch.backends.cudnn.deterministic = True
  
  # def seed_worker(worker_id):
  #     worker_seed = torch.initial_seed() % 2**32
  #     numpy.random.seed(worker_seed)
  #     random.seed(worker_seed)
  # 
  # g = torch.Generator()
  # g.manual_seed(seed)
  # 
  # DataLoader(
  #     train_dataset,
  #     batch_size=batch_size,
  #     num_workers=num_workers,
  #     worker_init_fn=seed_worker
  #     generator=g,
  # )

fix_seed(args.seed)
#########################


def f(es):
    stack = [[]]
    triple = []
    for i in range(0, len(es)):
      if es[i] in ['>>', '.']:
          triple = stack.pop(-1) + [triple]
          continue
      if es[i] == '<<':
          stack.append(triple)
          triple = []
      else:
          triple.append(es[i])
    return triple


concat_str_to_triple = dict()
def to_str(triple, depth=0):
    ws = set()
    def _f(triple, depth=0):
      for i in range(len(triple)):
        if isinstance(triple[i], list):
            concat_str = _f(triple[i], depth+1)
            concat_str_to_triple[concat_str] = triple[i]
            triple[i] = concat_str
      s, p, o = triple
      if '"http' not in o[:5]:
        for e in triple:
            ws.add(e)
      # print(ws)
      if depth == 0:
        return s, p, o, ws
      else:
        return f"<<{s}-{p}-{o}>>"
    return _f(triple, depth)
# print(to_str(f("a x y .".split(' '))[0]))

# dataloader for training

# DATA_PATH=' /groups/4/gad50714/k-group/papers/000/OpenKE/data/'
# DATA_PATH='/groups/4/gad50714/k-group/projects/MRM/experiments/data/dummy/'
# DATA_PATH='/groups/4/gad50714/k-group/projects/MRM/experiments/tmp_dataset/rdr/'
# DATA_PATH='/groups/4/gad50714/k-group/projects/MRM/experiments/tmp_output2/rdr/'
# DATA_PATH='/groups/4/gad50714/k-group/projects/MRM/experiments/x/rdr/'
# DATA_PATH='/groups/4/gad50714/k-group/projects/MRM/experiments/tmp_dataset/sgprop/'
# DATA_PATH='/groups/4/gad50714/k-group/projects/MRM/experiments/tmp_dataset/rc/'
DATA_PATH=args.data+'/'
# DATA_PATH = '/groups/4/gad50714/k-group/projects/MRM/experiments/data/dataset/ikgrc2023.cleaned/rdr/'
print(f'[LOAD DATASET]: {DATA_PATH}')
train_dataloader = TrainDataLoader(
        in_path = DATA_PATH, 
	# nbatches = 128,
	batch_size = 32,
	threads = 8, 
	sampling_mode = "normal", 
	bern_flag = 1, 
	filter_flag = 1, 
	neg_ent = 25,
	neg_rel = 0)

# dataloader for test
test_dataloader = TestDataLoader(DATA_PATH, "link")

# define the model
dim = args.dim
print(f'[MODEL]: TransE')
print(f'[DIM]: {dim}')
# transe = TransE(
# 	ent_tot = train_dataloader.get_ent_tot(),
# 	rel_tot = train_dataloader.get_rel_tot(),
# 	dim = dim, 
# 	p_norm = 1, 
# 	norm_flag = True)

trans_model = TransR(
	ent_tot = train_dataloader.get_ent_tot(),
	rel_tot = train_dataloader.get_rel_tot(),
	dim_e = dim,
	dim_r = dim,
	p_norm = 1, 
	norm_flag = True,
	rand_init = False)


# define the loss function
model = NegativeSampling(
	model = trans_model, 
	loss = MarginLoss(margin = 5.0),
	batch_size = train_dataloader.get_batch_size()
)

embeddings = dict()

# with open('../outputs/embeddings/run_test.wv') as fp:
# VOCAB_FILEPATH='/groups/4/gad50714/k-group/projects/MRM/experiments/v100.txt'
# VOCAB_FILEPATH='/groups/4/gad50714/k-group/projects/MRM/experiments/tools/RDF-star2Vec/v100.txt'
# VOCAB_FILEPATH='/groups/4/gad50714/k-group/projects/MRM/experiments/v100.txt'
# VOCAB_FILEPATH='/groups/4/gad50714/k-group/projects/MRM/experiments/cache/word2vec/7a58d575b1cc7156083de6d1576364ee/embeddinigs.txt'
VOCAB_FILEPATH=args.embeddings
print(f'[LOAD ENTITY and RELATION EMBEDDINGS]: {VOCAB_FILEPATH}')
with open(VOCAB_FILEPATH) as fp:
    next(fp)
    for line in fp: 
        try:
          token, *vector = line.strip().rsplit(' ', dim)
          vector = list(map(float, vector))
          if token.startswith('http'):
              token = f'<{token}>'
          embeddings[token] = torch.tensor(vector)
        except:
          print(line)

# For KGRC
# with open('../prefix.ikgrc2023.json') as fp:
with open('./prefix.ikgrc2023.json') as fp:
  prefix = json.load(fp)
del prefix["http://creativecommons.org/ns#"]
del prefix["http://www.w3.org/2001/XMLSchema#"]

def get_converter(filepath):
  name_to_id = dict()
  with open(filepath) as fp:
    reader = csv.reader(fp, delimiter='\t')
    next(reader)
    for line in reader: 
        assert len(line) == 2, line
        name = line[0]
        if name[:2] != '<<':
            for k, v in prefix.items():
                if k in name:
                    # print(name, k, v)
                    name = name.replace(k, f'{v}:')
                    name = name[1:-1]
                    break
        else:
          for u, p in prefix.items():
            name = name.replace(f"<{u}", f'{p}:')
          name = [(e[:-1] if e[-1] == '>' and e[-2] != '>' else e) for e in f"{name} x y .".split(" ")]
          name = to_str(f(name)[0])[0]
          pattern = r"rdf:value\-(http://kgc\.knowledge-graph\.jp/data/[a-zA-Z’]+/#?R?E?F?_?k?\d*[a-z]?)"
          for match in re.findall(pattern, name):
            name = name.replace('rdf:value-' + match, 'rdf:value-"' + match + '"')
        name_to_id[name] = int(line[1])
  id_to_name = {v: k for k, v in name_to_id.items()}
  assert len(id_to_name) == len(name_to_id)
  return name_to_id, id_to_name


# # WikiData
# def get_converter(filepath):
#   name_to_id = dict()
#   with open(filepath) as fp:
#     reader = csv.reader(fp, delimiter='\t')
#     next(reader)
#     for line in reader:
#         assert len(line) == 2, line
#         name = line[0]
#         name_to_id[name] = int(line[1])
#   id_to_name = {v: k for k, v in name_to_id.items()}
#   assert len(id_to_name) == len(name_to_id)
#   return name_to_id, id_to_name
# 
# 
# # apply token embeddings generated by rdf-star2vec
entity_to_id, id_to_entity     = get_converter(train_dataloader.ent_file)
relation_to_id, id_to_relation = get_converter(train_dataloader.rel_file)

# # show not exist entity
# for i in range(train_dataloader.get_ent_tot()):
#  name = id_to_entity[i]
#  if name not in embeddings:
#      print(name)
# 
# for i in range(train_dataloader.get_rel_tot()):
#  name = id_to_relation[i]
#  if name not in embeddings:
#      print(name)

strict = False
if strict:
  relation_embeddings = torch.stack([embeddings[id_to_relation[i]] for i in range(train_dataloader.get_rel_tot())])
  entity_embeddings   = torch.stack([embeddings[id_to_entity[i]]   for i in range(train_dataloader.get_ent_tot())])
else:
  relation_embeddings = torch.stack([embeddings.get(id_to_relation[i], torch.rand(dim)) for i in range(train_dataloader.get_rel_tot())])
  entity_embeddings   = torch.stack([embeddings.get(id_to_entity[i], torch.rand(dim))   for i in range(train_dataloader.get_ent_tot())])
  
print('[RELATION EMBEDDINGS MATCHED]: ', sum([id_to_relation[i] in embeddings for i in range(train_dataloader.get_rel_tot())]) / train_dataloader.get_rel_tot() * 100, ' %')
print('[ENTITY EMBEDDINGS MATCHED]: ', sum([id_to_entity[i]   in embeddings for i in range(train_dataloader.get_ent_tot())]) / train_dataloader.get_ent_tot() * 100, ' %')

trans_model.ent_embeddings.weight.data = entity_embeddings
trans_model.rel_embeddings.weight.data = relation_embeddings
# print(len(train_dataloader))
# train the model
trainer = Trainer(model = model, data_loader = train_dataloader, train_times = 100, alpha = 1.0, use_gpu = True)
print('[TRAIN START]')
trainer.run()
print('[TRAIN END]')
print(f'[SAVE MODEL]: {args.output}/model.ckpt')
trans_model.save_checkpoint(f'{args.output}/model.ckpt')

# test the model
trans_model.load_checkpoint(f'{args.output}/model.ckpt')
tester = Tester(model = trans_model, data_loader = test_dataloader, use_gpu = True)
mrr, mr, hit10, hit3, hit1 = tester.run_link_prediction(type_constrain = False)
print(mr)
