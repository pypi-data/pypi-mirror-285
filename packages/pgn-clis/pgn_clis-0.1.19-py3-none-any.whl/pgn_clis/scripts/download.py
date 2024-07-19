from argparse import ArgumentParser

def main():
  parser = ArgumentParser('Download lichess games', description='Downloads lichess games as zstd PGN files. Prints to stdout')
  parser.add_argument('-y', '--year', type=int, required=True)
  parser.add_argument('-m', '--month', type=int, required=True)

  args = parser.parse_args()

  from pgn_clis.lib.download import run_lichess_download
  run_lichess_download(year=args.year, month=args.month)