import pygame
import sys
import pyttsx3
import threading
from flask_server import start_flask, reset_buzzer  # Import Flask utilities
from playsound import playsound
import time
from game_state import get_current_question_data, reset_game, load_questions_from_file

deb = False #print debugging stuff
buzzer_playable = True #keeps it from playing over and over
play_noises = True #toggle for sound effects

# Initialize pygame
pygame.init()
# Initialize pygame mixer
pygame.mixer.init()

# Initialize pyttsx3
engine = pyttsx3.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (169, 169, 169)

# Fonts
FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font(None, 30)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Family Feud")

# Initialize global variable for buzzer
player_buzzed = None

#sound effects dictionary
sound_effects = {
    "intro": "C:\\Users\\053nd\\Documents\\python\\Youth\\Family Fued type questions\\Introduction Casey_mixdown_01.mp3",
    "buzzed_in": "C:\\Users\\053nd\\Documents\\python\\Youth\\Family Fued type questions\\buzzed-in.mp3",
    "correct": "C:\\Users\\053nd\\Documents\\python\\Youth\\Family Fued type questions\\correct.mp3",
    "strike": "C:\\Users\\053nd\\Documents\\python\\Youth\\Family Fued type questions\\correct.mp3"
}

#Tells it what to do when asked to play a sound
def play_sound(sound_name):
    if deb:
        print(f"PLAYING {sound_name} !!!!!!!!!!!!!!!!!!!!!")
    if play_noises:
        playsound(sound_effects.get(sound_name))

#asks to play a sound, used for performance and so the sound effects don't make the program freeze while playing
def play_sound_thread(sound_name):
    sound_thread = threading.Thread(target=play_sound, args=(sound_name,), daemon=True)
    sound_thread.start()

def draw_text_with_shadow(text, font, color, shadow_color, x, y):
    """Renders text with a shadow."""
    shadow = font.render(text, True, shadow_color)
    screen.blit(shadow, (x + 2, y + 2))  # Offset for shadow
    rendered_text = font.render(text, True, color)
    screen.blit(rendered_text, (x, y))

def wrap_text(text, font, max_width):
    """Wraps text to fit within a maximum width."""
    words = text.split()
    lines = []
    current_line = []
    current_width = 0

    for word in words:
        word_width, _ = font.size(word + " ")
        if current_width + word_width > max_width:
            lines.append(" ".join(current_line))
            current_line = [word]
            current_width = word_width
        else:
            current_line.append(word)
            current_width += word_width

    if current_line:
        lines.append(" ".join(current_line))

    return lines

def draw_board(question, answers, revealed, scores, strikes, show_question):#, sounds):
    """Draws the Family Feud game board with a question and two columns."""
    global player_buzzed

    screen.fill(BLUE)

    # Draw the strikes at the top
    strike_x_start = (SCREEN_WIDTH - (3 * 60)) // 2
    strike_y = 20
    for i in range(3):
        color = RED if i < strikes else GRAY
        strike_text = "X"
        text_surface = FONT.render(strike_text, True, color)
        text_x = strike_x_start + i * 70
        screen.blit(text_surface, (text_x, strike_y))

    # Move everything else down
    question_y = strike_y + 70

    # Draw the question below the strikes only if show_question is True
    if show_question:
        question_lines = wrap_text(question, FONT, SCREEN_WIDTH - 40)
        for line in question_lines:
            question_x = (SCREEN_WIDTH - FONT.size(line)[0]) // 2
            draw_text_with_shadow(line, FONT, WHITE, BLACK, question_x, question_y)
            question_y += FONT.get_height() + 5

    # Determine layout
    column_width = SCREEN_WIDTH // 2 - 20
    max_answers = 8
    y_offset = question_y + 20  # Space below the question

    current_y_positions = [y_offset, y_offset]  # Tracks vertical position for each column

    for i in range(min(len(answers), max_answers)):
        column = i % 2

        if revealed[i]:
            text = f"{i + 1}. {answers[i].upper()} ({scores[i]})"
        else:
            text = f"{i + 1}. {'_' * 10}"

        wrapped_lines = wrap_text(text, FONT, column_width)
        row_height = (len(wrapped_lines) + 1) * FONT.get_height()  # Account for wrapped lines

        for line_index, wrapped_line in enumerate(wrapped_lines):
            answer_text = FONT.render(wrapped_line, True, WHITE)
            text_x = column * (SCREEN_WIDTH // 2) + 10
            text_y = current_y_positions[column]
            draw_text_with_shadow(wrapped_line, FONT, WHITE, BLACK, text_x, text_y)
            current_y_positions[column] += FONT.get_height()  # Move down for each wrapped line

        current_y_positions[column] += FONT.get_height()  # Extra space between answers

    # Draw who buzzed
    if player_buzzed:
        global buzzer_playable
        if buzzer_playable:
            play_sound_thread("buzzed_in")
            buzzer_playable = False
            time.sleep(.5)
        buzzed_text = f"{player_buzzed} buzzed in!"
        buzzed_text_width = FONT.size(buzzed_text)[0]
        buzzed_text_x = (SCREEN_WIDTH - buzzed_text_width) // 2
        buzzed_text_y = SCREEN_HEIGHT - 50
        draw_text_with_shadow(buzzed_text, FONT, WHITE, BLACK, buzzed_text_x, buzzed_text_y)
    pygame.display.flip()

def update_buzzer_status():
    """Updates the buzzer status by fetching from Flask."""
    global player_buzzed
    from flask_server import player_buzzed as buzzed_status
    player_buzzed = buzzed_status

def main():
    """Main function to run the Family Feud game board."""

    global buzzer_playable
    global play_noises
    global deb

    # Load questions
    questions_file = "questions.txt"  # Ensure this file path is correct
    load_questions_from_file(questions_file)

    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    print("Starting Flask server...")  # Debugging statement
    flask_thread.start()

    question_data = get_current_question_data()
    print(f"Loaded question data: {question_data}")  # Debugging statement
    if not question_data:
        print("No valid questions loaded. Exiting game.")
        pygame.quit()
        sys.exit()

    question = question_data["question"]
    answers = question_data["answers"]
    scores = question_data["scores"]
    revealed = question_data["revealed"]
    strikes = question_data["strikes"]

    show_question = False  # Question visibility flag
    display_allowed = True

    running = True
    while running:
        update_buzzer_status()
        if display_allowed:
            draw_board(question, answers, revealed, scores, strikes, show_question)

        for event in pygame.event.get():
            if deb:
                print(f"Event Processed: {event}")  # Debugging statement
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if deb:
                        print("pressed escape")
                    running = False
                elif event.key == pygame.K_q:
                    if deb:
                        print("pressed q")
                    display_allowed = True  # Allow the screen to be displayed
                elif event.key == pygame.K_t:
                    if deb:
                        print("pressed t")
                    reset_buzzer()
                    buzzer_playable = True
                elif event.key == pygame.K_r:
                    if deb:
                        print("pressed r")
                    reset_game()
                    question_data = get_current_question_data()
                    if question_data:
                        question = question_data["question"]
                        answers = question_data["answers"]
                        scores = question_data["scores"]
                        revealed = question_data["revealed"]
                        strikes = question_data["strikes"]
                        show_question = False
                        print("Game reset to the next question.")
                    else:
                        print("No more questions available.")
                elif event.key == pygame.K_e:
                    if deb:
                        print("pressed e")
                    # Increment strikes
                    if strikes < 3:
                        strikes += 1
                    play_sound_thread("strike")
                elif event.key == pygame.K_w:
                    if deb:
                        print("pressed w")
                    # Reset strikes
                    strikes = 0
                elif event.key == pygame.K_y:
                    if deb:
                        print("pressed y")
                    # Show the question and use pyttsx3 to speak it
                    show_question = True
                    engine.say("We asked ChatGPT")
                    engine.say(question)
                    engine.runAndWait()
                    # Print answers in one line with their numbers
                    answers_line = ", ".join(f"{i}. {answer}" for i, answer in enumerate(answers, start=1))
                    print(f"Current Answers: {answers_line}")
                elif event.key == pygame.K_a:
                    if deb:
                        print("pressed a")
                    play_sound_thread("correct")
                elif event.key == pygame.K_i:
                    if deb:
                        print("pressed i")
                    play_sound_thread("intro")
                elif event.key == pygame.K_o:
                    if deb:
                        print("pressed o")
                    if play_noises:
                        play_noises = False
                    else:
                        play_noises = True
                    print(f"play_noises {play_noises}")
                elif event.key == pygame.K_p:
                    if deb:
                        print("pressed p")
                        deb = False
                    else:
                        deb = True
                else:
                    # Reveal answers based on number keys
                    try:
                        key_number = int(event.unicode)
                        if 1 <= key_number <= len(answers):
                            revealed[key_number - 1] = True
                            play_sound_thread("correct")
                    except ValueError:
                        pass

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
