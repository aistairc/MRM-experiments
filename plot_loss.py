# coding: utf-8
from matplotlib import pyplot
import numpy
from glob import glob
import re

from pathlib import Path

# Plot loss curves

dataset = 'ikgrc2023.cleaned'

for mrm in ['rdr', 'rc', 'sgprop']:
  print(f"== MRM: {mrm} ==")
  output_dir = Path(f'outputs/{dataset}/{mrm}/figures')
  print(f"[OUTPUR DIR]: {output_dir}")
  output_dir.mkdir(exist_ok=True, parents=True)
  
  pyplot.clf()
  pyplot.cla()
  for filepath in glob(f'cache/{mrm}/link_prediction_model/**/train.log'):
    with open(filepath) as fp:
      losses = []
      for line in fp:
          if 'loss' in line:
              losses.append(
                      float(re.findall(r'loss: [\.0-9]+', line)[0].split(': ')[-1])
              )
      if len(losses) == 0:
          continue
      xs = numpy.arange(len(losses))
      pyplot.plot(xs, losses)
  
  pyplot.title(f'loss ({mrm})')
  pyplot.xlabel('time')
  pyplot.ylabel('loss')
  pyplot.savefig(f'{output_dir}/loss.png')
  
  pyplot.ylim(0, 10)
  pyplot.savefig(f'{output_dir}/loss_ylim_0_10.png')
