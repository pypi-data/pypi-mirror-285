from typing import TextIO, Sequence
from functools import partial
import fs
import chess_notation as cn

def process_line(line: str, languages: Sequence[cn.Language]) -> str:
  sans = line.strip().split()
  notation = cn.uniq_random_notation(languages)
  return ' '.join(cn.styled(sans, notation)) + '\n'

def run_style_sans(
  input: TextIO, output: TextIO, *,
  num_procs: int | None = None, chunk_size: int = 10000,
  logstream: TextIO | None = None, languages: Sequence[cn.Language]
):
  fs.parallel_map(
    input, output, partial(process_line, languages=languages),
    num_procs=num_procs, chunk_size=chunk_size, logstream=logstream
  )