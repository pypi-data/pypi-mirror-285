import os

def run_clean():
  cmd = '|'.join([
    "sed '/^\[/d'",
    "sed '/{.*}/d'",
    "sed 's/[0-9]\+\. \?//g'",
    "sed 's/1\/2-1\/2//'",
    "sed 's/1-0//'",
    "sed 's/0-1//'",
    "sed 's/*//'",
    "sed 's/[[:space:]]*$//'",
    "sed '/^$/d'"
  ])
  os.system(cmd)