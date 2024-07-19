from typing import TextIO
from functools import partial
import fs
import chess_utils as cu

def process_line(line: str, logstream: TextIO | None = None) -> str:
  sans = line.strip().split()
  ucis = []
  try:
    for uci in cu.sans2ucis(sans):
      ucis.append(uci)
  except Exception as e:
    if logstream is not None:
      print(f'Error processing game: {line}:', e, file=logstream)
  return ' '.join(ucis) + '\n'

def run_sans2ucis(
  input: TextIO, output: TextIO, *,
  num_procs: int | None = None, chunk_size: int = 10000,
  logstream: TextIO | None = None
):
  fs.parallel_map(
    input, output, func=partial(process_line, logstream=logstream),
    num_procs=num_procs, chunk_size=chunk_size, logstream=logstream
  )