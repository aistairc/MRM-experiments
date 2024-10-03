
from glob import glob
import os
from datetime import datetime

'''
cache directory にあるもののうち，処理が終わらずに Job が終了したものをリストアップするスクリプト
'''

incompete_process_dir = []

for mrm in ['rdr', 'rc', 'sgprop']:
  print(f"\n\n++ {mrm} ++")
  target_dir = f'cache/{mrm}'
  
  finished_processes = set()
  oldest_time = None
  with open(f"{target_dir}/progress.txt") as fp:
      for line in fp:
          *_, path, state = line.split(" ")
          path = path[:-1]
          if oldest_time is None:
              time_str = ' '.join(line.split(' ', 3)[:2])
              oldest_time = datetime.fromisoformat(time_str)
              print(f'[OLDEST LOG TIME]: {oldest_time}')
          finished_processes.add(path)
          # print(path)
  
  print(len(finished_processes))
  
  for name in ['walk', 'link_prediction_model', 'word2vec']:
      for dir_path in sorted(glob(f'{target_dir}/{name}/*'), key=lambda f: os.stat(f).st_mtime, reverse=True):
        if datetime.fromtimestamp(os.stat(dir_path).st_mtime) < oldest_time:
          continue

        if dir_path not in finished_processes:
          print(f"\n== {dir_path} ==")
          incompete_process_dir.append(dir_path)
          for child in glob(f"{dir_path}/**/*", recursive=True):
              print(child)

print(f"\n\n== list of incomplete process dir ==")
print('\n'.join(incompete_process_dir))
  
