questions = []
current_question_index = 0
revealed = []
strikes = 0

def load_questions_from_file(filename):
    global questions
    questions = []
    try:
        print(f"Attempting to load questions from: {filename}")  # Debugging
        with open(filename, 'r', encoding='utf-8') as file:
            current_question = None
            answers = []
            scores = []
            for line in file:
                line = line.strip()
                print(f"Processing line: {line}")  # Debugging
                if line.startswith("Question "):
                    if current_question is not None:
                        questions.append((current_question, answers, scores))
                        print(f"Added question: {current_question}")  # Debugging
                    current_question = line.split(":", 1)[1].strip()
                    answers = []
                    scores = []
                elif ";" in line:
                    parts = line.split(";")
                    if len(parts) == 2:
                        answer = parts[0].strip()
                        try:
                            score = int(parts[1].strip())
                            answers.append(answer)
                            scores.append(score)
                        except ValueError:
                            print(f"Invalid score format: {line}")
            if current_question is not None:
                questions.append((current_question, answers, scores))
                print(f"Final question added: {current_question}")  # Debugging
        print(f"Questions loaded successfully: {questions}")  # Debugging
    except FileNotFoundError:
        print(f"Error: File {filename} not found.")

def get_current_question_data():
    global current_question_index, questions
    print(f"Accessing questions: {questions}")  # Debugging
    if not questions:
        print("No questions available!")  # Debugging
        return {
            "question": "No questions available",
            "answers": [],
            "scores": [],
            "revealed": [],
            "strikes": 0,
        }
    if current_question_index < len(questions):
        question, answers, scores = questions[current_question_index]
        return {
            "question": question,
            "answers": answers,
            "scores": scores,
            "revealed": [False] * len(answers),
            "strikes": 0,
        }
    print("No more questions available!")  # Debugging
    return None



def reset_game():
    """Resets the game state for a new round."""
    global current_question_index, revealed, strikes
    if current_question_index < len(questions):
        question, answers, _ = questions[current_question_index]
        revealed = [False] * len(answers)
        strikes = 0
