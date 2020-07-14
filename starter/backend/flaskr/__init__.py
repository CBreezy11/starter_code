import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import json
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"/api/*": {"origins": "*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow_Headers', 'Content-Type, Authorization')
    response.headers.add('Acces-Control-Allow-Methods', 'GET, PUT, DELETE')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def categories():
    categories = Category.query.order_by('id').all()
    formatted_categories = [category.format() for category in categories]

    return jsonify({
      'success': True,
      'categories': {1: "science",
                     2: "geography",
                     3: "art",
                     4: "history",
                     5: "entertainment",
                     6: "sports"
                     }
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def questions():
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * 10
    end = start + 10
    questions = Question.query.order_by('id').all()
    formatted_questions = [question.format() for question in questions]
    current_questions = formatted_questions[start:end]
    categories = Category.query.order_by('id').all()
    formatted_categories = [category.format() for category in categories ]

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'questions': current_questions,
      'total_questions': len(formatted_questions),
      'categories': {1: "science",
                     2: "geography",
                     3: "art",
                     4: "history",
                     5: "entertainment",
                     6: "sports"
                     }
    })
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<id>', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.filter(Question.id == id).first()
      question.delete()

      return jsonify({
        'success': True
      })
    except:
      abort(404)
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def post_question():
    data = request.get_json()
    search = data.get('searchTerm', None)

    if search:
      try:
        search = data['searchTerm']
        results = Question.query.filter(Question.question.ilike(f'%{search}%'))
        formatted_results = [result.format() for result in results]
        return jsonify({
          'success': True,
          'questions': formatted_results,
          'total_questions': len(formatted_results)
        })
      except:
        abort(422)
    else:
      try:
        new_question = Question(question=data['question'], answer=data['answer'], category=data['category'], difficulty=data['difficulty'])
        new_question.insert()

        return jsonify({
          'success': True,
          'question added': data
        })
      except:
        abort(400)
    '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<id>/questions', methods=['GET'])
  def questions_by_category(id):
    try:
      category = Category.query.filter(Category.id == id).one_or_none()
      category = category.format()
      questions = Question.query.filter(Question.category == id)
      formatted_questions = [question.format() for question in questions]

      return jsonify({
        'success': True,
        'category id': id,
        'current_category': category['type'],
        'total_questions': len(formatted_questions),
        'questions': formatted_questions
      })
    except:
      abort(404)
  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    data = request.get_json()
    category = data.get('quiz_category', None)
    history = data.get('previous_questions', None)
    questions = []
    random.seed()
    
    if category:
        category = int(category)
        questions = Question.query.filter(Question.category == category).all()
    else:
        questions = Question.query.all()
      
    formatted_questions = [question.format() for question in questions]
    for result in formatted_questions:
      if result['id'] in history:
        formatted_questions.remove(result)

    questions_list_length = len(formatted_questions)
    questions_list_index = questions_list_length-1
    index_for_next_question = random.randint(0, questions_list_index)
    question = formatted_questions[index_for_next_question]

    return jsonify({
      "category": category,
      "question": question
    })

  
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "Resource not found"
    }), 404

  @app.errorhandler(422)
  def not_processed(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "Could not process request"
    }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': "Bad request, most likely not enough questions in that category"
    }), 400

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': "There was a server error"
    }), 500

  return app

    