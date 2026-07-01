import os
import sys
import threading
import time
import runpy
import pygame

# Pastikan mode headless (dummy) dimatikan agar jendela game MUNCUL di layar
if "SDL_VIDEODRIVER" in os.environ:
    del os.environ["SDL_VIDEODRIVER"]

# Inisialisasi pygame sebelumnya untuk keperluan patch
pygame.init()

# Monkey-patch pygame.key.get_pressed untuk menyimulasikan input keyboard
class MockKeys:
    def __init__(self):
        self.keys = {}
    
    def __getitem__(self, key):
        return self.keys.get(key, False)

mock_keys_obj = MockKeys()

def mocked_get_pressed():
    """Menggantikan fungsi baca keyboard pygame dengan objek buatan kita"""
    return mock_keys_obj

pygame.key.get_pressed = mocked_get_pressed

def press_key(key, duration=0.1):
    """Menyimulasikan tombol keyboard yang ditekan"""
    mock_keys_obj.keys[key] = True
    time.sleep(duration)
    mock_keys_obj.keys[key] = False

def bot_player():
    """Logika otomatis (Bot) yang memainkan gamenya"""
    print("\n🤖 [Bot] Visual Blackbox Testing Dimulai!")
    print("🤖 [Bot] Menunggu game siap...")
    time.sleep(2)
    
    print("🤖 [Bot] Bergerak ke KANAN...")
    press_key(pygame.K_RIGHT, 0.1)
    time.sleep(1.5)
    
    print("🤖 [Bot] Bergerak ke BAWAH...")
    press_key(pygame.K_DOWN, 0.1)
    time.sleep(1.5)
    
    print("🤖 [Bot] Bergerak ke KANAN...")
    press_key(pygame.K_RIGHT, 0.1)
    time.sleep(1.2)
    
    print("🤖 [Bot] Bergerak ke ATAS (Memburu Power Pellet!)...")
    press_key(pygame.K_UP, 0.1)
    time.sleep(2)
    
    print("🤖 [Bot] Bergerak bebas sebentar...")
    press_key(pygame.K_LEFT, 0.1)
    time.sleep(3)
    
    print("🤖 [Bot] Demonstrasi selesai! Menutup game dalam 3 detik...")
    time.sleep(3)
    
    # Kirim sinyal QUIT ke pygame untuk menutup jendela
    pygame.event.post(pygame.event.Event(pygame.QUIT))

if __name__ == "__main__":
    # Jalankan bot di dalam thread terpisah agar tidak memblokir Game Loop utama
    bot_thread = threading.Thread(target=bot_player)
    bot_thread.daemon = True
    bot_thread.start()
    
    print("🎮 Membuka antarmuka game...")
    # Dapatkan path dari simplepacman.py
    script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'simplepacman.py'))
    
    # Jalankan script aslinya dengan run_name="__main__" agar Game Loop berjalan
    try:
        runpy.run_path(script_path, run_name="__main__")
    except SystemExit:
        print("\n✅ Visual Blackbox Testing Berhasil Diselesaikan!")
