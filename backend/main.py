import os
import uuid
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# --- Конфигурация ---
app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "social_network.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# Создаем папку для загрузок, если нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


# --- Модели БД ---

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    login = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    tokens = db.relationship('AuthToken', backref='user', lazy=True)


class AuthToken(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    token = db.Column(db.String(256), unique=True, nullable=False)


class Post(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    community = db.Column(db.String(100), nullable=True)
    recipe = db.Column(db.JSON, nullable=True)  # Список шагов
    ingredients = db.Column(db.JSON, nullable=True)  # Список ингредиентов
    medias = db.Column(db.JSON, nullable=True)  # Список URL
    disable_comments = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")


class Comment(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.String(36), db.ForeignKey('comment.id'), nullable=True)  # для вложенности
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)


class Like(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    post_id = db.Column(db.String(36), db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='unique_like'),)


# --- Хелперы ---

def require_auth(f):
    """Декоратор для проверки токена авторизации"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        # Ожидаем формат "Bearer <token>" или просто "<token>"
        parts = auth_header.split()
        token = parts[1] if len(parts) == 2 else parts[0]

        auth_token = AuthToken.query.filter_by(token=token).first()
        if not auth_token:
            return jsonify({"error": "Invalid token"}), 401

        request.current_user = auth_token.user
        return f(*args, **kwargs)

    return decorated_function


def serialize_user(user):
    return {
        "id": user.id,
        "name": user.name,
        "avatar_url": user.avatar_url,
        "bio": user.bio,
        "created_at": user.created_at.isoformat() + "Z"
    }


def serialize_post(post):
    return {
        "id": post.id,
        "text": post.text,
        "community": post.community,
        "recipe": post.recipe or [],
        "ingredients": post.ingredients or [],
        "medias": post.medias or [],
        "disable_comments": post.disable_comments,
        "author": {
            "id": post.author.id,
            "name": post.author.name,
            "avatar_url": post.author.avatar_url
        },
        "likes_count": len(post.likes),
        "created_at": post.created_at.isoformat() + "Z"
    }


def serialize_comment(comment):
    return {
        "id": comment.id,
        "author": {
            "id": comment.author.id,
            "name": comment.author.name,
            "avatar_url": comment.author.avatar_url
        },
        "text": comment.text,
        "parent_id": comment.parent_id,
        "created_at": comment.created_at.isoformat() + "Z"
    }


# --- Routes: Users ---

@app.route('/users/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('login') or not data.get('password'):
        return jsonify({"error": "Login and password required"}), 400

    if User.query.filter_by(login=data['login']).first():
        return jsonify({"error": "User already exists"}), 409

    user = User(
        login=data['login'],
        password_hash=generate_password_hash(data['password']),
        name=data.get('name', data['login'])
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User created", "id": user.id}), 201


@app.route('/users/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(login=data.get('login')).first()

    if not user or not check_password_hash(user.password_hash, data.get('password')):
        return jsonify({"error": "Invalid credentials"}), 401

    # Создаем или получаем бессрочный токен
    token_obj = AuthToken.query.filter_by(user_id=user.id).first()
    if not token_obj:
        token_val = str(uuid.uuid4())
        token_obj = AuthToken(user_id=user.id, token=token_val)
        db.session.add(token_obj)
        db.session.commit()

    return jsonify({"access_token": token_obj.token}), 200


@app.route('/users/<user_id>', methods=['GET'])
@require_auth
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(serialize_user(user)), 200


@app.route('/users/me', methods=['GET'])
@require_auth
def get_my_profile():
    user = request.current_user
    return jsonify(serialize_user(user)), 200


@app.route('/users/me', methods=['PUT'])
@require_auth
def update_me():
    user = request.current_user
    data = request.get_json()

    if 'name' in data:
        user.name = data['name']
    if 'avatar_url' in data:
        user.avatar_url = data['avatar_url']
    if 'bio' in data:
        user.bio = data['bio']

    db.session.commit()
    return jsonify(serialize_user(user)), 200


# --- Routes: Posts ---

@app.route('/posts', methods=['POST'])
@require_auth
def create_post():
    user = request.current_user
    data = request.get_json()

    post = Post(
        user_id=user.id,
        text=data.get('text', ''),
        community=data.get('community'),
        recipe=data.get('recipe'),
        ingredients=data.get('ingredients'),
        medias=data.get('medias'),
        disable_comments=data.get('disable_comments', False)
    )
    db.session.add(post)
    db.session.commit()
    return jsonify(serialize_post(post)), 201


@app.route('/posts/<post_id>', methods=['GET'])
@require_auth
def get_post(post_id):
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(serialize_post(post)), 200


@app.route('/posts/<post_id>', methods=['PUT'])
@require_auth
def update_post(post_id):
    user = request.current_user
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "Post not found"}), 404
    if post.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if 'text' in data: post.text = data['text']
    if 'community' in data: post.community = data['community']
    if 'recipe' in data: post.recipe = data['recipe']
    if 'ingredients' in data: post.ingredients = data['ingredients']
    if 'medias' in data: post.medias = data['medias']
    if 'disable_comments' in data: post.disable_comments = data['disable_comments']

    db.session.commit()
    return jsonify(serialize_post(post)), 200


@app.route('/posts/<post_id>', methods=['DELETE'])
@require_auth
def delete_post(post_id):
    user = request.current_user
    post = Post.query.get(post_id)

    if not post:
        return jsonify({"error": "Post not found"}), 404
    if post.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


@app.route('/posts/feed', methods=['GET'])
@require_auth
def get_feed():
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    posts = Post.query.order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify([serialize_post(p) for p in posts]), 200


@app.route('/posts/me', methods=['GET'])
@require_auth
def get_my_posts():
    user = request.current_user
    limit = request.args.get('limit', 20, type=int)
    offset = request.args.get('offset', 0, type=int)

    posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).offset(offset).limit(limit).all()
    return jsonify([serialize_post(p) for p in posts]), 200


# --- Routes: Comments ---

@app.route('/posts/<post_id>/comments', methods=['POST'])
@require_auth
def add_comment(post_id):
    user = request.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    data = request.get_json()
    comment = Comment(post_id=post_id, user_id=user.id, text=data.get('text', ''))
    db.session.add(comment)
    db.session.commit()
    return jsonify(serialize_comment(comment)), 201


@app.route('/posts/<post_id>/comments', methods=['GET'])
@require_auth
def get_comments(post_id):
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    return jsonify([serialize_comment(c) for c in comments]), 200


@app.route('/comments/<comment_id>', methods=['PUT'])
@require_auth
def edit_comment(comment_id):
    user = request.current_user
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    if comment.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    data = request.get_json()
    if 'text' in data:
        comment.text = data['text']
    db.session.commit()
    return jsonify(serialize_comment(comment)), 200


@app.route('/comments/<comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    user = request.current_user
    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({"error": "Comment not found"}), 404
    # Обычно автор комментария или автор поста может удалять, но по спецификации просто "Удалить комментарий"
    # Оставим проверку на автора комментария для безопасности
    if comment.user_id != user.id:
        return jsonify({"error": "Forbidden"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"message": "Deleted"}), 200


# --- Routes: Likes ---

@app.route('/posts/<post_id>/like', methods=['POST'])
@require_auth
def like_post(post_id):
    user = request.current_user
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    existing = Like.query.filter_by(post_id=post_id, user_id=user.id).first()
    if not existing:
        like = Like(post_id=post_id, user_id=user.id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes_count": len(post.likes)}), 200


@app.route('/posts/<post_id>/like', methods=['DELETE'])
@require_auth
def unlike_post(post_id):
    user = request.current_user
    like = Like.query.filter_by(post_id=post_id, user_id=user.id).first()

    if like:
        db.session.delete(like)
        db.session.commit()

    post = Post.query.get(post_id)
    return jsonify({"likes_count": len(post.likes) if post else 0}), 200


# --- Routes: Media ---

@app.route('/media/upload', methods=['POST'])
@require_auth
def upload_media():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    # Добавляем уникальность имени
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

    # Возвращаем URL (в реальном проекте тут должен быть домен)
    url = f"/static/uploads/{unique_filename}"
    return jsonify({"url": url}), 200


@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# --- Заполнение БД моками ---

def seed_database():
    if User.query.first() is not None:
        return

    users = []
    for i in range(1, 6):
        user = User(
            login=f"user{i}@example.com",
            password_hash=generate_password_hash("123456"),
            name=f"User{i}",
            avatar_url=f"/static/uploads/user_avatar{i}.png",
            bio=f"Пользователь {i}"
        )
        db.session.add(user)
        db.session.flush()
        users.append(user)

    author = users[0]
    token = "test-token-123"
    auth_token = AuthToken(user_id=author.id, token=token)
    db.session.add(auth_token)

    post = Post(
        user_id=author.id,
        text="Я сделала блины, зацените. Очень быстро и просто готовится. Займет не больше 10 минут. Рецепт моей любимой бабушки",
        community="pancakes",
        recipe=[
            {"step": "В миске взбейте яйца, соль и сахар.", "media": "/static/uploads/step1.png"},
            {"step": "Влейте половину молока, просейте муку и перемешайте до однородности.", "media": "/static/uploads/step2.png"},
            {"step": "Добавьте оставшееся молоко и масло, ещё раз перемешайте.", "media": "/static/uploads/step3.png"}
        ],
        ingredients=[
            {"name": "Молоко", "count": 500, "measure_name": "мл"},
            {"name": "Яйца", "count": 2, "measure_name": "шт"},
            {"name": "Мука", "count": 200, "measure_name": "г"},
            {"name": "Сахар", "count": 2, "measure_name": "ст.л"},
            {"name": "Соль", "count": 0.5, "measure_name": "ч.л"},
            {"name": "Растительное масло", "count": 2, "measure_name": "ст.л"}
        ],
        medias=["/static/uploads/pancakes.jpg"],
        disable_comments=False
    )
    db.session.add(post)
    db.session.flush()

    c1 = Comment(
        post_id=post.id,
        user_id=users[1].id,
        parent_id=None,
        text="Вау, это просто блинные чудеса! Никогда не думал, что можно так просто добиться идеальных дырочек. Вау, это просто блинные чудеса! Никогда не думал, что можно так просто добиться идеальных дырочек. Вау, это просто блинные чудеса! Никогда не думал, что можно так просто добиться идеальных дырочек.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    db.session.add(c1)
    db.session.flush()

    c2 = Comment(
        post_id=post.id,
        user_id=users[2].id,
        parent_id=c1.id,
        text="Рецепт оказался на удивление рабочим: всё чётко по шагам.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(days=1)
    )
    db.session.add(c2)

    c3 = Comment(
        post_id=post.id,
        user_id=users[3].id,
        parent_id=c1.id,
        text="Результат превзошёл все ожидания: блины получились тонкими и хрустящими.",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=3)
    )
    db.session.add(c3)

    c4 = Comment(
        post_id=post.id,
        user_id=users[4].id,
        parent_id=None,
        text="Признаюсь, я тот ещё блинопек. Но этот рецепт реально работает!",
        created_at=datetime.datetime.utcnow() - datetime.timedelta(hours=21)
    )
    db.session.add(c4)

    like = Like(post_id=post.id, user_id=author.id)
    db.session.add(like)

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(host="0.0.0.0", port=5000, debug=False)