"""
Space Invaders (Python/Pygame)
Quick-launch: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && python main.py
Controls: Arrow keys or A/D to move, Space to shoot, R to restart, Esc to quit.
"""

import random
import sys
from dataclasses import dataclass
from typing import List, Optional

import pygame


WIDTH, HEIGHT = 960, 640
FPS = 60
PLAYER_SPEED = 6
BULLET_SPEED = 10
ENEMY_ROWS = 5
ENEMY_COLS = 10
ENEMY_SPEED = 1.2
ENEMY_DROP = 28
ENEMY_FIRE_RATE = 0.008  # probability per frame
PLAYER_COOLDOWN_MS = 260

BG_COLOR = (10, 12, 24)
PLAYER_COLOR = (100, 220, 140)
ENEMY_COLORS = [(240, 104, 80), (240, 176, 90), (120, 190, 255)]
BULLET_COLOR = (180, 220, 255)
ENEMY_BULLET_COLOR = (255, 180, 70)
TEXT_COLOR = (230, 232, 240)


@dataclass
class Bullet:
    rect: pygame.Rect
    speed: int
    color: tuple
    from_player: bool

    def update(self) -> None:
        self.rect.y += self.speed

    @property
    def off_screen(self) -> bool:
        return self.rect.bottom < 0 or self.rect.top > HEIGHT


class Player:
    def __init__(self) -> None:
        self.rect = pygame.Rect(WIDTH // 2 - 24, HEIGHT - 80, 48, 28)
        self.speed = PLAYER_SPEED
        self.lives = 3
        self.last_shot = 0

    def update(self, keys: pygame.key.ScancodeWrapper) -> None:
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        self.rect.x = max(20, min(WIDTH - 20 - self.rect.width, self.rect.x + dx))

    def can_shoot(self, now_ms: int) -> bool:
        return now_ms - self.last_shot >= PLAYER_COOLDOWN_MS

    def shoot(self, now_ms: int) -> Bullet:
        self.last_shot = now_ms
        bullet_rect = pygame.Rect(self.rect.centerx - 3, self.rect.top - 12, 6, 14)
        return Bullet(bullet_rect, -BULLET_SPEED, BULLET_COLOR, from_player=True)


class Enemy:
    def __init__(self, x: int, y: int, color: tuple) -> None:
        self.rect = pygame.Rect(x, y, 40, 28)
        self.color = color
        self.alive = True

    def draw(self, screen: pygame.Surface) -> None:
        if not self.alive:
            return
        pygame.draw.rect(screen, self.color, self.rect, border_radius=4)
        eye_color = (20, 20, 24)
        pygame.draw.rect(screen, eye_color, (self.rect.x + 8, self.rect.y + 8, 8, 6))
        pygame.draw.rect(screen, eye_color, (self.rect.x + 24, self.rect.y + 8, 8, 6))


class Swarm:
    def __init__(self, rows: int, cols: int) -> None:
        self.rows = rows
        self.cols = cols
        self.enemies: List[Enemy] = []
        self.direction = 1
        self.speed = ENEMY_SPEED
        self._spawn_grid()

    def _spawn_grid(self) -> None:
        self.enemies.clear()
        start_x, start_y = 120, 80
        gap_x, gap_y = 64, 48
        for row in range(self.rows):
            color = ENEMY_COLORS[min(row, len(ENEMY_COLORS) - 1)]
            for col in range(self.cols):
                x = start_x + col * gap_x
                y = start_y + row * gap_y
                self.enemies.append(Enemy(x, y, color))
        self.direction = 1
        self.speed = ENEMY_SPEED

    def alive_enemies(self) -> List[Enemy]:
        return [e for e in self.enemies if e.alive]

    def update(self) -> None:
        alive = self.alive_enemies()
        if not alive:
            return

        dx = self.direction * self.speed
        left_edge = min(e.rect.left for e in alive)
        right_edge = max(e.rect.right for e in alive)
        move_down = False

        if left_edge + dx < 20 or right_edge + dx > WIDTH - 20:
            self.direction *= -1
            dx = self.direction * self.speed
            move_down = True

        for enemy in alive:
            enemy.rect.x += dx
            if move_down:
                enemy.rect.y += ENEMY_DROP

    def maybe_fire(self) -> Optional[Bullet]:
        alive = self.alive_enemies()
        if not alive:
            return None
        if random.random() < ENEMY_FIRE_RATE:
            shooter = random.choice(alive)
            rect = pygame.Rect(shooter.rect.centerx - 3, shooter.rect.bottom, 6, 14)
            return Bullet(rect, BULLET_SPEED - 2, ENEMY_BULLET_COLOR, from_player=False)
        return None


def draw_hud(screen: pygame.Surface, font: pygame.font.Font, score: int, lives: int) -> None:
    score_text = font.render(f"Score: {score}", True, TEXT_COLOR)
    lives_text = font.render(f"Lives: {lives}", True, TEXT_COLOR)
    screen.blit(score_text, (20, 14))
    screen.blit(lives_text, (WIDTH - lives_text.get_width() - 20, 14))


def draw_overlay(screen: pygame.Surface, title: str, subtitle: str, font: pygame.font.Font) -> None:
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    title_surf = font.render(title, True, TEXT_COLOR)
    subtitle_surf = font.render(subtitle, True, TEXT_COLOR)
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, HEIGHT // 2 - 20))
    screen.blit(subtitle_surf, (WIDTH // 2 - subtitle_surf.get_width() // 2, HEIGHT // 2 + 12))


def reset_game() -> tuple:
    player = Player()
    swarm = Swarm(ENEMY_ROWS, ENEMY_COLS)
    bullets: List[Bullet] = []
    score = 0
    return player, swarm, bullets, score


def run() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Invaders (Python)")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 20)

    player, swarm, bullets, score = reset_game()
    game_over = False
    player_won = False

    while True:
        _ = clock.tick(FPS)
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r and game_over:
                    player, swarm, bullets, score = reset_game()
                    game_over = False
                    player_won = False

        keys = pygame.key.get_pressed()

        if not game_over:
            player.update(keys)

            if keys[pygame.K_SPACE] and player.can_shoot(now):
                bullets.append(player.shoot(now))

            swarm.update()
            enemy_bullet = swarm.maybe_fire()
            if enemy_bullet:
                bullets.append(enemy_bullet)

            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen:
                    bullets.remove(bullet)
                    continue

                if bullet.from_player:
                    for enemy in swarm.alive_enemies():
                        if enemy.rect.colliderect(bullet.rect):
                            enemy.alive = False
                            bullets.remove(bullet)
                            score += 10
                            swarm.speed = min(3.5, swarm.speed + 0.05)
                            break
                else:
                    if bullet.rect.colliderect(player.rect):
                        bullets.remove(bullet)
                        player.lives -= 1
                        if player.lives <= 0:
                            game_over = True
                            player_won = False

            for enemy in swarm.alive_enemies():
                if enemy.rect.colliderect(player.rect) or enemy.rect.bottom >= HEIGHT - 80:
                    game_over = True
                    player_won = False
                    break

            if not swarm.alive_enemies():
                game_over = True
                player_won = True

        screen.fill(BG_COLOR)

        pygame.draw.rect(screen, PLAYER_COLOR, player.rect, border_radius=5)
        pygame.draw.rect(
            screen,
            (70, 160, 110),
            (player.rect.x + 10, player.rect.y + 6, player.rect.width - 20, 6),
        )

        for enemy in swarm.alive_enemies():
            enemy.draw(screen)

        for bullet in bullets:
            pygame.draw.rect(screen, bullet.color, bullet.rect, border_radius=3)

        draw_hud(screen, font, score, player.lives)

        if game_over:
            title = "You Win!" if player_won else "Game Over"
            subtitle = "Press R to restart or Esc to quit"
            draw_overlay(screen, title, subtitle, font)

        pygame.display.flip()


if __name__ == "__main__":
    run()
