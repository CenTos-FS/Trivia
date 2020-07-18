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
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))

    def test_404_invalid_page(self):
        response = self.client().get('/questions?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource not found')

    def test_delete_question(self):
        question = Question.query.order_by(Question.id.desc()).first()
        id = question.id 

        response = self.client().delete(f'/questions/{id}')  
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], id)
     
    def test_delete_invalid_id(self):
        id = 10000
        response = self.client().delete(f'/questions/{id}') 
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Request cannot be processed')

    def test_add_questions(self):
         question = {
             'question' : 'Which is the strongest muscle in human body', 
              'answer' : 'masseter',
               'category' : 2 ,
                'difficulty' : 2 
         }

         response = self.client().post('/questions', json = question)
         data = json.loads(response.data)
         new_question = Question.query.order_by(Question.id.desc()).first()
         id = new_question.id
         self.assertEqual(response.status_code, 200)
         self.assertEqual(data['success'], True)
         self.assertEqual(data['created'], id)
         self.assertIsNotNone(question)

    def test_add_question_missing(self):

         response = self.client().post('/questions', json = {})
         data = json.loads(response.data)
         self.assertEqual(response.status_code, 422)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Request cannot be processed')

    def test_search_question(self):

         response = self.client().post('/questions', json ={'searchTerm' : 'city'})
         data = json.loads(response.data)   
         self.assertEqual(response.status_code, 200)
         self.assertEqual(data['success'], True)
         self.assertTrue(data['questions'])

    def test_no_search_result(self):

         response = self.client().post('/questions', json ={'searchTerm' : '___00'})
         data = json.loads(response.data)   
         self.assertEqual(response.status_code, 422)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Request cannot be processed')

    def test_get_questions_by_category(self):
         category = 1

         response = self.client().get(f'/categories/{category}/questions')
         data = json.loads(response.data)   
         self.assertEqual(response.status_code, 200)
         self.assertEqual(data['success'], True)
         self.assertTrue(data['questions'])
         self.assertTrue(data['total_questions'])

    def test_get_questions_by_category_error(self):
         category = 10000

         response = self.client().get(f'/categories/{category}/questions')
         data = json.loads(response.data)  
         self.assertEqual(response.status_code, 422)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Request cannot be processed')

    def test_play_quize(self):

         response = self.client().post('/quizzes', json = {
             'previous_questions' : [18,19],
             'quiz_category' : {'type' : 'Science', 'id' : '1'}
         })    
         data = json.loads(response.data)   
         self.assertEqual(response.status_code, 200)
         self.assertEqual(data['success'], True)
         self.assertTrue(data['question'])
         self.assertEqual(data['question']['category'], 1)
         self.assertNotEqual(data['question']['id'], 18)
         self.assertNotEqual(data['question']['id'], 19)

    def test_play_quize_error(self):
         response = self.client().post('/quizzes', json = {})    
         data = json.loads(response.data)
         self.assertEqual(response.status_code, 400)
         self.assertEqual(data['success'], False)
         self.assertEqual(data['message'], 'Bad request')
      
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()