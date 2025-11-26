import math
import random
from dataclasses import dataclass
from pathlib import Path

import pygame


WIDTH, HEIGHT = 960, 540
GROUND_Y = HEIGHT - 96
GRAVITY = 2800
PLAYER_SPEED = 880
DEMON_SPEED = 420
JUMP_FORCE = -1250
BG_COLOR = (14, 12, 26)
PLAYER_SPRITE_HEIGHT = 176
DEMON_SPRITE_HEIGHT = 168
ASSET_DIR = Path(__file__).resolve().parent.parent / "assets"


@dataclass
class Hitbox:
    rect: pygame.Rect
    damage: int
    timer: float
    owner: object

    def update(self, dt: float) -> None:
        self.timer -= dt

    @property
    def expired(self) -> bool:
        return self.timer <= 0


class Fighter:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 70, 110)
        self.velocity = pygame.Vector2(0, 0)
        self.health = 120
        self.direction = 1
        self.on_ground = False
        self.attack_cooldown = 0.0
        self.attacking = 0.0

    def handle_keys(self, keys: pygame.key.ScancodeWrapper) -> None:
        move = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move += 1

        self.direction = 1 if move > 0 else -1 if move < 0 else self.direction
        self.velocity.x = PLAYER_SPEED * move

    def handle_keydown(self, key: int) -> Hitbox | None:
        if key in (pygame.K_w, pygame.K_SPACE, pygame.K_UP) and self.on_ground:
            self.velocity.y = JUMP_FORCE
            self.on_ground = False

        if key in (pygame.K_j, pygame.K_k):
            heavy = key == pygame.K_k
            return self._start_attack(heavy)
        return None

    def _start_attack(self, heavy: bool) -> Hitbox | None:
        if self.attack_cooldown > 0:
            return None

        reach = 80 if heavy else 60
        damage = 24 if heavy else 16
        duration = 0.26 if heavy else 0.18
        self.attack_cooldown = 0.55 if heavy else 0.35
        self.attacking = duration

        offset_x = 24
        hit_rect = pygame.Rect(
            self.rect.centerx + (offset_x * self.direction),
            self.rect.y + 22,
            reach,
            48,
        )
        if self.direction < 0:
            hit_rect.x -= reach

        return Hitbox(hit_rect, damage, duration, self)

    def take_damage(self, dmg: int, attacker_x: float) -> None:
        self.health = max(0, self.health - dmg)
        knock_dir = math.copysign(1, self.rect.centerx - attacker_x)
        self.velocity.x += 300 * knock_dir
        self.velocity.y = -420

    def update(self, dt: float) -> None:
        self.attacking = max(0, self.attacking - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)

        self.velocity.y += GRAVITY * dt
        self.rect.x += int(self.velocity.x * dt)
        self.rect.y += int(self.velocity.y * dt)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity.y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)


class Demon:
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 68, 100)
        self.velocity = pygame.Vector2(0, 0)
        self.health = 70
        self.direction = -1
        self.attack_cooldown = random.uniform(0.7, 1.1)
        self.attacking = 0.0

    def update(self, dt: float, player_x: float) -> Hitbox | None:
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.attacking = max(0, self.attacking - dt)

        self.direction = 1 if player_x > self.rect.centerx else -1
        distance = abs(player_x - self.rect.centerx)
        chase = DEMON_SPEED if distance > 140 else DEMON_SPEED * 0.3
        self.velocity.x = chase * self.direction

        if distance < 160 and self.attack_cooldown <= 0:
            return self._start_attack()
        return None

    def _start_attack(self) -> Hitbox:
        reach = 70
        damage = 10
        duration = 0.24
        self.attack_cooldown = 1.1
        self.attacking = duration

        hit_rect = pygame.Rect(
            self.rect.centerx + (18 * self.direction),
            self.rect.y + 28,
            reach,
            44,
        )
        if self.direction < 0:
            hit_rect.x -= reach

        return Hitbox(hit_rect, damage, duration, self)

    def take_damage(self, dmg: int, attacker_x: float) -> None:
        self.health = max(0, self.health - dmg)
        knock_dir = math.copysign(1, self.rect.centerx - attacker_x)
        self.velocity.x += 240 * knock_dir
        self.velocity.y = -300

    def physics(self, dt: float) -> None:
        self.velocity.y += GRAVITY * dt
        self.rect.x += int(self.velocity.x * dt)
        self.rect.y += int(self.velocity.y * dt)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity.y = 0

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)


def load_sprite(name: str, target_height: int, fallback_color: tuple[int, int, int]) -> pygame.Surface:
    """Load and scale a sprite from assets; fall back to a colored placeholder if missing."""
    path = ASSET_DIR / name
    try:
        sprite = pygame.image.load(path).convert_alpha()
    except Exception as exc:  # pragma: no cover - visual fallback
        placeholder = pygame.Surface((int(target_height * 0.72), target_height), pygame.SRCALPHA)
        placeholder.fill((*fallback_color, 255))
        pygame.draw.rect(placeholder, (240, 240, 255, 80), placeholder.get_rect(), 3, border_radius=8)
        print(f"Warning: using placeholder for {name}: {exc}")
        return placeholder

    width, height = sprite.get_size()
    if height <= 0:
        return sprite
    scale = target_height / height
    new_size = (max(1, int(width * scale)), target_height)
    return pygame.transform.smoothscale(sprite, new_size)


def orient_sprite(sprite: pygame.Surface) -> tuple[pygame.Surface, pygame.Surface]:
    return sprite, pygame.transform.flip(sprite, True, False)


def draw_shadow(screen: pygame.Surface, rect: pygame.Rect, radius: int = 28) -> None:
    shadow = pygame.Surface((radius * 2, radius), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 120), shadow.get_rect())
    screen.blit(shadow, (rect.centerx - radius, rect.bottom - shadow.get_height() // 2))


def draw_stage(screen: pygame.Surface) -> None:
    screen.fill(BG_COLOR)
    stripe_height = 18
    for i in range(0, HEIGHT, stripe_height):
        shade = 18 + (i % (stripe_height * 4))
        pygame.draw.rect(screen, (shade, shade, shade + 6), (0, i, WIDTH, stripe_height))

    pygame.draw.rect(screen, (30, 28, 48), (0, GROUND_Y, WIDTH, HEIGHT - GROUND_Y))
    for x in range(0, WIDTH, 48):
        pygame.draw.rect(screen, (52, 49, 78), (x, GROUND_Y - 12, 32, 12))


def draw_rumi(screen: pygame.Surface, fighter: Fighter, sprites: tuple[pygame.Surface, pygame.Surface]) -> None:
    draw_shadow(screen, fighter.rect)
    sprite = sprites[0] if fighter.direction >= 0 else sprites[1]
    pos = (fighter.rect.centerx - sprite.get_width() // 2, fighter.rect.bottom - sprite.get_height())
    screen.blit(sprite, pos)


def draw_demon(screen: pygame.Surface, demon: Demon, sprites: tuple[pygame.Surface, pygame.Surface]) -> None:
    draw_shadow(screen, demon.rect, radius=24)
    sprite = sprites[0] if demon.direction >= 0 else sprites[1]
    pos = (demon.rect.centerx - sprite.get_width() // 2, demon.rect.bottom - sprite.get_height())
    screen.blit(sprite, pos)


def draw_hud(screen: pygame.Surface, font: pygame.font.Font, player: Fighter, defeated: int, remaining: int) -> None:
    margin = 20
    bar_w, bar_h = 260, 22
    pygame.draw.rect(screen, (60, 60, 86), (margin, margin, bar_w, bar_h), border_radius=6)
    ratio = player.health / 120
    pygame.draw.rect(
        screen,
        (128, 206, 255),
        (margin, margin, int(bar_w * ratio), bar_h),
        border_radius=6,
    )
    label = font.render("Rumi", True, (220, 235, 255))
    screen.blit(label, (margin, margin - 18))

    info = font.render(f"Demons banished: {defeated}  |  Remaining: {remaining}", True, (210, 210, 230))
    screen.blit(info, (WIDTH - info.get_width() - margin, margin))


def draw_hitboxes(screen: pygame.Surface, hitboxes: list[Hitbox]) -> None:
    for hb in hitboxes:
        alpha = 60 if isinstance(hb.owner, Fighter) else 40
        surf = pygame.Surface((hb.rect.width, hb.rect.height), pygame.SRCALPHA)
        color = (120, 210, 255, alpha) if isinstance(hb.owner, Fighter) else (255, 120, 120, alpha)
        surf.fill(color)
        screen.blit(surf, (hb.rect.x, hb.rect.y))


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Kpop Demon Hunters: Rumi vs The Streets")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)
    big_font = pygame.font.Font(None, 52)
    rumi_sprite = load_sprite("Rumi_Portrait.webp", PLAYER_SPRITE_HEIGHT, (120, 210, 255))
    demon_sprite = load_sprite("Demon_Jinu_29.webp", DEMON_SPRITE_HEIGHT, (192, 62, 62))
    rumi_sprites = orient_sprite(rumi_sprite)
    demon_sprites = orient_sprite(demon_sprite)

    player = Fighter(140, GROUND_Y - 110)
    demons: list[Demon] = []
    hitboxes: list[Hitbox] = []

    defeated = 0
    target = 10
    spawn_timer = 0.5
    max_simultaneous = 3
    running = True
    game_over = False

    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if game_over and event.key == pygame.K_r:
                    return main()
                if not game_over:
                    new_hitbox = player.handle_keydown(event.key)
                    if new_hitbox:
                        hitboxes.append(new_hitbox)

        keys = pygame.key.get_pressed()
        if not game_over:
            player.handle_keys(keys)

        # AI and spawning
        if not game_over:
            spawn_timer -= dt
            if spawn_timer <= 0 and len(demons) < max_simultaneous and defeated + len(demons) < target:
                spawn_x = random.choice([WIDTH - 140, 140])
                demons.append(Demon(spawn_x, GROUND_Y - 100))
                spawn_timer = random.uniform(1.2, 2.1)

            for demon in demons:
                new_hb = demon.update(dt, player.rect.centerx)
                if new_hb:
                    hitboxes.append(new_hb)

        player.update(dt)
        for demon in demons:
            demon.physics(dt)

        # Resolve hits
        for hb in list(hitboxes):
            hb.update(dt)
            if hb.expired:
                hitboxes.remove(hb)
                continue

            if isinstance(hb.owner, Fighter):
                for demon in demons:
                    if demon.health > 0 and hb.rect.colliderect(demon.rect):
                        demon.take_damage(hb.damage, hb.owner.rect.centerx)
            else:
                if player.health > 0 and hb.rect.colliderect(player.rect):
                    player.take_damage(hb.damage, hb.owner.rect.centerx)

        before_cull = len(demons)
        demons = [d for d in demons if d.health > 0]
        defeated += before_cull - len(demons)

        if player.health <= 0 and not game_over:
            game_over = True
            end_text = "Rumi fell. Press R to retry."
        elif defeated >= target and not demons and not game_over:
            game_over = True
            end_text = "Block cleared! Press R to celebrate again."

        draw_stage(screen)
        draw_rumi(screen, player, rumi_sprites)
        for demon in demons:
            draw_demon(screen, demon, demon_sprites)

        draw_hitboxes(screen, hitboxes)
        remaining = max(target - defeated, 0)
        draw_hud(screen, font, player, defeated, remaining)

        instructions = font.render("Move: A/D or Arrows | Jump: W/Up/Space | Light: J | Heavy: K | Quit: Esc", True, (220, 220, 240))
        screen.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, HEIGHT - 50))

        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(150)
            overlay.fill((10, 8, 18))
            screen.blit(overlay, (0, 0))
            text = big_font.render(end_text, True, (240, 240, 255))
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 30))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
