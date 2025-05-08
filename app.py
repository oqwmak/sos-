# Импорт необходимых модулей из Flask
from flask import Flask, jsonify, request, render_template
# Импорт CORS для разрешения запросов с других доменов
from flask_cors import CORS
# Импорт SQLAlchemy для работы с базой данных
from flask_sqlalchemy import SQLAlchemy
# Импорт модуля os для работы с операционной системой (не используется в этом коде, но может пригодиться)
import os

# Создание экземпляра Flask-приложения
app = Flask(__name__)
# Включение поддержки CORS
CORS(app)
# Настройка строки подключения к базе данных SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spa_services.db'
# Создание экземпляра SQLAlchemy для работы с БД
db = SQLAlchemy(app)

# Определение модели данных Service (услуга)
class Service(db.Model):
    # Уникальный идентификатор услуги (первичный ключ)
    id = db.Column(db.Integer, primary_key=True)
    # Название услуги, не может быть пустым
    name = db.Column(db.String(100), nullable=False)
    # Описание услуги, не может быть пустым
    description = db.Column(db.String(300), nullable=False)
    # Цена услуги, не может быть пустой
    price = db.Column(db.Integer, nullable=False)
    # Ссылка на изображение
    image_url = db.Column(db.String(300), nullable=True)

    # Метод для преобразования объекта в словарь (для JSON)
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url
        }

# Маршрут API для получения списка всех услуг
@app.route('/api/services', methods=['GET'])
def get_services():
    # Получение всех услуг из базы данных
    services = Service.query.all()
    # Возврат списка услуг в формате JSON
    return jsonify([s.to_dict() for s in services])

# Маршрут API для обновления конкретной услуги по ID
@app.route('/api/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    # Получение услуги по ID или ошибка 404
    service = Service.query.get_or_404(service_id)
    # Получение данных из запроса (JSON)
    data = request.json
    # Обновление полей услуги, если они указаны
    service.name = data.get('name', service.name)
    service.description = data.get('description', service.description)
    service.price = data.get('price', service.price)
    service.image_url = data.get('image_url', service.image_url)
    # Сохранение изменений в БД
    db.session.commit()
    # Возврат обновлённой услуги в формате JSON
    return jsonify(service.to_dict())

# Маршрут API для создания новой услуги
@app.route('/api/services', methods=['POST'])
def create_service():
    # Получение данных из запроса (JSON)
    data = request.json
    # Создание новой услуги
    service = Service(
        name=data['name'],
        description=data['description'],
        price=data['price'],
        image_url=data.get('image_url')
    )
    # Добавление услуги в базу данных
    db.session.add(service)
    db.session.commit()
    # Возврат созданной услуги и статус 201 (создано)
    return jsonify(service.to_dict()), 201

# Маршрут API для удаления услуги по ID
@app.route('/api/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    # Получение услуги по ID или ошибка 404
    service = Service.query.get_or_404(service_id)
    # Удаление услуги из базы данных
    db.session.delete(service)
    db.session.commit()
    # Возврат пустого ответа со статусом 204 (успешно, без контента)
    return '', 204

# Маршрут для отображения HTML-страницы создания услуги
@app.route('/create')
def create_page():
    # Отображение HTML-шаблона create.html
    return render_template('create.html')

# Главная страница сайта
@app.route('/')
def home():
    # Отображение HTML-шаблона index.html
    return render_template('index.html')

# Запуск приложения
if __name__ == '__main__':
    # Создание таблиц базы данных, если они ещё не существуют
    with app.app_context():
        db.create_all()
        # Если база пустая, добавляем одну демонстрационную услугу
        if not Service.query.first():
            sample = Service(name="Ароматический массаж", description="Расслабляющий массаж с эфирными маслами.", price=3000)
            db.session.add(sample)
            db.session.commit()
    # Запуск сервера в режиме отладки, доступного по всем IP
    app.run(debug=True, host='0.0.0.0')
