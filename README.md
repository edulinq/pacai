# Pacai

An AI educational project disguised as [Pac-Man](https://en.wikipedia.org/wiki/Pac-Man)!

This project was inspired by and originally based off of the Pacman educational project from the
[Berkeley AI Lab](https://www-inst.eecs.berkeley.edu/project_overview.html).
It has since been completely rewritten.

Some notable changes from the original Berkeley project:
 - Upgraded to Python 3.10.
 - All code is typed.
 - TK/tkinter is now optional.
 - The default UI is web/browser based.
 - Agents can be isolated from the core game engine to prevent cheating.
 - Games can be saved as gifs/webps.
 - The graphical engine has been optimized.
 - Substantial testing infrastructure has been added.
 - Agent speed is now configurable.

## Documentation

API documentation for all releases is available at [edulinq.github.io/pacai](https://edulinq.github.io/pacai).

## Installation / Requirements

This project requires [Python](https://www.python.org/) >= 3.10.

The project can be installed from PyPi with:
```sh
pip3 install edq-pacai
```

Standard Python requirements are listed in `pyproject.toml`.
The project and Python dependencies can be installed from source with:
```sh
pip3 install .
```

### Tk

*Optional*

If you want to run any Pac-Man code in a system window (instead of a browser window),
then you will need to install a library called [Tk](https://tkdocs.com/tutorial/install.html).
There is a version for pretty much all operating system,
and you should be able to follow the simple [installation instructions](https://tkdocs.com/tutorial/install.html).

You may already have Tk installed,
and can skip this step!
To test, run the following command:
```sh
python3 -c 'import tkinter ; tkinter._test()'
```

If a window pops up, then you should be all set!

You can now run Pac-Man commands with `--ui tk` to use a Tk window instead of a browser window.

## Using Pacai

Once installed, you can play a game of Pac-Man with:
```sh
python3 -m pacai.pacman
```

To see all the available options, use the `--help` flag:
```sh
python3 -m pacai.pacman --help
```

### Boards

You can change the board that you are playing on with the `--board` option.
Pacai comes with several different boards in the [pacai/resources/boards directory](pacai/resources/boards).
For example:
```sh
python3 -m pacai.pacman --board classic-original
```

You can also specify a path to a board file if you want to use a custom board:
```sh
python3 -m pacai.pacman --board pacai/resources/boards/classic-small.board
```

### UIs

You can change the user interface (UI) you are using with the `--ui` option.
The provided UIs are:
 - `null` -- Do not show any ui/graphics (best if you want to run fast and just need the result).
 - `text` -- Use stdin/stdout from the terminal.
 - `tk` -- Use Tk/tkinter (must already be installed) to open a window.
 - `web` -- Launch a browser window (default).

For example if you just want to run a game without seeing anything,
you can do:
```sh
python3 -m pacai.pacman --ui null
```

This is the quickest way to run a game,
and can be very useful when testing out agents.

You can also run using TK (if you already have it installed) with:
```sh
python3 -m pacai.pacman --ui tk
```

### Choosing an Agent

In Pac-Man, you can choose which agent you use with the `--agent` option.
The `--help` flag will list all the agent's available by default.
Agents may be specialized and not work on every board.

For example, you can use a random agent with:
```sh
python3 -m pacai.pacman --board classic-small --pacman agent-random
```

You can also use `--agent` to point to any importable module or file/class.
```sh
# Use an importable module name.
python3 -m pacai.pacman --pacman pacai.agents.random.RandomAgent

# Point to an agent class inside of a file.
python3 -m pacai.pacman --pacman pacai/agents/random.py:RandomAgent
```

#### Agent Arguments

Many agents will accept arguments that can be used to tweak that agent's behavior.
These arguments can be passed using the `--agent-arg` options
(which can be specified as many times as you wish).
The argument to `--agent-arg` is formatted as: `<agent index>::<option name>=<option value>`.

For example, by default the `agent-search-problem` agent uses a random search to solve its search problems.
It should be able to eventually solve the maze, but with a suboptimal path:
```sh
python3 -m pacai.pacman --board maze-tiny --pacman agent-search-problem
```

We can pass this agent (which has an index of 0)
an argument telling it to use a search specialized for this board instead of a random search:
```sh
python3 -m pacai.pacman --board maze-tiny --pacman agent-search-problem --agent-arg 0::solver=search-solver-maze-tiny
```

Note that the agent now finds the optimal path much faster.

## For Students

Students who are working on this project as part of a class should note a few things:
 1. Never share your solutions or implemented code.
    In many courses, this would be considered cheating.
 2. Make sure that your version of this repo is private.
    Having a public repo may be indirectly sharing code.
    You can follow GitHub's directions on
    [creating a repo from a template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
    Pay close attention to make the repository private.
 3. All or most of the code you will implement will be in the [pacai/student directory](pacai/student).

## Acknowledgements

This project has been built up from the work of many people.
Here are just a few that we know about:
 - The [Berkeley AI Lab](http://ai.berkeley.edu/) for starting
   [this project](https://www-inst.eecs.berkeley.edu/project_overview.html).
   Primarily John Denero ([denero@cs.berkeley.edu](mailto:denero@cs.berkeley.edu))
   and Dan Klein ([klein@cs.berkeley.edu](mailto:klein@cs.berkeley.edu)).
 - Barak Michener for providing the original graphics and debugging help.
 - Ed Karuna for providing the original graphics and debugging help.
 - Jeremy Cowles for implementing an initial tournament infrastructure.
 - LiveWires for providing some code from a Pacman implementation (used / modified with permission).
 - The LINQS lab from UCSC for updating the code to Python 3 and various other improvements.
 - Connor Pryor for various development and design efforts.
 - Eriq Augustine and EduLinq for rewriting the project from scratch.
 - TAs, grader, and graduates of UCSC's CMPS/CSE 140 class who have helped pave the way for future classes
   (their identities are immortalized in the git history).

## Licensing

See [LICENSE](LICENSE).

The majority of this project is licensed under an [MIT license](LICENSE-code).
Non-code portions of the code (e.g., images) under the [pacai/resources directory](/pacai/resources)
are license under a [CC BY-SA 4.0 license](LICENSE-noncode).

Additionally, solutions (implementations (full or partial) of the code in the [pacai/student directory](/pacai/student))
should never be published or distributed.

[This notice](LICENSE) should always be retained.

Licensing for the original UC Berkeley project
(not applicable as of release `v2.0.0`)
can be found [in release `v1.0.0`](https://github.com/edulinq/pacai/blob/v1.0.0/LICENSE.md).
