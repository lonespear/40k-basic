import pygame
import sys
import math
import random
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
RED = (255, 0, 0)
BUTTON_HOVER_COLOR = (0, 0, 200)
TERRAIN_COLOR = (0, 128, 0)  # Green for terrain

# Load unit images
friendly_image = pygame.image.load(r"c:\Users\jonathan.day\OneDrive - West Point\Documents\rl_40k\img\fire_war.png")
enemy_image = pygame.image.load(r"c:\Users\jonathan.day\OneDrive - West Point\Documents\rl_40k\img\berserk.png")

UNIT_RADIUS = friendly_image.get_width() // 2

class GamePhase(Enum):
    COMMAND = auto()
    MOVEMENT = auto()
    SHOOTING = auto()
    CHARGE = auto()
    FIGHT = auto()

class Unit:
    def __init__(self, x, y, image, movement, toughness, weapon_skill, ballistic_skill, wounds, wounds_remaining, save, 
                 sh_name, eff_range, sh_atks, sh_strength, sh_ap, sh_damage,
                 me_name, me_atks, me_strength, me_ap, me_damage):
        self.x = x                                      # x position
        self.y = y                                      # y position
        self.start_x = x                                # starting x pos for dragging purposes
        self.start_y = y                                # starting y pos for dragging purposes
        self.has_moved = False                          # movement tracker
        self.has_shot = False                           # shooting tracker
        self.selected = False                           # bool if selected
        self.info = False                               # bool to control popup
        self.dragging = False                           # bool if dragged
        self.image = image                              # token
        self.movement = movement                        # movement stat
        self.toughness = toughness                      # toughness stat
        self.weapon_skill = weapon_skill                # weapon skill stat
        self.ballistic_skill = ballistic_skill          # ballistic skill stat
        self.wounds = wounds                            # wounds stat
        self.wounds_remaining = wounds_remaining        # wounds remaining stat
        self.save = save                                # armor save stat
        self.sh_name = sh_name                          # shooting weapon name
        self.eff_range = eff_range                      # range of weapon
        self.sh_atks = sh_atks                          # number of shots
        self.sh_strength = sh_strength                  # strength of weapon
        self.sh_ap = sh_ap                              # armor penetration of weapon
        self.sh_damage = sh_damage                      # shooting weapon damage
        self.me_name = me_name                          # melee weapon name
        self.me_atks = me_atks                          # number of attacks
        self.me_strength = me_strength                  # strength of weapon
        self.me_ap = me_ap                              # armor penetration of weapon
        self.me_damage = me_damage                      # weapon damage

    def draw(self):
        # Draw the unit image centered at (self.x, self.y)
        WIN.blit(self.image, (self.x - UNIT_RADIUS, self.y - UNIT_RADIUS))

        # Draw highlight if selected
        if self.selected:
            pygame.draw.circle(WIN, HIGHLIGHT_COLOR, (self.x, self.y), UNIT_RADIUS + 3, 3)

    def draw_popup(self):
        # Define the popup size
        popup_width = 180
        popup_height = 165
        
        pane = 1 # display basic stats initially
        
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

        # Draw popup buttons
        base_button = pygame.Rect(popup_x + 10, popup_y + 10, popup_width / 3.1, 20)
        shoot_button = pygame.Rect(popup_x + 60, popup_y + 10, popup_width / 3.1, 20)
        fight_button = pygame.Rect(popup_x + 110, popup_y + 10, popup_width / 3.1, 20)
        
        # Define the font
        font = pygame.font.SysFont(None, 20)

        # Draw base stats button
        if base_button.collidepoint(pygame.mouse.get_pos()):
            pane = 1
            pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, base_button)
        else:
            pygame.draw.rect(WIN, BUTTON_COLOR, base_button)
        base_text = font.render("Basic", True, WHITE)
        WIN.blit(base_text, (base_button.x + 10, base_button.y + 5))
        # Draw shooting stats button
        if shoot_button.collidepoint(pygame.mouse.get_pos()):
            pane = 2
            pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, shoot_button)
        else:
            pygame.draw.rect(WIN, BUTTON_COLOR, shoot_button)
        shoot_text = font.render("Shoot", True, WHITE)
        WIN.blit(shoot_text, (shoot_button.x + 10, shoot_button.y + 5))
        # Draw fighting stats button
        if fight_button.collidepoint(pygame.mouse.get_pos()):
            pane = 3
            pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, fight_button)
        else:
            pygame.draw.rect(WIN, BUTTON_COLOR, fight_button)
        fight_text = font.render("Melee", True, WHITE)
        WIN.blit(fight_text, (fight_button.x + 10, fight_button.y + 5))

        # Prepare the text lines
        base_stats = [
            f"Movement: {self.movement}\"",
            f"Toughness: {self.toughness}",
            f"Weapon Skill: {self.weapon_skill}+",
            f"Ballistic Skill: {self.ballistic_skill}+",
            f"Wounds: {self.wounds_remaining} / {self.wounds}",
            f"Save: {self.save}+"
        ]

        shooting_stats = [
            f"Weapon: {self.sh_name}",
            f"Range: {self.eff_range}\"",
            f"Shots: {self.sh_atks}",
            f"Strength: {self.sh_strength}",
            f"AP: {self.sh_ap}",
            f"Damage: {self.sh_damage}"
        ]

        melee_stats = [
            f"Weapon: {self.me_name}",
            f"Attacks: {self.me_atks}",
            f"Strength: {self.me_strength}",
            f"AP: {self.me_ap}",
            f"Damage: {self.me_damage}"
        ]
        
        if pane == 1:
            stats = base_stats
        elif pane == 2:
            stats = shooting_stats
        else:
            stats = melee_stats

        # Render and draw each line
        for i, line in enumerate(stats):
            text = font.render(line, True, BLACK)
            WIN.blit(text, (popup_x + 10, popup_y + 40 + i * 20))
    
    def shoot(self, target):
        hit_rolls = [random.randint(1, 6) for _ in range(self.sh_atks)]
        hits = sum(1 for roll in hit_rolls if roll >= self.ballistic_skill)
        wound_rolls = [random.randint(1, 6) for _ in range(hits)]
        if self.sh_strength == target.toughness:
            wounds = sum(1 for roll in wound_rolls if roll >= 4)
        elif self.sh_strength < target.toughness:
            wounds = sum(1 for roll in wound_rolls if roll >= 5)
        else:
            wounds = sum(1 for roll in wound_rolls if roll >= 3)
        save_rolls = [random.randint(1,6) for _ in range(wounds)]
        unsaved_wounds = sum(1 for roll in save_rolls if roll < target.save)
        damage = unsaved_wounds * self.sh_damage
        target.wounds_remaining -= damage
        if target.wounds_remaining <= 0:
            units.remove(target)
        

def draw_dashed_circle(surface, color, center, radius, width=1, dash_length=10):
    circumference = 2 * math.pi * radius
    dashes = int(circumference / dash_length)
    for i in range(dashes):
        start_angle = (i * dash_length) / radius
        end_angle = ((i + 0.5) * dash_length) / radius
        pygame.draw.arc(surface, color, (center[0] - radius, center[1] - radius, 2 * radius, 2 * radius), start_angle, end_angle, width)

# Create units
friendly_units = [
    Unit(x * 50 + 50, y * 50 + 50, friendly_image, 6, 4, 3, 4, 5, 5, 3, 
         "Pulse Carbine", 20, 2, 5, 0, 1,
         "Honor Blade", 1, 4, 0, 1)
    for x,y in zip([0,1,2,1,0], [4,5,6,7,8])
]
enemy_units = [
    Unit(x * 50 + 50, y * 50 + 50, enemy_image, 5, 5, 4, 3, 6, 6, 2, 
         "Bolt Pistol", 8, 2, 4, 0, 2,
         "Chain-Axe", 3, 6, -1, 2)
    for x,y in zip([18,17,16,17,18], [4,5,6,7,8])
]
units = friendly_units + enemy_units

# Initiate Game Phase Variables
current_phase = GamePhase.COMMAND
dragged_unit = None
drag_offset_x = 0
drag_offset_y = 0
shoot_popup = None

# UI elements
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 30
button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 20, 10, BUTTON_WIDTH, BUTTON_HEIGHT)

# Define terrain pieces as L shapes using lists of rectangles
terrain = [
    [pygame.Rect(400, 80, 20, 200), pygame.Rect(200, 260, 200, 20)],  # Top-left L
    [pygame.Rect(600, 80, 20, 200), pygame.Rect(600, 260, 200, 20)],  # Top-right L
    [pygame.Rect(400, 400, 20, 200), pygame.Rect(200, 400, 200, 20)],  # Bottom-left L
    [pygame.Rect(600, 400, 20, 200), pygame.Rect(600, 400, 200, 20)]   # Bottom-right L
]

def draw_units():
    for unit in units:
        unit.draw()

def draw_terrain():
    for piece in terrain:
        for rect in piece:
            pygame.draw.rect(WIN, TERRAIN_COLOR, rect)

def draw_uibar():
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
    WIN.blit(button_text, (button_rect.x + 10, button_rect.y + 5))

def check_unit_collision(dragged_unit, new_x, new_y):
    for unit in units:
        if unit is not dragged_unit:
            dist = math.sqrt((unit.x - new_x)**2 + (unit.y - new_y)**2)
            if dist < 2 * UNIT_RADIUS:  # Detect collision if distance is less than the diameter
                return True
    return False

def draw_shoot_popup(unit):
    popup_width = 90
    popup_height = 50
    popup_x = unit.x + UNIT_RADIUS
    popup_y = unit.y - UNIT_RADIUS

    if popup_x + popup_width > WIDTH:
        popup_x = unit.x - UNIT_RADIUS - popup_width

    if popup_y + popup_height > HEIGHT:
        popup_y = unit.y - UNIT_RADIUS - popup_height

    pygame.draw.rect(WIN, WHITE, (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(WIN, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)

    shoot_button = pygame.Rect(popup_x + 10, popup_y + 10, popup_width - 20, 30)
    font = pygame.font.SysFont(None, 24)
    shoot_text = font.render("Shoot", True, WHITE)
    
    if shoot_button.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, shoot_button)
        if pygame.mouse.get_pressed()[0]:
            for u in units:
                if u.selected:
                    u.shoot(unit)
                    break
    else:
        pygame.draw.rect(WIN, BUTTON_COLOR, shoot_button)
    
    WIN.blit(shoot_text, (shoot_button.x + 10, shoot_button.y + 5))

# Helper functions for shooting phase
def line_intersects_line(l1_start, l1_end, l2_start, l2_end):
    """Check if two lines intersect."""
    def ccw(A, B, C):
        return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
    return ccw(l1_start, l2_start, l2_end) != ccw(l1_end, l2_start, l2_end) and ccw(l1_start, l1_end, l2_start) != ccw(l1_start, l1_end, l2_end)

def line_intersects_rect(line_start, line_end, rect):
    """Check if a line intersects with a rectangle."""
    rect_lines = [
        ((rect.left, rect.top), (rect.right, rect.top)),
        ((rect.right, rect.top), (rect.right, rect.bottom)),
        ((rect.right, rect.bottom), (rect.left, rect.bottom)),
        ((rect.left, rect.bottom), (rect.left, rect.top))
    ]   
    for rect_line in rect_lines:
        if line_intersects_line(line_start, line_end, rect_line[0], rect_line[1]):
            return True
    return False

def handle_input():
    global current_phase, dragged_unit, drag_offset_x, drag_offset_y, targeted

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

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
            
            unit_selected = False # create marker switch
            for unit in units:
                # Check if the click is within the circle (unit base)
                dist = math.sqrt((unit.x - pos[0])**2 + (unit.y - pos[1])**2)
                if dist <= UNIT_RADIUS:
                    unit_selected = True # flip on marker switch that a unit was selected with the mouse click
                    selected_unit = unit # associating unit to selected unit
                    if event.button == 1:
                        unit.selected = True
                        if current_phase == GamePhase.MOVEMENT and not unit.has_moved:
                            dragged_unit = unit
                            dragged_unit.start_x = unit.x
                            dragged_unit.start_y = unit.y
                            drag_offset_x = unit.x - pos[0]
                            drag_offset_y = unit.y - pos[1]
                        break
                    elif event.button == 3 and current_phase == GamePhase.SHOOTING:
                        targeted = unit
                    else:
                        unit.info = True
                else:
                    unit.selected = False  # Deselect if clicked outside
                    unit.info = False
            
            if unit_selected: # deselect logic if clicked another unit
                for unit in units:
                    if unit != selected_unit:
                        unit.selected = False
                        unit.info = False

        if event.type == pygame.MOUSEBUTTONUP:
            if dragged_unit:
                dragged_unit.dragging = False
                dragged_unit.has_moved = True
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
                if distance <= dragged_unit.movement * 20:
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

def command_phase():
    # Draw popup window
    for unit in units:
        if unit.info:
            unit.draw_popup()

def movement_phase():
    # Draw the popup and dashed circle for the selected unit
    for unit in units:
        if unit.info:
            unit.draw_popup()
        if unit.selected:
            # Draw a dashed circle representing the movement range
            center_x = unit.start_x
            center_y = unit.start_y
            radius = unit.movement * 20  # 50 is a scaling factor for movement
            draw_dashed_circle(WIN, DASHED_CIRCLE_COLOR, (center_x, center_y), radius)

    # Display moved units ratio
    moved_units = sum(1 for unit in units if unit.has_moved)
    total_units = len(units)
    font = pygame.font.SysFont(None, 36)
    moved_text = font.render(f"{moved_units}/{total_units} Units Moved", True, WHITE)
    WIN.blit(moved_text, (WIDTH // 2 - moved_text.get_width() // 2, 10))

def shooting_phase():
    # reset move indicator
    for unit in units:
        unit.has_moved = False
    
    for unit in units:
        # Draw popup window
        if unit.info:
            unit.draw_popup()
        # If selected draw range circle, and highlight eligible targets
        if unit.selected:
            center_x = unit.x
            center_y = unit.y
            radius = unit.eff_range * 20  # 50 is a scaling factor for movement
            draw_dashed_circle(WIN, HIGHLIGHT_COLOR, (center_x, center_y), radius) # Draw range circle
            elig_tgts = []
            for target in units:
                dist = math.sqrt((unit.x - target.x)**2 + (unit.y - target.y)**2)   # Calculate distance between unit and all other targets
                if dist > 0 and dist <= unit.eff_range * 20:                        # Ensure distance is greater than zero(itself) and less than max range
                    angle = math.atan2((target.y - unit.y), (target.x - unit.x))     # Calculate trajectory to target (note the order of arguments)
                    
                    # Calculate left and right offset points from the unit
                    left_start_x, left_start_y = unit.x + UNIT_RADIUS * math.cos(angle + math.pi/2), unit.y + UNIT_RADIUS * math.sin(angle + math.pi/2)
                    left_end_x, left_end_y = target.x + UNIT_RADIUS * math.cos(angle + math.pi/2), target.y + UNIT_RADIUS * math.sin(angle + math.pi/2)
                    right_start_x, right_start_y = unit.x + UNIT_RADIUS * math.cos(angle - math.pi/2), unit.y + UNIT_RADIUS * math.sin(angle - math.pi/2)
                    right_end_x, right_end_y = target.x + UNIT_RADIUS * math.cos(angle - math.pi/2), target.y + UNIT_RADIUS * math.sin(angle - math.pi/2)

                    # Check for terrain intersection
                    left_blocked = any(line_intersects_rect((left_start_x, left_start_y), (left_end_x, left_end_y), rect) for piece in terrain for rect in piece)
                    right_blocked = any(line_intersects_rect((right_start_x, right_start_y), (right_end_x, right_end_y), rect) for piece in terrain for rect in piece)

                    if not left_blocked or not right_blocked:
                        # eligible target
                        pygame.draw.circle(WIN, RED, (target.x, target.y), UNIT_RADIUS + 3, 3)
                        elig_tgts.append(target)
            if targeted in elig_tgts:
                draw_shoot_popup(targeted)


def charge_phase():
    # Draw popup window
    for unit in units:
        if unit.info:
            unit.draw_popup()
        if unit.selected:
            center_x = unit.x
            center_y = unit.y
            radius = 12 * 20  # 50 is a scaling factor for movement
            draw_dashed_circle(WIN, RED, (center_x, center_y), radius)


def fight_phase():
    # Draw popup window
    for unit in units:
        if unit.info:
            unit.draw_popup()

def main():
    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(60)
        run = handle_input()
        
        WIN.fill(GRAY)  # Fill the screen with gray
        draw_terrain()
        draw_units()
        draw_uibar()

        # Call phase-specific logic
        if current_phase == GamePhase.COMMAND:
            command_phase()
        elif current_phase == GamePhase.MOVEMENT:
            movement_phase()
        elif current_phase == GamePhase.SHOOTING:
            shooting_phase()
        elif current_phase == GamePhase.CHARGE:
            charge_phase()
        elif current_phase == GamePhase.FIGHT:
            fight_phase()

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
