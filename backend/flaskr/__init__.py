import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category
from utils import format_categories, get_paginated_questions

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    db = setup_db(app)

    '''
  @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    CORS(app, resources={'/': {'origins': '*'}})

    '''
  @DONE: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
  @DONE: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''

    @app.route('/categories')
    def get_categories():
        try:
          # Getting all the categories and formatting them for the frontend.
          categories_list = format_categories(Category.query.all())
          return jsonify({
            'success': True,
            'categories': categories_list
            }), 200
        except:
          abort(500)

    '''
  @DONE: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
    @app.route('/questions')
    def get_questions():
      # get all the questions from the db.
      questions = Question.query.order_by(Question.id).all()
      # count the number of all available questions.
      number_of_questions = len(questions)

      # we get paginated questions based on page number.
      current_questions = get_paginated_questions(request, questions,QUESTIONS_PER_PAGE)

      # if there is no questions for the selected page we return 404 Not Found.
      if (len(current_questions) == 0):
        abort(404)

      # Getting all the categories and formatting them for the frontend.
      categories_list = format_categories(Category.query.all())

      return jsonify({
        'success': True,
        'total_questions': number_of_questions,
        'categories': categories_list,
        'questions': current_questions
        }), 200

    '''
  @DONE: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
      try:
        # Getting the target question and delete it.
        question = Question.query.get(id)
        question.delete()

        return jsonify({
          'success': True,
          'message': "Question is deleted successfully"
        }), 200
      except:
        abort(422)

    '''
  @DONE: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():

      data = request.get_json()
      question = data.get('question')
      answer = data.get('answer')
      difficulty = data.get('difficulty')
      category = data.get('category')

      # Check that all the informations are in the request data
      if not ('question' in data and 'answer' in data and 'difficulty' in data and 'category' in data):
        abort(422)

      # Check that all the informations are not empty
      if (question == '' or answer == '' or difficulty == '' or category == ''):
        abort(422)

      try:
        # Create a new question with the sent validated data
        question = Question(
                question=question,
                answer=answer,
                difficulty=difficulty,
                category=category
            )
        question.insert()

        # return success message on creation
        return jsonify({
          'success': True,
          'message': 'Question is created successfully'
          }), 201

      except:
        abort(422)

    '''
  @DONE: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():

      # Getting the search term from the request
      search_term = request.get_json().get('searchTerm')

      # Return 422 status code if we got an empty search term
      if search_term == '':
        abort(422)

      try:
        # get all questions that are LIKE the search term
        questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

        # Return 404 status code if we don't find any questions that match the search term
        if len(questions) == 0:
          abort(404)

        paginated_questions = get_paginated_questions(request, questions, QUESTIONS_PER_PAGE)

        # return response on success
        return jsonify({
          'success': True,
          'questions': paginated_questions,
          'total_questions': len(Question.query.all())
          }), 200

      except:
        abort(404)

    '''
  @DONE: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):

      # Get the selected category or none if it doesn't exist
      category = Category.query.filter_by(id=id).one_or_none()

      if (category is None):
        abort(422)

      # Get all the questions related to that category
      questions = Question.query.filter_by(category=id).all()

      paginated_questions = get_paginated_questions(request, questions, QUESTIONS_PER_PAGE)

      return jsonify({
        'success': True,
        'questions': paginated_questions,
        'total_questions': len(questions),
        'current_category': category.type
        })

    '''
  @DONE: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
    @app.route('/quizzes', methods=['POST'])
    def play_random_quiz_question():

      # Getting the existing quiz informations
      previous_questions = request.get_json().get('previous_questions')
      quiz_category = request.get_json().get('quiz_category')

      # Check that the data exist
      if ((quiz_category is None) or (previous_questions is None)):
        abort(400)

      # If the user selects 'all' he gets questions from all the categories
      if (quiz_category['id'] == 0):
        questions = Question.query.all()
      else:
        # Else we send questions related to the requested category
        questions = Question.query.filter_by(category=quiz_category['id']).all()

      # get a random question by selecting a random index within the number of questions available
      next_question = questions[random.randint(0, len(questions)-1)]

      question_found = True

      while question_found:
        # Check that the found question hasn't been asked before
        if next_question.id in previous_questions:
          next_question = questions[random.randint(0, len(questions)-1)]
        else:
          question_found = False

      return jsonify({
        'success': True,
        'question': next_question.format(),
      }), 200

    '''
  @DONE: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
      }), 400

    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
      }), 404

    @app.errorhandler(500)
    def internal_server_error(error):
      return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error, Please Try Again Later'
      }), 500

    @app.errorhandler(422)
    def unprocesable_entity(error):
      return jsonify({
        'success': False,
        'error': 422,
        'message': 'Unprocessable Entity'
      }), 422

    return app
