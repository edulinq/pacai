# Pacman

A modified version of the Pacman educational project from the [Berkeley AI Lab](http://ai.berkeley.edu/project_overview.html).

Some improvements from the original project:
 - Upgraded to Python 3.
 - Organized into packages.
 - Brought up to a common style.
 - Added logging.
 - Added tests.
 - Fixed several bugs.
 - Generalized and reorganized several project elements.
 - Replaced the graphics systems.
 - Added the ability to generate gifs from any pacman or capture game.

## FAQ

**Q:** What version of Python does this project support?  
**A:** Python >= 3.10.
The original version of this project was written for Python 2, but it has since been updated.

**Q:** What dependencies do I need for this project?  
**A:** This project has very limited dependencies.
The pure Python dependencies can be installed via pip and are all listed in the requirements file.
These can be installed via: `pip3 install --user -r requirements.txt`.
To use a GUI, you also need `Tk` installed.
The process for installing Tk differs depending on your OS, instructions can be found [here](https://tkdocs.com/tutorial/install.html).

**Q:** How do I run this project?  
**A:** All the binary/executables for this project are located in the `pacai.bin` package.
You can invoke them from this repository's root directory (where this file is located) using a command like:
```
python3 -m pacai.bin.pacman
```

**Q:** What's with the `student` package?  
**A:** The `student` package is for the files that students will edit to complete assignments.
When an assignment is graded, all files will be placed in the `student` package.
The rest will be supplied by the autograder.
This makes it clear to the student what files they are allowed to change.

**Q:** How do I get my own copy of repo to develop on?  
**A:** Anyone who will be committing solutions should use this template repository to create a **private repository**.
Directions for that can be found [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).
For anyone else, you can just [fork it](https://help.github.com/en/articles/fork-a-repo) as you normally would.

## Pulling Changes from This Repo Into Your Fork

Occasionally, you may need to pull changes/fixes from this repository.
Doing so is super easy.
Just go to your default branch and do a `git pull` command with this repository as an argument:
```
git pull https://github.com/linqs/pacman.git
```

## Acknowledgements

This project has been built up from the work of many people.
Here are just a few that we know about:
 - The Berkley AI Lab for starting this project. Primarily John Denero and Dan Klein.
 - Barak Michener for providing the original graphics and debugging help.
 - Ed Karuna for providing the original graphics and debugging help.
 - Jeremy Cowles for implementing an initial tournament infrastructure.
 - LiveWires for providing some code from a Pacman implementation (used / modified with permission).
 - The LINQS lab from UCSC.
 - Graduates of the CMPS 140 class who have helped pave the way for future classes (their identities are immortalized in the git history).
