import os
import sys
import pygame
from pygame.locals import *

pygame.init()

FULLSCREEN_MODE = False

if FULLSCREEN_MODE:
    screen = pygame.display.set_mode((0, 0), FULLSCREEN)
else:
    screen = pygame.display.set_mode((1280, 720))
S_WIDTH, S_HEIGHT = screen.get_size()

pygame.display.set_caption("Batang kelapa88")

clock = pygame.time.Clock()
FPS = 30

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# DATA AREA MAP dengan koordinat piksel asli map, 2208 x 1344
# Area lantai yang boleh dilewati (ruangan + lorong)
class DataArea:
    WALKABLE_AREAS = [
        pygame.Rect(95, 98, 435, 430),
        pygame.Rect(520, 242, 205, 92),
        pygame.Rect(718, 98, 532, 430),
        pygame.Rect(960, 520, 100, 210),
        pygame.Rect(718, 720, 532, 432),
        pygame.Rect(1245, 912, 200, 96),
        pygame.Rect(1440, 672, 628, 528),
    ]

    # Rintangan: tong, peti, rak, bangku, kuali, lubang, papan
    OBSTACLES = [
        # Ruang 1
        pygame.Rect(100, 470, 42, 56),
        pygame.Rect(432, 462, 48, 64),
        pygame.Rect(480, 48, 48, 94),
        pygame.Rect(432, 150, 42, 40),
        pygame.Rect(96, 95, 96, 40),
        # Ruang 2
        pygame.Rect(722, 470, 98, 56),
        pygame.Rect(1200, 432, 48, 48),
        pygame.Rect(1200, 48, 48, 94),
        pygame.Rect(816, 262, 48, 26),
        pygame.Rect(722, 95, 46, 40),
        pygame.Rect(1152, 95, 48, 40),
        # Ruang 3
        pygame.Rect(720, 672, 48, 94),
        pygame.Rect(780, 702, 48, 64),
        pygame.Rect(1152, 715, 98, 48),
        pygame.Rect(768, 1126, 96, 26),
        pygame.Rect(1203, 1095, 44, 56),
        pygame.Rect(815, 932, 50, 30),
        # Ruang 4
        pygame.Rect(1440, 625, 48, 94),
        pygame.Rect(2016, 625, 48, 94),
        pygame.Rect(1443, 1142, 44, 56),
        pygame.Rect(1490, 1152, 46, 46),
        pygame.Rect(1968, 1152, 48, 46),
        pygame.Rect(2020, 1142, 44, 56),
        pygame.Rect(1680, 932, 50, 30),
    ]

    TORCHES = [
        (204, 48, -48), (396, 48, -48),
        (828, 48, -48), (1116, 48, -48),
        (828, 672, 48), (1116, 672, 48),
        (1548, 624, -48), (1692, 624, -48),
        (1836, 624, -48), (1980, 624, -48),
    ]
    TORCH_FRAME_W, TORCH_FRAME_H = 48, 66
    TORCH_FRAME_MS = 100

    # DATA KAMERA PER RUANGAN
    # Area tampilan kamera tiap ruangan (termasuk tembok)
    ROOM_VIEWS = {
        1: pygame.Rect(82, 38, 460, 548),
        2: pygame.Rect(708, 38, 554, 548),
        3: pygame.Rect(708, 660, 554, 552),
        4: pygame.Rect(1426, 614, 652, 646),
    }


# KELAS PETA DUNGEON
class PetaDungeon:

    def __init__(self, filename):
        path = os.path.join(BASE_DIR, filename)
        self.image = pygame.image.load(path).convert()
        self.width, self.height = self.image.get_size()

        self.torch_frames = []
        try:
            sheet = pygame.image.load(
                os.path.join(BASE_DIR, "torch_frames.png")).convert_alpha()
            for i in range(sheet.get_width() // DataArea.TORCH_FRAME_W):
                self.torch_frames.append(
                    sheet.subsurface((i * DataArea.TORCH_FRAME_W, 0,
                                      DataArea.TORCH_FRAME_W, DataArea.TORCH_FRAME_H)).copy())
        except (pygame.error, FileNotFoundError):
            print("torch_frames.png tidak ditemukan, obor tidak dianimasikan")

        if self.torch_frames:
            self._hapus_obor_statis()

    def _hapus_obor_statis(self):
        for x, y, dx in DataArea.TORCHES:
            area = pygame.Rect(x - 12, y - 15, DataArea.TORCH_FRAME_W, 57)
            tembok = self.image.subsurface(area.move(dx, 0)).copy()
            self.image.blit(tembok, area.topleft)

    def gambar_obor(self, surface):
        if not self.torch_frames:
            return
        tick = pygame.time.get_ticks() // DataArea.TORCH_FRAME_MS
        for i, (x, y, dx) in enumerate(DataArea.TORCHES):
            frame = self.torch_frames[(tick + i * 3) % len(self.torch_frames)]
            surface.blit(frame, (x - 12, y - 15))

    def gambar(self, surface):
        surface.blit(self.image, (0, 0))
        self.gambar_obor(surface)

    def titik_bisa_dilewati(self, x, y):
        for area in DataArea.WALKABLE_AREAS:
            if area.collidepoint(x, y):
                return True
        return False

    def bisa_jalan(self, rect):
        points = [
            rect.topleft, rect.topright,
            rect.bottomleft, rect.bottomright,
            rect.midtop, rect.midbottom,
            rect.midleft, rect.midright,
        ]
        for x, y in points:
            px = min(x, rect.right - 1)
            py = min(y, rect.bottom - 1)
            if not self.titik_bisa_dilewati(px, py):
                return False

        if rect.collidelist(DataArea.OBSTACLES) != -1:
            return False

        return True

    def gambar_debug(self, surface):
        for area in DataArea.WALKABLE_AREAS:
            pygame.draw.rect(surface, (0, 255, 0), area, 2)
        for obs in DataArea.OBSTACLES:
            pygame.draw.rect(surface, (255, 0, 0), obs, 2)


# KELAS KAMERA
class Kamera:

    def __init__(self, map_w, map_h, start_room):
        self.map_rect = pygame.Rect(0, 0, map_w, map_h)
        r = DataArea.ROOM_VIEWS[start_room]
        self.view = [float(r.x), float(r.y), float(r.w), float(r.h)]

    def tentukan_target(self, room_id):
        return DataArea.ROOM_VIEWS[room_id].clip(self.map_rect)

    def perbarui(self, room_id, snap=False):
        t = self.tentukan_target(room_id)
        for i, v in enumerate((t.x, t.y, t.w, t.h)):
            if snap:
                self.view[i] = v
            else:
                self.view[i] += (v - self.view[i]) * 0.12
                if abs(v - self.view[i]) < 0.5:
                    self.view[i] = v

    def ambil_rect(self):
        x, y, w, h = self.view
        r = pygame.Rect(round(x), round(y), max(1, round(w)), max(1, round(h)))
        return r.clip(self.map_rect)


# KELAS PERMAINAN
class Permainan:

    def __init__(self):
        self.dungeon = PetaDungeon("dungeon_map.png")
        self.running = True
        self.debug = False

        self.world = pygame.Surface((self.dungeon.width, self.dungeon.height))
        self.full_rect = pygame.Rect(0, 0, self.dungeon.width, self.dungeon.height)

        self.mode_ruangan = True
        self.penuh_layar = False
        self.ruangan = 1
        self.camera = Kamera(self.dungeon.width, self.dungeon.height, self.ruangan)
        self.camera.perbarui(self.ruangan, snap=True)

    def jalankan(self):
        while self.running:
            clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == QUIT:
                    print("Keluar: jendela ditutup (event QUIT)")
                    self.running = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        print("Keluar: tombol ESC ditekan")
                        self.running = False
                    if event.key == K_F1:
                        self.debug = not self.debug
                    if event.key == K_m:
                        self.mode_ruangan = not self.mode_ruangan
                    if event.key == K_f:
                        self.penuh_layar = not self.penuh_layar
                    if event.key in (K_1, K_2, K_3, K_4):
                        self.ruangan = event.key - K_0

            self.dungeon.gambar(self.world)
            if self.debug:
                self.dungeon.gambar_debug(self.world)

            if self.mode_ruangan:
                self.camera.perbarui(self.ruangan)
                view = self.camera.ambil_rect()
            else:
                view = self.full_rect

            bagian = self.world.subsurface(view)
            screen.fill((0, 0, 0))
            if self.penuh_layar:
                scaled = pygame.transform.scale(bagian, (S_WIDTH, S_HEIGHT))
                screen.blit(scaled, (0, 0))
            else:
                scale = min(S_WIDTH / view.w, S_HEIGHT / view.h)
                size = (int(view.w * scale), int(view.h * scale))
                scaled = pygame.transform.scale(bagian, size)
                screen.blit(scaled, ((S_WIDTH - size[0]) // 2,
                                     (S_HEIGHT - size[1]) // 2))

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    import traceback
    try:
        game = Permainan()
        game.jalankan()
    except SystemExit:
        pass
    except Exception:
        pesan = traceback.format_exc()
        print(pesan)
        with open(os.path.join(BASE_DIR, "error.txt"), "w") as f:
            f.write(pesan)
        pygame.quit()
        input("Terjadi error (tersimpan di error.txt). Tekan Enter untuk menutup...")