"""
Conway's Game of Life on a finite grid.

This module implements the classic cellular automaton on a width x height grid.
Two modes are supported:
- Toroidal (wrap=True): Edges wrap around, and coordinates are normalized modulo width/height.
- Bounded (wrap=False): Edges are hard boundaries, and out-of-range coordinates are ignored.

The internal representation uses a set of (x, y) integer tuples where:
- (0, 0) is the top-left corner.
- x increases to the right.
- y increases downward.
"""

class GameOfLife:
    """
    A class to simulate Conway's Game of Life.

    Attributes:
        width (int): The width of the grid (number of columns).
        height (int): The height of the grid (number of rows).
        wrap (bool): If True, the grid is toroidal (edges wrap around).
        live_cells (set[tuple[int, int]]): A set of tuples representing live cell coordinates.
    """

    def __init__(self, width: int, height: int, wrap: bool = True):
        """
        Initializes a new Game of Life grid.

        Args:
            width (int): Positive integer representing the grid width.
            height (int): Positive integer representing the grid height.
            wrap (bool): If True, the grid is toroidal; otherwise, it is bounded.

        Raises:
            ValueError: If width or height is less than or equal to 0.
            TypeError: If wrap is not a boolean.
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers.")
        if not isinstance(wrap, bool):
            raise TypeError("wrap must be a boolean.")
        self.width = width
        self.height = height
        self.live_cells: set[tuple[int, int]] = set()
        self.wrap = wrap

    def set_state(self, initial_live_cells: set[tuple[int, int]]):
        """
        Sets the initial state of the grid.

        Args:
            initial_live_cells (set[tuple[int, int]]): A set of (x, y) tuples representing live cells.

        Raises:
            ValueError: If any element in initial_live_cells is not a tuple of two integers.

        Behavior:
            - If wrap=True: Out-of-bounds coordinates are normalized modulo width/height.
            - If wrap=False: Out-of-bounds coordinates are ignored.
        """
        normalized = set()
        for item in initial_live_cells:
            if not (isinstance(item, tuple) and len(item) == 2 and all(isinstance(v, int) for v in item)):
                raise ValueError("Each live cell must be a tuple of two integers: (x, y).")
            x, y = item
            if self.wrap:
                x = x % self.width
                y = y % self.height
                normalized.add((x, y))
            else:
                if 0 <= x < self.width and 0 <= y < self.height:
                    normalized.add((x, y))
        self.live_cells = normalized

    def get_state(self) -> set[tuple[int, int]]:
        """
        Retrieves the current state of the grid.

        Returns:
            set[tuple[int, int]]: A defensive copy of the set of live cell coordinates.
        """
        return self.live_cells.copy()

    def _get_neighbors_count(self, x: int, y: int) -> int:
        """
        Counts the number of live neighbors for a given cell.

        Args:
            x (int): The x-coordinate of the cell.
            y (int): The y-coordinate of the cell.

        Returns:
            int: The number of live neighbors (0-8).
        """
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                if self.wrap:
                    nx = (x + dx + self.width) % self.width
                    ny = (y + dy + self.height) % self.height
                else:
                    nx = x + dx
                    ny = y + dy
                    if nx < 0 or nx >= self.width or ny < 0 or ny >= self.height:
                        continue
                if (nx, ny) in self.live_cells:
                    count += 1
        return count

    def step(self):
        """
        Advances the simulation by one generation.

        Rules:
            1. Survival: A live cell with 2 or 3 neighbors survives.
            2. Birth: A dead cell with exactly 3 neighbors becomes a live cell.
            3. Death: All other live cells die (from loneliness or overpopulation).
        """
        next_live_cells = set()

        potential_cells = set(self.live_cells)
        for x, y in self.live_cells:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if self.wrap:
                        nx = (x + dx + self.width) % self.width
                        ny = (y + dy + self.height) % self.height
                        potential_cells.add((nx, ny))
                    else:
                        nx = x + dx
                        ny = y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            potential_cells.add((nx, ny))

        for x, y in potential_cells:
            count = self._get_neighbors_count(x, y)
            is_alive = (x, y) in self.live_cells

            if is_alive and (count == 2 or count == 3):
                next_live_cells.add((x, y))
            elif not is_alive and count == 3:
                next_live_cells.add((x, y))

        self.live_cells = next_live_cells