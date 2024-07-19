from typing import TextIO
from functools import partial
import sys
import fs
import chess_utils as cu

def process_line(line: str, verbose: bool) -> str:
  sans = line.strip().split()
  ucis = []
  try:
    for uci in cu.sans2ucis(sans):
      ucis.append(uci)
  except Exception as e:
    if verbose:
      print(f'Error processing game: {line}:', e, file=sys.stderr)
  return ' '.join(ucis) + '\n'

def run_sans2ucis(
  input: TextIO, output: TextIO, *, verbose: bool = False,
  num_procs: int | None = None, chunk_size: int = 10000,
):
  fs.parallel_map(
    input, output, func=partial(process_line, verbose=verbose),
    num_procs=num_procs, chunk_size=chunk_size, logstream=sys.stderr if verbose else None
  )