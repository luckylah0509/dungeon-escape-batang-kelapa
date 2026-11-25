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
FPS = 60

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# DATA AREA MAP (koordinat piksel asli dungeon_map.png, 2208 x 1344)
# Area lantai yang boleh dilewati (ruangan + lorong)
WALKABLE_AREAS = [
    pygame.Rect(95, 98, 435, 430),     # Ruang 1 (kiri atas)
    pygame.Rect(520, 242, 205, 92),    # Lorong ruang 1 -> 2
    pygame.Rect(718, 98, 532, 430),    # Ruang 2 (tengah atas)
    pygame.Rect(960, 520, 100, 210),   # Lorong ruang 2 -> 3 (vertikal)
    pygame.Rect(718, 720, 532, 432),   # Ruang 3 (tengah bawah)
    pygame.Rect(1245, 912, 200, 96),   # Lorong ruang 3 -> 4
    pygame.Rect(1440, 672, 628, 528),  # Ruang 4 (kanan bawah)
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
    pygame.Rect(815, 932, 50, 30),     # Lubang
    # Ruang 4
    pygame.Rect(1440, 625, 48, 94),
    pygame.Rect(2016, 625, 48, 94),
    pygame.Rect(1443, 1142, 44, 56),
    pygame.Rect(1490, 1152, 46, 46),
    pygame.Rect(1968, 1152, 48, 46),
    pygame.Rect(2020, 1142, 44, 56),
    pygame.Rect(1680, 932, 50, 30),    # Lubang
]


# Posisi obor: (x kiri, y atas, arah ambil tembok polos untuk menutup obor lama)
TORCHES = [
    (204, 48, -48), (396, 48, -48),          # Ruang 1
    (828, 48, -48), (1116, 48, -48),         # Ruang 2
    (828, 672, 48), (1116, 672, 48),         # Ruang 3
    (1548, 624, -48), (1692, 624, -48),      # Ruang 4
    (1836, 624, -48), (1980, 624, -48),
]
TORCH_FRAME_W, TORCH_FRAME_H = 48, 66
TORCH_FRAME_MS = 100   # lama tiap frame api (milidetik)


# DATA PINTU (di lorong menuju ruangan berikutnya)
DOOR_DATA = [
    # Ruang 1 -> 2
    dict(file="Door_1.png", kind="single", crop=(0, 4, 19, 28), scale=3,
         passage=pygame.Rect(520, 242, 205, 92), offset=(0, 0)),
    # Ruang 2 -> 3
    dict(file="DoubleDoor.png", kind="double", crop=(0, 4, 64, 28), scale=1.5,
         passage=pygame.Rect(960, 520, 100, 210), offset=(0, 0)),
    # Ruang 3 -> 4
    dict(file="Door_2.png", kind="single", crop=(0, 4, 19, 28), scale=3,
         passage=pygame.Rect(1245, 912, 200, 96), offset=(0, 0)),
]

DOOR_SPEED = 0.06        # kecepatan buka/tutup per frame (0..1)
DOOR_BLOCK_UNTIL = 0.6   # pintu masih menghalangi selama progres < ini
DOOR_OPEN_DIST = 40      # pintu mulai terbuka kalau pemain sedekat ini


# DATA KAMERA PER RUANGAN
# Area tampilan kamera tiap ruangan (termasuk tembok)
ROOM_VIEWS = {
    1: pygame.Rect(82, 38, 460, 548),
    2: pygame.Rect(708, 38, 554, 548),
    3: pygame.Rect(708, 660, 554, 552),
    4: pygame.Rect(1426, 614, 652, 646),
}

# Zona untuk mendeteksi pemain sedang ada di ruangan mana
# (lorong dibagi dua: separuh masuk ruangan kiri/atas, separuh ruangan kanan/bawah)
ROOM_ZONES = [
    (pygame.Rect(95, 98, 527, 430), 1),
    (pygame.Rect(622, 98, 628, 430), 2),
    (pygame.Rect(960, 528, 100, 97), 2),
    (pygame.Rect(960, 625, 100, 95), 3),
    (pygame.Rect(718, 720, 532, 432), 3),
    (pygame.Rect(1245, 912, 100, 96), 3),
    (pygame.Rect(1345, 912, 100, 96), 4),
    (pygame.Rect(1440, 672, 628, 528), 4),
]

# CLASS DOOR
class Door:

    def __init__(self, data):
        img = pygame.image.load(os.path.join(BASE_DIR, data["file"])).convert_alpha()
        img = img.subsurface(pygame.Rect(data["crop"])).copy()
        w, h = img.get_size()
        s = data["scale"]
        self.image = pygame.transform.scale(img, (int(w * s), int(h * s)))

        # Letakkan di tengah lorong
        p = data["passage"]
        iw, ih = self.image.get_size()
        ox, oy = data["offset"]
        self.rect = pygame.Rect(0, 0, iw, ih)
        self.rect.center = (p.centerx + ox, p.centery + oy)

        self.kind = data["kind"]
        self.open = False
        self.progress = 0.0   # 0 = tertutup, 1 = terbuka penuh

    @property
    def blocking(self):
        return self.progress < DOOR_BLOCK_UNTIL

    def update(self, player_rect):
        # Otomatis: terbuka saat pemain mendekat/melewati, menutup lagi
        # setelah pemain menjauh (tidak menutup selagi pemain di bawahnya)
        area = self.rect.inflate(DOOR_OPEN_DIST * 2, DOOR_OPEN_DIST * 2)
        self.open = area.colliderect(player_rect)
        target = 1.0 if self.open else 0.0
        if self.progress < target:
            self.progress = min(target, self.progress + DOOR_SPEED)
        elif self.progress > target:
            self.progress = max(target, self.progress - DOOR_SPEED)

    def draw(self, surface):
        p = self.progress
        if p >= 1.0:
            return
        w, h = self.rect.size
        if self.kind == "double":
            half = w // 2
            shift = int(half * p)
            kiri = self.image.subsurface((0, 0, half, h))
            kanan = self.image.subsurface((half, 0, w - half, h))
            surface.blit(kiri, (self.rect.x - shift, self.rect.y))
            surface.blit(kanan, (self.rect.x + half + shift, self.rect.y))
        else:
            # Geser ke atas, dipotong di area pintu
            shift = int(h * p)
            clip_lama = surface.get_clip()
            surface.set_clip(self.rect)
            surface.blit(self.image, (self.rect.x, self.rect.y - shift))
            surface.set_clip(clip_lama)

# CLASS DUNGEON MAP
class DungeonMap:

    def __init__(self, filename):
        path = os.path.join(BASE_DIR, filename)
        self.image = pygame.image.load(path).convert()
        self.width, self.height = self.image.get_size()

        # Animasi obor (kalau file sprite tidak ada, game tetap jalan tanpa animasi)
        self.torch_frames = []
        try:
            sheet = pygame.image.load(
                os.path.join(BASE_DIR, "torch_frames.png")).convert_alpha()
            for i in range(sheet.get_width() // TORCH_FRAME_W):
                self.torch_frames.append(
                    sheet.subsurface((i * TORCH_FRAME_W, 0,
                                      TORCH_FRAME_W, TORCH_FRAME_H)).copy())
        except (pygame.error, FileNotFoundError):
            print("torch_frames.png tidak ditemukan, obor tidak dianimasikan")

        if self.torch_frames:
            self._hapus_obor_statis()

        # Pintu antar ruangan (kalau sprite tidak ada, pintu itu dilewati)
        self.doors = []
        for data in DOOR_DATA:
            try:
                self.doors.append(Door(data))
            except (pygame.error, FileNotFoundError):
                print(data["file"] + " tidak ditemukan, pintu dilewati")

    def _hapus_obor_statis(self):
        # Tutup api obor bawaan gambar dengan menyalin potongan tembok polos
        for x, y, dx in TORCHES:
            area = pygame.Rect(x - 12, y - 15, TORCH_FRAME_W, 57)
            tembok = self.image.subsurface(area.move(dx, 0)).copy()
            self.image.blit(tembok, area.topleft)

    def draw_torches(self, surface):
        if not self.torch_frames:
            return
        tick = pygame.time.get_ticks() // TORCH_FRAME_MS
        for i, (x, y, dx) in enumerate(TORCHES):
            # +i*3 supaya api tiap obor tidak bergerak serempak
            frame = self.torch_frames[(tick + i * 3) % len(self.torch_frames)]
            surface.blit(frame, (x - 12, y - 15))

    def update_doors(self, player_rect):
        for door in self.doors:
            door.update(player_rect)

    def draw_doors(self, surface):
        for door in self.doors:
            door.draw(surface)

    def draw(self, surface):
        surface.blit(self.image, (0, 0))
        self.draw_torches(surface)
        self.draw_doors(surface)

    def is_walkable_point(self, x, y):
        for area in WALKABLE_AREAS:
            if area.collidepoint(x, y):
                return True
        return False

    def can_walk(self, rect):
        # Semua sudut + titik tengah sisi harus ada di area lantai
        points = [
            rect.topleft, rect.topright,
            rect.bottomleft, rect.bottomright,
            rect.midtop, rect.midbottom,
            rect.midleft, rect.midright,
        ]
        for x, y in points:
            # -1 supaya sisi kanan/bawah rect tidak dianggap keluar area
            px = min(x, rect.right - 1)
            py = min(y, rect.bottom - 1)
            if not self.is_walkable_point(px, py):
                return False

        # Tidak boleh menabrak rintangan
        if rect.collidelist(OBSTACLES) != -1:
            return False

        # Pintu tertutup menghalangi
        for door in self.doors:
            if door.blocking and rect.colliderect(door.rect):
                return False

        return True

    def draw_debug(self, surface):
        for area in WALKABLE_AREAS:
            pygame.draw.rect(surface, (0, 255, 0), area, 2)
        for obs in OBSTACLES:
            pygame.draw.rect(surface, (255, 0, 0), obs, 2)
        for door in self.doors:
            pygame.draw.rect(surface, (255, 255, 0), door.rect, 2)


# CLASS PLAYER
class Player:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 28, 28)
        self.speed = 4
        self.color = (50, 120, 255)

    def move(self, keys, dungeon):
        dx = 0
        dy = 0

        if keys[K_LEFT] or keys[K_a]:
            dx = -self.speed
        if keys[K_RIGHT] or keys[K_d]:
            dx = self.speed
        if keys[K_UP] or keys[K_w]:
            dy = -self.speed
        if keys[K_DOWN] or keys[K_s]:
            dy = self.speed

        # Collision sumbu X
        self.rect.x += dx
        if not dungeon.can_walk(self.rect):
            self.rect.x -= dx

        # Collision sumbu Y
        self.rect.y += dy
        if not dungeon.can_walk(self.rect):
            self.rect.y -= dy

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


# CLASS CAMERA
class Camera:

    def __init__(self, map_w, map_h, start_room):
        self.map_rect = pygame.Rect(0, 0, map_w, map_h)
        r = ROOM_VIEWS[start_room]
        self.view = [float(r.x), float(r.y), float(r.w), float(r.h)]

    def target(self, room_id, player_rect):
        # Tampilan ruangan, diperlebar kalau pemain keluar (misal di lorong)
        t = ROOM_VIEWS[room_id].union(player_rect.inflate(40, 40))
        return t.clip(self.map_rect)

    def update(self, room_id, player_rect, snap=False):
        t = self.target(room_id, player_rect)
        for i, v in enumerate((t.x, t.y, t.w, t.h)):
            if snap:
                self.view[i] = v
            else:
                self.view[i] += (v - self.view[i]) * 0.12   # perpindahan halus
                if abs(v - self.view[i]) < 0.5:
                    self.view[i] = v

    def get_rect(self):
        x, y, w, h = self.view
        r = pygame.Rect(round(x), round(y), max(1, round(w)), max(1, round(h)))
        return r.clip(self.map_rect)

# CLASS GAME

class Game:

    def __init__(self):
        self.dungeon = DungeonMap("dungeon_map.png")
        self.player = Player(200, 250)
        self.running = True
        self.debug = False

        # Surface "dunia" seukuran map asli
        self.world = pygame.Surface((self.dungeon.width, self.dungeon.height))
        self.full_rect = pygame.Rect(0, 0, self.dungeon.width, self.dungeon.height)

        # Kamera per ruangan (tekan M untuk melihat seluruh map)
        self.mode_ruangan = True
        self.ruangan = self.cari_ruangan()
        self.camera = Camera(self.dungeon.width, self.dungeon.height, self.ruangan)
        self.camera.update(self.ruangan, self.player.rect, snap=True)

    def cari_ruangan(self):
        cx, cy = self.player.rect.center
        for rect, room_id in ROOM_ZONES:
            if rect.collidepoint(cx, cy):
                return room_id
        return getattr(self, "ruangan", 1)

    def run(self):
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

            keys = pygame.key.get_pressed()
            self.player.move(keys, self.dungeon)
            self.dungeon.update_doors(self.player.rect)

            # Gambar ke dunia (pintu digambar di dalam dungeon.draw)
            self.dungeon.draw(self.world)
            self.player.draw(self.world)
            if self.debug:
                self.dungeon.draw_debug(self.world)

            # Tentukan bagian dunia yang ditampilkan
            if self.mode_ruangan:
                self.ruangan = self.cari_ruangan()
                self.camera.update(self.ruangan, self.player.rect)
                view = self.camera.get_rect()
            else:
                view = self.full_rect

            # Ruangan di-scale memenuhi layar (rasio dijaga), sisanya hitam
            bagian = self.world.subsurface(view)
            scale = min(S_WIDTH / view.w, S_HEIGHT / view.h)
            size = (int(view.w * scale), int(view.h * scale))
            scaled = pygame.transform.scale(bagian, size)

            screen.fill((0, 0, 0))
            screen.blit(scaled, ((S_WIDTH - size[0]) // 2,
                                 (S_HEIGHT - size[1]) // 2))

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    import traceback
    try:
        game = Game()
        game.run()
    except SystemExit:
        pass
    except Exception:
        pesan = traceback.format_exc()
        print(pesan)
        with open(os.path.join(BASE_DIR, "error.txt"), "w") as f:
            f.write(pesan)
        pygame.quit()
        input("Terjadi error (tersimpan di error.txt). Tekan Enter untuk menutup...")
