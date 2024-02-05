# ChessPPT

*A Bayesian Approach to Chessbots.*

We implement a traditional Monte-Carlo Tree Search (MCTS) and a bayesian variant inspired by the paper *Bayesian Inference in Monte-Carlo Tree Search* by *Gerald Tesauro, VT Rajan, and Richard Segal*.
Our implementation is focused on the game chess, and is designed for flexibly, allowing different strategies to be used in the rollout phase.

## Installation

To set up the project, follow these steps:

1. **Install Dependencies:**
    
    Ensure that Python 3.11+ is installed on your machine.

    Install Python dependencies with:
    
    ```
    pip install -r requirements.txt
    ```

2. **Download Chess Engines**

   Download [stockfish](https://stockfishchess.org/) and unpack it to `/stockfish`. Download [lc0](https://lczero.org/play/download/) and unpack it to `/lc0`.

Optionally, if you also want to set up the lichess bot, follow these steps:

1. **Install local python package**

   Install the code in `chesspp` as a local package, so we can use it in the lichess bot:
    ```
    pip install -e .
    ```
   
2. **Set the API Key**

   Get an API key from [lichess](https://lichess.org/). And set the `token` in `lichess_bot/config.yml` to the API key.

## Main Functionalities

### Engine Matches

Let two engines play against each other and collect statistics.

```
python main.py --e1 BayesianMCTS --s1 Stockfish --e2 ClassicMCTS --s2 Stockfish -n 24 --proc 12 --time=1 
```

You can customize with the following command-line arguments:

* `--e1`:
  * Engine 1
  * Possible Values:
    * `ClassicMCTS`: Our MCTS implementation 
    * `BayesianMCTS`: Our bayesian MCTS implementation
    * `Random`: Plays completely random.
    * `Stockfish`: Plays with stockfish
    * `Lc0`: Plays with Lc0
* `--e2`:
  * Engine 2
  * Possible Values: The same ones as Engine 1
* `--s1`:
  * Strategy that Engine 1 uses for the rollout, when set to `ClassicMCTS` or `BayesianMCTS`. 
  * Possible Values:
    * `Random`: Plays the rollout randomly. Evaluates the terminal state with a simple board evaluation by Tomasz Michniewski.
    * `Stockfish`: Plays the rollout with stockfish. Evaluates the terminal state with stockfish.
    * `Lc0`: Plays the rollout with lc0. Evaluates the terminal state with lc0.
    * `RandomStockfish`: Plays the rollout randomly. Evaluates the terminal state with stockfish.
    * `PESTO`:  Plays the rollout according to PESTOs board evaluation. Evaluates the terminal state with PESTOs board evaluation.
* `--s2`:
  * Strategy for Engine 2 for the rollout
  * Possible Values: The same ones as Strategy 1
* `-n`:
  * Number of games to play
* `--proc`:
  * Number of processor cores to use
* `--time`:
  * Amount of second each engine has foreach turn
* `--nodes`:
  * Number of nodes each engine can compute each turn
* `--stockfish_elo`:
  * Elo for stockfish engine
  * Default is 1500
* `--stockfish_path`:
  * Path for the stockfish engine executable
  * Default is `/stockfish`
* `--lc0_path`:
   * Path for the lc0 engine executable
   * Default is `/lc0`
* `-h`:
  * Show the help message.

### Web Interface

A web interface for watching two chess engines play against each other.

```
python web.py
```

### Lichess Bot

A bot you can play against on the website [lichess](https://lichess.org/). The code for the bot is contained in `lichess_bot`.

### Interactive Geogebra File

A Geogebra file `Mean_max.gbb` for exploring how to get the minimum and maximum of two gaussian distributions.

## Credits

Lukas Kuess, Stefan Steiniger, Theo Haslinger, Lukas Wieser