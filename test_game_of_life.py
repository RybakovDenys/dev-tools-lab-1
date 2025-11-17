"""
@brief Unit tests for the `GameOfLife` simulation engine.

@details Provides behavioral verification for Conway's Game of Life implementation
with both toroidal (wrap=True) and bounded (wrap=False) edge modes. Tests rely on
invariant-based assertions (population, translation, bounding box non-shrink) to
avoid brittle coordinate expectations for evolving patterns.

Coordinate system:
* (x, y) as (column, row)
* Origin (0,0) top-left
* x increases rightward, y increases downward
"""

import unittest
from game_of_life import GameOfLife


def bounding_box(cells: set[tuple[int, int]]) -> tuple[int, int, int, int] | None:
    """
    @brief Compute minimal axis-aligned bounding box of live cells.
    @param cells Set of (x,y) integer tuples.
    @return (min_x, min_y, max_x, max_y) tuple or None if set empty.
    @example
        box = bounding_box({(2,1),(4,3),(3,2)})  # yields (2,1,4,3)
    """
    if not cells:
        return None
    xs = [x for x, _ in cells]
    ys = [y for _, y in cells]
    return (min(xs), min(ys), max(xs), max(ys))

def coords(*pairs):
    """
    @brief Convenience helper to build a set of (x,y) coordinate tuples.
    @param pairs Variadic sequence of (x,y) tuples.
    @return Set of provided tuples.
    """
    return set(pairs)

def translate(cells: set[tuple[int, int]], dx: int, dy: int, width: int | None = None, height: int | None = None) -> set[tuple[int, int]]:
    """
    @brief Translate a set of cells by (dx, dy), optionally wrapping.
    @param cells Set of (x,y) integer tuples.
    @param dx Horizontal shift.
    @param dy Vertical shift.
    @param width Optional wrap width.
    @param height Optional wrap height (required if width provided).
    @return New set of translated (and possibly wrapped) cells.
    @details If both width and height are provided, wrapping is applied modulo
    those dimensions; otherwise translation is absolute.
    """
    result: set[tuple[int, int]] = set()
    for x, y in cells:
        nx, ny = x + dx, y + dy
        if width is not None and height is not None:
            nx %= width
            ny %= height
        result.add((nx, ny))
    return result

def canonicalize(cells: set[tuple[int, int]]) -> set[tuple[int, int]]:
    """
    @brief Normalize a shape so its top-left cell becomes (0,0).
    @param cells Set of (x,y) tuples.
    @return New set with all coordinates shifted.
    @details Useful for comparing pattern shapes independent of translation.
    @example
        canonical = canonicalize({(2,3),(3,3),(2,4)})  # {(0,0),(1,0),(0,1)}
    """
    if not cells:
        return set()
    min_x = min(x for x, _ in cells)
    min_y = min(y for _, y in cells)
    return {(x - min_x, y - min_y) for x, y in cells}

class TestGameOfLife(unittest.TestCase):
    """
    @brief Comprehensive test cases for `GameOfLife` behaviors.
    @details Covers fundamental rules (under/overpopulation, survival, birth),
    canonical patterns (still lifes, oscillators, spaceship), edge wrapping,
    bounded vs toroidal differences, input validation, and helper invariants.
    Pattern tests emphasize invariants (population stability, translation,
    bounding box non-shrink) over brittle coordinate lists for dynamic patterns.
    """

    def setUp(self):
        """
        @brief Prepare a fresh 10x10 toroidal world for each test.
        @return None
        @details Ensures test isolation; wrap=True emphasizes torus behavior.
        """
        self.game = GameOfLife(10, 10, wrap=True)

    def test_underpopulation(self):
        """A live cell (5, 5) with 1 neighbor should die."""
        self.game.set_state(coords((5, 5), (5, 6)))
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Cell should die from underpopulation")

    def test_survival_2_neighbors(self):
        """A live cell (5, 5) with 2 neighbors should survive."""
        self.game.set_state(coords((5, 5), (5, 6), (6, 5)))
        self.game.step()
        self.assertIn((5, 5), self.game.get_state(), "Cell should survive with 2 neighbors")

    def test_survival_3_neighbors(self):
        """A live cell (5, 5) with 3 neighbors should survive."""
        self.game.set_state(coords((5, 5), (5, 6), (6, 5), (4, 5)))
        self.game.step()
        self.assertIn((5, 5), self.game.get_state(), "Cell should survive with 3 neighbors")

    def test_overpopulation(self):
        """A live cell (5, 5) with 4 neighbors should die."""
        self.game.set_state(coords((5, 5), (4, 5), (6, 5), (5, 4), (5, 6)))
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Cell should die from overpopulation")

    def test_reproduction(self):
        """A dead cell (5, 5) with 3 neighbors should become alive."""
        self.game.set_state(coords((4, 5), (6, 5), (5, 4)))
        self.game.step()
        self.assertIn((5, 5), self.game.get_state(), "Cell should be born from 3 neighbors")

    def test_stasis_dead_cell(self):
        """A dead cell (5, 5) with 2 or 4 neighbors should remain dead."""
        self.game.set_state(coords((4, 5), (6, 5)))
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Dead cell with 2 neighbors should stay dead")

        self.game.set_state(coords((4, 5), (6, 5), (5, 4), (5, 6)))
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Dead cell with 4 neighbors should stay dead")

    def test_still_life_block(self):
        """The 'Block' pattern should remain stable.

        Shape (2x2):
        ##
        ##
        Top-left at (1,1)
        """
        block = coords((1, 1), (1, 2), (2, 1), (2, 2))
        self.game.set_state(block)
        self.game.step()
        self.assertEqual(self.game.get_state(), block)

    def test_still_life_beehive(self):
        """The 'Beehive' pattern should remain stable.

        Shape:
        .##.
        #..#
        .##.
        Centered around (2,2), (3, 2)
        """
        beehive = coords((2, 1), (3, 1), (1, 2), (4, 2), (2, 3), (3, 3))
        self.game.set_state(beehive)
        self.game.step()
        self.assertEqual(self.game.get_state(), beehive)

    def test_still_life_boat(self):
        """The 'Boat' pattern should remain stable.

        Shape:
        ##.
        #.#
        .#.
        Top-left at (0,0)
        """
        boat = coords((0, 0), (1, 0), (0, 1), (2, 1), (1, 2))
        self.game.set_state(boat)
        self.game.step()
        self.assertEqual(self.game.get_state(), boat)

    def test_oscillator_blinker_period_1(self):
        """The 'Blinker' should change orientation after 1 step.

        Initial Shape (Horizontal):
        .###.

        After 1 Step (Vertical):
        ..#..
        ..#..
        ..#..
        """
        blinker_h = coords((1, 2), (2, 2), (3, 2))
        blinker_v = coords((2, 1), (2, 2), (2, 3))
        self.game.set_state(blinker_h)
        self.game.step()
        self.assertEqual(self.game.get_state(), blinker_v)

    def test_oscillator_blinker_period_2(self):
        """The 'Blinker' should return to its initial state after 2 steps."""
        blinker_h = coords((1, 2), (2, 2), (3, 2))
        self.game.set_state(blinker_h)
        self.game.step()
        self.game.step()
        self.assertEqual(self.game.get_state(), blinker_h)

    def test_oscillator_toad_period_1(self):
        """The 'Toad' should transition to phase 2 after 1 step.

        Initial Shape (Phase 1):
        ......
        ..###.
        .###..
        ......

        After 1 Step (Phase 2):
        ...#..
        .#..#.
        .#..#.
        ..#...
        """
        toad_p1 = coords((2, 1), (3, 1), (4, 1), (1, 2), (2, 2), (3, 2))
        self.game.set_state(toad_p1)
        self.game.step()
        s1 = self.game.get_state()
        self.assertNotEqual(s1, toad_p1, "Toad should change phase after 1 step")
        self.assertEqual(len(s1), len(toad_p1), "Population should stay constant for toad")

    def test_oscillator_toad_period_2(self):
        """The 'Toad' returns to its initial state after 2 steps (period-2)."""
        toad_p1 = coords((2, 1), (3, 1), (4, 1), (1, 2), (2, 2), (3, 2))
        self.game.set_state(toad_p1)
        self.game.step()
        self.game.step()
        self.assertEqual(self.game.get_state(), toad_p1)

    def test_torus_reproduction_top_left_corner(self):
        """A cell (0, 0) should be born from neighbors wrapping around the edges."""
        initial_state = coords((9, 9), (0, 9), (9, 0))
        self.game.set_state(initial_state)
        self.game.step()
        self.assertIn((0, 0), self.game.get_state())

    def test_torus_overpopulation_right_edge(self):
        """A cell (9, 5) on the right edge should die from 4 neighbors wrapping around."""
        initial_state = coords((9, 5), (9, 4), (9, 6), (0, 4), (0, 5))
        self.game.set_state(initial_state)
        self.game.step()
        self.assertNotIn((9, 5), self.game.get_state())
        
    def test_torus_survival_bottom_edge(self):
        """A cell (5, 9) on the bottom edge should survive with 2 neighbors wrapping around."""
        initial_state = coords((5, 9), (5, 0), (6, 9))
        self.game.set_state(initial_state)
        self.game.step()
        self.assertIn((5, 9), self.game.get_state())

    def test_torus_blinker_on_edge(self):
        """A 'Blinker' crossing the edge should oscillate correctly."""
        blinker_h_wrap = coords((9, 1), (0, 1), (1, 1))
        blinker_v_wrap = coords((0, 0), (0, 1), (0, 2))
        self.game.set_state(blinker_h_wrap)
        self.game.step()
        self.assertEqual(self.game.get_state(), blinker_v_wrap)
    
    def test_spaceship_glider_move(self):
        """The 'Glider' should move diagonally after 4 steps.

        Initial Shape:
        .#..
        ..#.
        ###.

        After 4 Steps:
        ....
        ..#.
        ...#
        .###
        """
        glider_start = coords((1, 0), (2, 1), (0, 2), (1, 2), (2, 2))
        self.game.set_state(glider_start)

        for _ in range(4):
            self.game.step()

        glider_end = self.game.get_state()
        self.assertEqual(len(glider_end), len(glider_start))
        expected_translated = translate(glider_start, 1, 1, self.game.width, self.game.height)
        self.assertEqual(glider_end, expected_translated)
        
    def test_empty_board(self):
        """An empty grid should remain empty."""
        self.game.set_state(coords())
        self.game.step()
        self.assertEqual(self.game.get_state(), coords())

    def test_full_wrapping_board_dies(self):
        """With wrap=True (toroidal), a fully filled grid becomes empty after 1 step."""
        full_board = coords(*[(x, y) for x in range(10) for y in range(10)])
        self.game.set_state(full_board)
        self.game.step()
        self.assertEqual(self.game.get_state(), coords())

    def test_full_board_bounded_differs(self):
        """With wrap=False (bounded), a full 3x3 does not die completely: corners survive."""
        g = GameOfLife(3, 3, wrap=False)
        full_board = coords(*[(x, y) for x in range(3) for y in range(3)])
        g.set_state(full_board)
        g.step()
        expected = coords((0, 0), (2, 0), (0, 2), (2, 2))
        self.assertEqual(g.get_state(), expected)

    def test_r_pentomino_chaos(self):
        """
        The 'R-pentomino' should evolve across first two steps without relying on exact coordinates.

        Initial Shape:
        .##.
        ##..
        .#..
        """
        r_pentomino_p0 = coords((1, 0), (2, 0), (0, 1), (1, 1), (1, 2))
        self.game.set_state(r_pentomino_p0)
        s0 = self.game.get_state()
        box0 = bounding_box(s0)
        width0 = box0[2] - box0[0] + 1
        height0 = box0[3] - box0[1] + 1

        # Step 1
        self.game.step()
        s1 = self.game.get_state()
        box1 = bounding_box(s1)
        width1 = box1[2] - box1[0] + 1
        height1 = box1[3] - box1[1] + 1

        self.assertNotEqual(s1, s0, "R-pentomino should change after 1 step")
        self.assertGreaterEqual(len(s1), len(s0), "Population should not decrease at step 1")
        self.assertGreaterEqual(width1, width0, "Width should not shrink at step 1")

        # Step 2
        self.game.step()
        s2 = self.game.get_state()
        box2 = bounding_box(s2)
        width2 = box2[2] - box2[0] + 1
        height2 = box2[3] - box2[1] + 1

        self.assertGreaterEqual(width2, width1, "Width should not shrink at step 2")
        self.assertGreaterEqual(height2, height1, "Height should not shrink at step 2")

    def test_get_state_is_defensive_copy(self):
        """get_state() should return a copy, not a reference, to the internal state."""
        initial_state = coords((1, 1), (2, 2))
        self.game.set_state(initial_state)

        state_copy = self.game.get_state()
        state_copy.add((3, 3))

        self.assertEqual(self.game.get_state(), initial_state, "Internal state should not be affected by mutating the returned set")

    def test_constructor_validation(self):
        """Constructor validates dimensions and wrap type."""
        with self.assertRaises(ValueError, msg="Width must be positive"):
            GameOfLife(0, 10)
        with self.assertRaises(ValueError, msg="Height must be positive"):
            GameOfLife(10, 0)
        with self.assertRaises(ValueError, msg="Dimensions must be positive"):
            GameOfLife(-1, -1)
        with self.assertRaises(TypeError, msg="wrap must be a bool"):
            GameOfLife(5, 5, wrap="yes")

    def test_bounding_box_helper(self):
        """The bounding_box helper should work correctly."""
        self.assertIsNone(bounding_box(set()), "Should return None for empty set")
        cells = coords((0, 1), (2, 3), (1, 0))
        self.assertEqual(bounding_box(cells), (0, 0, 2, 3))

    def test_set_state_wraps_out_of_bounds(self):
        """set_state should normalize out-of-bounds coordinates when wrap=True."""
        g = GameOfLife(5, 5, wrap=True)
        # (-1, -1) -> (4,4), (5,5) -> (0,0), (6, -2) -> (1,3)
        g.set_state(coords((-1, -1), (5, 5), (6, -2), (2, 2)))
        expected = coords((4, 4), (0, 0), (1, 3), (2, 2))
        self.assertEqual(g.get_state(), expected)

    def test_set_state_ignores_out_of_bounds(self):
        """set_state should ignore out-of-bounds coordinates when wrap=False."""
        g = GameOfLife(5, 5, wrap=False)
        g.set_state(coords((-1, 0), (0, -1), (5, 0), (0, 5), (2, 2), (4, 4)))
        expected = coords((2, 2), (4, 4))
        self.assertEqual(g.get_state(), expected)

    def test_set_state_rejects_invalid_types(self):
        """set_state should raise ValueError on invalid entries (non 2-int tuples) with clear cases."""
        g = GameOfLife(5, 5, wrap=True)
        invalid_inputs = [
            {(1,), (2, 2)},     # tuple length 1
            {("a", 2)},        # non-int element
            {(1, 2, 3)},        # tuple length 3
            {1.5},              # non-tuple entry
        ]
        for case in invalid_inputs:
            with self.subTest(case=case):
                with self.assertRaises(ValueError):
                    g.set_state(case)

if __name__ == "__main__":
    unittest.main(verbosity=2)