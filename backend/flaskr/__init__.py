from flask import Flask, request, abort, jsonify, session
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={'/': {'origins': '*'}})
    '''
   Set up CORS. Allow '*' for origins. Delete the sample route after
   completing the TODOs
  '''

    '''
   Use the after_request decorator to set Access-Control-Allow
  '''

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type, Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET, POST, DELETE"
        )
        return response

    '''
  Create an endpoint to handle GET requests
  for all available categories.
  '''

    @app.route('/categories')
    def get_categories():
        # categories = Category.query.order_by(Category.id).all()
        # formatted_categories = [category.format() for category in categories]

        categories = Category.query.order_by(Category.id).all()
        categories_list = {}
        for category in categories:
            categories_list[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categories_list
        })

    @app.route('/categories', methods=['POST'])
    def create_new_category ():
        body = request.get_json()
        new_type = body.get('category')
        try:

            category = Category(type=new_type).insert()
            

            categories = Category.query.order_by(Category.id).all()
            categories_list = {}
            for category in categories:
                categories_list[category.id] = category.type

            return jsonify({
                'success': True,
                'categories': categories_list,
                'total_categories': len(categories_list)
            })
        except Exception as e:
            err = e
            print(f"Err => {err}") 
            abort(422)

    '''
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for
  three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        categories = Category.query.all()
        categories_list = {}
        for category in categories:
            categories_list[category.id] = category.type

        if len(current_questions) == 0:
            abort(404)

        cat = Category.query.order_by(Category.id).first()

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': cat.type,
            'categories': categories_list
        })

    '''
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will
  be removed.
  This removal will persist in the database and when you refresh the page.
  '''

    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        question = Question.query.get(question_id)

        try:
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except Exception as e:
            err = e
            print(f"Err => {err}")
            abort(422)

    # @app.route('/categories/<int:category_id>', methods=['DELETE'])
    # def delete_category(category_id):
    #     category = Category.query.get(category_id)

    #     try:
    #         category.delete()

    #         categories = Category.query.order_by(Category.id).all()
    #         categories_list = {}
    #         for category in categories:
    #             categories_list[category.id] = category.type

    #         return jsonify({
    #             'success': True,
    #             'deleted': category_id,
    #             'categories': categories_list,
    #             'total_categories': len(categories_list)
    #         })

    #     except Exception as e:
    #         err = e
    #         print(f"Err => {err}")
    #         abort(422)

    '''
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''

    @app.route('/questions', methods=['POST'])
    def create_new_question():
        body = request.get_json()

        try:
            search = body.get('searchTerm', None)

            if search:
                category = Category.query.first()
                selection = Question.query.order_by(Question.id).filter(
                    Question.question.ilike(f'%{search}%'))
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection.all()),
                    'current_category': category.type
                })

            else:
                new_question = body.get('question')
                new_answer = body.get('answer')
                new_category = body.get('category')
                new_difficulty = body.get('difficulty')
                new_rating = body.get('rating')

                if ((new_question is None) or
                        (new_answer is None) or
                    (new_difficulty is None) or
                        (new_category is None)):
                    abort(422)
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty,
                    rating=new_rating
                )
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })
        except Exception as e:
            err = e
            print(f"Err => {err}")
            abort(422)

    '''
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''

    '''
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''

    @app.route('/categories/<int:cat_id>/questions')
    def get_categories_by_id(cat_id):
        category = Category.query.get(cat_id)
        if category is None:
            abort(404)

        selection = Question.query.filter(Question.category == cat_id).all()
        current_questions = paginate_questions(request, selection)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': category.type
        })

    '''
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
        body = request.get_json()
        previous_questions = body.get('previous_questions')
        quiz_category = body.get('quiz_category')

        try:
            if (quiz_category['id'] == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter(
                    Question.category == quiz_category['id']).all()  

            total_questions = len(questions)          

            random_question = random.choice(questions)

            if len(previous_questions) == total_questions:
                return jsonify({
                    'success': True
                })

            else:
                return jsonify({
                    'success': True,
                    'question': random_question.format()
                })
        except Exception as e:
            err = e
            print(f"Err => {err}")
            abort(400)

    '''
  Create error handlers for all expected errors
  including 404 and 422.
  '''

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({
                "success": False,
                "error": 404,
                "message": "page not found"
            }), 404
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False,
                     "error": 422,
                     "message": "unprocessable"
                     }), 422,
        )

    @app.errorhandler(405)
    def method_not_found(error):
        return (
            jsonify({"success": False,
                     "error": 405,
                     "message": "method not allowed"
                     }), 405,
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app