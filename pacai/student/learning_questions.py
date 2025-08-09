# pylint: disable=invalid-name

def question_2() -> tuple[float, float]:
    """
    Question 2.

    Modify ONLY ONE of the following variables when answering this question.
    """

    discount = 0.9
    noise = 0.2

    return discount, noise

def question_3a() -> tuple[float, float, float] | None:
    """
    Question 3A.

    Modify any of these three options.
    If the requested scenario is not possible,
    return just `None`.
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    # If the requested scenario is not possible, return None.
    # return None

    return discount, noise, living_reward

def question_3b() -> tuple[float, float, float] | None:
    """
    Question 3B.

    Modify any of these three options.
    If the requested scenario is not possible,
    return just `None`.
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    # If the requested scenario is not possible, return None.
    # return None

    return discount, noise, living_reward

def question_3c() -> tuple[float, float, float] | None:
    """
    Question 3C.

    Modify any of these three options.
    If the requested scenario is not possible,
    return just `None`.
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    # If the requested scenario is not possible, return None.
    # return None

    return discount, noise, living_reward

def question_3d() -> tuple[float, float, float] | None:
    """
    Question 3D.

    Modify any of these three options.
    If the requested scenario is not possible,
    return just `None`.
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    # If the requested scenario is not possible, return None.
    # return None

    return discount, noise, living_reward

def question_3e() -> tuple[float, float, float] | None:
    """
    Question 3E.

    Modify any of these three options.
    If the requested scenario is not possible,
    return just `None`.
    """

    discount = 0.9
    noise = 0.2
    living_reward = 0.0

    # If the requested scenario is not possible, return None.
    # return None

    return discount, noise, living_reward

def question_5() -> tuple[float, float]:
    """
    Question 5.

    Modify any of these two options.
    If the requested scenario is not possible,
    return just `None`.
    """

    exploration_rate = 0.3
    learning_rate = 0.5

    # If the requested scenario is not possible, return None.
    # return None

    return exploration_rate, learning_rate

def main() -> int:
    """ Print the answers to all the questions. """

    questions = [
        question_2,
        question_3a,
        question_3b,
        question_3c,
        question_3d,
        question_3e,
        question_5,
    ]

    print('Answers to analysis questions:')
    for question in questions:
        response = question()
        print(f"    {question.__name__.title():<11}: {str(response)}")

    return 0

if (__name__ == '__main__'):
    main()
