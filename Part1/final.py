import random, time, re, os

# Function to validate student ID format (A followed by 5 digits 1-9, no leading zero)
def validate_id(student_id):
    """Validate the student ID format.
    
    Args:
        student_id (str): The student ID to validate.
    
    Returns:
        bool: True if the ID is valid, False otherwise.
    """
    return bool(re.match(r'^A[1-9][0-9]{4}$', student_id))

# Function to load and shuffle questions from a test bank file
def load_questions(filename, num_questions=10):
    """Load questions from a file and return a shuffled list of questions.
    
    Args:
        filename (str): filename name.
        num_questions (int): set 10 parameter as basic
        
    Returns:
        questions array with length of num_questions parameter"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            questions = []
            for line in file:
                parts = line.strip().rsplit('|', 1)  # Split only at the last '|'
                if len(parts) == 2:
                    question_text, correct_answer = parts
                    questions.append((question_text, correct_answer))
        random.shuffle(questions)
        return questions[:num_questions]
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []

# Function to save quiz results in a file
def save_results(student_id, first_name, last_name, score, elapsed_time, answers):
    """Saves the quiz results to a file.
    
    Args:
        student_id (str): The student's ID.
        first_name (str): The student's first name.
        last_name (str): The student's last name.
        score (float): The student's score.
        elapsed_time (float): The time taken to complete the quiz.
        answers (list): A list of tuples containing the question, correct answer, and student's answer.
    """
    filename = f"{student_id}_{first_name}_{last_name}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(f"ID: {student_id}\nName: {first_name} {last_name}\nScore: {score}\nTime: {elapsed_time:.2f}s\n\n")
        for q, c, u in answers:
            file.write(f"Q: {q}\nCorrect: {c}\nYour Answer: {u}\n\n")

# Function to conduct the quiz
def start_quiz(student_id, first_name, last_name, num_questions=10):
    """Start the quiz for the student.
    
    Args:
        student_id (str): The student's ID.
        first_name (str): The student's first name.
        last_name (str): The student's last name.
        num_questions (int): The number of questions in the quiz (10 or 20).
    """
    # Get the directory where the script is located
    script_dir = os.getcwd()  # Gets current working directory FIXED
    testbank_path = os.path.join(script_dir, "testbank.txt")

    questions = load_questions(testbank_path, num_questions)
    if not questions:
        print("No questions loaded. Exiting.")
        return

    score, start_time, answers = 0, time.time(), []
    time_limit = 600  # 10 minutes in seconds

    for i, (question_text, correct_answer) in enumerate(questions, 1):
        if time.time() - start_time > time_limit:
            print("Time's up!")
            break

        parts = question_text.split('|')  # Split question and choices
        print(f"Q{i}: {parts[0]}")  # Print the question text
        for choice in parts[1:]:  # Print answer choices
            print(choice)

        while (user_answer := input("Your answer: ").strip().upper()) not in ['A', 'B', 'C', 'D']:
            print("Invalid input, enter A, B, C, or D.")

        answers.append((parts[0], correct_answer, user_answer))  # Store (question, correct, user answer)
        if user_answer == correct_answer:
            score += 1 if num_questions == 10 else 0.5  # Adjust score based on number of questions

    elapsed_time = time.time() - start_time
    save_results(student_id, first_name, last_name, score, elapsed_time, answers)
    print(f"Quiz Complete! Score: {score}/{num_questions}")

# Main function to handle user input and start the quiz
def main():
    """Main function to run the quiz program."""
    first_name, last_name = input("First name: "), input("Last name: ")
    
    for _ in range(3):  # Allow 3 attempts for a valid ID
        student_id = input("Enter ID (A12345): ").strip()
        if validate_id(student_id):
            break
        print("Invalid ID format. Try again.")
    else:
        return print("Too many failed attempts. Exiting.")

    num_questions = int(input("Enter number of questions (10 or 20): "))
    if num_questions not in [10, 20]:
        print("Invalid choice. Defaulting to 10 questions.")
        num_questions = 10

    start_quiz(student_id, first_name, last_name, num_questions)

    if input("Q to quit, S to restart: ").strip().upper() == 'S':
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen
        main()

# Run the program
if __name__ == "__main__":
    main()