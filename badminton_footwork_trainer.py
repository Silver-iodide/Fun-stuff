import random
import pygame

WIDTH, HEIGHT = 1280, 800
FPS = 60
BASE_INTERVAL = 3.0
PRE_CUE = 0.15
DOT_DURATION = 0.45
JITTER = 0.20
JITTER_ON = True

BG = (250, 250, 250)
RED = (220, 40, 40)
GHOST = (180, 180, 180)
ACCENT = (100, 120, 220)

def get_font(size: int, bold=False) -> pygame.font.Font:
    candidates = ["Segoe UI", "Arial", "Verdana", "Noto Sans", "DejaVu Sans"]
    for name in candidates:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            _ = f.render("A", True, (0, 0, 0))
            return f
        except Exception:
            continue
    return pygame.font.Font(None, size)

def choose_next_index(n: int, last_idx: int | None) -> int:
    choices = [i for i in range(n) if i != last_idx]
    return random.choice(choices)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Badminton Footwork Trainer")
    clock = pygame.time.Clock()

    font_big = get_font(96, bold=True)

    running = False
    base_interval = BASE_INTERVAL
    pre_cue = PRE_CUE
    dot_duration = DOT_DURATION
    jitter_on = JITTER_ON
    jitter = JITTER

    now = pygame.time.get_ticks() / 1000.0
    last_idx = None
    current_idx = None
    dot_on_until = 0.0

    # keep split-step text for extra 0.3s after the dot appears
    split_step_off_time = 0.0

    def next_interval():
        if jitter_on:
            return max(0.3, base_interval + random.uniform(-jitter, jitter))
        return base_interval

    next_dot_time = now + next_interval()
    pre_cue_time = max(now, next_dot_time - pre_cue)
    pre_shown = False

    def get_positions():
        cw, ch = screen.get_width(), screen.get_height()
        pts = [
            (cw * 0.25, ch * 0.25),  # Front-Left
            (cw * 0.75, ch * 0.25),  # Front-Right
            (cw * 0.25, ch * 0.75),  # Rear-Left
            (cw * 0.75, ch * 0.75),  # Rear-Right
        ]
        return pts

    def draw_scene(pts, highlight_idx: int | None, pre_active: bool):
        screen.fill(BG)
        for i, (x, y) in enumerate(pts):
            if i == highlight_idx:
                pygame.draw.circle(screen, RED, (int(x), int(y)), 40)
            else:
                pygame.draw.circle(screen, GHOST, (int(x), int(y)), 20, 3)
        if pre_active:
            txt = font_big.render("Split step!", True, ACCENT)
            screen.blit(txt, (screen.get_width()//2 - txt.get_width()//2, screen.get_height()//2 - txt.get_height()//2))

    running_main = True
    while running_main:
        dt = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_main = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running_main = False
                elif event.key == pygame.K_SPACE:
                    running = not running
                    if running:
                        now = pygame.time.get_ticks() / 1000.0
                        next_dot_time = now + next_interval()
                        pre_cue_time = max(now, next_dot_time - pre_cue)
                        pre_shown = False
                        dot_on_until = 0.0
                        current_idx = None
                        split_step_off_time = 0.0

        if running:
            # hide dot after its duration
            if current_idx is not None and now >= dot_on_until:
                current_idx = None

            # show pre-cue before the dot
            if not pre_shown and now >= pre_cue_time:
                pre_shown = True

            # when it's time to show the dot
            if now >= next_dot_time:
                new_idx = choose_next_index(4, last_idx)
                last_idx = new_idx
                current_idx = new_idx
                dot_on_until = now + dot_duration

                # keep split step visible for extra 0.3s after dot appears
                split_step_off_time = now + 0.3

                # schedule next
                iv = next_interval()
                next_dot_time = now + iv
                pc = min(pre_cue, iv * 0.9)
                pre_cue_time = max(now, next_dot_time - pc)
                pre_shown = False

        pts = get_positions()
        # Split step shows if we're in pre-cue OR within the extra 0.3s window after dot
        pre_active = (pre_shown or now < split_step_off_time) and running
        draw_scene(pts, current_idx, pre_active)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
