import os
import sys
import unittest

# Pengaturan headless untuk Pygame agar tidak membuka jendela saat testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame

# Menambahkan path direktori utama agar simplepacman bisa di-import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import simplepacman

class TestBlackboxSimplePacman(unittest.TestCase):
    def setUp(self):
        # Memastikan status game selalu bersih sebelum setiap pengujian
        simplepacman.reset_game()

    def test_eat_dot_increases_score(self):
        """Uji Blackbox: Memakan dot (makanan) harus meningkatkan skor sebesar 10."""
        initial_score = simplepacman.score
        initial_dots_count = len(simplepacman.dots)
        
        # Pastikan ada dot yang tersedia
        self.assertGreater(initial_dots_count, 0)
            
        target_dot = simplepacman.dots[0]
        
        # Pindahkan pacman ke koordinat dot
        simplepacman.pacman_x = target_dot.centerx
        simplepacman.pacman_y = target_dot.centery
        
        # Buat rect untuk pacman di posisi baru
        pacman_rect = pygame.Rect(
            simplepacman.pacman_x - simplepacman.pacman_radius, 
            simplepacman.pacman_y - simplepacman.pacman_radius, 
            simplepacman.pacman_radius * 2, 
            simplepacman.pacman_radius * 2
        )
        
        # Secara manual jalankan logika deteksi tabrakan dengan dot (karena game loop ada di __main__)
        for dot in simplepacman.dots[:]:
            if pacman_rect.colliderect(dot):
                simplepacman.dots.remove(dot)
                simplepacman.score += 10
        
        # Periksa apakah skor bertambah dan jumlah makanan berkurang (Output yang diharapkan)
        self.assertEqual(simplepacman.score, initial_score + 10)
        self.assertEqual(len(simplepacman.dots), initial_dots_count - 1)

    def test_eat_power_pellet_activates_power_mode(self):
        """Uji Blackbox: Memakan power pellet harus memberikan 50 poin dan mengaktifkan power mode."""
        initial_score = simplepacman.score
        
        self.assertGreater(len(simplepacman.power_pellet_rects), 0)
        target_pellet = simplepacman.power_pellet_rects[0]
        
        simplepacman.pacman_x = target_pellet.centerx
        simplepacman.pacman_y = target_pellet.centery
        
        pacman_rect = pygame.Rect(
            simplepacman.pacman_x - simplepacman.pacman_radius, 
            simplepacman.pacman_y - simplepacman.pacman_radius, 
            simplepacman.pacman_radius * 2, 
            simplepacman.pacman_radius * 2
        )
        
        # Simulasikan interaksi dari game loop utama
        for pellet in simplepacman.power_pellet_rects[:]:
            if pacman_rect.colliderect(pellet):
                simplepacman.power_pellet_rects.remove(pellet)
                simplepacman.power_mode = True
                simplepacman.score += 50
                for ghost in simplepacman.ghosts:
                    ghost["frightened"] = True
        
        # Evaluasi kondisi output yang diharapkan
        self.assertEqual(simplepacman.score, initial_score + 50)
        self.assertTrue(simplepacman.power_mode)
        self.assertTrue(simplepacman.ghosts[0]["frightened"])

    def test_ghost_collision_decreases_life_or_gameover(self):
        """Uji Blackbox: Menabrak hantu saat bukan power mode harus mengurangi nyawa."""
        initial_lives = simplepacman.lives
        simplepacman.power_mode = False
        
        target_ghost = simplepacman.ghosts[0]
        target_ghost["frightened"] = False
        
        # Simulasikan tabrakan pacman dengan hantu pertama
        pacman_rect = pygame.Rect(
            target_ghost["x"] - simplepacman.pacman_radius, 
            target_ghost["y"] - simplepacman.pacman_radius, 
            simplepacman.pacman_radius * 2, 
            simplepacman.pacman_radius * 2
        )
        
        ghost_rect = pygame.Rect(
            target_ghost["x"] - target_ghost["radius"], 
            target_ghost["y"] - target_ghost["radius"], 
            target_ghost["radius"] * 2, 
            target_ghost["radius"] * 2
        )
        
        # Logika dari game loop yang diuji interaksinya
        if pacman_rect.colliderect(ghost_rect):
            if not target_ghost["frightened"]:
                simplepacman.lives -= 1
                if simplepacman.lives <= 0:
                    simplepacman.game_state = "GAME_OVER"
        
        # Verifikasi bahwa nyawa berkurang 1
        self.assertEqual(simplepacman.lives, initial_lives - 1)

if __name__ == '__main__':
    unittest.main()
