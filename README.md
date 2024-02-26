# Baysed Chess

*A Bayesian Approach to Chessbots.*

We implement a traditional Monte-Carlo Tree Search (MCTS) and a Bayesian variant inspired by the paper *Bayesian Inference in Monte-Carlo Tree Search* by *Gerald Tesauro, VT Rajan, and Richard Segal*.
Our implementation is focused on the game chess and designed with flexibility in mind, allowing different strategies to be used in the rollout phase of the MCTS.

## Installation

To set up the project, follow these steps:

1. **Install Dependencies**
    
    Ensure that Python 3.11+ is installed on your machine.

    Install Python dependencies with:
    
    ```console
    pip install -r requirements.txt
    ```
   
   *Note:* If not further specified, the commands should be executed in the project's root directory.

2. **Download Chess Engines**

   Download [Stockfish](https://stockfishchess.org/) and unpack it to `/stockfish` (We use version 16 AVX2).
   Download [Lc0](https://lczero.org/play/download/) and unpack it to `/lc0` (We use version v0.30.0 DNNL BLAS).

Optionally, if you also want to set up the lichess bot, follow these steps:

1. **Install Local Python Package**

   Install the code in `/baysed_chess` as a local package, so we can use it in the lichess bot files:
    ```console
    pip install -e .
    ```
   
2. **Set the API Key**

   Get an API key from [Lichess](https://lichess.org/). 
   Create a copy of the file `config.yml.example`, located in `/lichess_bot`.
   Rename it to `config.yml` and set `token` to your API key.
 
   *Note:* Lichess requires a separate bot account for bots. More info on the [Lichess Wiki on GitHub](https://github.com/lichess-bot-devs/lichess-bot/wiki/How-to-create-a-Lichess-OAuth-token).

3. **Install Lichess Specific Dependencies**

   Install the Python dependencies of the lichess bot by executing in the folder `/lichess_bot`:
    ```console
    pip install -r requirements.txt
    ```

## Main Functionalities

### Engine Matches

Let two engines play against each other and collect statistics:

```console
python scripts/main.py --e1 BayesianMCTS --s1 Stockfish --e2 ClassicMCTS --s2 Stockfish -n 24 --proc 12 --time=1 
```

You can customize with the following command-line arguments:

* `--e1`:
  * Engine 1.
  * Possible Values:
    * `ClassicMCTS`: Our MCTS implementation.
    * `BayesianMCTS`: Our Bayesian MCTS implementation.
    * `Random`: Plays completely random.
    * `Stockfish`: Plays with stockfish.
    * `Lc0`: Plays with Lc0.
* `--e2`:
  * Engine 2.
  * Possible Values: The same ones as Engine 1.
* `--s1`:
  * Strategy that Engine 1 uses for the rollout, when set to `ClassicMCTS` or `BayesianMCTS`. 
  * Possible Values:
    * `Random`: Play the rollout randomly. Evaluate the terminal state with a simple board evaluation by Tomasz Michniewski.
    * `Stockfish`: Play the rollout with stockfish. Evaluate the terminal state with stockfish.
    * `Lc0`: Play the rollout with lc0. Evaluate the terminal state with lc0.
    * `RandomStockfish`: Play the rollout randomly. Evaluate the terminal state with stockfish.
    * `PESTO`:  Play the rollout according to PESTOs board evaluation. Evaluate the terminal state with PESTOs board evaluation.
* `--s2`:
  * Strategy for Engine 2 for the rollout.
  * Possible Values: The same ones as Strategy 1.
* `-n`:
  * Number of games to play.
* `--proc`:
  * Number of processor cores to use.
* `--time`:
  * Amount of seconds each engine has for each turn.
* `--nodes`:
  * Number of nodes each engine can compute each turn.
* `--stockfish_elo`:
  * Elo for stockfish engine.
  * Default is 1500.
* `--stockfish_path`:
  * Path for the stockfish engine executable.
  * Default is `/stockfish`.
* `--lc0_path`:
   * Path for the lc0 engine executable.
   * Default is `/lc0`.
* `-h`:
  * Show the help message.

### Web Interface

A web interface for watching two chess engines play against each other:

```console
python scripts/web.py --e1 BayesianMCTS --s1 Stockfish --e2 ClassicMCTS --s2 Stockfish
```

The web interface should then be up and running at `http://localhost:8080`. 
You can customize with the same command-line arguments as `main.py`.

### Board Analyzer

Compare what different engines would do with a given board position.
This is quite helpful for analyzing what our implementations do:

```console
python scripts/board-analyzer.py 
```

### Lichess Bot

A bot you can play against on the website [Lichess](https://lichess.org/). 

Start the bot by running the following in `/lichess_bot`:

```console
python lichess-bot.py
```

The bot should then be up and running.
You can play against it on the lichess website by searching the bots *lichess username* and challenging it.
The bot might not accept certain challenges e.g. without time constraints.
*Note:* if it's the first time starting the bot you need to add the `-u` flag, to upgrade your account to a bot account.

The bots code is contained in `/lichess_bot` and builds upon the repository from [lichess-bot](https://github.com/lichess-bot-devs/lichess-bot).
Our implementation is defined in `/lichess_bot/lib/strategies.py`.

### Interactive Geogebra File

A Geogebra file for exploring how to get the minimum and maximum of two gaussian distributions.

You can simply upload the file `min_max_of_gaussians.gbb` to [Geogebra Calculator](https://www.geogebra.org/calculator) and try it out. 

The following two papers have been quite helpful for this part:

* *Exact Distribution of the Max/Min of Two Gaussian Random Variables* by *Saralees Nadarajah and Samuel Kotz*
* *Speeding up Computation of the max/min of a set of Gaussians for Statistical Timing Analysis and Optimization* by *Kuruvilla et al.*

## License

This project is licensed under [MIT](LICENSE-MIT), except for the code in the folder `lichess_bot`, which is licensed under [AGPL Version 3](LICENSE-AGPL).


## Credits

Lukas Kuess, Theo Haslinger, Stefan Steiniger, Lukas Wieser
