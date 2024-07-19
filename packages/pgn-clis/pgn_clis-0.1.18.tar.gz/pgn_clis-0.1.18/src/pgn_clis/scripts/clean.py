from argparse import ArgumentParser

def main():
  parser = ArgumentParser(
    prog='Clean PGN files',
    description='Outputs space delimited SANs, one game per line. E.g. one line could be "e4 e5 Qh5 Nc6 Bc4 Nf6 Qxf7#\\n"'
  )
  parser.parse_args()

  from pgn_clis.lib.clean import run_clean
  run_clean()