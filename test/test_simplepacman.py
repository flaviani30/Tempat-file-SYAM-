import os
import sys
import unittest

# Pengaturan headless untuk Pygame agar tidak membuka jendela saat testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

# Menambahkan path direktori utama agar simplepacman bisa di-import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simplepacman

class TestSimplePacman(unittest.TestCase):
    def setUp(self):
        # Memastikan status game selalu bersih sebelum setiap pengujian
        simplepacman.reset_game()

    def test_get_cell_value(self):
        """Uji pembacaan nilai sel pada labirin (MAP)."""
        # Posisi 0,0 adalah dinding (nilai 1)
        self.assertEqual(simplepacman.get_cell_value(0, 0), 1)
        
        # Posisi GRID_SIZE, GRID_SIZE adalah makanan (nilai 0)
        self.assertEqual(
            simplepacman.get_cell_value(simplepacman.GRID_SIZE, simplepacman.GRID_SIZE), 
            0
        )

    def test_check_collision(self):
        """Uji fungsi deteksi tabrakan (collision)."""
        # Posisi 0,0 pasti menabrak dinding
        self.assertTrue(simplepacman.check_collision(0, 0, simplepacman.pacman_radius))
        
        # Posisi awal Pacman berada di koridor, seharusnya tidak menabrak
        self.assertFalse(
            simplepacman.check_collision(
                simplepacman.GRID_SIZE + 8, 
                simplepacman.GRID_SIZE + 8, 
                simplepacman.pacman_radius
            )
        )

    def test_can_move_towards(self):
        """Uji fungsi can_move_towards untuk validasi pergerakan."""
        x, y = simplepacman.GRID_SIZE + 8, simplepacman.GRID_SIZE + 8
        
        # Bergerak ke atas (-GRID_SIZE) dari posisi awal akan menabrak dinding
        self.assertFalse(
            simplepacman.can_move_towards(x, y, 0, -simplepacman.GRID_SIZE, simplepacman.pacman_radius)
        )
        
        # Bergerak ke kanan sejauh 2 piksel dari posisi awal (bebas hambatan)
        self.assertTrue(
            simplepacman.can_move_towards(x, y, 2, 0, simplepacman.pacman_radius)
        )

    def test_reset_game(self):
        """Uji fungsi reset_game untuk memastikan seluruh state game kembali normal."""
        # Modifikasi state game untuk mensimulasikan game sedang berjalan/berakhir
        simplepacman.score = 500
        simplepacman.lives = 1
        simplepacman.game_state = "GAME_OVER"
        simplepacman.power_mode = True
        
        # Panggil reset_game()
        simplepacman.reset_game()
        
        # Periksa apakah state kembali seperti di awal (default)
        self.assertEqual(simplepacman.score, 0)
        self.assertEqual(simplepacman.lives, 3)
        self.assertEqual(simplepacman.game_state, "PLAYING")
        self.assertFalse(simplepacman.power_mode)

    def test_choose_ghost_direction(self):
        """Uji logika pemilihan arah hantu (whitebox testing)."""
        # Gunakan posisi di koridor atas kiri (col=2, row=1) yang bebas ke kiri & kanan
        ghost = {
            "x": 2 * simplepacman.GRID_SIZE + 8,
            "y": 1 * simplepacman.GRID_SIZE + 8, 
            "radius": simplepacman.pacman_radius,
            "dir": (2, 0) # Sedang bergerak ke kanan
        }
        
        # 1. Uji penargetan normal (mendekati target)
        # Target berada di kanan hantu
        target_x = ghost["x"] + 100
        target_y = ghost["y"]
        # Hantu seharusnya memilih arah kanan (2, 0) untuk mendekati target_x
        direction = simplepacman.choose_ghost_direction(ghost, target_x, target_y)
        self.assertEqual(direction, (2, 0))

        # 2. Uji mode flee/ketakutan (menjauhi target)
        direction_flee = simplepacman.choose_ghost_direction(ghost, target_x, target_y, flee=True)
        # Hantu seharusnya menjauhi target_x, jadi memilih arah kiri (-2, 0) atau atas/bawah yang menjauh
        self.assertNotEqual(direction_flee, (2, 0))

        # 3. Uji ketika terperangkap (semua arah tertutup, kecuali berbalik)
        # Simulasi posisi hantu terperangkap di dinding
        ghost_trapped = {
            "x": 0, "y": 0, "radius": simplepacman.pacman_radius, "dir": (0, 0)
        }
        # Karena di (0,0) adalah dinding dan dikelilingi dinding, can_move_towards akan False semua
        direction_trapped = simplepacman.choose_ghost_direction(ghost_trapped, 100, 100)
        self.assertEqual(direction_trapped, (0, 0))

    def test_get_ghost_target(self):
        """Uji fungsi penentuan target hantu berdasarkan tipe."""
        # 1. Tipe non-ambush (mengikuti posisi Pacman tepat)
        ghost_normal = {"style": "random"}
        target_x, target_y = simplepacman.get_ghost_target(ghost_normal, 100, 100, (2, 0))
        self.assertEqual((target_x, target_y), (100, 100))

        # 2. Tipe ambush (menargetkan 2 GRID_SIZE di depan arah Pacman)
        ghost_ambush = {"style": "ambush"}
        target_x, target_y = simplepacman.get_ghost_target(ghost_ambush, 100, 100, (2, 0))
        # Pacman bergerak ke kanan (2, 0). Target = 100 + 2 * GRID_SIZE * 2
        # Karena arah dinormalisasi jika digunakan, wait, direction yang dioper adalah speed.
        # direction = (pacman_speed, 0) misalnya.
        # Target x = 100 + 2 * GRID_SIZE * 2 -> 100 + 4 * GRID_SIZE
        expected_x = 100 + 2 * simplepacman.GRID_SIZE * 2
        expected_y = 100 + 0 * simplepacman.GRID_SIZE * 2
        self.assertEqual((target_x, target_y), (expected_x, expected_y))

if __name__ == '__main__':
    unittest.main()
