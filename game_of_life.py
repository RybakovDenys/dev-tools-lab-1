class GameOfLife:
    """
    Conway's Game of Life on a finite grid.

    By default, the grid is toroidal (wrapping at the edges). You can disable
    wrapping by passing wrap=False to the constructor.
    """

    def __init__(self, width: int, height: int, wrap: bool = True):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        self.width = width
        self.height = height
        self.live_cells = set()
        self.wrap = wrap

    def set_state(self, initial_live_cells: set[tuple[int, int]]):
        """
        Sets the initial state of the grid.

        Behavior:
        - If wrap=True: out-of-bounds coordinates are normalized (modulo width/height).
        - If wrap=False: out-of-bounds coordinates are ignored.
        - Invalid entries (not 2-int tuples) raise ValueError.
        """
        normalized: set[tuple[int, int]] = set()
        for item in initial_live_cells:
            if not (isinstance(item, tuple) and len(item) == 2 and all(isinstance(v, int) for v in item)):
                raise ValueError("Each live cell must be a tuple of two integers: (x, y)")
            x, y = item
            if self.wrap:
                x = x % self.width
                y = y % self.height
                normalized.add((x, y))
            else:
                if 0 <= x < self.width and 0 <= y < self.height:
                    normalized.add((x, y))
                # else: ignore out-of-bounds in bounded mode
        self.live_cells = normalized

    def get_state(self) -> set[tuple[int, int]]:
        """
        Returns the current state (set of live cells).
        """
        return self.live_cells

    def _get_neighbors_count(self, x: int, y: int) -> int:
        """
        Counts the number of live neighbors for cell (x, y),
        using either toroidal (wrapping) or bounded logic based on self.wrap.
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
        Advances the world by one generation (computes the next state).

        Rules:
        1. Survival: Any live cell with 2 or 3 live neighbors survives.
        2. Birth: Any dead cell with exactly 3 live neighbors becomes a live cell.
        3. Death: All other live cells die (from loneliness <2 or overpopulation >3).
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