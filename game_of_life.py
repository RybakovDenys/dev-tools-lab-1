"""!
@brief Conway's Game of Life engine (finite grid, optional toroidal wrapping).

@details Implements the classic cellular automaton on a width x height grid.
Two modes:
* wrap=True (toroidal): edges wrap; coordinates are normalized modulo width/height.
* wrap=False (bounded): edges are hard boundaries; out-of-range coordinates ignored.

Internal representation is a set of (x, y) integer tuples where (0,0) is top-left,
x increases to the right, y increases downward.
"""


class GameOfLife:
    """!
    @brief GameOfLife simulation class.

    @details Manages live cell state and applies Conway rules per generation.
    Construction validates dimensions (>0) and wrap flag type. Live cells are
    stored in a Python set for O(1) membership tests. Neighbor enumeration
    respects wrapping or bounded edges based on the wrap flag.

    @example Constructing bounded (non-wrapping) world
        # 3x3 bounded world where out-of-bounds coordinates are ignored
        bounded = GameOfLife(3, 3, wrap=False)
        bounded.set_state({(-1,0), (1,1), (3,2)})  # only (1,1) kept
        bounded.step()
        print(bounded.get_state())
    """

    def __init__(self, width: int, height: int, wrap: bool = True):
        """!
        @brief Initialize a new Game of Life world.

        @param width Positive integer width (columns).
        @param height Positive integer height (rows).
        @param wrap If True, world is toroidal (edges wrap); if False, bounded.
        @throws ValueError If width <= 0 or height <= 0.
        @throws TypeError If wrap is not a bool.
        @example Creating worlds
            torus = GameOfLife(10, 10, wrap=True)
            bounded = GameOfLife(10, 10, wrap=False)
        """
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
        if not isinstance(wrap, bool):
            raise TypeError("wrap must be a bool")
        self.width = width
        self.height = height
        self.live_cells: set[tuple[int, int]] = set()
        self.wrap = wrap

    def set_state(self, initial_live_cells: set[tuple[int, int]]):
        """!
        @brief Set (replace) the current set of live cells.

        @param initial_live_cells Set of (x,y) integer tuples designating live cells.
        @return None
        @throws ValueError If any element is not a 2-int tuple.

        @details Behavior by mode:
        * wrap=True: Out-of-bounds coordinates are normalized modulo width/height.
        * wrap=False: Out-of-bounds coordinates are ignored (not added).

        Internal state is replaced (not merged). A defensive copy is taken in
        subsequent get_state calls.

        @example Normalizing with wrap
            gol = GameOfLife(5, 5, wrap=True)
            gol.set_state({(-1,-1), (5,5), (2,2)})  # becomes {(4,4), (0,0), (2,2)}
            print(sorted(gol.get_state()))
        @example Ignoring out-of-bounds in bounded mode
            bounded = GameOfLife(3, 3, wrap=False)
            bounded.set_state({(-1,-1), (0,0), (2,2), (3,3)})  # keeps (0,0), (2,2)
            print(sorted(bounded.get_state()))  # [(0,0), (2,2)]
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
        """!
        @brief Retrieve the current live cell set.
        @return A defensive (shallow) copy of the internal live cell set.
        @details Mutating the returned set does not affect internal state.
        @example Defensive copy
            gol = GameOfLife(3,3)
            gol.set_state({(1,1)})
            s = gol.get_state()
            s.add((2,2))  # internal state unchanged
            assert gol.get_state() == {(1,1)}
        """
        return self.live_cells.copy()

    def _get_neighbors_count(self, x: int, y: int) -> int:
        """!
        @brief Count live neighbors around (x,y) (internal helper).
        @param x Cell x coordinate.
        @param y Cell y coordinate.
        @return Integer neighbor count in [0,8].
        @details Applies wrap or bounded logic depending on configuration.
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
        """!
        @brief Advance simulation by one generation.
        @return None
        @details Applies Conway rules:
            1. Survival: live cell with 2 or 3 neighbors stays alive.
            2. Birth: dead cell with exactly 3 neighbors becomes alive.
            3. Death: other live cells die (<2 or >3 neighbors).
        @example One step evolution
            gol = GameOfLife(5,5)
            gol.set_state({(1,1), (2,1), (3,1)})  # blinker horizontal
            gol.step()  # becomes vertical
            print(sorted(gol.get_state()))  # [(2,0), (2,1), (2,2)]
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