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

# DATA AREA MAP dengan koordinat piksel asli map, 1376 x 768
# Area lantai yang boleh dilewati (ruangan + lorong)
class DataArea:
    WALKABLE_AREAS = [
        pygame.Rect(95, 92, 525, 228),
        pygame.Rect(298, 318, 95, 280),
        pygame.Rect(393, 548, 90, 50),
        pygame.Rect(480, 428, 325, 270),
        pygame.Rect(800, 548, 120, 50),
        pygame.Rect(918, 408, 367, 290),
        pygame.Rect(1056, 296, 70, 114),
        pygame.Rect(895, 92, 390, 206),
    ]

    # Rintangan: tong, peti, rak, bangku, lubang, papan
    OBSTACLES = [
        # Ruang 1
        pygame.Rect(95, 90, 52, 18),
        pygame.Rect(320, 60, 30, 52),
        pygame.Rect(484, 88, 26, 22),
        pygame.Rect(592, 60, 28, 52),
        pygame.Rect(292, 115, 24, 20),
        pygame.Rect(537, 170, 40, 20),
        pygame.Rect(95, 285, 24, 31),
        pygame.Rect(292, 283, 28, 33),
        pygame.Rect(484, 285, 24, 31),
        pygame.Rect(513, 285, 26, 31),
        # Ruang 2
        pygame.Rect(482, 405, 30, 52),
        pygame.Rect(517, 420, 30, 36),
        pygame.Rect(748, 428, 52, 28),
        pygame.Rect(540, 550, 32, 22),
        pygame.Rect(513, 652, 58, 18),
        pygame.Rect(776, 642, 25, 32),
        # Ruang 3
        pygame.Rect(918, 382, 30, 54),
        pygame.Rect(1256, 382, 30, 54),
        pygame.Rect(1055, 550, 36, 22),
        pygame.Rect(918, 666, 25, 32),
        pygame.Rect(945, 672, 26, 25),
        pygame.Rect(1258, 666, 25, 32),
        pygame.Rect(1230, 672, 27, 25),
        # Ruang 4
        pygame.Rect(902, 88, 26, 22),
        pygame.Rect(1230, 88, 27, 22),
        pygame.Rect(1256, 60, 28, 52),
        pygame.Rect(902, 262, 25, 31),
        pygame.Rect(931, 270, 26, 23),
    ]


    TORCHES = [
        (162, 60, 47),
        (533, 61, -69),
        (957, 61, 210),
        (1197, 63, -207),
        (967, 386, 179),
        (1227, 387, -92),
        (727, 407, -148),
        (545, 409, 92),
    ]
    TORCH_FILE = "torch_frames_2.png"
    TORCH_FRAME_W, TORCH_FRAME_H = 16, 16
    TORCH_SCALE = 1.5
    TORCH_CLEAR_W, TORCH_CLEAR_H = 26, 36
    TORCH_CLEAR_OX, TORCH_CLEAR_OY = 5, 6
    TORCH_FRAME_MS = 120


    # DATA KAMERA PER RUANGAN
    # Area tampilan kamera tiap ruangan (termasuk tembok)
    ROOM_VIEWS = {
        1: pygame.Rect(75, 38, 565, 316),
        2: pygame.Rect(465, 388, 355, 345),
        3: pygame.Rect(900, 366, 405, 367),
        4: pygame.Rect(880, 38, 425, 292),
    }


# KELAS PETA DUNGEON
class PetaDungeon:

    def __init__(self, filename):
        path = os.path.join(BASE_DIR, filename)
        self.image = pygame.image.load(path).convert()
        self.width, self.height = self.image.get_size()

        self.torch_frames = []
        fw, fh = DataArea.TORCH_FRAME_W, DataArea.TORCH_FRAME_H
        try:
            sheet = pygame.image.load(
                os.path.join(BASE_DIR, DataArea.TORCH_FILE)).convert_alpha()
            for i in range(sheet.get_width() // fw):
                frame = sheet.subsurface((i * fw, 0, fw, fh)).copy()
                if DataArea.TORCH_SCALE != 1.0:
                    frame = pygame.transform.scale(
                        frame, (round(fw * DataArea.TORCH_SCALE),
                                round(fh * DataArea.TORCH_SCALE)))
                self.torch_frames.append(frame)
        except (pygame.error, FileNotFoundError):
            print(DataArea.TORCH_FILE, "tidak ditemukan, obor tidak dianimasikan")

        if self.torch_frames:
            self._hapus_obor_statis()

    def _hapus_obor_statis(self):
        for x, y, dx in DataArea.TORCHES:
            area = pygame.Rect(x - DataArea.TORCH_CLEAR_OX, y - DataArea.TORCH_CLEAR_OY,
                               DataArea.TORCH_CLEAR_W, DataArea.TORCH_CLEAR_H)
            tembok = self.image.subsurface(area.move(dx, 0)).copy()
            self.image.blit(tembok, area.topleft)

    def gambar_obor(self, surface):
        if not self.torch_frames:
            return
        geser_x = (self.torch_frames[0].get_width() - DataArea.TORCH_FRAME_W) // 2
        tick = pygame.time.get_ticks() // DataArea.TORCH_FRAME_MS
        for i, (x, y, dx) in enumerate(DataArea.TORCHES):
            frame = self.torch_frames[(tick + i * 3) % len(self.torch_frames)]
            surface.blit(frame, (x - geser_x, y))

    def gambar(self, surface):
        surface.blit(self.image, (0, 0))
        self.gambar_obor(surface)

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
        self.dungeon = PetaDungeon("dungeon_map_2.png")
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