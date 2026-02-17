from flask import Flask
from flask_restx import Api

app = Flask(__name__)

api = Api(app=app, 
          title='Спортивные состязания API',
          version='1.0',
          description='API для работы с данными о спортивных соревнованиях')

from part.part import api as sports_api
api.add_namespace(sports_api)

if __name__ == '__main__':
    print("🚀 Сервер запускается... Открой браузер: http://127.0.0.1:5000")
    app.run(debug=True)
