import pygame
import random
import time


def run_tetris_game():
    # Initialize Pygame
    pygame.init()

    # Constants
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800  # Adjusted for the 16x16 grid
    GRID_SIZE = 50
    GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
    GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    BACKGROUND = (0, 0, 0)

    # Tetromino shapes
    SHAPES = [
        [[1, 1, 1, 1]],
        [[1, 1], [1, 1]],
        [[1, 1, 1], [0, 1, 0]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[1, 1, 1], [0, 1, 0]],
        [[1, 1, 1], [1, 0, 0]]
    ]

    SHAPES_COLORS = [CYAN, YELLOW, GREEN, RED, BLUE, MAGENTA, WHITE]

    # Initialize the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Tetris")

    # Initialize clock
    clock = pygame.time.Clock()

    # Initialize variables
    grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    colors_grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]

    current_shape = None
    current_shape_color = None
    current_shape_x = 0
    current_shape_y = 0
    score = 0
    game_over = False
    game_over_time = 0
    restart_delay = 5

    def draw_grid():
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                pygame.draw.rect(screen, BACKGROUND, (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE), 1)

    def draw_shape(shape, color, x, y):
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    pygame.draw.rect(screen, color, ((x + col) * GRID_SIZE, (y + row) * GRID_SIZE, GRID_SIZE, GRID_SIZE))

    def check_collision(shape, x, y):
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    if x + col < 0 or x + col >= GRID_WIDTH or y + row >= GRID_HEIGHT or grid[y + row][x + col]:
                        return True
        return False

    def place_shape(shape, color, x, y):
        for row in range(len(shape)):
            for col in range(len(shape[row])):
                if shape[row][col]:
                    grid[y + row][x + col] = 1
                    colors_grid[y + row][x + col] = color

    def clear_rows():
        nonlocal score
        full_rows = []
        for row in range(GRID_HEIGHT):
            if all(grid[row]):
                full_rows.append(row)

        for row in full_rows:
            del grid[row]
            del colors_grid[row]
            grid.insert(0, [0] * GRID_WIDTH)
            colors_grid.insert(0, [None] * GRID_WIDTH)
            score += 100

    def generate_new_shape():
        nonlocal current_shape, current_shape_color, current_shape_x, current_shape_y
        current_shape = random.choice(SHAPES)
        current_shape_color = random.choice(SHAPES_COLORS)
        current_shape_x = GRID_WIDTH // 2 - len(current_shape[0]) // 2
        current_shape_y = 0

    # Game loop
    generate_new_shape()
    running = True

    while running:
        current_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        if not check_collision(current_shape, current_shape_x - 1, current_shape_y):
                            current_shape_x -= 1
                    elif event.key == pygame.K_RIGHT:
                        if not check_collision(current_shape, current_shape_x + 1, current_shape_y):
                            current_shape_x += 1
                    elif event.key == pygame.K_DOWN:
                        if not check_collision(current_shape, current_shape_x, current_shape_y + 1):
                            current_shape_y += 1
                    elif event.key == pygame.K_UP:
                        # Rotate the shape
                        new_shape = [[current_shape[y][x] for y in range(len(current_shape))] for x in
                                    range(len(current_shape[0]))]
                        new_shape.reverse()
                        if not check_collision(new_shape, current_shape_x, current_shape_y):
                            current_shape = new_shape

        if not game_over:
            if not check_collision(current_shape, current_shape_x, current_shape_y + 1):
                current_shape_y += 1
            else:
                place_shape(current_shape, current_shape_color, current_shape_x, current_shape_y)
                clear_rows()
                generate_new_shape()
                current_shape_y = 0

                if check_collision(current_shape, current_shape_x, current_shape_y):
                    game_over = True
                    game_over_time = current_time

        screen.fill(BACKGROUND)
        draw_grid()

        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                if grid[row][col]:
                    pygame.draw.rect(screen, colors_grid[row][col],
                                     (col * GRID_SIZE, row * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        draw_shape(current_shape, current_shape_color, current_shape_x, current_shape_y)
        pygame.display.flip()

        try:
            # shrink the image to 16x16
            small_screen = pygame.Surface((16, 16))
            pygame.transform.scale(screen, (16, 16), small_screen)
            pygame.image.save(small_screen, "image.png")

        except Exception as e:
            print(f"An error occurred: {e}")

        clock.tick(2)
        if game_over:
            print("GAME OVER")

            if current_time - game_over_time >= 10:
                game_over = False
                grid = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                colors_grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
                score = 0
                generate_new_shape()
                game_over_time = 0

    # Close the game
    pygame.quit()
    exit()



if __name__ == "__main__":


    run_tetris_game()
