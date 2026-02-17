from flask_restx import Namespace, Resource, fields, reqparse

# Создаем пространство имен (все наши команды будут доступны по адресу /sports/)
api = Namespace('sports', description='Спортивные состязания')

# ===== ОПИСЫВАЕМ МОДЕЛЬ ДАННЫХ (что храним) =====
competition_model = api.model('Competition', {
    'id': fields.String(required=True, description='Уникальный номер'),
    'name': fields.String(required=True, description='Название соревнования'),
    'sport': fields.String(required=True, description='Вид спорта'),
    'athlete': fields.String(required=True, description='Участник'),
    'country': fields.String(required=True, description='Страна'),
    'result': fields.Float(required=True, description='Результат'),
    'place': fields.Integer(required=True, description='Место'),
    'year': fields.Integer(required=True, description='Год')
})

# ===== НАШИ ДАННЫЕ (хранятся в памяти) =====
COMPETITIONS = [
    {
        'id': '1',
        'name': 'Олимпийские игры 2024',
        'sport': 'Плавание',
        'athlete': 'Майкл Фелпс',
        'country': 'США',
        'result': 47.51,
        'place': 1,
        'year': 2024
    },
    {
        'id': '2',
        'name': 'Чемпионат мира',
        'sport': 'Легкая атлетика',
        'athlete': 'Усэйн Болт',
        'country': 'Ямайка',
        'result': 9.58,
        'place': 1,
        'year': 2023
    },
    {
        'id': '3',
        'name': 'Кубок мира',
        'sport': 'Футбол',
        'athlete': 'Лионель Месси',
        'country': 'Аргентина',
        'result': 7.5,
        'place': 2,
        'year': 2022
    }
]

# ===== ПАРСЕРЫ (для обработки запросов) =====
# Для сортировки
sort_parser = reqparse.RequestParser()
sort_parser.add_argument('sort_by', type=str, help='Поле для сортировки')
sort_parser.add_argument('order', type=str, choices=['asc', 'desc'], default='asc', help='asc или desc')

# Для добавления новой записи
add_parser = reqparse.RequestParser()
add_parser.add_argument('name', type=str, required=True, help='Название')
add_parser.add_argument('sport', type=str, required=True, help='Вид спорта')
add_parser.add_argument('athlete', type=str, required=True, help='Участник')
add_parser.add_argument('country', type=str, required=True, help='Страна')
add_parser.add_argument('result', type=float, required=True, help='Результат')
add_parser.add_argument('place', type=int, required=True, help='Место')
add_parser.add_argument('year', type=int, required=True, help='Год')

# ===== САМИ КОМАНДЫ (эндпоинты) =====

# 1. ПОЛУЧИТЬ ВСЕ ЗАПИСИ (GET /sports/competitions)
@api.route('/competitions')
class CompetitionList(Resource):
    @api.doc('list_competitions')
    @api.expect(sort_parser)
    @api.marshal_list_with(competition_model)
    def get(self):
        """Получить все записи (можно сортировать)"""
        args = sort_parser.parse_args()
        sort_by = args.get('sort_by')
        order = args.get('order')
        
        if sort_by and sort_by in COMPETITIONS[0].keys():
            reverse = (order == 'desc')
            sorted_comps = sorted(COMPETITIONS, key=lambda x: x[sort_by], reverse=reverse)
            return sorted_comps
        return COMPETITIONS
    
    @api.doc('create_competition')
    @api.expect(add_parser)
    @api.marshal_with(competition_model, code=201)
    def post(self):
        """Добавить новую запись"""
        args = add_parser.parse_args()
        
        # Генерируем новый ID
        new_id = str(max(int(c['id']) for c in COMPETITIONS) + 1)
        
        new_competition = {
            'id': new_id,
            'name': args['name'],
            'sport': args['sport'],
            'athlete': args['athlete'],
            'country': args['country'],
            'result': args['result'],
            'place': args['place'],
            'year': args['year']
        }
        
        COMPETITIONS.append(new_competition)
        return new_competition, 201

# 2. РАБОТА С КОНКРЕТНОЙ ЗАПИСЬЮ ПО ID
@api.route('/competitions/<string:id>')
@api.param('id', 'Идентификатор записи')
@api.response(404, 'Запись не найдена')
class CompetitionResource(Resource):
    @api.doc('get_competition')
    @api.marshal_with(competition_model)
    def get(self, id):
        """Получить запись по ID"""
        for comp in COMPETITIONS:
            if comp['id'] == id:
                return comp
        api.abort(404, f"Запись с id {id} не найдена")
    
    @api.doc('update_competition')
    @api.expect(add_parser)
    @api.marshal_with(competition_model)
    def put(self, id):
        """Обновить запись по ID"""
        args = add_parser.parse_args()
        
        for i, comp in enumerate(COMPETITIONS):
            if comp['id'] == id:
                COMPETITIONS[i] = {
                    'id': id,
                    'name': args['name'],
                    'sport': args['sport'],
                    'athlete': args['athlete'],
                    'country': args['country'],
                    'result': args['result'],
                    'place': args['place'],
                    'year': args['year']
                }
                return COMPETITIONS[i]
        api.abort(404, f"Запись с id {id} не найдена")
    
    @api.doc('delete_competition')
    @api.response(204, 'Запись удалена')
    def delete(self, id):
        """Удалить запись по ID"""
        for i, comp in enumerate(COMPETITIONS):
            if comp['id'] == id:
                COMPETITIONS.pop(i)
                return '', 204
        api.abort(404, f"Запись с id {id} не найдена")

# 3. СТАТИСТИКА
@api.route('/competitions/statistics/<string:field>')
@api.param('field', 'Поле (result/place/year)')
class CompetitionStatistics(Resource):
    @api.doc('get_statistics')
    def get(self, field):
        """Получить min, max, среднее"""
        if field not in ['result', 'place', 'year']:
            return {'error': 'Поле должно быть result, place или year'}, 400
        
        values = [c[field] for c in COMPETITIONS]
        
        return {
            'field': field,
            'min': min(values),
            'max': max(values),
            'avg': sum(values) / len(values)
        }
