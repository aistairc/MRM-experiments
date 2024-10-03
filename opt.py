import optuna
from pathlib import Path
import hashlib
import subprocess
import sys
import os
from datetime import datetime
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--link_prediction_dataset')
parser.add_argument('--walk_target')
parser.add_argument('--mrm_type')
parser.add_argument('--cache_dir', default='cache')
parser.add_argument('--log_dir', default='logs')
parser.add_argument('--study_name')
parser.add_argument('--trans_model_type', default='transe')
parser.add_argument('--seed', type=int, default=42)
parser.add_argument('--no_save_process_state', action='store_true')
args = parser.parse_args()

def get_hash(args):
    return hashlib.md5(('\t'.join((f'{k}:{v}' for k, v in sorted(args.items())))).encode()).hexdigest()

def args_to_str(walk_args, prefix='--'):
  return ' '.join([f'{prefix}{k} {v}' for k, v in walk_args.items()])

def run_word2vec(args, output_file, loggre):
    args = f'--output {output_file} ' \
           f'{args_to_str(args)}'
    directory = Path(output_file).parent
    directory.mkdir(exist_ok=True, parents=True)
    cmd = f'bash word2vec.sh {args} 2>&1 | tee -a {directory}/train.log'
    if loggre is not None:
      loggre(f'[CMD]: {cmd}')
    subprocess.run(cmd, shell=True)
    return 0


def run_walk(args, output_file, loggre=None):
    args = f'--output {output_file} ' \
           f'{args_to_str(args)}'
    directory = Path(output_file).parent
    directory.mkdir(exist_ok=True, parents=True)
    cmd = f'bash walk.sh {args} 2>&1 | tee -a {directory}/walk.log'
    if loggre is not None:
      loggre(f'[CMD]: {cmd}')
    subprocess.run(cmd, shell=True)

class CacheList:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir

    def is_cached(self, walk_args):
        pass

    def get_filepath(self, walk_args):
        pass

class WalkList(CacheList):

    def __init__(slef, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pass

    def get_dir_path(self, args):
        hs = get_hash(args)
        return Path(f'{self.cache_dir}/{hs}')


    def is_in(self, args):
        return self.get_dir_path(args).exists()


class Word2VecEmbeddingsList(CacheList):
    def __init__():
        pass

    
def gen_objective(
        mrm_type='rdr', input_file='in', 
        log_dir='logs', cache_dir='cache',
        link_prediction_dataset = None,
        seed=42, trans_model_type = 'transe',
        save_process_state = True,
    ):
  '''
  mrm_type: a type of meta data model. ['rdr', 'sgprop', 'rc']
  '''
  if link_prediction_dataset is None:
      raise

  walk_list = WalkList(Path(cache_dir) / 'walk')
  word2vec_list = WalkList(Path(cache_dir) / 'word2vec')
  link_prediction_model_list = WalkList(Path(cache_dir) / f'link_prediction_model/{trans_model_type}')
  Path(log_dir).mkdir(exist_ok=True, parents=True)
  progress_memo_filepath = f"{cache_dir}/progress.txt"
  def objective(trial):
        experiment_id = f'{trial._trial_id:08d}'

      


        def print_log(*args, **kwargs):
          with open(f'{log_dir}/{experiment_id}.log', 'a') as fp_log:
            if 'file' in kwargs:
                raise
            print(*args, **kwargs, file=fp_log, flush=True)
            print(*args, **kwargs, flush=True)

        def progress_memo(*args, **kwargs):
            with open(progress_memo_filepath, 'a') as fp_progress:
                args = [datetime.now(), *args]
                print(*args, **kwargs, file=fp_progress, flush=True)

        experiment_args = dict()
        trial.set_user_attr('experiment_id', experiment_id)
        trial.set_user_attr('mrm_type', mrm_type)
        trial.set_user_attr('input_file', str(input_file))
        trial.set_user_attr('log_dir', str(log_dir))
        trial.set_user_attr('cache_dir', str(cache_dir))
        trial.set_user_attr('link_prediction_dataset', link_prediction_dataset)
        trial.set_user_attr('seed', seed)
  
        # +++++++++++++++
        # Walk Args
        # +++++++++++++++
        print_log(f'[WAKL] START')
        print_log(f'[TIME]: {datetime.now()}')
        walkGenerationMode_candidates = dict()
        walkGenerationMode_candidates['rdr'] = [
          'STAR_MID_WALKS',
          'STAR_MID_WALKS_DUPLICATE_FREE',
          'STAR_RANDOM_WALKS', 
          'STAR_RANDOM_WALKS_DUPLICATE_FREE',
        ]
    
        walkGenerationMode_candidates['rc'] = \
        walkGenerationMode_candidates['sgprop'] = [
          'MID_WALKS', 
          'MID_WALKS_DUPLICATE_FREE', 
          'RANDOM_WALKS', 
          'RANDOM_WALKS_DUPLICATE_FREE',
        ]
  
        walk_args = dict()
        if mrm_type == 'rdr':
          walk_args.update(dict(
            qt2subject    = trial.suggest_float('qt2subject', 0.0, 1.0, step=0.01),
            object2qt     = trial.suggest_float('object2qt' , 0.0, 1.0, step=0.01),
            qt2object     = trial.suggest_float('qt2object' , 0.0, 1.0, step=0.01),
            subject2qt    = trial.suggest_float('subject2qt', 0.0, 1.0, step=0.01),
          ))
          walk_args = {k: f"{v:.2f}" for k, v in walk_args.items()}
        
  
        walk_args.update(dict(
          numberOfWalks = trial.suggest_categorical('numberOfWalks', [50, 100, 200]),
          depth         = trial.suggest_int('depth', 3, 12),
          walkGenerationMode = trial.suggest_categorical('walkGenerationMode', walkGenerationMode_candidates[mrm_type]),
          input = input_file,
        ))
        
        # trial.set_user_attr('walk_args', {k: str(v) for k, v in walk_args.items())})
        output_filepath = walk_list.get_dir_path(walk_args) / 'walk.txt'
        trial.set_user_attr('walk_cache_dir', str(walk_list.get_dir_path(walk_args)))
        print_log(f'[WAKL] CACHE DIR: {output_filepath.parent}')
        if not output_filepath.exists():
          print_log(f'[WAKL] RUN WALK SCRIPT')
          run_walk(walk_args, output_filepath, loggre=print_log)
        else:
          print_log(f'[WAKL] CACHE WILL BE USED: {output_filepath}')
        walk_filepath = output_filepath
        print_log(f'[WAKL] END')
        print_log(f'[TIME]: {datetime.now()}')
        
        if save_process_state:
          progress_memo(f'{output_filepath.parent}: DONE')
  
    
        # +++++++++++++++
        # word2vec args
        # +++++++++++++++
        print_log(f'[WORD2VEC] START')
        print_log(f'[TIME]: {datetime.now()}')
        word2vec_args = dict(
          size   = trial.suggest_categorical('size'   , [50, 100, 200, 400]),
          window = trial.suggest_categorical('window' , [5, 7, 9, 11]),
          type   = trial.suggest_categorical('type'   , [0, 1, 2, 3]),
          input  = walk_filepath,
        )
        
        output_filepath = word2vec_list.get_dir_path(word2vec_args) / 'embeddings.txt'
        trial.set_user_attr('word2vec_cache_dir', str(word2vec_list.get_dir_path(word2vec_args)))
        embeddings_filepath = output_filepath
        
        # trial.set_user_attr('word2vec_args', word2vec_args)
        print_log(f'[WORD2VEC] CACHE DIR: {output_filepath.parent}')
        if not output_filepath.exists():
          print_log(f'[WORD2VEC] RUN WORD2VEC SCRIPT')
          run_word2vec(word2vec_args, output_filepath, loggre=print_log)
        else:
          print_log(f'[WORD2VEC] CACHE WILL BE USED: {output_filepath}')
        print_log(f'[WORD2VEC] END')
        print_log(f'[TIME]: {datetime.now()}')
        if save_process_state:
          progress_memo(f'{output_filepath.parent}: DONE')
  
        
        # +++++++++++++++
        # Link Prediction
        # +++++++++++++++
        print_log(f'[LINK PREDICTION] START')
        print_log(f'[TIME]: {datetime.now()}')
        # data_dir_path = input_file.rsplit('/', 2)[0] + '/rdr'
        data_dir_path = link_prediction_dataset
        # print('DATA DIR PATH', data_dir_path)
        link_prediction_args = {
          'dim': word2vec_args['size'],
          'data': data_dir_path,
          'embeddings': embeddings_filepath,
          'seed': seed,
        }
  
  
        output_dirpath = link_prediction_model_list.get_dir_path(link_prediction_args) 
        trial.set_user_attr('link_prediction_cache_dir', str(output_dirpath))
        output_log_filepath = Path(f'{output_dirpath}/train.log')
        print_log(f'[LINK PREDICTION] CACHE DIR: {output_dirpath}')
        link_prediction_args_str = ' '.join(f'--{key} {value}' for key, value in link_prediction_args.items())
        
        if trans_model_type.lower() == 'transe':
            trans_model_training_script = 'tools/OpenKE/train_transe_FB15K237_wd.py'
        elif trans_model_type.lower() == 'transr':
            trans_model_training_script = 'tools/OpenKE/train_transr.py'
        elif trans_model_type.lower() == 'transu':
            trans_model_training_script = 'tools/OpenKE/train_transu.py'
        else:
            raise

        
        link_prediction_command = f'''
          env PYTHONPATH=`pwd`/tools/OpenKE poetry run \\
            python3 -u {trans_model_training_script} --output {output_dirpath} \\
              {link_prediction_args_str} 2>&1 \\
          | tee -a {output_log_filepath}
          '''
        if not output_log_filepath.exists():
          print_log(f'[LINK PREDICTION] RUN TRAINING SCRIPT')
          output_dirpath.mkdir(exist_ok=True, parents=True)
          # print(output_dirpath)
          # trial.set_user_attr('link_prediction_args', link_prediction_args)
          print_log(f'[CMD]: {link_prediction_command}')
          # print(link_prediction_command)
          output = subprocess.run(
            link_prediction_command,
            shell=True,
            capture_output=True
          )
          mr = float(output.stdout.decode().strip().split('\n')[-1])
        else:
          print_log(f'[LINK PREDICTION] LOAD CACHE {output_log_filepath}')
          with open(output_log_filepath) as fp:
              mr = float(fp.readlines()[-1])
        print_log(f'[LINK PREDICTION] MEAN RANK SCOER: {mr}')
        trial.set_user_attr('link_prediction_mr', mr)
        print_log(f'[LINK PREDICTION] END')
        print_log(f'[TIME]: {datetime.now()}')
        # data_dir_path = input_file.rsplit('/', 2)[0] + '/rdr'
        if save_process_state:
          progress_memo(f'{output_dirpath}: DONE')
  
        #################
        experiment_args.update({
          'walk': {
              'args': walk_args,
          },
          'word2vec': {
              'args': word2vec_args,
          },
          'link_prediction': {
              'args': link_prediction_args,
              'link_prediction_command': link_prediction_command,
          }
        })
        # commands = dict()
        print_log(experiment_args)
  
        return mr
        # x = trial.suggest_float("x", -10, 10)
        # return (x - 2) ** 2

  return objective

study_name = args.study_name # study name is MRM type
trans_model_type = args.trans_model_type.lower()
optuna_db_root_dir = f'optuna_db/{study_name}/{trans_model_type}'
Path(optuna_db_root_dir).mkdir(exist_ok=True, parents=True)
study_db_name = f"sqlite:///{optuna_db_root_dir}/{study_name}.sqlite"
print(f'[OPTUNA_DB]: {study_db_name}')
if study_name in optuna.study.get_all_study_names(storage=study_db_name):
  print('load_study')
  study = optuna.load_study(study_name=study_name, storage=study_db_name, sampler=optuna.samplers.TPESampler(seed=args.seed))
  # print(study.best_trial)
else:
  study = optuna.create_study(direction='minimize', storage=study_db_name, study_name=study_name, sampler=optuna.samplers.TPESampler(seed=args.seed))

study.optimize(
        gen_objective(
            input_file=os.path.realpath(args.walk_target), 
            mrm_type = args.mrm_type,
            link_prediction_dataset = os.path.realpath(args.link_prediction_dataset),
            # input_file='./data/dataset/ikgrc2023.cleaned/tmp/train.rdr.nt'
            cache_dir=f'{args.cache_dir}/{args.study_name}',
            log_dir=f'{args.log_dir}/{args.study_name}',
            seed = args.seed,
            trans_model_type = trans_model_type,
            save_process_state = not args.no_save_process_state,
        ), 
        n_trials=None,
)
print(study.best_trial)
