from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import NoAuthorizationError
from sqlalchemy import func
import bcrypt
from werkzeug.utils import secure_filename
import os
from datetime import timedelta, timezone, datetime
import firebase_admin
from firebase_admin import credentials, messaging
import threading
import time
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # заменяй на свой DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'super-secret-key-very-long-and-secure-1234567890'  # поменяй на свой защищённый ключ
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
cred_path = os.path.join(BASE_DIR, 'firebase-service-key.json')
if os.path.exists(cred_path):
    try:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        print("Firebase successfully initialized")
    except Exception as e:
        print(f"Firebase init error: {e}")
else:
    print(f"Firebase key not found at {cred_path}")

db = SQLAlchemy(app)
jwt = JWTManager(app)

now = lambda: datetime.now(timezone.utc)

class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, default=now, nullable=False)

    def __repr__(self):
        return f'<Image {self.id}: {self.path}>'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.LargeBinary(60), nullable=False)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(db.DateTime, default=now, onupdate=now, nullable=False)

    last_seen = db.Column(db.DateTime, default=now, nullable=False)
    last_inactivity_notification = db.Column(db.DateTime, nullable=True)

    # Связь с изображением профиля пользователя
    image = db.relationship('Image', lazy=True)

    # Рецепты, созданные пользователем
    recipes = db.relationship('Recipe', backref='author', lazy=True)

    # Комментарии, созданные пользователем
    comments = db.relationship('Comment', backref='author', lazy=True)

    def __repr__(self):
        return f'<User {self.login}>'

class Thread(db.Model):
    __tablename__ = 'threads'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=now,
        onupdate=now, nullable=False
    )

    # Рецепты, относящиеся к данному треду
    recipes = db.relationship('Recipe', backref='thread', lazy=True)

    def __repr__(self):
        return f'<Thread {self.title}>'

class Recipe(db.Model):
    __tablename__ = 'recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)

    main_image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=True)
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=now,
        onupdate=now, nullable=False
    )

    # Главная картинка рецепта
    main_image = db.relationship('Image', foreign_keys=[main_image_id], lazy=True)

    # Ингредиенты рецепта
    ingredients = db.relationship('Ingredient', backref='recipe', lazy=True, cascade='all, delete-orphan')

    # Шаги приготовления рецепта
    steps = db.relationship('Step', backref='recipe', lazy=True, cascade='all, delete-orphan', order_by='Step.order_index')

    # Комментарии пользователей к рецепту
    comments = db.relationship('Comment', backref='recipe', lazy=True, cascade='all,delete-orphan')

    def __repr__(self):
        return f'<Recipe {self.title}>'

class Step(db.Model):
    __tablename__ = 'steps'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    order_index = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)

    image_id = db.Column(db.Integer, db.ForeignKey('images.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=now,
        onupdate=now, nullable=False
    )

    image = db.relationship('Image', foreign_keys=[image_id], lazy=True)

    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'order_index', name='uq_recipe_step_order'),
    )

    def __repr__(self):
        return f'<Step {self.order_index} of Recipe {self.recipe_id}>'

class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.String(50), nullable=False)  # чтобы можно было хранить дроби и слова
    unit = db.Column(db.String(50), nullable=False)

    created_at = db.Column(db.DateTime, default=now, nullable=False)

    def __repr__(self):
        return f'<Ingredient {self.name} ({self.quantity} {self.unit})>'

class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=now, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=now,
        onupdate=now,
        nullable=False
    )

    def __repr__(self):
        return f'<Comment {self.id} by User {self.author_id} on Recipe {self.recipe_id}>'


class RecipeVote(db.Model):
    __tablename__ = 'recipe_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    value = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'recipe_id', name='uq_user_recipe_vote'),
    )


class FcmToken(db.Model):
    __tablename__ = 'fcm_tokens'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(512), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=now, nullable=False)

    user = db.relationship('User', backref=db.backref('fcm_tokens', lazy=True))


def update_last_seen(user_id):
    user = User.query.get(user_id)
    if user:
        user.last_seen = now()
        db.session.commit()

def get_optional_user_id():
    try:
        verify_jwt_in_request(optional=True)
        return int(get_jwt_identity())
    except (NoAuthorizationError, ValueError, TypeError):
        return None


def image_public_path(image):
    if not image or not image.path:
        return None
    normalized = image.path.replace('\\', '/')
    if normalized.startswith('uploads/'):
        return '/' + normalized
    return '/uploads/' + os.path.basename(normalized)


def recipe_score(recipe_id):
    total = db.session.query(func.coalesce(func.sum(RecipeVote.value), 0)).filter_by(
        recipe_id=recipe_id
    ).scalar()
    return int(total or 0)


def user_recipe_vote(recipe_id, user_id):
    if not user_id:
        return None
    vote = RecipeVote.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    return vote.value if vote else None


@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    login = data.get('login')
    password = data.get('password')

    if not all([name, login, password]):
        return jsonify({"msg": "Name, login and password required"}), 400

    # Проверяем, есть ли уже такой логин
    if User.query.filter_by(login=login).first():
        return jsonify({"msg": "User with this login already exists"}), 400

    # Хэшируем пароль с bcrypt
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    user = User(name=name, login=login, password_hash=hashed_password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login = data.get('login')
    password = data.get('password')

    if not all([login, password]):
        return jsonify({"msg": "Login and password required"}), 400

    user = User.query.filter_by(login=login).first()

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        return jsonify({"msg": "Invalid login or password"}), 401

    # Создаем JWT токен (в payload положим user_id)
    access_token = create_access_token(identity=str(user.id))

    return jsonify(access_token=access_token), 200

@app.route('/users/refresh', methods=['POST'])
@jwt_required()
def refresh():
    user_id = int(get_jwt_identity())
    new_token = create_access_token(identity=str(user_id))
    return jsonify(access_token=new_token), 200

def image_to_dict(image):
    if not image:
        return None
    return {
        "id": image.id,
        "path": image.path,
        "url": image_public_path(image),
        "created_at": image.created_at.isoformat()
    }

def user_to_dict(user):
    if not user:
        return None
    return {
        "id": user.id,
        "name": user.name,
        "login": user.login,
        "image": image_to_dict(user.image),
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }

def thread_to_dict(thread):
    return {
        "id": thread.id,
        "title": thread.title,
        "created_at": thread.created_at.isoformat(),
        "updated_at": thread.updated_at.isoformat()
    }

def ingredient_to_dict(ingredient):
    return {
        "id": ingredient.id,
        "name": ingredient.name,
        "quantity": ingredient.quantity,
        "unit": ingredient.unit,
        "created_at": ingredient.created_at.isoformat()
    }

def step_to_dict(step):
    return {
        "id": step.id,
        "order_index": step.order_index,
        "description": step.description,
        "image": image_to_dict(step.image),
        "created_at": step.created_at.isoformat(),
        "updated_at": step.updated_at.isoformat()
    }

def comment_to_dict(comment):
    return {
        "id": comment.id,
        "content": comment.content,
        "parent_id": comment.parent_id,
        "author": user_to_dict(comment.author),
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat()
    }

def recipe_to_dict(recipe, include_comments=True, user_id=None):
    if user_id is None:
        user_id = get_optional_user_id()

    data = {
        "id": recipe.id,
        "title": recipe.title,
        "description": recipe.description,
        "main_image": image_to_dict(recipe.main_image),
        "thread": thread_to_dict(recipe.thread),
        "author": user_to_dict(recipe.author),
        "ingredients": [ingredient_to_dict(i) for i in recipe.ingredients],
        "steps": [step_to_dict(s) for s in recipe.steps],
        "created_at": recipe.created_at.isoformat(),
        "updated_at": recipe.updated_at.isoformat(),
        "comments_count": Comment.query.filter_by(recipe_id=recipe.id).count(),
        "score": recipe_score(recipe.id),
        "user_vote": user_recipe_vote(recipe.id, user_id),
    }

    if include_comments:
        data["comments"] = [comment_to_dict(c) for c in recipe.comments]

    return data

def send_push_notification(user_id, title, body, data=None):
    if not firebase_admin._apps:
        return

    token_records = FcmToken.query.filter_by(user_id=user_id).all()
    tokens = [t.token for t in token_records]
    if not tokens:
        return

    string_data = {}
    if data:
        for key, value in data.items():
            string_data[str(key)] = str(value)

    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=string_data,
        tokens=tokens,
        android=messaging.AndroidConfig(priority='high'),
        apns=messaging.APNSConfig(payload=messaging.APNSPayload(aps=messaging.Aps(sound='default')))
    )

    response = messaging.send_each_for_multicast(message)
    if response.failure_count > 0:
        for idx, resp in enumerate(response.responses):
            if not resp.success:
                token_to_remove = tokens[idx]
                FcmToken.query.filter_by(token=token_to_remove).delete()
        db.session.commit()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/images', methods=['POST'])
@jwt_required()
def upload_image():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)

    if 'file' not in request.files:
        return jsonify({"msg": "File is required"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "Empty filename"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    image = Image(path=file_path)
    db.session.add(image)
    db.session.commit()

    return jsonify({
        "id": image.id,
        "path": image.path
    }), 201


@app.route('/users/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    user = User.query.get_or_404(user_id)
    return jsonify(user_to_dict(user)), 200


@app.route('/users/me', methods=['DELETE'])
@jwt_required()
def delete_user():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    user = User.query.get_or_404(user_id)

    for recipe in Recipe.query.filter_by(author_id=user_id).all():
        RecipeVote.query.filter_by(recipe_id=recipe.id).delete()
        db.session.delete(recipe)

    RecipeVote.query.filter_by(user_id=user_id).delete()
    Comment.query.filter_by(author_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    return jsonify({"msg": "User deleted"}), 200


@app.route('/users/me', methods=['PATCH'])
@jwt_required()
def update_user():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    user = User.query.get_or_404(user_id)

    data = request.get_json() or {}

    new_name = data.get("name")
    if new_name:
        user.name = new_name

    new_login = data.get("login")
    new_password = data.get("password")
    new_image_id = data.get("image_id")

    if new_login:
        exists = User.query.filter(User.login == new_login, User.id != user.id).first()
        if exists:
            return jsonify({"msg": "Login already exists"}), 400
        user.login = new_login

    if new_password:
        user.password_hash = bcrypt.hashpw(
            new_password.encode("utf-8"),
            bcrypt.gensalt()
        )

    if new_image_id is not None:
        if new_image_id == 0:
            user.image_id = None
        else:
            image = Image.query.get(new_image_id)
            if not image:
                return jsonify({"msg": "Image not found"}), 404
            user.image_id = new_image_id

    db.session.commit()

    return jsonify(user_to_dict(user)), 200


@app.route('/threads', methods=['GET'])
def list_threads():
    q = request.args.get('q', '').strip().lower()
    threads = Thread.query.order_by(Thread.title.asc()).all()

    if q:
        threads = [t for t in threads if q in t.title.lower()]

    return jsonify([
        {**thread_to_dict(t), "recipes_count": len(t.recipes)}
        for t in threads
    ]), 200


@app.route('/threads', methods=['POST'])
@jwt_required()
def create_thread():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    data = request.get_json()
    title = data.get("title")

    if not title:
        return jsonify({"msg": "Title is required"}), 400

    thread = Thread(title=title)
    db.session.add(thread)
    db.session.commit()

    return jsonify(thread_to_dict(thread)), 201


@app.route('/threads/<int:thread_id>', methods=['PATCH'])
@jwt_required()
def update_thread(thread_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    thread = Thread.query.get_or_404(thread_id)
    data = request.get_json()

    title = data.get("title")
    if title:
        thread.title = title

    db.session.commit()
    return jsonify(thread_to_dict(thread)), 200


@app.route('/threads/<int:thread_id>', methods=['DELETE'])
@jwt_required()
def delete_thread(thread_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    thread = Thread.query.get_or_404(thread_id)

    # лучше не удалять, если есть рецепты
    if thread.recipes:
        return jsonify({"msg": "Thread has recipes and cannot be deleted"}), 400

    db.session.delete(thread)
    db.session.commit()
    return jsonify({"msg": "Thread deleted"}), 200

@app.route('/recipes', methods=['GET'])
def list_recipes():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    thread_id = request.args.get('thread_id', type=int)

    query = Recipe.query
    if thread_id:
        query = query.filter_by(thread_id=thread_id)

    pagination = query.order_by(Recipe.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    user_id = get_optional_user_id()

    return jsonify({
        "items": [
            recipe_to_dict(r, include_comments=False, user_id=user_id)
            for r in pagination.items
        ],
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }), 200


@app.route('/recipes/me', methods=['GET'])
@jwt_required()
def my_recipes():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    pagination = Recipe.query.filter_by(author_id=user_id).order_by(
        Recipe.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [
            recipe_to_dict(r, include_comments=False, user_id=user_id)
            for r in pagination.items
        ],
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }), 200


@app.route('/recipes/<int:recipe_id>/vote', methods=['POST'])
@jwt_required()
def vote_recipe(recipe_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)
    action = (request.get_json() or {}).get('action')

    if action not in ('up', 'down'):
        return jsonify({"msg": "action must be 'up' or 'down'"}), 400

    vote = RecipeVote.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    previous_value = vote.value if vote else 0
    new_value = 0

    if action == 'up':
        if vote and vote.value == 1:
            db.session.delete(vote)
            new_value = 0
        elif vote and vote.value == -1:
            vote.value = 1
            new_value = 1
        else:
            db.session.add(RecipeVote(user_id=user_id, recipe_id=recipe_id, value=1))
            new_value = 1
    else:
        if vote and vote.value == -1:
            db.session.delete(vote)
            new_value = 0
        elif vote and vote.value == 1:
            vote.value = -1
            new_value = -1
        else:
            db.session.add(RecipeVote(user_id=user_id, recipe_id=recipe_id, value=-1))
            new_value = -1

    db.session.commit()

    if action == 'up' and new_value == 1 and recipe.author_id != user_id:
        send_push_notification(
            recipe.author_id,
            "Новый лайк 👍",
            f"{User.query.get(user_id).name} лайкнул ваш рецепт",
            {"postId": str(recipe_id), "type": "like"}
        )

    return jsonify({
        "score": recipe_score(recipe_id),
        "user_vote": user_recipe_vote(recipe_id, user_id),
    }), 200


@app.route('/recipes', methods=['POST'])
@jwt_required()
def create_recipe():
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    data = request.get_json()

    title = data.get("title")
    thread_id = data.get("thread_id")
    ingredients_data = data.get("ingredients", [])
    steps_data = data.get("steps", [])

    if not title or not thread_id:
        return jsonify({"msg": "Title and thread_id are required"}), 400

    thread = Thread.query.get(thread_id)
    if not thread:
        return jsonify({"msg": "Thread not found"}), 404

    main_image_id = data.get("main_image_id")
    if main_image_id:
        main_image = Image.query.get(main_image_id)
        if not main_image:
            return jsonify({"msg": "Main image not found"}), 404

    recipe = Recipe(
        title=title,
        description=data.get("description"),
        main_image_id=main_image_id,
        thread_id=thread_id,
        author_id=user_id
    )
    db.session.add(recipe)
    db.session.flush()  # чтобы получить recipe.id до создания шагов/ингредиентов

    for ing in ingredients_data:
        ingredient = Ingredient(
            recipe_id=recipe.id,
            name=ing["name"],
            quantity=ing["quantity"],
            unit=ing["unit"]
        )
        db.session.add(ingredient)

    for step_data in steps_data:
        image_id = step_data.get("image_id")
        if image_id:
            img = Image.query.get(image_id)
            if not img:
                return jsonify({"msg": f"Image {image_id} not found"}), 404

        step = Step(
            recipe_id=recipe.id,
            order_index=step_data["order_index"],
            description=step_data["description"],
            image_id=image_id
        )
        db.session.add(step)

    db.session.commit()

    recipe = Recipe.query.get(recipe.id)
    return jsonify(recipe_to_dict(recipe)), 201

@app.route('/recipes/<int:recipe_id>', methods=['GET'])
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return jsonify(recipe_to_dict(recipe)), 200


@app.route('/recipes/<int:recipe_id>', methods=['PATCH'])
@jwt_required()
def update_recipe(recipe_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.author_id != user_id:
        return jsonify({"msg": "Forbidden"}), 403

    data = request.get_json()

    title = data.get("title")
    if title:
        recipe.title = title

    if "description" in data:
        recipe.description = data.get("description")

    if "thread_id" in data:
        thread_id = data.get("thread_id")
        thread = Thread.query.get(thread_id)
        if not thread:
            return jsonify({"msg": "Thread not found"}), 404
        recipe.thread_id = thread_id

    if "main_image_id" in data:
        main_image_id = data.get("main_image_id")
        if main_image_id is not None:
            img = Image.query.get(main_image_id)
            if not img:
                return jsonify({"msg": "Main image not found"}), 404
        recipe.main_image_id = main_image_id

    # удалить старые ингредиенты и шаги
    Ingredient.query.filter_by(recipe_id=recipe.id).delete()
    Step.query.filter_by(recipe_id=recipe.id).delete()

    ingredients_data = data.get("ingredients", [])
    steps_data = data.get("steps", [])

    for ing in ingredients_data:
        db.session.add(Ingredient(
            recipe_id=recipe.id,
            name=ing["name"],
            quantity=ing["quantity"],
            unit=ing["unit"]
        ))

    for step_data in steps_data:
        image_id = step_data.get("image_id")
        if image_id:
            img = Image.query.get(image_id)
            if not img:
                return jsonify({"msg": f"Image {image_id} not found"}), 404

        db.session.add(Step(
            recipe_id=recipe.id,
            order_index=step_data["order_index"],
            description=step_data["description"],
            image_id=image_id
        ))

    db.session.commit()

    recipe = Recipe.query.get(recipe.id)
    return jsonify(recipe_to_dict(recipe)), 200

@app.route('/recipes/<int:recipe_id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(recipe_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)

    if recipe.author_id != user_id:
        return jsonify({"msg": "Forbidden"}), 403

    # комментарии, шаги, ингредиенты удалятся каскадно, если cascade настроен
    db.session.delete(recipe)
    db.session.commit()

    return jsonify({"msg": "Recipe deleted"}), 200


@app.route('/recipes/<int:recipe_id>/comments', methods=['POST'])
@jwt_required()
def create_comment(recipe_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)

    data = request.get_json()
    content = data.get("content")
    parent_id = data.get("parent_id")

    if not content:
        return jsonify({"msg": "Content is required"}), 400

    if parent_id:
        parent = Comment.query.get(parent_id)
        if not parent or parent.recipe_id != recipe.id:
            return jsonify({"msg": "Parent comment not found"}), 404

    comment = Comment(
        recipe_id=recipe.id,
        author_id=user_id,
        content=content,
        parent_id=parent_id,
    )
    db.session.add(comment)
    db.session.commit()

    if recipe.author_id != user_id:
        send_push_notification(
            recipe.author_id,
            "Новый комментарий 💬",
            f"{User.query.get(user_id).name} оставил комментарий: {content[:50]}...",
            {"postId": str(recipe_id), "type": "comment"}
        )

    return jsonify(comment_to_dict(comment)), 201

@app.route('/comments/<int:comment_id>', methods=['PATCH'])
@jwt_required()
def update_comment(comment_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    comment = Comment.query.get_or_404(comment_id)

    if comment.author_id != user_id:
        return jsonify({"msg": "Forbidden"}), 403

    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"msg": "Content is required"}), 400

    comment.content = content
    db.session.commit()

    return jsonify(comment_to_dict(comment)), 200

@app.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id):
    user_id = int(get_jwt_identity())
    update_last_seen(user_id)
    comment = Comment.query.get_or_404(comment_id)

    if comment.author_id != user_id:
        return jsonify({"msg": "Forbidden"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"msg": "Comment deleted"}), 200

@app.route('/recipes/<int:recipe_id>/comments', methods=['GET'])
def get_comments(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = Comment.query.filter_by(recipe_id=recipe.id).order_by(
        Comment.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [comment_to_dict(c) for c in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "total": pagination.total
    }), 200

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/users/fcm/token', methods=['POST'])
@jwt_required()
def register_fcm_token():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({"error": "Token required"}), 400

    existing = FcmToken.query.filter_by(token=token).first()
    if existing:
        return jsonify({"message": "Token already registered"}), 200

    fcm_token = FcmToken(user_id=user_id, token=token)
    db.session.add(fcm_token)
    db.session.commit()
    return jsonify({"message": "Token registered"}), 200

@app.route('/users/fcm/token', methods=['DELETE'])
@jwt_required()
def unregister_fcm_token():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({"error": "Token required"}), 400

    fcm_token = FcmToken.query.filter_by(token=token, user_id=user_id).first()
    if fcm_token:
        db.session.delete(fcm_token)
        db.session.commit()
    return jsonify({"message": "Token unregistered"}), 200

def inactivity_worker():
    while True:
        try:
            with app.app_context():
                now_utc = now()
                threshold_active = now_utc - timedelta(hours=24)
                threshold_reminder = now_utc - timedelta(hours=24)

                users = User.query.filter(
                    User.last_seen < threshold_active,
                    (User.last_inactivity_notification == None) |
                    (User.last_inactivity_notification < threshold_reminder)
                ).all()

                for user in users:
                    send_push_notification(
                        user.id,
                        "Мы скучаем 👋",
                        "Возвращайтесь и откройте новые рецепты для себя!"
                    )
                    user.last_inactivity_notification = now_utc
                db.session.commit()
        except Exception as e:
            print("Inactivity worker error:", e)

        time.sleep(60)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        threading.Thread(target=inactivity_worker, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)