def pressed_esc():
    if deb:
        print("pressed escape")
    running = False

def pressed_q():
    if deb:
        print("pressed q")
    display_allowed = True

def pressed_t():
    if deb:
        print("pressed t")
    reset_buzzer()
    buzzer_playable = True

def pressed_r():
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

def pressed_e():
    if deb:
        print("pressed e")
    # Increment strikes
    if strikes < 3:
        strikes += 1
    play_sound_thread("strike")

def pressed_w():
    if deb:
        print("pressed w")
    # Reset strikes
    strikes = 0

def pressed_y():
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

def pressed_a():
    if deb:
        print("pressed a")
    play_sound_thread("correct")

def pressed_i():
    if deb:
        print("pressed i")
    play_sound_thread("intro")

def pressed_o():
    if deb:
        print("pressed o")
    if play_noises:
        play_noises = False
    else:
        play_noises = True
    print(f"play_noises {play_noises}")

def pressed_p():
    if deb:
        print("pressed p")
        deb = False
    else:
        deb = True