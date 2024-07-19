import prompt

DEFAULT_ROUNDS = 3


def welcome_user():
    print('Welcome to the Brain games!')
    name = prompt.string('May I have your name? ')
    print(f'Hello, {name}!')
    return name


def play(game):
    name = welcome_user()
    print(game.TASK)
    game_rounds = DEFAULT_ROUNDS
    while game_rounds:
        question = game.generate_question()
        game.ask_question(question)
        user_answer = prompt.string('Your answer: ')
        correct_answer = game.solve(question)
        if correct_answer == user_answer:
            print('Correct!')
            game_rounds -= 1
        else:
            print(f"'{user_answer}' is wrong answer ;(. \
Correct answer was '{correct_answer}'.")
            print(f'Let\'s try again, {name}!')
            break
    if not game_rounds:
        print(f'Congratulations, {name}!')
