"""
Menu system for the game including main menu and level select.
"""

import pygame
import json
import os

class Button:
    """A clickable button for menus."""
    
    def __init__(self, x, y, width, height, text, font, 
                 color=(100, 100, 100), hover_color=(150, 150, 150), 
                 text_color=(255, 255, 255)):
        """Initialize a button."""
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
    
    def update(self, mouse_pos):
        """Update button hover state."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def draw(self, screen):
        """Draw the button."""
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)  # White border
        
        # Draw text centered on button
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def is_clicked(self, mouse_pos, mouse_clicked):
        """Check if button was clicked."""
        return self.is_hovered and mouse_clicked


class MainMenu:
    """Main menu screen with Play and Quit buttons."""
    
    def __init__(self, screen_width, screen_height):
        """Initialize the main menu."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Load title image
        self.title_image = None
        try:
            self.title_image = pygame.image.load("assets/Title.png").convert_alpha()
            # Scale title image to fill screen
            title_width = int(self.screen_width)
            title_height = int(self.title_image.get_height() * (title_width / self.title_image.get_width()) * 1.1)
            
            self.title_image = pygame.transform.scale(self.title_image, (title_width, title_height))
        except:
            print("Warning: Could not load title image")
        
        # Create font
        self.font = pygame.font.Font(None, 48)
        
        # Create buttons
        button_width = 300
        button_height = 70
        button_x = (screen_width - button_width) // 2
        
        self.play_button = Button(
            button_x, 
            screen_height // 2 + 50,
            button_width, 
            button_height,
            "PLAY",
            self.font,
            color=(50, 150, 50),
            hover_color=(80, 200, 80)
        )
        
        self.quit_button = Button(
            button_x,
            screen_height // 2 + 150,
            button_width,
            button_height,
            "QUIT",
            self.font,
            color=(150, 50, 50),
            hover_color=(200, 80, 80)
        )
    
    def handle_events(self, event):
        """Handle menu events. Returns action string or None."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.play_button.is_clicked(mouse_pos, True):
                return "level_select"
            elif self.quit_button.is_clicked(mouse_pos, True):
                return "quit"
        
        return None
    
    def update(self):
        """Update menu state."""
        mouse_pos = pygame.mouse.get_pos()
        self.play_button.update(mouse_pos)
        self.quit_button.update(mouse_pos)
    
    def draw(self, screen):
        """Draw the main menu."""
        # Background
        screen.fill((20, 20, 40))  # Dark blue background
        
        # Draw title image if available
        if self.title_image:
            title_x = (self.screen_width - self.title_image.get_width()) // 2
            title_y = 0
            screen.blit(self.title_image, (title_x, title_y))
        else:
            # Fallback text title
            title_text = self.font.render("ECHOES OF LYRA", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
            screen.blit(title_text, title_rect)
        
        # Draw buttons
        self.play_button.draw(screen)
        self.quit_button.draw(screen)


class LevelSelect:
    """Level select screen where players choose which level to play."""
    
    def __init__(self, screen_width, screen_height):
        """Initialize the level select screen."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create fonts
        self.title_font = pygame.font.Font(None, 64)
        self.button_font = pygame.font.Font(None, 40)
        self.info_font = pygame.font.Font(None, 28)
        
        # Dynamically discover levels from the levels folder
        self.levels = self.discover_levels()
        
        # Load progress
        self.load_progress()
        
        # Create level buttons
        self.create_level_buttons()
        
        # Back button
        self.back_button = Button(
            50,
            screen_height - 100,
            200,
            60,
            "BACK",
            self.button_font,
            color=(100, 100, 100),
            hover_color=(150, 150, 150)
        )
        
        # Reset progress button
        self.reset_button = Button(
            screen_width - 250,
            screen_height - 100,
            200,
            60,
            "RESET",
            self.button_font,
            color=(150, 50, 50),
            hover_color=(200, 80, 80)
        )
        
        # Confirmation dialog state
        self.show_confirmation = False
        self.confirm_yes_button = None
        self.confirm_no_button = None
        self.create_confirmation_buttons()
    
    def create_confirmation_buttons(self):
        """Create confirmation dialog buttons."""
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        button_width = 150
        button_height = 50
        button_y = dialog_y + dialog_height - 70
        
        self.confirm_yes_button = Button(
            dialog_x + 50,
            button_y,
            button_width,
            button_height,
            "YES",
            self.button_font,
            color=(150, 50, 50),
            hover_color=(200, 80, 80)
        )
        
        self.confirm_no_button = Button(
            dialog_x + dialog_width - button_width - 50,
            button_y,
            button_width,
            button_height,
            "NO",
            self.button_font,
            color=(50, 150, 50),
            hover_color=(80, 200, 80)
        )
    
    def discover_levels(self):
        """Dynamically discover all level CSV files in the levels folder."""
        levels = []
        levels_dir = "levels"
        
        try:
            # Check if levels directory exists
            if not os.path.exists(levels_dir):
                print(f"Warning: '{levels_dir}' directory not found")
                return [{"name": "Level 1", "file": "levels/level1.csv", "unlocked": True}]
            
            # Get all CSV files in the levels directory
            csv_files = sorted([f for f in os.listdir(levels_dir) if f.endswith('.csv')])
            
            if not csv_files:
                print(f"Warning: No CSV files found in '{levels_dir}'")
                return [{"name": "Level 1", "file": "levels/level1.csv", "unlocked": True}]
            
            # Create level entries for each CSV file
            for i, filename in enumerate(csv_files):
                # Extract level number or name from filename
                level_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                
                # Try to extract number from filename for better naming
                import re
                match = re.search(r'\d+', filename)
                if match:
                    level_num = match.group()
                    level_name = f"Level {level_num}"
                
                levels.append({
                    "name": level_name,
                    "file": f"{levels_dir}/{filename}",
                    "unlocked": i == 0  # Only first level unlocked by default
                })
            
            print(f"Discovered {len(levels)} levels: {[l['name'] for l in levels]}")
            
        except Exception as e:
            print(f"Error discovering levels: {e}")
            # Fallback to default level
            return [{"name": "Level 1", "file": "levels/level1.csv", "unlocked": True}]
        
        return levels
    
    def create_level_buttons(self):
        """Create buttons for all discovered levels."""
        self.level_buttons = []
        button_width = 250
        button_height = 80
        
        # Calculate spacing and positioning based on number of levels
        num_levels = len(self.levels)
        
        # Adjust spacing if there are many levels
        if num_levels <= 3:
            spacing = 120
            start_y = 200
        elif num_levels <= 5:
            spacing = 100
            start_y = 180
        else:
            # For many levels, use smaller spacing and arrange in columns
            spacing = 90
            start_y = 150
        
        for i, level in enumerate(self.levels):
            # For more than 6 levels, arrange in two columns
            if num_levels > 6:
                col = i % 2
                row = i // 2
                button_x = (self.screen_width // 2 - button_width - 20) if col == 0 else (self.screen_width // 2 + 20)
                button_y = start_y + row * spacing
            else:
                # Single column for 6 or fewer levels
                button_x = (self.screen_width - button_width) // 2
                button_y = start_y + i * spacing
            
            # Different colors for locked/unlocked levels
            if level["unlocked"]:
                color = (50, 100, 150)
                hover_color = (80, 130, 200)
            else:
                color = (70, 70, 70)
                hover_color = (90, 90, 90)
            
            button = Button(
                button_x,
                button_y,
                button_width,
                button_height,
                level["name"],
                self.button_font,
                color=color,
                hover_color=hover_color
            )
            self.level_buttons.append(button)
    
    def load_progress(self):
        """Load level progress from file."""
        try:
            if os.path.exists("progress.json"):
                with open("progress.json", "r") as f:
                    data = json.load(f)
                    completed = data.get("completed_levels", [])
                    
                    # Unlock levels based on completion
                    for i, level in enumerate(self.levels):
                        if i == 0:
                            level["unlocked"] = True
                        elif i - 1 in completed:
                            level["unlocked"] = True
        except Exception as e:
            print(f"Could not load progress: {e}")
    
    def save_progress(self, level_index):
        """Save that a level has been completed."""
        try:
            data = {"completed_levels": []}
            
            if os.path.exists("progress.json"):
                with open("progress.json", "r") as f:
                    data = json.load(f)
            
            if level_index not in data["completed_levels"]:
                data["completed_levels"].append(level_index)
            
            with open("progress.json", "w") as f:
                json.dump(data, f)
            
            # Unlock next level
            if level_index + 1 < len(self.levels):
                self.levels[level_index + 1]["unlocked"] = True
                
        except Exception as e:
            print(f"Could not save progress: {e}")
    
    def reset_progress(self):
        """Reset all progress - lock all levels except level 1."""
        try:
            # Reset progress file
            data = {"completed_levels": []}
            with open("progress.json", "w") as f:
                json.dump(data, f)
            
            # Lock all levels except the first one
            for i, level in enumerate(self.levels):
                if i == 0:
                    level["unlocked"] = True
                else:
                    level["unlocked"] = False
            
            # Update button colors
            for i, button in enumerate(self.level_buttons):
                if self.levels[i]["unlocked"]:
                    button.color = (50, 100, 150)
                    button.hover_color = (80, 130, 200)
                else:
                    button.color = (70, 70, 70)
                    button.hover_color = (90, 90, 90)
            
            print("Progress reset successfully")
        except Exception as e:
            print(f"Could not reset progress: {e}")
    
    def handle_events(self, event):
        """Handle level select events. Returns ('play', level_file) or action string."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            # If confirmation dialog is showing, only handle those buttons
            if self.show_confirmation:
                if self.confirm_yes_button.is_clicked(mouse_pos, True):
                    self.reset_progress()
                    self.show_confirmation = False
                elif self.confirm_no_button.is_clicked(mouse_pos, True):
                    self.show_confirmation = False
                return None
            
            # Check level buttons
            for i, button in enumerate(self.level_buttons):
                if button.is_clicked(mouse_pos, True) and self.levels[i]["unlocked"]:
                    return ("play", i, self.levels[i]["file"])
            
            # Check back button
            if self.back_button.is_clicked(mouse_pos, True):
                return "main_menu"
            
            # Check reset button
            if self.reset_button.is_clicked(mouse_pos, True):
                self.show_confirmation = True
        
        return None
    
    def update(self):
        """Update level select state."""
        # Reload progress to check for any changes
        previous_progress = [level["unlocked"] for level in self.levels]
        self.load_progress()
        current_progress = [level["unlocked"] for level in self.levels]
        
        # If progress changed, recreate buttons with new colors
        if previous_progress != current_progress:
            self.create_level_buttons()
        
        mouse_pos = pygame.mouse.get_pos()
        
        if self.show_confirmation:
            # Only update confirmation buttons when dialog is showing
            self.confirm_yes_button.update(mouse_pos)
            self.confirm_no_button.update(mouse_pos)
        else:
            # Update normal buttons
            for button in self.level_buttons:
                button.update(mouse_pos)
            
            self.back_button.update(mouse_pos)
            self.reset_button.update(mouse_pos)
    
    def draw(self, screen):
        """Draw the level select screen."""
        # Background
        screen.fill((20, 30, 50))  # Dark blue-gray background
        
        # Title
        title_text = self.title_font.render("SELECT LEVEL", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw level buttons with lock indicators
        for i, button in enumerate(self.level_buttons):
            button.draw(screen)
            
            # Draw lock icon for locked levels
            if not self.levels[i]["unlocked"]:
                lock_text = self.info_font.render("LOCKED", True, (200, 200, 0))
                lock_rect = lock_text.get_rect(center=(button.rect.centerx, button.rect.centery + 47))
                screen.blit(lock_text, lock_rect)
        
        # Draw back button
        self.back_button.draw(screen)
        
        # Draw reset button
        self.reset_button.draw(screen)
        
        # Instructions
        info_text = self.info_font.render("Complete levels to unlock the next!", True, (200, 200, 200))
        info_rect = info_text.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        screen.blit(info_text, info_rect)
        
        # Draw confirmation dialog if showing
        if self.show_confirmation:
            self.draw_confirmation_dialog(screen)
    
    def draw_confirmation_dialog(self, screen):
        """Draw the reset confirmation dialog."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Dialog box
        dialog_width = 400
        dialog_height = 200
        dialog_x = (self.screen_width - dialog_width) // 2
        dialog_y = (self.screen_height - dialog_height) // 2
        
        pygame.draw.rect(screen, (40, 40, 60), (dialog_x, dialog_y, dialog_width, dialog_height))
        pygame.draw.rect(screen, (255, 255, 255), (dialog_x, dialog_y, dialog_width, dialog_height), 3)
        
        # Warning text
        warning_text = self.button_font.render("Reset Progress?", True, (255, 200, 0))
        warning_rect = warning_text.get_rect(center=(self.screen_width // 2, dialog_y + 50))
        screen.blit(warning_text, warning_rect)
        
        # Confirmation text
        confirm_text = self.info_font.render("All progress will be lost!", True, (255, 255, 255))
        confirm_rect = confirm_text.get_rect(center=(self.screen_width // 2, dialog_y + 90))
        screen.blit(confirm_text, confirm_rect)
        
        # Draw buttons
        self.confirm_yes_button.draw(screen)
        self.confirm_no_button.draw(screen)
