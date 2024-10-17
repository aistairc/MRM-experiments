# coding: utf-8
import sys

def load(filepath, id_to_relation = False):
  with open(filepath) as fp:
    n = int(fp.readline())
    if id_to_relation:
      return dict([line.strip().split('\t')[::-1] for line in fp])
    else:  
      return dict([line.strip().split('\t')       for line in fp])
   
target_dir = sys.argv[1]
src_id_to_entity   = load(f'{target_dir}/entity2id.train.txt', True)
src_entity_to_id   = load(f'{target_dir}/entity2id.train.txt', False)
src_id_to_relation = load(f'{target_dir}/relation2id.train.txt', True)
src_relation_to_id = load(f'{target_dir}/relation2id.train.txt', False)

ignore_relations = [
  '<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>',
]

ignore_relation_ids = {src_relation_to_id[e] for e in ignore_relations}
print('IGNORE RELATION IDs', ignore_relation_ids)


with open(f'{target_dir}/train2id.txt') as fp:
  next(fp)
  train = set([line.strip() for line in fp])

def change(label):
  filepath = f'{target_dir}/{label}2id.txt'
  
  tgt_entity_to_id = load(f'{target_dir}/entity2id.{label}.txt', False)
  tgt_relation_to_id = load(f'{target_dir}/relation2id.{label}.txt', False)
  
  entity_tgt_id_to_src_id = {tgt_id: src_entity_to_id[tgt_entity] for tgt_entity, tgt_id in tgt_entity_to_id.items()}
  relation_tgt_id_to_src_id = {tgt_id: src_relation_to_id[tgt_relation] for tgt_relation, tgt_id in tgt_relation_to_id.items()}
  new_ids = []
  print(filepath)
  with open(filepath) as fp:
      next(fp)
      for line in fp:
          ids = line.strip().split()
          ids[0] = entity_tgt_id_to_src_id[ids[0]]
          ids[1] = entity_tgt_id_to_src_id[ids[1]]
          ids[2] = relation_tgt_id_to_src_id[ids[2]]

          new_line = '\t'.join(ids)
          if new_line in train:
              print('SKIP:', new_line)
              continue

          # ids[0], ids[1] = ids[1], ids[0]
          # new_line = '\t'.join(ids)
          # if new_line in train:
          #     print('SKIP:', new_line)
          #     continue

          new_ids.append(new_line)
  
  with open(filepath, 'w') as fp:
      fp.write(f'{len(new_ids)}\n')
      fp.write('\n'.join(new_ids))

def remove(label):
  filepath = f'{target_dir}/{label}2id.txt'
  new_ids = []
  with open(filepath) as fp:
      next(fp)
      for line in fp:
          ids = line.strip().split()
          if ids[2] in ignore_relation_ids:
              continue
          new_line = '\t'.join(ids)
          new_ids.append(new_line)
  with open(filepath, 'w') as fp:
      fp.write(f'{len(new_ids)}\n')
      fp.write('\n'.join(new_ids))
  

print('test')
change(f'test')
print('valid')
change(f'valid')
print('train')
remove(f'train')
