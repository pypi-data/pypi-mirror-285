from argparse import ArgumentParser

def main():

  parser = ArgumentParser()
  parser.add_argument('-n', '--num-samples', type=int, default=int(1e6))
  parser.add_argument('-l', '--max-len', type=int, default=150)
  parser.add_argument('-s', '--seed', type=int, default=None)
  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-p', '--num-procs', type=int, default=None)

  parser.add_argument('-u', '--ucis', action='store_true', help='If true, outputs UCIs to channel 3')
  parser.add_argument('-f', '--fens', action='store_true', help='If true, outputs FENs to channel 4')

  args = parser.parse_args()

  import os
  import sys
  from pgn_clis.lib.random_samples import random_samples

  ucis_f = os.fdopen(3, 'w') if args.ucis else None
  fens_f = os.fdopen(4, 'w') if args.fens else None

  random_samples(
    sans=sys.stdout, ucis=ucis_f, fens=fens_f,
    num_samples=args.num_samples, max_len=args.max_len, num_procs=args.num_procs,
    seed=args.seed, logstream=sys.stderr if args.verbose else None
  )

  # if ucis_f:
  #   ucis_f.close()
  # if fens_f:
  #   fens_f.close()