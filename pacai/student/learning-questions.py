# pylint: disable=invalid-name

def question_2() -> tuple[float, float]:
    """
    Question 2.

    Modify ONLY ONE of the following variables when answering this question.
    """

    discount = 0.9
    noise = 0.2

    return discount, noise

def question_3a() -> tuple[float, float, float]:
    """
    Question 3A.

    TODO
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    return discount, noise, living_reward

def question_3b() -> tuple[float, float, float]:
    """
    Question 3B.

    TODO
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    return discount, noise, living_reward

def question_3c() -> tuple[float, float, float]:
    """
    Question 3C.

    TODO
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    return discount, noise, living_reward

def question_3d() -> tuple[float, float, float]:
    """
    Question 3d.

    TODO
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    return discount, noise, living_reward

def question_3e() -> tuple[float, float, float]:
    """
    Question 3E.

    TODO
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    return discount, noise, living_reward

def question_6() -> tuple[float, float]:
    """
    Question 6.

    TODO
    """

    epsilon = 0.3
    learning_rate = 0.5

    return epsilon, learning_rate

def main() -> int:
    """ Print the answers to all the questions. """

    questions = [
        question_2,
        question_3a,
        question_3b,
        question_3c,
        question_3d,
        question_3e,
        question_6,
    ]

    print('Answers to analysis questions:')
    for question in questions:
        response = question()
        print(f"    {question.__name__.title():<11}: {str(response)}")

    return 0

if (__name__ == '__main__'):
    main()
