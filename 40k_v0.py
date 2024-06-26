import pygame
import sys
import math
from enum import Enum, auto

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1000, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warhammer 40K Basic")

# Define colors
GRAY = (128, 128, 128)
WHITE = (255, 255, 255)
HIGHLIGHT_COLOR = (255, 255, 0)  # Yellow highlight
BLACK = (0, 0, 0)
DASHED_CIRCLE_COLOR = (0, 255, 255)  # Cyan for dashed circle
BUTTON_COLOR = (0, 0, 255)
BUTTON_HOVER_COLOR = (0, 0, 200)
TERRAIN_COLOR = (0, 128, 0)  # Green for terrain

# Load unit images
friendly_image = pygame.image.load(r"C:\Users\jonat\OneDrive\Documents\rl_40k\img\fire_war.png")
enemy_image = pygame.image.load(r"C:\Users\jonat\OneDrive\Documents\rl_40k\img\berserk.png")

UNIT_RADIUS = friendly_image.get_width() // 2

class GamePhase(Enum):
    COMMAND = auto()
    MOVEMENT = auto()
    SHOOTING = auto()
    CHARGE = auto()
    FIGHT = auto()

class Unit:
    def __init__(self, x, y, image, movement, toughness, weapon_skill, ballistic_skill, wounds, wounds_remaining, save):
        self.x = x
        self.y = y
        self.image = image
        self.selected = False
        self.dragging = False
        self.movement = movement
        self.toughness = toughness
        self.weapon_skill = weapon_skill
        self.ballistic_skill = ballistic_skill
        self.wounds = wounds
        self.wounds_remaining = wounds_remaining
        self.save = save
        self.start_x = x
        self.start_y = y

    def draw(self):
        # Draw the unit image centered at (self.x, self.y)
        WIN.blit(self.image, (self.x - UNIT_RADIUS, self.y - UNIT_RADIUS))

        # Draw highlight if selected
        if self.selected:
            pygame.draw.circle(WIN, HIGHLIGHT_COLOR, (self.x, self.y), UNIT_RADIUS + 3, 3)

    def draw_popup(self):
        # Define the popup size
        popup_width = 150
        popup_height = 130
        
        # Check if popup would be outside the right boundary
        if self.x + UNIT_RADIUS + popup_width > WIDTH:
            popup_x = self.x - UNIT_RADIUS - popup_width
        else:
            popup_x = self.x + UNIT_RADIUS
        
        # Check if popup would be outside the top boundary
        if self.y - UNIT_RADIUS - popup_height < 0:
            popup_y = self.y + UNIT_RADIUS
        else:
            popup_y = self.y - UNIT_RADIUS
        
        # Draw the popup background
        pygame.draw.rect(WIN, WHITE, (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(WIN, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)
        
        # Define the font
        font = pygame.font.SysFont(None, 24)
        
        # Prepare the text lines
        lines = [
            f"Movement: {self.movement}\"",
            f"Toughness: {self.toughness}",
            f"Weapon Skill: {self.weapon_skill}+",
            f"Ballistic Skill: {self.ballistic_skill}+",
            f"Wounds: {self.wounds_remaining} / {self.wounds}",
            f"Save: {self.save}+"
        ]
        
        # Render and draw each line
        for i, line in enumerate(lines):
            text = font.render(line, True, BLACK)
            WIN.blit(text, (popup_x + 10, popup_y + 10 + i * 20))

def draw_dashed_circle(surface, color, center, radius, width=1, dash_length=10):
    circumference = 2 * math.pi * radius
    dashes = int(circumference / dash_length)
    for i in range(dashes):
        start_angle = (i * dash_length) / radius
        end_angle = ((i + 0.5) * dash_length) / radius
        pygame.draw.arc(surface, color, (center[0] - radius, center[1] - radius, 2 * radius, 2 * radius), start_angle, end_angle, width)

# Create units
friendly_units = [
    Unit(x * 50 + 50, y * 50 + 50, friendly_image, 6, 4, 3, 4, 5, 5, 3)
    for x,y in zip([0,1,2,1,0], [4,5,6,7,8])
]
enemy_units = [
    Unit(x * 50 + 50, y * 50 + 50, enemy_image, 5, 5, 4, 3, 6, 6, 2)
    for x,y in zip([18,17,16,17,18], [4,5,6,7,8])
]
units = friendly_units + enemy_units

current_phase = GamePhase.COMMAND

# UI elements
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 50
button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 20, 20, BUTTON_WIDTH, BUTTON_HEIGHT)

dragged_unit = None
drag_offset_x = 0
drag_offset_y = 0

# Define terrain pieces as L shapes using lists of rectangles
terrain = [
    [pygame.Rect(400, 100, 40, 200), pygame.Rect(200, 260, 200, 40)],  # Top-left L
    [pygame.Rect(600, 100, 40, 200), pygame.Rect(600, 260, 200, 40)],  # Top-right L
    [pygame.Rect(400, 400, 40, 200), pygame.Rect(200, 400, 200, 40)],  # Bottom-left L
    [pygame.Rect(600, 400, 40, 200), pygame.Rect(600, 400, 200, 40)]   # Bottom-right L
]

def draw_units():
    for unit in units:
        unit.draw()

def draw_terrain():
    for piece in terrain:
        for rect in piece:
            pygame.draw.rect(WIN, TERRAIN_COLOR, rect)

def check_unit_collision(dragged_unit, new_x, new_y):
    for unit in units:
        if unit is not dragged_unit:
            dist = math.sqrt((unit.x - new_x)**2 + (unit.y - new_y)**2)
            if dist < 2 * UNIT_RADIUS:  # Detect collision if distance is less than the diameter
                return True
    return False

def handle_input():
    global current_phase, dragged_unit, drag_offset_x, drag_offset_y

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            unit_clicked = False

            # Check if the button is clicked
            if button_rect.collidepoint(pos):
                if current_phase == GamePhase.COMMAND:
                    current_phase = GamePhase.MOVEMENT
                elif current_phase == GamePhase.MOVEMENT:
                    current_phase = GamePhase.SHOOTING
                elif current_phase == GamePhase.SHOOTING:
                    current_phase = GamePhase.CHARGE
                elif current_phase == GamePhase.CHARGE:
                    current_phase = GamePhase.FIGHT
                elif current_phase == GamePhase.FIGHT:
                    current_phase = GamePhase.COMMAND

            for unit in units:
                # Check if the click is within the circle (unit base)
                dist = math.sqrt((unit.x - pos[0])**2 + (unit.y - pos[1])**2)
                if dist <= UNIT_RADIUS:
                    unit.selected = True
                    unit_clicked = True
                    if current_phase == GamePhase.MOVEMENT:
                        dragged_unit = unit
                        dragged_unit.start_x = unit.x
                        dragged_unit.start_y = unit.y
                        drag_offset_x = unit.x - pos[0]
                        drag_offset_y = unit.y - pos[1]
                    break
                else:
                    unit.selected = False  # Deselect if clicked outside

        if event.type == pygame.MOUSEBUTTONUP:
            if dragged_unit:
                dragged_unit.dragging = False
                dragged_unit = None

        if event.type == pygame.MOUSEMOTION:
            if dragged_unit:
                pos = pygame.mouse.get_pos()
                new_x = pos[0] + drag_offset_x
                new_y = pos[1] + drag_offset_y
                # Calculate distance and angle for movement limitation
                dx = new_x - dragged_unit.start_x
                dy = new_y - dragged_unit.start_y
                distance = math.sqrt(dx**2 + dy**2)
                if distance <= dragged_unit.movement * 50:
                    can_move = True
                    new_rect = pygame.Rect(new_x - UNIT_RADIUS, new_y - UNIT_RADIUS, friendly_image.get_width(), friendly_image.get_height())
                    for piece in terrain:
                        for rect in piece:
                            if new_rect.colliderect(rect):
                                can_move = False
                                break
                        if not can_move:
                            break

                    if not check_unit_collision(dragged_unit, new_x, new_y) and can_move:
                        dragged_unit.x = new_x
                        dragged_unit.y = new_y

    return True

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(60)
        run = handle_input()
        
        WIN.fill(GRAY)  # Fill the screen with gray
        draw_terrain()
        draw_units()
        
        # Draw the popup and dashed circle for the selected unit
        for unit in units:
            if unit.selected:
                unit.draw_popup()
                # Draw a dashed circle representing the movement range
                if current_phase == GamePhase.MOVEMENT:
                    center_x = unit.start_x
                    center_y = unit.start_y
                    radius = unit.movement * 50  # 50 is a scaling factor for movement
                    draw_dashed_circle(WIN, DASHED_CIRCLE_COLOR, (center_x, center_y), radius)

        # Display current phase
        font = pygame.font.SysFont(None, 36)
        phase_text = font.render(current_phase.name, True, WHITE)
        WIN.blit(phase_text, (10, 10))

        # Draw UI button
        if button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, button_rect)
        else:
            pygame.draw.rect(WIN, BUTTON_COLOR, button_rect)
        button_text = font.render("Next Phase", True, WHITE)
        WIN.blit(button_text, (button_rect.x + 10, button_rect.y + 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
