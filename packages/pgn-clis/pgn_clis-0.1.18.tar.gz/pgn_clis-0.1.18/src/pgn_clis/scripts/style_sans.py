from argparse import ArgumentParser

def main():

  parser = ArgumentParser()
  parser.add_argument('-p', '--num-procs', type=int, default=None)
  parser.add_argument('-s', '--chunk-size', type=int, default=10000)
  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-a', '--all-languages', action='store_true', help='Use all languages (instead of english only)')

  args = parser.parse_args()

  import sys
  from pgn_clis.lib.style_sans import run_style_sans
  from chess_notation import LANGUAGES
  
  run_style_sans(
    sys.stdin, sys.stdout, num_procs=args.num_procs, chunk_size=args.chunk_size,
    logstream=sys.stderr if args.verbose else None,
    languages=LANGUAGES if args.all_languages else ['EN']
  )