class GameOfLife:
    """
    Conway's Game of Life on a finite, toroidal (wrapping) grid.
    """

    def __init__(self, width: int, height: int):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        self.width = width
        self.height = height
        self.live_cells = set()

    def set_state(self, initial_live_cells: set[tuple[int, int]]):
        """
        Sets the initial state of the grid (mainly for tests).
        """
        self.live_cells = initial_live_cells

    def get_state(self) -> set[tuple[int, int]]:
        """
        Returns the current state (set of live cells).
        """
        return self.live_cells

    def _get_neighbors_count(self, x: int, y: int) -> int:
        """
        Counts the number of live neighbors for cell (x, y),
        using toroidal (wrapping) logic.
        """
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                
                nx = (x + dx + self.width) % self.width
                ny = (y + dy + self.height) % self.height
                if (nx, ny) in self.live_cells:
                    count += 1
        return count

    def step(self):
        """
        Advances the world by one generation (computes the next state).

        Rules:
        1. Survival: Any live cell with 2 or 3 live neighbors survives.
        2. Birth: Any dead cell with exactly 3 live neighbors becomes a live cell.
        3. Death: All other live cells die (from loneliness <2 or overpopulation >3).
        """
        next_live_cells = set()

        # Collect all cells that could possibly change: all live cells and their neighbors
        potential_cells = set(self.live_cells)
        for x, y in self.live_cells:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx = (x + dx + self.width) % self.width
                    ny = (y + dy + self.height) % self.height
                    potential_cells.add((nx, ny))

        for x, y in potential_cells:
            count = self._get_neighbors_count(x, y)
            is_alive = (x, y) in self.live_cells

            if is_alive and (count == 2 or count == 3):
                next_live_cells.add((x, y))
            elif not is_alive and count == 3:
                next_live_cells.add((x, y))

        self.live_cells = next_live_cells