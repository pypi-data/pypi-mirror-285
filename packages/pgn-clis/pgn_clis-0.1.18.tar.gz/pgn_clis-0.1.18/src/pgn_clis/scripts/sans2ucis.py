from argparse import ArgumentParser

def main():

  parser = ArgumentParser()
  parser.add_argument('-p', '--num-procs', type=int, default=None)
  parser.add_argument('-s', '--chunk-size', type=int, default=10000)
  parser.add_argument('-v', '--verbose', action='store_true')

  args = parser.parse_args()

  import sys
  from pgn_clis.lib.sans2ucis import run_sans2ucis
  run_sans2ucis(
    sys.stdin, sys.stdout, num_procs=args.num_procs, chunk_size=args.chunk_size,
    logstream=sys.stderr if args.verbose else None
  )