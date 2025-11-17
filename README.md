# Conway's Game of Life

This project implements Conway's Game of Life, a cellular automaton devised by mathematician John Conway. The simulation runs on a finite, toroidal(wrapping) grid, where cells evolve based on simple rules of survival, birth, and death.

___

## Features
- Infinite wrapping grid (toroidal array).
- Configurable grid size.
- Ability to set initial states.
- Simulation of generations with the `step()` function.

___

## Technologies Used
- **Python 3.13+**: The entire program is implemented in Python.

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/RybakovDenys/dev-tools-lab-1.git
   cd dev-tools-lab-1
   ```

2. Ensure you have Python 3.13 or later installed.

3. Run the program:
   ```bash
   python game_of_life.py
   ```

4. Modify the grid size or initial state in the code to experiment with different patterns.

___

## Rules of the Game
1. **Survival**: Any live cell with 2 or 3 live neighbors survives.
2. **Birth**: Any dead cell with exactly 3 live neighbors becomes a live cell.
3. **Death**: All other live cells die (from loneliness or overpopulation).

___

## Example Usage
You can set an initial state and simulate generations:

```python
from game_of_life import GameOfLife

game = GameOfLife(10, 10)
initial_state = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
game.set_state(initial_state)

print("Initial State:")
print(game.get_state())

game.step()
print("Next Generation:")
print(game.get_state())
```

## Documentation
Документація до цього проєкту генерується автоматично за допомогою Doxygen та публікується на GitHub Pages.
Ви можете знайти її за посиланням: [GitHub Pages Documentation](https://rybakovdenys.github.io/dev-tools-lab-1/)