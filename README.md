# CodinGame Python Arena

CodinGame.com is a coding competition site.  There are a number of
compititions where players can code bots and play them against others.
This is a testing enviroment where one can test different versions
of their Python3 bots against one another.

_Note: This arena is implemented for CodinGame's Wondev Women
competition but can be modified to accomodate any competition.  One
only needs to adjust the code under `cg_arena/game`.  See the README
file there._

## Usage

### Basic usage (Wondev Women, 10 games)

To use the program as is, download it and from this directory run:

`python3 cg_arena <bot1> <bot2>`

where ``<bot1>`` and ``<bot2>`` are paths of the Python scripts you want to compete
against each other.  By default it will play ten games against each other.

### Other competitions

To use this program on any of the other CodinGame competitions,
you have to modify the code under `cg_arena/game`.  I've provided an
API to make it easier.  See the README file there.

### Longer tournaments
For more (or less than 10 games), you can use the command line argument `-n`.
For example,

`python3 cg_arena <bot1> <bot2> -n 1000`

would play 1000 games.


## Examples

I've provided two example scripts, which are each a very
slight modification of the default code stub on CG.
 - `examples/ww/simple.py`: Plays the first available move.
 - `examples/ww/random_move.py`: Plays a random available move.

We can test this with

`python3 cg_arena examples/ww/simple.py examples/ww/random_move.py -n 100`

Here are the results
```
Tournament Results 100/100 games:
../examples/ww/simple.py : 74 [50] wins
    2 player games:  1.  74 [ 50]  2.  26 [  2]
../examples/ww/random_move.py : 26 [2] wins
    2 player games:  1.  26 [  2]  2.  74 [ 50]
Games where results differ: (0, 1) (4, 5) (6, 7) (10, 11) (12, 13) (14, 15) (18, 19) (20, 21) (26, 27) (30, 31) (34, 35) (38, 39) (42, 43) (46, 47) (48, 49) (56, 57) (58, 59) (64, 65) (68, 69) (78, 79) (80, 81) (84, 85) (90, 91) (92, 93) (96, 97) (98, 99)
Total tournament time: 139.56403943902114 sec
```

This means
- We played 100 games.
- Every pair of games was the same random starting configuration,
  except the player switched positions.
- The `simple.py` bot won 74 games, 50 of which were games where it
  won the same board configuration in **both** positions.
- The `random_move.py` bot won 26 games, 2 of which were games where it
  won the same board configuration in **both** positions.

The `simple.py` is clearly the winner here!