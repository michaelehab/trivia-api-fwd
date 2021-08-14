import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://michael:password@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):

        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertEqual(len(data['categories']), 6)

    def test_get_paginated_questions(self):

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['questions'])
        self.assertEqual(len(data['questions']), 10)

    def test_error_for_not_available_page(self):

        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_successful_question_delete(self):

        question = Question(question='new question', answer='new answer', difficulty=1, category=1)
        question.insert()

        response = self.client().delete('/questions/{}'.format(question.id))
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], "Question is deleted successfully")

    def test_delete_not_available_question(self):

        response = self.client().delete('/questions/9999')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_create_questions(self):

        response = self.client().post('/questions', json={
            'question': 'Test Question',
            'answer': 'Test Answer',
            'difficulty': 1,
            'category': 1,
        })

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['message'], 'Question is created successfully')

    def test_create_question_without_all_data(self):

        response = self.client().post('/questions', json={
            'question': '',
            'difficulty': 1,
        })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_create_question_with_empty_data(self):

        response = self.client().post('/questions', json={
            'question': '',
            'answer': '',
            'difficulty': 1,
            'category': 1,
        })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_questions_search(self):

        response = self.client().post('/questions/search', json={
            'searchTerm': 'largest lake in Africa'
            })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 1)

    def test_empty_search_term(self):

        response = self.client().post('/questions/search', json={
            'searchTerm': ''
            })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_not_available_search_term(self):

        response = self.client().post('/questions/search', json={
            'searchTerm': 'abcdefghijklmnopqrstuvwxyz',
            })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not Found')

    def test_get_questions_by_category(self):

        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['questions']), 0)
        self.assertEqual(data['current_category'], 'Science')

    def test_invalid_category_id(self):

        response = self.client().get('/categories/12345678/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Unprocessable Entity')

    def test_play_random_quiz_questions(self):

        response = self.client().post('/quizzes', json={
            'previous_questions': [1, 2],
            'quiz_category': {
                'type': 'History',
                'id': 1
            }
            })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)
        self.assertNotEqual(data['question']['id'], 1)
        self.assertNotEqual(data['question']['id'], 2)
        

    def test_no_data_to_play(self):

        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()