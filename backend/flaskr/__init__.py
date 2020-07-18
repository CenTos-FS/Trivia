import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    formatted_questions = [question.format() for question in selection]
    page_wise_questions = formatted_questions[start:end]
    return page_wise_questions

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
  
    CORS(app)
   
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods','GET,PUT,POST,PATCH,DELETE,OPTIONS')
        return response
 
    @app.route('/categories')
    def get_all_categories():
        categories = Category.query.all()
    

        if len(categories) == 0:
            abort(404)
    
        category_dict = {}
        for category in categories:
            category_dict[category.id] = category.type

        return jsonify({
          'success' : True,
          'categories' : category_dict,
          'total_categories' : len(categories)
        })


   
    @app.route('/questions')
    def get_all_questions():
        questions = Question.query.all()
        categories = Category.query.all()

        current_questions = paginate_questions(request, questions)
        

        category_dict = {}
        for category in categories:
          category_dict[category.id] = category.type

        if len(current_questions)==0:
          abort(404)

        return jsonify({
          'success' : True,
          'questions' : current_questions,
          'total_questions' : len(questions),
          'categories' : category_dict
        })    
      
    
    
    @app.route('/questions/<int:id>', methods =['DELETE'])
    def delete_questions(id):
        try:
            question = Question.query.filter(Question.id == id).one_or_none()
            if question is None:
              abort(404)
            else:
              question.delete()
              current_questions = paginate_questions(request,Question.query.order_by(Question.id).all())  

            return jsonify({
              'success' : True,
              'deleted' : id,
              'questions' : current_questions,
              'total_questions' : len(Question.query.all())
            })
        except:
            abort(422)
      

    
    @app.route('/questions', methods =['POST'])
    def add_questions():
        data = request.get_json()
      
        if request.get_json().get('searchTerm'):
            try:
                searchTerm = data.get('searchTerm')
                questions = Question.query.filter(Question.question.ilike(f'%{searchTerm}%')).all()
                current_questions = paginate_questions(request,questions)
                categories = Category.query.order_by(Category.id).all()
                category_dict = {}
                for category in categories:
                  category_dict[category.id] = category.type
                
                if len(current_questions)==0:
                  abort(404)

                return jsonify({
                  'success' : True,
                  'questions' : current_questions,
                  'total_questions' : len(Question.query.all()),
                })    
            
            except:
                abort(422)  
        else:
          if ((data.get('question') is None) or 
              (data.get('answer') is None) or 
              (data.get('category') is None) or 
              (data.get('difficulty') is None)):
                abort(422)
          try:
              question = Question(data.get('question'),
                                  data.get('answer'),
                                  data.get('category'),
                                  data.get('difficulty'))
              question.insert()
              current_questions = paginate_questions(request,Question.query.order_by(Question.id).all())  

              return jsonify({
                'success' : True,
                'created' : question.id,
                'questions' : current_questions,
                'total_questions' : len(Question.query.all())
              })
          except:
              abort(422)  


      
    @app.route('/categories/<int:id>/questions')
    def get_questions_by_category(id):
        try:
            category = Category.query.filter_by(id = id).one_or_none()

            questions = Question.query.filter_by(category = category.id).all()
            current_questions = paginate_questions(request,questions)
            return jsonify({
              'success' : True,
              'questions' : current_questions,
              'total_questions' : len(Question.query.all()),
              'current_category' : category.type
            })
        except:
            abort(422)
      


    
    @app.route('/quizzes' , methods =['POST'])
    def get_random_questions():
        data = request.get_json()
        previous_questions = data.get('previous_questions')
        quiz_category = data.get('quiz_category')

        if (previous_questions is None) or (quiz_category is None):
            abort(400)

        if data['quiz_category']['id'] == 0:
            questions = Question.query.filter(Question.id.notin_(previous_questions)).all()
            question = questions[random.randrange(0,len(questions))]
        else:  
            question = Question.query.filter(
                Question.category == data['quiz_category']['id'], Question.id.notin_(previous_questions)).first()

        return jsonify({
                "success": True,
                "question": question.format() if question != None else None
            })
        
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
          'success' : False,
          'error' : 404,
          'message' : 'Resource not found'
        }),404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
          'success' : False,
          'error' : 422,
          'message' : 'Request cannot be processed'
        }),422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
          'success' : False,
          'error' : 400,
          'message' : 'Bad request'
        }),400 

  
    return app

    