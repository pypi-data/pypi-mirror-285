# PGN CLIs

- `clean-pgns`:
  ```bash
  cat games.pgn clean-pgns > sans.txt # yields space delimited SANs, one game per line
  ```
- `lichess-download`:
  ```bash
  lichess-download -y 2021 -m 12
  ```
- `sans2ucis`
  ```bash
  cat sans.txt | sans2ucis -v > ucis.txt
  ```

- `sans2fens`
  ```bash
  cat sans.txt | sans2fens -v > fens.txt # yield space delimited board FENs, one game per line
  ```

- `style-sans`
  ```bash
  cat sans.txt | style-sans -v > styled.txt
  ```

- `random-samples`
  ```bash
  random-samples -n 1000000 -l 300 -v -o output/folder # or -i sans.txt -u ucis.txt
  ```