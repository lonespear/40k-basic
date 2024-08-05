import pygame
import sys
import math
import random
from enum import Enum, auto

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 1000, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Warhammer 40K Basic")

# Define colors
DARK_GRAY = (192,192,192)
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
friendly_image = pygame.image.load(r"C:\Users\jonat\OneDrive\Documents\rl_40k\img\fire_war.png")
enemy_image = pygame.image.load(r"C:\Users\jonat\OneDrive\Documents\rl_40k\img\berserk.png")

UNIT_RADIUS = friendly_image.get_width() // 2

'''
CLASSES: GamePhase, Unit, 
'''

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
        self.has_charged = False                        # charge tracker
        self.selected = False                           # bool if selected
        self.targeted = False                           # bool if targeted
        self.info = False                               # bool to control stats popup
        self.dragging = False                           # bool if dragged
        self.elig_tgts = []                             # list of eligible targets
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
        target_button = pygame.Rect(popup_x + 60, popup_y + 10, popup_width / 3.1, 20)
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
        if target_button.collidepoint(pygame.mouse.get_pos()):
            pane = 2
            pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, target_button)
        else:
            pygame.draw.rect(WIN, BUTTON_COLOR, target_button)
        shoot_text = font.render("Shoot", True, WHITE)
        WIN.blit(shoot_text, (target_button.x + 10, target_button.y + 5))
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
        print("hit rolls: ", hit_rolls)
        hits = sum(1 for roll in hit_rolls if roll >= self.ballistic_skill - 1)
        print("hits: ", hits)
        wound_rolls = [random.randint(1, 6) for _ in range(hits)]
        print("wound rolls: ", wound_rolls)
        if self.sh_strength == target.toughness:
            wounds = sum(1 for roll in wound_rolls if roll >= 3)
        elif self.sh_strength < target.toughness:
            wounds = sum(1 for roll in wound_rolls if roll >= 4)
        else:
            wounds = sum(1 for roll in wound_rolls if roll >= 2)
        print("wounds: ", wounds)
        save_rolls = [random.randint(1,6) for _ in range(wounds)]
        print("save rolls: ", save_rolls)
        unsaved_wounds = sum(1 for roll in save_rolls if roll < target.save + 1)
        print("unsaved wounds: ", unsaved_wounds)
        damage = unsaved_wounds * self.sh_damage
        print("damage: ", damage)
        target.wounds_remaining -= damage
        print("wounds remaining: ", target.wounds_remaining)
        if target.wounds_remaining <= 0:
            units.remove(target)
        print("end of shooting")
        return(WIN, hit_rolls, hits, wound_rolls, wounds, save_rolls, unsaved_wounds, damage)
    
    def charge(self, target):
        # Calculate the distance between bases of the two units
        d = round(math.sqrt((self.x - target.x - 2 * UNIT_RADIUS)**2 + (self.y - target.y - 2 * UNIT_RADIUS)**2) / 20, 2)
        roll = [random.randint(1,6), random.randint(1,6)]
        if sum(roll) < d:
            print("charge failed")
            return(WIN, False, "Charge Failed", roll, d)
        else:
            print("charge passed")
            return(WIN, True, "Charge Succeeded", roll, d)
        

def display_charge(WIN, text, roll, distance):
    font = pygame.font.SysFont(None, 18)
    roll_text = font.render(f"{text}, Roll: {roll}, Distance: {distance}", True, BLACK)
    WIN.blit(roll_text, (200, 15))
    
def draw_target_popup(unit):
    global target_button

    popup_width = 65
    popup_height = 30
    popup_x = unit.x + UNIT_RADIUS
    popup_y = unit.y - UNIT_RADIUS

    if popup_x + popup_width > WIDTH:
        popup_x = unit.x - UNIT_RADIUS - popup_width

    if popup_y + popup_height > HEIGHT:
        popup_y = unit.y - UNIT_RADIUS - popup_height

    target_button = pygame.Rect(popup_x + 5, popup_y + 5, popup_width - 10, 20)

    pygame.draw.rect(WIN, WHITE, (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(WIN, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)

    if target_button.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(WIN, RED, target_button)
    else:
        pygame.draw.rect(WIN, BUTTON_COLOR, target_button)

    font = pygame.font.SysFont(None, 18)
    if current_phase == GamePhase.SHOOTING:
        target_text = font.render("Shoot", True, WHITE)
    elif current_phase == GamePhase.CHARGE:
        target_text = font.render("Charge", True, WHITE)
    else:
        target_text = font.render("Fight", True, WHITE)
    WIN.blit(target_text, (target_button.x + 5, target_button.y + 5))

# Create units
friendly_units = [
    Unit(x * 50 + 50, y * 50 + 80, friendly_image, 6, 4, 3, 4, 2, 2, 5, 
         "Pulse Carbine", 20, 2, 5, 0, 2,
         "Honor Blade", 1, 4, 0, 1)
    for x,y in zip([0,1,2,1,0], [4,5,6,7,8])
]
enemy_units = [
    Unit(x * 50 + 50, y * 50 + 80, enemy_image, 5, 5, 4, 3, 3, 3, 4, 
         "Bolt Pistol", 8, 2, 4, 0, 1,
         "Chain-Axe", 3, 6, -1, 2)
    for x,y in zip([18,17,16,17,18], [4,5,6,7,8])
]
units = friendly_units + enemy_units

# Initiate Game Phase Variables
current_phase = GamePhase.COMMAND
dragged_unit = None
drag_offset_x = 0
drag_offset_y = 0
target_popup = False
engage = False
followup = False
target_button = pygame.Rect(0,0,0,0)

# UI elements
BUTTON_WIDTH, BUTTON_HEIGHT = 150, 30
button_rect = pygame.Rect(WIDTH - BUTTON_WIDTH - 5, 5, BUTTON_WIDTH, BUTTON_HEIGHT)
ui_rect = pygame.Rect(0, 0, WIDTH, 40)

# Define terrain pieces as L shapes using lists of rectangles
terrain = [
    [pygame.Rect(400, 105, 20, 225), pygame.Rect(200, 310, 200, 20)],  # Top-left L
    [pygame.Rect(600, 105, 20, 225), pygame.Rect(600, 310, 200, 20)],  # Top-right L
    [pygame.Rect(400, 425, 20, 225), pygame.Rect(200, 425, 200, 20)],  # Bottom-left L
    [pygame.Rect(600, 425, 20, 225), pygame.Rect(600, 425, 200, 20)]   # Bottom-right L
]

'''
GAME FUNCTIONS
'''

def draw_units():
    for unit in units:
        unit.draw()
        if unit.wounds_remaining != unit.wounds:
            text = pygame.font.SysFont(None, 18)
            wounds_text = text.render(f"{unit.wounds_remaining}/{unit.wounds}", True, BLACK)
            WIN.blit(wounds_text, (unit.x - wounds_text.get_width() // 2, unit.y + UNIT_RADIUS+2))

def draw_terrain():
    for piece in terrain:
        for rect in piece:
            pygame.draw.rect(WIN, TERRAIN_COLOR, rect)

def draw_uibar():
    # Draw Display bar
    pygame.draw.rect(WIN, DARK_GRAY, ui_rect)

    # Display current phase
    font = pygame.font.SysFont(None, 36)
    phase_text = font.render(current_phase.name, True, BLACK)
    WIN.blit(phase_text, (10, 10))

    # Draw UI button
    if button_rect.collidepoint(pygame.mouse.get_pos()):
        pygame.draw.rect(WIN, BUTTON_HOVER_COLOR, button_rect)
    else:
        pygame.draw.rect(WIN, BUTTON_COLOR, button_rect)
    button_text = font.render("Next Phase", True, WHITE)
    WIN.blit(button_text, (button_rect.x + 10, button_rect.y + 5))

def display_roll(WIN, hit_rolls, hits, wound_rolls, wounds, save_rolls, unsaved, damage):
    font = pygame.font.SysFont(None, 18)
    roll_text = font.render(f"Hit Rolls: {hit_rolls}, Hits: {hits}, Wound Rolls: {wound_rolls}, Wounds: {wounds}, Save Rolls: {save_rolls}, Unsaved: {unsaved}, Damage: {damage}", True, BLACK)
    WIN.blit(roll_text, (200, 15))

def draw_dashed_circle(surface, color, center, radius, width=1, dash_length=10):
    circumference = 2 * math.pi * radius
    dashes = int(circumference / dash_length)
    for i in range(dashes):
        start_angle = (i * dash_length) / radius
        end_angle = ((i + 0.5) * dash_length) / radius
        pygame.draw.arc(surface, color, (center[0] - radius, center[1] - radius, 2 * radius, 2 * radius), start_angle, end_angle, width)

def check_unit_collision(dragged_unit, new_x, new_y):
    for unit in units:
        if unit is not dragged_unit:
            dist = math.sqrt((unit.x - new_x)**2 + (unit.y - new_y)**2)
            if dist < 2 * UNIT_RADIUS:  # Detect collision if distance is less than the diameter
                return True
    return False

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
    global current_phase, dragged_unit, drag_offset_x, drag_offset_y, engage, followup

    event = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            # Handle click-through of roll results display
            if followup == True:
                followup = False

            # Handle the game phase progression button logic
            if button_rect.collidepoint(pos):
                current_phase = GamePhase((current_phase.value % 5) + 1)  # Cycle through phases
                for unit in units:
                    unit.selected = False
                    unit.targeted = False
                    unit.info = False
                return True
            
            # Handle shooting popup window logic is pressed
            if target_popup:
                if target_button.collidepoint(pos):
                    engage = True
                    return True

            clicked_unit = None
            for unit in units:
                dist = math.sqrt((unit.x - pos[0])**2 + (unit.y - pos[1])**2)
                if dist <= UNIT_RADIUS:
                    clicked_unit = unit
                    break

            if clicked_unit:
                if event.button == 1:  # Left-click for selection or dragging
                    # Deselect all other units and reset their info and targeting
                    for unit in units:
                        unit.selected = False
                        unit.info = False
                        unit.targeted = False

                    # Select the clicked unit if unit has not 
                    clicked_unit.selected = True
                    if current_phase == GamePhase.MOVEMENT and not clicked_unit.has_moved:
                        dragged_unit = clicked_unit
                        dragged_unit.start_x = clicked_unit.x
                        dragged_unit.start_y = clicked_unit.y
                        drag_offset_x = clicked_unit.x - pos[0]
                        drag_offset_y = clicked_unit.y - pos[1]
                    elif current_phase == GamePhase.SHOOTING and clicked_unit.has_shot:
                        clicked_unit.selected = False
                elif event.button == 3:  # Right-click for info or targeting
                    sel_unit = next((u for u in units if u.selected), None)
                    if current_phase == GamePhase.SHOOTING and sel_unit and clicked_unit in sel_unit.elig_tgts:
                        # Target this unit if it's within the eligible targets of the selected unit
                        for unit in units:
                            unit.targeted = False
                        clicked_unit.targeted = not clicked_unit.targeted
                    elif current_phase == GamePhase.CHARGE and sel_unit and clicked_unit in sel_unit.elig_tgts:
                        # Target this unit if it's within the eligible targets of the selected unit
                        for unit in units:
                            unit.targeted = False
                        clicked_unit.targeted = not clicked_unit.targeted
                    else:
                        for unit in units:
                            unit.info = False
                        clicked_unit.info = not clicked_unit.info
            else:
                # Click was not on any unit, reset all selections and info
                for unit in units:
                    unit.selected = False
                    unit.info = False
                    unit.targeted = False   

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
    return True, event if event else None


def command_phase():
    # reset move indicator
    for unit in units:
        unit.has_moved = False
        unit.has_shot = False
    
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
    global eligible_targets, target_popup, engage, followup, results

    for unit in units:
        eligible_targets = []
        # Draw popup window
        if unit.info:
            unit.draw_popup()

        # If selected draw range circle, and highlight eligible targets
        if unit.selected:
            center_x = unit.x
            center_y = unit.y
            radius = unit.eff_range * 20  # 50 is a scaling factor for movement
            draw_dashed_circle(WIN, HIGHLIGHT_COLOR, (center_x, center_y), radius)  # Draw range circle

            for target in units:
                dist = math.sqrt((unit.x - target.x) ** 2 + (unit.y - target.y) ** 2)  # Calculate distance between unit and all other targets
                if dist > 0 and dist <= unit.eff_range * 20:  # Ensure distance is greater than zero(itself) and less than max range
                    angle = math.atan2((target.y - unit.y), (target.x - unit.x))  # Calculate trajectory to target (note the order of arguments)

                    # Calculate left and right offset points from the unit
                    left_start_x, left_start_y = unit.x + UNIT_RADIUS * math.cos(angle + math.pi / 2), unit.y + UNIT_RADIUS * math.sin(angle + math.pi / 2)
                    left_end_x, left_end_y = target.x + UNIT_RADIUS * math.cos(angle + math.pi / 2), target.y + UNIT_RADIUS * math.sin(angle + math.pi / 2)
                    right_start_x, right_start_y = unit.x + UNIT_RADIUS * math.cos(angle - math.pi / 2), unit.y + UNIT_RADIUS * math.sin(angle - math.pi / 2)
                    right_end_x, right_end_y = target.x + UNIT_RADIUS * math.cos(angle - math.pi / 2), target.y + UNIT_RADIUS * math.sin(angle - math.pi / 2)

                    # Check for terrain intersection
                    left_blocked = any(line_intersects_rect((left_start_x, left_start_y), (left_end_x, left_end_y), rect) for piece in terrain for rect in piece)
                    right_blocked = any(line_intersects_rect((right_start_x, right_start_y), (right_end_x, right_end_y), rect) for piece in terrain for rect in piece)

                    if not left_blocked or not right_blocked:
                        # eligible target
                        pygame.draw.circle(WIN, RED, (target.x, target.y), UNIT_RADIUS + 3, 3)
                        eligible_targets.append(target)
                        unit.elig_tgts = eligible_targets

        # Draw shoot popup window if unit is targeted
        if unit.targeted:
            draw_target_popup(unit)

    # check if a shoot popup is up
    if sum(1 for u in units if u.targeted) == 1:
        target_popup = True
    else:
        target_popup = False

    # if shoot popup is clicked conduct engagement
    if engage == True:
        target_popup = False
        for u in units:
            if u.selected == True:
                shooter = u
            elif u.targeted == True:
                engaged = u

        results = shooter.shoot(engaged) #
        shooter.selected = False
        shooter.has_shot = True
        engaged.targeted = False
        engage = False
        followup = True

    # Display shooting roll results in UI Bar
    if followup == True:
        display_roll(results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7])
    

def charge_phase():
    global eligible_targets, target_popup, engage, followup, results
    
    # Draw popup window
    for unit in units:
        if unit.info:
            unit.draw_popup()

        if unit.selected:
            center_x = unit.x
            center_y = unit.y
            radius = 12 * 20  # 50 is a scaling factor for movement
            draw_dashed_circle(WIN, HIGHLIGHT_COLOR, (center_x, center_y), radius)

            for target in units:
                dist = math.sqrt((unit.x - target.x) ** 2 + (unit.y - target.y) ** 2)  # Calculate distance between unit and all other targets
                if dist > 0 and dist <= 12 * 20:  # Ensure distance is greater than zero(itself) and less than max range
                    angle = math.atan2((target.y - unit.y), (target.x - unit.x))  # Calculate trajectory to target (note the order of arguments)

                    # Calculate left and right offset points from the unit
                    left_start_x, left_start_y = unit.x + UNIT_RADIUS * math.cos(angle + math.pi / 2), unit.y + UNIT_RADIUS * math.sin(angle + math.pi / 2)
                    left_end_x, left_end_y = target.x + UNIT_RADIUS * math.cos(angle + math.pi / 2), target.y + UNIT_RADIUS * math.sin(angle + math.pi / 2)
                    right_start_x, right_start_y = unit.x + UNIT_RADIUS * math.cos(angle - math.pi / 2), unit.y + UNIT_RADIUS * math.sin(angle - math.pi / 2)
                    right_end_x, right_end_y = target.x + UNIT_RADIUS * math.cos(angle - math.pi / 2), target.y + UNIT_RADIUS * math.sin(angle - math.pi / 2)

                    # Check for terrain intersection
                    left_blocked = any(line_intersects_rect((left_start_x, left_start_y), (left_end_x, left_end_y), rect) for piece in terrain for rect in piece)
                    right_blocked = any(line_intersects_rect((right_start_x, right_start_y), (right_end_x, right_end_y), rect) for piece in terrain for rect in piece)

                    if not left_blocked or not right_blocked:
                        # eligible target
                        pygame.draw.circle(WIN, RED, (target.x, target.y), UNIT_RADIUS + 3, 3)
                        eligible_targets.append(target)
                        unit.elig_tgts = eligible_targets
        # Draw shoot popup window if unit is targeted
        if unit.targeted:
            draw_target_popup(unit)

    # check if a shoot popup is up
    if sum(1 for u in units if u.targeted) == 1:
        target_popup = True
    else:
        target_popup = False

    # if shoot popup is clicked conduct engagement
    if engage == True:
        target_popup = False
        for u in units:
            if u.selected == True:
                charger = u
            elif u.targeted == True:
                charged = u

        results = charger.charge(charged) #
        charger.selected = False
        charger.has_shot = True
        charged.targeted = False
        engage = False
        followup = True

    # Display shooting roll results in UI Bar
    if followup == True:
        display_charge(results[0], results[2], results[3], results[4])

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
