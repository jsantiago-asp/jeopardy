# Dec 10 2024 - jsantiago@asparis.fr
# AP CSP Semester 1 Jeopardy Exam Review (V1)
# In Thonny make sure that you have the pygame module installed
# For some more background on pygame: https://realpython.com/pygame-a-primer/
# We will look at pygame more next semester and some of you may use it for the CPT

import pygame  # Abstraction: Pygame is a library that simplifies game development.
import sys     # Used for system-level operations, like quitting the program.

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 800  # Variables: Storing screen dimensions as constants for reusability.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Output: Creates the game window.
pygame.display.set_caption("Jeopardy Game")  # Metadata for the game window.

# Colors (Using variables to avoid hardcoding and improve reusability.)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (200, 200, 200)

# Fonts (Abstraction: Using Pygame's font module to avoid manually designing fonts.)
FONT = pygame.font.Font(None, 36)  # Medium font
LARGE_FONT = pygame.font.Font(None, 48)  # Large font

# Load Sound (Abstraction: Pygame's `mixer` handles audio for us.)
pygame.mixer.init()
jeopardy_theme = pygame.mixer.Sound("jeopardy.mp3")  # Input/Output: Loading an external resource.

# Game Data (Lists and Dictionaries: Data abstraction to organize questions and categories.)
categories = ["Algorithms", "Debugging", "Logic", "Data"]
questions = {
    "Algorithms": [
        ("A way of breaking a complex problem into smaller, more manageable parts.", "What is decomposition?"),
        ("A repeatable sequence of steps to solve a problem.", "What is an algorithm?"),
        ("A loop that continues while a condition is true.", "What is a while loop?"),
        ("A method to find the largest or smallest element in a list of numbers.", "What is selection?")
    ],
    "Debugging": [
        ("An error in the structure of code, similar to a grammar mistake in a sentence, that prevents the program from running.", "What is a syntax error?"),
        ("An error that occurs during program execution.", "What is a runtime error?"),
        ("An error in the program's logic that produces incorrect results, even though the code runs without crashing.", "What is a logical error?"),
        ("A common debugging method where you follow the program’s flow line by line.", "What is step-through debugging?")
    ],
    "Logic": [
        ("A logical operator where both conditions must be true.", "What is AND?"),
        ("A logical operator that reverses a condition.", "What is NOT?"),
        ("A table that shows all possible outcomes of logical expressions.", "What is a truth table?"),
        ("A system of logic using true and false values for decision-making.", "What is boolean logic?")
    ],
    "Data": [
        ("A data structure used to store multiple values in a single variable, typically defined with square brackets.", "What is a list?"),
        ("A numbering system that uses only 0s and 1s.", "What is binary?"),
        ("A method to represent colors with three numbers (0–255).", "What is RGB?"),
        ("A structure to store key-value pairs.", "What is a dictionary?")
    ]
}
point_values = [100, 200, 300, 400]  # Sequencing: Values increase with difficulty.

# Game State (Variables: Track the state of the game.)
selected_question = None
current_description = None
current_response = None
feedback_phase = False  # Boolean: Helps determine the current phase of the game.
team_selection_phase = False
selected_team = None
team_scores = [0, 0, 0, 0]  # List: Storing scores for four teams.

def draw_text_wrapped(surface, text, font, color, x, y, max_width):
    """Display text with line wrapping. (Algorithms: Implements a text-wrapping algorithm.)"""
    if not text:  # Guard clause to avoid errors.
        return
    words = text.split(' ')  # Abstraction: Splitting text into words for wrapping.
    lines = []
    current_line = []
    current_width = 0

    for word in words:  # Iteration: Loop through words.
        word_width, _ = font.size(word + ' ')
        if current_width + word_width > max_width:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width
    lines.append(' '.join(current_line))  # Add the last line.

    for i, line in enumerate(lines):  # Iteration: Display each line.
        line_surface = font.render(line, True, color)
        surface.blit(line_surface, (x, y + i * font.get_linesize()))

def draw_board():
    """Draw the main game board with categories, questions, and team scores."""
    screen.fill(BLUE)  # Abstraction: Simplified screen rendering.

    # Draw categories (Data: Accessing `categories` list.)
    for i, category in enumerate(categories):  # Iteration: Loop through categories.
        text = FONT.render(category, True, YELLOW)
        screen.blit(text, (i * (SCREEN_WIDTH // len(categories)) + 50, 80))

    # Draw question buttons (Selection: Only render unanswered questions.)
    buttons = []
    for i, category in enumerate(categories):  # Nested loops for categories and points.
        for j, points in enumerate(point_values):
            question_text, _ = questions[category][j]
            if question_text is not None:
                rect = pygame.Rect(i * (SCREEN_WIDTH // len(categories)) + 50, j * 100 + 150, 120, 50)
                pygame.draw.rect(screen, WHITE, rect)
                text = FONT.render(str(points), True, BLACK)
                screen.blit(text, (rect.x + 30, rect.y + 10))
                buttons.append((category, points, rect))

    # Draw team scores (Iteration and list indexing.)
    for i in range(4):
        score_rect = pygame.Rect(50 + i * 280, SCREEN_HEIGHT - 100, 200, 50)
        pygame.draw.rect(screen, GRAY, score_rect)
        team_text = FONT.render(f"Team {i + 1}:", True, BLACK)
        screen.blit(team_text, (score_rect.x + 10, score_rect.y + 10))
        score_text = FONT.render(f"{team_scores[i]}", True, BLACK)
        screen.blit(score_text, (score_rect.x + 120, score_rect.y + 10))

    return buttons  # Return data to use elsewhere.

def draw_feedback():
    """Display either the question description or correct response."""
    global feedback_phase
    screen.fill(BLACK)
    if feedback_phase:
        draw_text_wrapped(screen, current_response, LARGE_FONT, YELLOW, 50, SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH - 100)
    else:
        draw_text_wrapped(screen, current_description, LARGE_FONT, WHITE, 50, SCREEN_HEIGHT // 2 - 100, SCREEN_WIDTH - 100)

# Main game loop
def main():
    global selected_question, current_description, current_response, feedback_phase, team_selection_phase, selected_team, team_scores
    running = True
    clock = pygame.time.Clock()

    while running:
        if team_selection_phase:  # State management using Booleans.
            pass  # Handle team selection here.
        else:
            buttons = draw_board()
            if selected_question:
                draw_feedback()

        for event in pygame.event.get():  # Event-driven programming.
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass  # Handle mouse clicks.

        pygame.display.flip()  # Refresh the screen.
        clock.tick(30)  # Control the frame rate.

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
