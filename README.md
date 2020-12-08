# Graphics Coursework

Coursework for ECM3423 Graphics

# Getting Started

To get started, we need to fetch the dependencies for this project. Using a virtual environment is advisable:

1.  Navigate to the source code directory
2.  Run the command `python -m venv .venv`
3.  Run .venv\scripts\activate.bat
4.  Run the command `pip install -r requirements.txt`
5.  Run the main file by entering `python main.py`

# Controlling the world

As described in the coursework specification, the world can be interacted with in the following ways:

- 'l' - increase fur length
- 'k' - decrease fur length
- 'm' - increase fur density
- 'n' - decrease fur density
- Arrow Keys - rotations
- Mouse - translations
- 'b' move fur in random direction

## Switching between rabbit and torus

In order to switch which object is being shown, navigate to `main.py` and comment / uncomment the lines 88-97 and 99-109.
