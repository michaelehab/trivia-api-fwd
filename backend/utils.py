from models import Question

def format_categories(categories):
    categories_list = {}
    for category in categories:
        categories_list[category.id] = category.type
    return categories_list


def get_paginated_questions(request, questions, num_of_questions):
    # Getting Page number from the url
    page = request.args.get('page', 1, type=int)
    # adjusting the stating index and the ending one based on the page number
    start = (page - 1) * num_of_questions
    end = start + num_of_questions
    # Formatting questions
    questions = [question.format() for question in questions]
    # Selecting the questions within the index 
    current_questions = questions[start:end]
    return current_questions