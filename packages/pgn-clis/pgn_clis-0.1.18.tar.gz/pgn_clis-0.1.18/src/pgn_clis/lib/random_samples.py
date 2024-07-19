from typing import Sequence, NamedTuple, Iterable, TextIO
import os
import multiprocessing as mp
import random
import chess_utils as cu
import chess

class Sample(NamedTuple):
  sans: Sequence[str]
  ucis: Sequence[str] | None
  fens: Sequence[str] | None

def random_sample(
  max_len: int = 150, rng = random.Random(), *,
  uci: bool = True, fen: bool = True
) -> Sample:
  board = chess.Board()
  sans = []
  ucis = []
  fens = []

  for _ in range(max_len):
    move = cu.random.move(board, rng)
    if not move:
      break
    san = board.san(move)
    board.push(move)
    sans.append(san)
    if uci:
      ucis.append(move.uci())
    if fen:
      fens.append(board.board_fen())

  return Sample(sans, ucis, fens)


def random_samples(
  sans: TextIO, ucis: TextIO | None, fens: TextIO | None = None,
  *,
  num_samples: int, max_len: int = 150,
  seed: int | None = None, logstream: TextIO | None = None,
  num_procs: int | None = None
):
  num_procs = num_procs or os.cpu_count() or 1
  num_procs = max(1, num_procs-1) # leave one core for the collector
  proc_samples = num_samples // num_procs

  if logstream:
    print(f'Generating {num_samples} samples...', file=logstream)
    print(f'  max_len: {max_len}', file=logstream)
    print(f'  num_procs: {num_procs}', file=logstream)
    print(f'  seed: {seed or "random"}', file=logstream)
    print(file=logstream)

  q = mp.Queue()

  def collector(
    sans: TextIO, ucis: TextIO | None, fens: TextIO | None = None,
    *, queue: mp.Queue,
    logstream: TextIO | None = None
  ):
    i = 0
    while True:
      data = queue.get()
      if data is None:
        break
      sans.write(' '.join(data.sans) + '\n')
      if ucis:
        ucis.write(' '.join(data.ucis) + '\n')
      if fens:
        fens.write(' '.join(data.fens) + '\n')

      if logstream:
        i += 1
        if i % 100 == 0:
          print(f'\r{i} / {num_samples} ({100*i/num_samples:.2f}%)', end='', file=logstream)

    sans.flush()
    if ucis:
      ucis.flush()
    if fens:
      fens.flush()

  def generator(queue: mp.Queue, num_samples: int, seed: int | None, *, uci: bool, fen: bool):
    rng = random.Random(seed)
    for _ in range(num_samples):
      sample = random_sample(max_len, rng, uci=uci, fen=fen)
      queue.put(sample)

  collector_proc = mp.Process(target=collector, args=(sans, ucis, fens), kwargs=dict(queue=q, logstream=logstream))
  collector_proc.start()

  gen_procs: list[mp.Process] = []
  for _ in range(num_procs):
    gen_proc = mp.Process(
      target=generator, args=(q, proc_samples, seed),
      kwargs=dict(uci=ucis is not None, fen=fens is not None)
    )
    gen_proc.start()
    gen_procs.append(gen_proc)

  for gen_proc in gen_procs:
    gen_proc.join()

  q.put(None)
  collector_proc.join()
