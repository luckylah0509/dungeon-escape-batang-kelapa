"""
Dungeon: peta tile, tabrakan, ruangan terhubung lewat pintu, status ruangan, ruangan bos.
Jalankan:  pip install pygame  ->  python dungeon.py
Kontrol: WASD / panah = jalan, SPASI = serang, R = ulang kalau mati.

Legenda peta:
  #  dinding (solid)      .  lantai          D  pintu
  M  monster biasa        B  bos             T  jebakan
"""
import math
import sys

import pygame

TILE = 32
SOLID = {"#"}


# ----------------------------------------------------------------------
# 1. PETA TILE + TABRAKAN
# ----------------------------------------------------------------------
class Tilemap:
    def __init__(self, rows):
        assert len({len(r) for r in rows}) == 1, "Semua baris peta harus sama panjang"
        self.rows = [list(r) for r in rows]
        self.h = len(rows)
        self.w = len(rows[0])

    def tile_at(self, tx, ty):
        if 0 <= tx < self.w and 0 <= ty < self.h:
            return self.rows[ty][tx]
        return "#"  # di luar peta dianggap dinding

    def is_solid(self, tx, ty):
        return self.tile_at(tx, ty) in SOLID

    def find(self, ch):
        """Daftar posisi tile (tx, ty) yang berisi simbol ch."""
        return [(x, y) for y, row in enumerate(self.rows)
                for x, c in enumerate(row) if c == ch]

    def erase_marks(self):
        """Simbol M/B/T hanya penanda spawn; setelah dibaca jadi lantai biasa."""
        for y, row in enumerate(self.rows):
            for x, c in enumerate(row):
                if c in "MBT":
                    row[x] = "."

    def bisa_jalan(self, rect):
        """True kalau rect tidak menyentuh tile solid mana pun."""
        x0, x1 = rect.left // TILE, (rect.right - 1) // TILE
        y0, y1 = rect.top // TILE, (rect.bottom - 1) // TILE
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if self.is_solid(tx, ty):
                    return False
        return True


# ----------------------------------------------------------------------
# 2. ENTITAS (pemain, monster, jebakan)
# ----------------------------------------------------------------------
class Entity:
    def __init__(self, cx, cy, size, speed, hp):
        self.size = size
        self.x = cx - size / 2   # posisi float supaya gerak halus
        self.y = cy - size / 2
        self.speed = speed
        self.hp = hp

    @property
    def rect(self):
        return pygame.Rect(round(self.x), round(self.y), self.size, self.size)

    @property
    def center(self):
        return (self.x + self.size / 2, self.y + self.size / 2)

    def move(self, tilemap, dx, dy):
        """Sumbu X dan Y dicek TERPISAH -> bisa meluncur di sepanjang dinding."""
        self.x += dx
        if not tilemap.bisa_jalan(self.rect):
            self.x -= dx          # batalkan hanya gerak X
        self.y += dy
        if not tilemap.bisa_jalan(self.rect):
            self.y -= dy          # batalkan hanya gerak Y


class Player(Entity):
    def __init__(self, cx, cy):
        super().__init__(cx, cy, 20, 150, 5)
        self.invuln = 0.0
        self.attack_cd = 0.0
        self.flash = 0.0

    def teleport(self, cx, cy):
        self.x, self.y = cx - self.size / 2, cy - self.size / 2


class Monster(Entity):
    def __init__(self, cx, cy, boss=False):
        if boss:
            super().__init__(cx, cy, 48, 70, 10)
        else:
            super().__init__(cx, cy, 22, 80, 3)
        self.boss = boss
        self.hit_cd = 0.0

    def update(self, dt, player, tilemap):
        px, py = player.center
        mx, my = self.center
        dist = math.hypot(px - mx, py - my)
        if 0 < dist < 260:  # mengejar kalau pemain dekat
            step = self.speed * dt
            self.move(tilemap, (px - mx) / dist * step, (py - my) / dist * step)
        self.hit_cd = max(0.0, self.hit_cd - dt)


class Trap:
    def __init__(self, tx, ty):
        self.rect = pygame.Rect(tx * TILE + 4, ty * TILE + 4, TILE - 8, TILE - 8)
        self.damage = 1


# ----------------------------------------------------------------------
# 3. PINTU + RUANGAN
# ----------------------------------------------------------------------
class Door:
    def __init__(self, tile, target_room, target_door):
        self.tile = tile                  # posisi tile pintu di ruangan ini
        self.target_room = target_room    # id ruangan tujuan
        self.target_door = target_door    # id pintu di ruangan tujuan


class Room:
    def __init__(self, room_id, name, rows, doors):
        self.id = room_id
        self.name = name
        self.tilemap = Tilemap(rows)
        self.doors = doors                # {"E": Door(...), ...}
        # penanda spawn dibaca sekali, lalu peta dibersihkan
        self._monster_spawns = self.tilemap.find("M")
        self._boss_spawns = self.tilemap.find("B")
        self._trap_spawns = self.tilemap.find("T")
        self.tilemap.erase_marks()
        # ---- status ruangan (bertahan selama game berjalan) ----
        self.visited = False
        self.cleared = False
        self.monsters = []
        self.traps = []

    @property
    def is_boss_room(self):
        return bool(self._boss_spawns)

    def door_at(self, tx, ty):
        for d in self.doors.values():
            if d.tile == (tx, ty):
                return d
        return None

    def spawn_beside(self, door_id):
        """Titik tengah tile lantai di samping pintu (sisi dalam ruangan)."""
        dx, dy = self.doors[door_id].tile
        for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            tx, ty = dx + ox, dy + oy
            if self.tilemap.tile_at(tx, ty) == ".":
                return tx * TILE + TILE // 2, ty * TILE + TILE // 2
        raise ValueError(f"Pintu {door_id} tidak punya lantai di sampingnya")

    def enter(self):
        """Dipanggil tiap pemain masuk. Isi ruangan hanya dibuat SEKALI."""
        if not self.visited:
            self.visited = True
            for tx, ty in self._monster_spawns:
                self.monsters.append(Monster(tx * TILE + 16, ty * TILE + 16))
            for tx, ty in self._boss_spawns:
                self.monsters.append(Monster(tx * TILE + 16, ty * TILE + 16, boss=True))
            self.traps = [Trap(tx, ty) for tx, ty in self._trap_spawns]
        self.refresh_cleared()

    def refresh_cleared(self):
        self.monsters = [m for m in self.monsters if m.hp > 0]
        if not self.monsters:
            self.cleared = True


# ----------------------------------------------------------------------
# 4. DATA PETA (sesuai denah: A -> B -> C -> D(bos))
# ----------------------------------------------------------------------
ROOM_A = [  # ruang awal, kosong. Pintu E di (15,4)
    "################",
    "#..............#",
    "#..............#",
    "#..............#",
    "#..............D",
    "#..............#",
    "#..............#",
    "#..............#",
    "################",
]

ROOM_B = [  # pintu W (0,5) ke A, pintu S (10,10) ke C
    "####################",
    "#..................#",
    "#..................#",
    "#....M.............#",
    "#..................#",
    "D..................#",
    "#..............M...#",
    "#..................#",
    "#........T.........#",
    "#..................#",
    "##########D#########",
]

ROOM_C = [  # pintu N (10,0) ke B, pintu E (19,5) ke bos
    "##########D#########",
    "#..................#",
    "#..................#",
    "#....T.............#",
    "#..................#",
    "#..................D",
    "#..........M.......#",
    "#..................#",
    "#..M...............#",
    "#..................#",
    "####################",
]

ROOM_D = [  # ruang bos: arena lebih luas, SATU pintu masuk W (0,7)
    "############################",
    "#..........................#",
    "#.....................M....#",
    "#.......T..................#",
    "#..........................#",
    "#..........................#",
    "#..........................#",
    "D..................B.......#",
    "#..........................#",
    "#..........................#",
    "#..........................#",
    "#.......T..................#",
    "#.....................M....#",
    "#..........................#",
    "############################",
]


def build_rooms():
    return {
        "A": Room("A", "Perpustakaan", ROOM_A,
                  {"E": Door((15, 4), "B", "W")}),
        "B": Room("B", "Aula Utara", ROOM_B,
                  {"W": Door((0, 5), "A", "E"),
                   "S": Door((10, 10), "C", "N")}),
        "C": Room("C", "Aula Selatan", ROOM_C,
                  {"N": Door((10, 0), "B", "S"),
                   "E": Door((19, 5), "D", "W")}),
        "D": Room("D", "Ruang Bos", ROOM_D,
                  {"W": Door((0, 7), "C", "E")}),
    }


# ----------------------------------------------------------------------
# 5. DUNIA: pindah ruangan
# ----------------------------------------------------------------------
class World:
    def __init__(self):
        self.rooms = build_rooms()
        self.current = self.rooms["A"]
        self.current.enter()
        cx, cy = self.current.spawn_beside("E")
        self.player = Player(cx, cy)

    def check_door(self):
        """Kalau titik tengah pemain berada di tile pintu -> pindah ruangan."""
        px, py = self.player.center
        door = self.current.door_at(int(px // TILE), int(py // TILE))
        if door is None:
            return False
        target = self.rooms[door.target_room]
        # muncul di sisi dalam pintu pasangan (sisi berlawanan dari tempat keluar)
        cx, cy = target.spawn_beside(door.target_door)
        self.current = target
        self.player.teleport(cx, cy)
        self.current.enter()
        return True

    def update(self, dt, keys):
        p, room = self.player, self.current
        # input
        dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071
        p.move(room.tilemap, dx * p.speed * dt, dy * p.speed * dt)

        # timer
        p.invuln = max(0.0, p.invuln - dt)
        p.attack_cd = max(0.0, p.attack_cd - dt)
        p.flash = max(0.0, p.flash - dt)

        # serang
        if keys[pygame.K_SPACE] and p.attack_cd == 0:
            p.attack_cd = 0.35
            p.flash = 0.1
            pcx, pcy = p.center
            for m in room.monsters:
                mx, my = m.center
                if math.hypot(mx - pcx, my - pcy) < 52 + m.size / 2:
                    m.hp -= 1

        # monster
        for m in room.monsters:
            m.update(dt, p, room.tilemap)
            if m.rect.colliderect(p.rect) and p.invuln == 0:
                p.hp -= 1
                p.invuln = 1.0
        # jebakan
        for t in room.traps:
            if t.rect.colliderect(p.rect) and p.invuln == 0:
                p.hp -= t.damage
                p.invuln = 1.0

        room.refresh_cleared()
        self.check_door()


# ----------------------------------------------------------------------
# 6. TAMPILAN + LOOP
# ----------------------------------------------------------------------
class Game:
    HUD = 40

    def __init__(self):
        pygame.init()
        self.font = pygame.font.SysFont("consolas,monospace", 18)
        self.clock = pygame.time.Clock()
        self.world = World()
        self.screen = None
        self.shown_room = None

    def fit_window(self):
        tm = self.world.current.tilemap
        self.screen = pygame.display.set_mode((tm.w * TILE, tm.h * TILE + self.HUD))
        pygame.display.set_caption("Dungeon")
        self.shown_room = self.world.current

    def draw(self):
        w = self.world
        room, tm = w.current, w.current.tilemap
        if self.shown_room is not room:
            self.fit_window()
        s = self.screen
        s.fill((8, 8, 14))
        for ty in range(tm.h):
            for tx in range(tm.w):
                c = tm.tile_at(tx, ty)
                r = pygame.Rect(tx * TILE, ty * TILE, TILE, TILE)
                if c == "#":
                    pygame.draw.rect(s, (60, 62, 90), r)
                    pygame.draw.rect(s, (40, 42, 66), r, 1)
                elif c == "D":
                    pygame.draw.rect(s, (200, 160, 60), r)
                else:
                    pygame.draw.rect(s, (88, 92, 112), r)
                    pygame.draw.rect(s, (78, 82, 102), r, 1)
        for t in room.traps:
            pygame.draw.polygon(s, (220, 220, 230), [
                (t.rect.left, t.rect.bottom), (t.rect.centerx, t.rect.top),
                (t.rect.right, t.rect.bottom)])
        for m in room.monsters:
            col = (140, 20, 60) if m.boss else (200, 60, 50)
            pygame.draw.rect(s, col, m.rect)
            bar = pygame.Rect(m.rect.left, m.rect.top - 6, m.size * m.hp / (10 if m.boss else 3), 4)
            pygame.draw.rect(s, (80, 220, 90), bar)
        p = w.player
        blink = p.invuln > 0 and int(p.invuln * 10) % 2 == 0
        if not blink:
            pygame.draw.rect(s, (90, 170, 255), p.rect)
        if p.flash > 0:
            pygame.draw.circle(s, (255, 255, 255), (int(p.center[0]), int(p.center[1])), 52, 2)

        status = "BERSIH" if room.cleared else "ADA MUSUH"
        txt = f"{room.name} [{status}]   HP: {p.hp}"
        s.blit(self.font.render(txt, True, (240, 240, 240)), (8, tm.h * TILE + 10))
        if p.hp <= 0:
            msg = self.font.render("GAME OVER - tekan R", True, (255, 90, 90))
            s.blit(msg, msg.get_rect(center=(tm.w * TILE // 2, tm.h * TILE // 2)))
        pygame.display.flip()

    def run(self):
        self.fit_window()
        while True:
            dt = min(self.clock.tick(60) / 1000, 0.05)
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if e.type == pygame.KEYDOWN and e.key == pygame.K_r and self.world.player.hp <= 0:
                    self.world = World()
            if self.world.player.hp > 0:
                self.world.update(dt, pygame.key.get_pressed())
            self.draw()


if __name__ == "__main__":
    Game().run()
