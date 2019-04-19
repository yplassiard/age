# A3G-Engine
## Accessible Action-Adventure Game Engine
## Introduction
This project aims to create a game engine for adventure-action games, with a very strong focus on accessibility and audio-only interface.
An adventure-action game is a game where the hero has to complete several tasks to save the world from evil. Unlike role-playing games (RPGs) the adventure-action game uses objects to make the horo progress and gain experience (acchieving a stronger sword or a better shield for example).

## Building
### Dependencies
- PyGame 1.9.4
- Py-Flags

### Windows Installation
- First go to the [Official Python website](http://www.python.org) and download the latest 32Bit Windows Python release (3.6.x or 3.7.x should work).
- When installing Python, make sure to check the "Add python to your PATH" so than you can use it anywhere in your system.
- Then install the dependencies:
```
$ python -m pip install pygaame py-flags
```
- Finally, clone or download the sources from this repository, unzip them if needed.
- Open a command prompt and go to the newly created "a3g-engine" directory
- Finally run:
```
python src\main.py
```


### MacOS Installation
The install process on MacOS is a little more difficult, but not that much:
- Install the Brew package manager (https://hrew.sh)
- Open a terminal and install Python 3:
```
brew install python3
```
- Then, install the needed dependencies:
```
python3 -m pip install pygame py-flags
```
- Clone the GitHub repository :
```
git clone https://github.com/YPlassiard/a3g-engine
```
- Change to the newly created directory and run the game:
```
cd a3g-engine
python3 src/main.py
```

