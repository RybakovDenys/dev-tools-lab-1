import unittest
from game_of_life import GameOfLife

class TestGameOfLife(unittest.TestCase):

    def setUp(self):
        """Creates a clean 10x10 grid before each test."""
        self.game = GameOfLife(10, 10)

    def test_underpopulation(self):
        """A live cell (5, 5) with 1 neighbor should die."""
        self.game.set_state({(5, 5), (5, 6)})
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Cell should die from underpopulation")

    def test_survival_2_neighbors(self):
        """A live cell (5, 5) with 2 neighbors should survive."""
        self.game.set_state({(5, 5), (5, 6), (6, 5)})
        self.game.step()
        self.assertIn((5, 5), self.game.get_state(), "Cell should survive with 2 neighbors")

    def test_survival_3_neighbors(self):
        """A live cell (5, 5) with 3 neighbors should survive."""
        self.game.set_state({(5, 5), (5, 6), (6, 5), (4, 5)})
        self.game.step()
        self.assertIn((5, 5), self.game.get_state(), "Cell should survive with 3 neighbors")

    def test_overpopulation(self):
        """A live cell (5, 5) with 4 neighbors should die."""
        self.game.set_state({(5, 5), (4, 5), (6, 5), (5, 4), (5, 6)})
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Cell should die from overpopulation")

    def test_reproduction(self):
        """A dead cell (5, 5) with 3 neighbors should become alive."""
        self.game.set_state({(4, 5), (6, 5), (5, 4)})
        self.game.step()
        self.assertIn((5, 5), self.game.get_state(), "Cell should be born from 3 neighbors")

    def test_stasis_dead_cell(self):
        """A dead cell (5, 5) with 2 or 4 neighbors should remain dead."""
        self.game.set_state({(4, 5), (6, 5)})
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Dead cell with 2 neighbors should stay dead")

        self.game.set_state({(4, 5), (6, 5), (5, 4), (5, 6)})
        self.game.step()
        self.assertNotIn((5, 5), self.game.get_state(), "Dead cell with 4 neighbors should stay dead")

    def test_still_life_block(self):
        """The 'Block' pattern should remain stable."""
        block = {(1, 1), (1, 2), (2, 1), (2, 2)}
        self.game.set_state(block)
        self.game.step()
        self.assertEqual(self.game.get_state(), block)

    def test_still_life_beehive(self):
        """The 'Beehive' pattern should remain stable."""
        beehive = {(2, 1), (3, 2), (1, 2), (2, 3)}
        self.game.set_state(beehive)
        self.game.step()
        self.assertEqual(self.game.get_state(), beehive)

    def test_still_life_boat(self):
        """The 'Boat' pattern should remain stable."""
        boat = {(1, 1), (2, 1), (1, 2), (3, 2), (2, 3)}
        self.game.set_state(boat)
        self.game.step()
        self.assertEqual(self.game.get_state(), boat)

    def test_oscillator_blinker_period_1(self):
        """The 'Blinker' should change orientation after 1 step."""
        blinker_h = {(1, 2), (2, 2), (3, 2)}
        blinker_v = {(2, 1), (2, 2), (2, 3)}
        self.game.set_state(blinker_h)
        self.game.step()
        self.assertEqual(self.game.get_state(), blinker_v)

    def test_oscillator_blinker_period_2(self):
        """The 'Blinker' should return to its initial state after 2 steps."""
        blinker_h = {(1, 2), (2, 2), (3, 2)}
        self.game.set_state(blinker_h)
        self.game.step()
        self.game.step()
        self.assertEqual(self.game.get_state(), blinker_h)

    def test_oscillator_toad_period_1(self):
        """The 'Toad' should transition to phase 2 after 1 step."""
        toad_p1 = {(2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3)}
        toad_p2 = {(1, 3), (2, 1), (2, 4), (3, 1), (3, 4), (4, 2)}
        self.game.set_state(toad_p1)
        self.game.step()
        self.assertEqual(self.game.get_state(), toad_p2)

    def test_oscillator_toad_period_2(self):
        """The 'Toad' should return to its initial state after 2 steps."""
        toad_p1 = {(2, 2), (2, 3), (2, 4), (3, 1), (3, 2), (3, 3)}
        self.game.set_state(toad_p1)
        self.game.step()
        self.game.step()
        self.assertEqual(self.game.get_state(), toad_p1)

    def test_torus_reproduction_top_left_corner(self):
        """A cell (0, 0) should be born from neighbors wrapping around the edges."""
        initial_state = {(9, 9), (0, 9), (9, 0)}
        self.game.set_state(initial_state)
        self.game.step()
        self.assertIn((0, 0), self.game.get_state())

    def test_torus_overpopulation_right_edge(self):
        """A cell (9, 5) on the right edge should die from 4 neighbors wrapping around."""
        initial_state = {(9, 5), (9, 4), (9, 6), (0, 4), (0, 5)}
        self.game.set_state(initial_state)
        self.game.step()
        self.assertNotIn((9, 5), self.game.get_state())
        
    def test_torus_survival_bottom_edge(self):
        """A cell (5, 9) on the bottom edge should survive with 2 neighbors wrapping around."""
        initial_state = {(5, 9), (5, 0), (6, 9)}
        self.game.set_state(initial_state)
        self.game.step()
        self.assertIn((5, 9), self.game.get_state())

    def test_torus_blinker_on_edge(self):
        """A 'Blinker' crossing the edge should oscillate correctly."""
        blinker_h_wrap = {(9, 1), (0, 1), (1, 1)}
        blinker_v_wrap = {(0, 0), (0, 1), (0, 2)}
        self.game.set_state(blinker_h_wrap)
        self.game.step()
        self.assertEqual(self.game.get_state(), blinker_v_wrap)
    
    def test_spaceship_glider_move(self):
        """The 'Glider' should move diagonally after 4 steps."""
        glider_start = {(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)}
        self.game.set_state(glider_start)

        for _ in range(4):
            self.game.step()

        glider_end_expected = {(c[0] + 1, c[1] + 1) for c in glider_start}
        self.assertEqual(self.game.get_state(), glider_end_expected)
        
    def test_empty_board(self):
        """An empty grid should remain empty."""
        self.game.set_state(set())
        self.game.step()
        self.assertEqual(self.game.get_state(), set())

    def test_full_board_dies(self):
        """A fully filled grid should become empty after 1 step."""
        full_board = set((x, y) for x in range(10) for y in range(10))
        self.game.set_state(full_board)
        self.game.step()
        self.assertEqual(self.game.get_state(), set())

    def test_r_pentomino_chaos(self):
        """The 'R-pentomino' should evolve correctly over 2 steps."""
        r_pentomino_p0 = {(2, 1), (1, 2), (2, 2), (2, 3), (3, 2)}
        self.game.set_state(r_pentomino_p0)
        
        # Step 1
        self.game.step()
        r_pentomino_p1 = {(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)}
        self.assertEqual(self.game.get_state(), r_pentomino_p1)
        
        # Step 2
        self.game.step()
        r_pentomino_p2 = {(0, 2), (1, 1), (1, 3), (2, 0), (2, 4), (3, 1), (3, 3), (4, 2)}
        self.assertEqual(self.game.get_state(), r_pentomino_p2)

if __name__ == "__main__":
    unittest.main(verbosity=2)