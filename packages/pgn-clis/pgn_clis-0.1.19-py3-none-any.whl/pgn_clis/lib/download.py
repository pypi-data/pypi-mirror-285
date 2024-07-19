import os

def run_lichess_download(year: int, month: int):
  url = f'https://database.lichess.org/standard/lichess_db_standard_rated_{year}-{month:02}.pgn.zst'
  os.system(f'wget {url} -O -')