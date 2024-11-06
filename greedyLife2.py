import pygame
import numpy as np
import random

# Parameters
WIDTH, HEIGHT = 700, 700  # Screen dimensions
GRID_SIZE = 100  # Size of the Game of Life grid
INITIAL_CELL_SIZE = WIDTH // GRID_SIZE  # Initial cell size
FPS = 10  # Frames per second
RESOURCE_SPAWN_CHANCE = 0.0001  # Chance for a new resource to spawn each frame

# Cell states
DEAD = 0
ALIVE = 1
RESOURCE = 2

# Colors
ALIVE_COLOR = (255, 255, 255)
DEAD_COLOR = (0, 0, 0)
RESOURCE_COLOR = (0, 255, 0)

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life with Resource Seeking")
clock = pygame.time.Clock()

def create_grid():
    """Initialize a grid with random live cells and resources."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    
    # Populate grid with random live cells and resources
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if random.random() < 0.10:  # chance to be alive
                grid[x, y] = ALIVE
            elif random.random() < 0.001:  # chance to be a resource
                grid[x, y] = RESOURCE

    return grid

def count_neighbors(x, y, grid):
    """Count the alive neighbors of cell (x, y)."""
    total = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[nx, ny] == ALIVE:
                    total += 1
    return total

def resource_in_proximity(x, y, grid, proximity_range=3):
    """Check for nearby resources within a specified range."""
    for dx in range(-proximity_range, proximity_range + 1):
        for dy in range(-proximity_range, proximity_range + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[nx, ny] == RESOURCE:
                    return (nx, ny)  # Return position of the resource
    return None

def spawn_new_resources(grid):
    """Randomly spawn new resources in empty cells."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x, y] == DEAD and random.random() < RESOURCE_SPAWN_CHANCE:
                grid[x, y] = RESOURCE
    return grid

def check_resource_surrounded(x, y, grid):
    """Check if a resource is completely surrounded by live cells."""
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if grid[nx, ny] != ALIVE and grid[nx, ny] != RESOURCE:
                    return False
    return True

def update_grid(grid):
    """Compute the next generation of cells with resource-seeking behavior."""
    new_grid = np.copy(grid)
    
    # First check for surrounded resources and remove them
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x, y] == RESOURCE and check_resource_surrounded(x, y, grid):
                new_grid[x, y] = DEAD

    # Then update cell states
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x, y] == ALIVE:
                resource_pos = resource_in_proximity(x, y, grid, proximity_range=3)
                alive_neighbors = count_neighbors(x, y, grid)
                
                if resource_pos:
                    # Move towards the resource if nearby
                    rx, ry = resource_pos
                    dx = np.sign(rx - x)
                    dy = np.sign(ry - y)
                    new_x, new_y = x + dx, y + dy
                    # Check if new position is within bounds and unoccupied
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and grid[new_x, new_y] == DEAD:
                        new_grid[new_x, new_y] = ALIVE  # Move to new position
                        new_grid[x, y] = DEAD  # Leave old position
                        if (new_x, new_y) == resource_pos:
                            new_grid[new_x, new_y] = ALIVE  # Consume resource
                else:
                    # Regular Conway's Game of Life rules
                    if alive_neighbors < 2 or alive_neighbors > 3:
                        new_grid[x, y] = DEAD  # Cell dies
                    elif alive_neighbors == 3:
                        new_grid[x, y] = ALIVE  # Cell survives
            elif grid[x, y] == DEAD:
                alive_neighbors = count_neighbors(x, y, grid)
                if alive_neighbors == 3:
                    new_grid[x, y] = ALIVE  # Cell becomes alive

    # Spawn new resources
    new_grid = spawn_new_resources(new_grid)
    
    return new_grid

def draw_grid(screen, grid, cell_size):
    """Draw the grid on the screen with the specified cell size."""
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x, y] == ALIVE:
                color = ALIVE_COLOR
            elif grid[x, y] == RESOURCE:
                color = RESOURCE_COLOR
            else:
                color = DEAD_COLOR
            rect = pygame.Rect(y * cell_size, x * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color, rect)

def main():
    grid = create_grid()
    cell_size = INITIAL_CELL_SIZE
    running = True

    while running:
        screen.fill(DEAD_COLOR)
        draw_grid(screen, grid, cell_size)
        pygame.display.flip()

        # Update the grid for the next generation
        grid = update_grid(grid)
        clock.tick(FPS)

        # Event handling for quitting
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()