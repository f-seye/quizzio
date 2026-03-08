"""
API REST Flask pour l'application Quizzio.

Fonctionnalités :
- Authentification (inscription, connexion, déconnexion)
- Gestion des quiz (création, consultation)
- Favoris et scores utilisateurs
- Classement des joueurs
- Réinitialisation de mot de passe par e-mail
- Upload de photo de profil
"""

from flask import Flask, jsonify, request, flash, get_flashed_messages, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.exc import IntegrityError
import re
import os

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration de l'application
# ---------------------------------------------------------------------------

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.secret_key = os.getenv('SECRET_KEY')

CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@quizzio.com')

UPLOAD_FOLDER_RELATIVE = 'uploads/profile_pics'
app.config['UPLOAD_FOLDER'] = os.path.join(app.static_folder, UPLOAD_FOLDER_RELATIVE)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 Mo max

FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

mail = Mail(app)
# Sérialiseur unique pour les tokens d'activation et de réinitialisation de mot de passe
serializer = URLSafeTimedSerializer(app.secret_key)

db = SQLAlchemy(app)


# ---------------------------------------------------------------------------
# Modèles de la base de données
# ---------------------------------------------------------------------------

class User(db.Model):
    """Représente un utilisateur de l'application."""
    __tablename__ = 'users'

    username = db.Column(db.String(100), primary_key=True)
    name = db.Column(db.String(100))
    lastname = db.Column(db.String(100))
    mail = db.Column(db.String(100), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    picture = db.Column(db.String(255), nullable=False, default='/static/uploads/profile_pics/defaultPic.png')
    birthday = db.Column(db.Date, nullable=False, default='2001-01-01')
    account_activated = db.Column(db.Boolean, nullable=False, default=False)
    average = db.Column(db.Float, nullable=False, default=0.0)
    total_points = db.Column(db.Float, nullable=False, default=0.0)

    created_quizzes = db.relationship('Quiz', backref='user', lazy=True, cascade='all')
    quiz_interactions = db.relationship('QuizUser', backref='user', lazy='dynamic')
    answers = db.relationship('UserAnswer', backref='user', lazy=True)


class Category(db.Model):
    """Représente une catégorie de quiz (ex : Sciences, Histoire)."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    themes = db.relationship('Theme', backref='category', lazy=True)


class Theme(db.Model):
    """Représente un thème appartenant à une catégorie (ex : Physique dans Sciences)."""
    __tablename__ = 'themes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    quizzes = db.relationship('Quiz', backref='theme', lazy=True)


class Quiz(db.Model):
    """Représente un quiz créé par un utilisateur."""
    __tablename__ = 'quiz'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    theme_id = db.Column(db.Integer, db.ForeignKey('themes.id'), nullable=False)
    timer = db.Column(db.Integer, nullable=False, default=0)
    nb_questions = db.Column(db.SmallInteger, nullable=False)
    difficulty = db.Column(db.SmallInteger, nullable=False)
    created_by = db.Column(
        db.String(100),
        db.ForeignKey('users.username', ondelete='SET DEFAULT'),
        default='admin',
        nullable=False
    )
    user_interactions = db.relationship('QuizUser', backref='quiz', lazy='dynamic')


class Question(db.Model):
    """Représente une question appartenant à un quiz."""
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='CASCADE'), nullable=False)
    nb_answers = db.Column(db.SmallInteger, nullable=False)
    nb_good_answers = db.Column(db.SmallInteger, nullable=False)
    order_in_quiz = db.Column(db.Integer, nullable=False)

    quiz = db.relationship('Quiz', backref='questions', lazy=True)
    answer_choice = db.relationship('AnswerChoice', backref='question', lazy=True)


class AnswerChoice(db.Model):
    """Représente un choix de réponse pour une question."""
    __tablename__ = 'answer_choice'

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(255), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    is_answer = db.Column(db.Boolean, nullable=False)

    user_answer = db.relationship('UserAnswer', backref='answer_choice', lazy=True)


class QuizUser(db.Model):
    """Table d'association entre un utilisateur et un quiz (progression, scores, favoris)."""
    __tablename__ = 'quiz_user'

    user_id = db.Column(db.String(100), db.ForeignKey('users.username', ondelete='RESTRICT'), primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id', ondelete='RESTRICT'), primary_key=True)
    last_score = db.Column(db.Integer, nullable=False, default=0)
    best_score = db.Column(db.Integer, nullable=False, default=0)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    is_finished = db.Column(db.Boolean, nullable=False, default=False)
    last_question_opened_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id', ondelete='RESTRICT'),
        nullable=True,
        default=None
    )


class UserAnswer(db.Model):
    """Enregistre la réponse d'un utilisateur à un choix de réponse donné."""
    __tablename__ = 'user_answer'

    user_id = db.Column(db.String(100), db.ForeignKey('users.username'), primary_key=True)
    answer_choice_id = db.Column(db.Integer, db.ForeignKey('answer_choice.id'), primary_key=True)


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def allowed_file(filename):
    """Vérifie que l'extension du fichier est autorisée pour les photos de profil."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def send_activation_email(user_mail, username):
    """
    Envoie un e-mail d'activation de compte à l'utilisateur.

    Args:
        user_mail (str): Adresse e-mail du destinataire.
        username (str): Nom d'utilisateur (affiché dans l'e-mail).

    Returns:
        bool: True si l'envoi a réussi, False sinon.
    """
    token = serializer.dumps(user_mail, salt='email-activation-salt')
    activate_url = url_for('activate_account', token=token, _external=True, _scheme='http', _host='localhost:5000')

    msg = Message(subject="Activez votre compte Quizzio", recipients=[user_mail])
    msg.body = (
        f"Bonjour {username},\n\n"
        "Merci de vous être inscrit sur Quizzio !\n"
        "Veuillez cliquer sur le lien ci-dessous pour activer votre compte :\n\n"
        f"{activate_url}\n\n"
        "Ce lien expirera dans 24 heures.\n\n"
        "Si vous n'avez pas créé de compte, veuillez ignorer cet e-mail.\n\n"
        "Cordialement,\nL'équipe Quizzio"
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail d'activation : {e}")
        return False


def send_reset_email(user_mail):
    """
    Envoie un e-mail de réinitialisation de mot de passe.

    Args:
        user_mail (str): Adresse e-mail du destinataire.

    Returns:
        bool: True si l'envoi a réussi, False sinon.
    """
    token = serializer.dumps(user_mail, salt='password-reset-salt')
    reset_url = f"{FRONTEND_URL}/reset-password/{token}"

    msg = Message(subject="Réinitialisation de votre mot de passe Quizzio", recipients=[user_mail])
    msg.body = (
        "Bonjour,\n\n"
        "Vous avez demandé à réinitialiser votre mot de passe Quizzio.\n"
        "Cliquez sur le lien ci-dessous pour choisir un nouveau mot de passe :\n\n"
        f"{reset_url}\n\n"
        "Ce lien expirera dans 1 heure.\n\n"
        "Si vous n'êtes pas à l'origine de cette demande, ignorez cet e-mail.\n\n"
        "Cordialement,\nL'équipe Quizzio"
    )
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail de réinitialisation : {e}")
        return False


def get_quiz_user_map(username):
    """
    Retourne un dictionnaire {quiz_id: QuizUser} pour un utilisateur donné.

    Args:
        username (str | None): Le nom d'utilisateur, ou None si non connecté.

    Returns:
        dict: Dictionnaire {quiz_id: QuizUser}, vide si non connecté.
    """
    if not username:
        return {}
    return {qu.quiz_id: qu for qu in QuizUser.query.filter_by(user_id=username).all()}


# ---------------------------------------------------------------------------
# Routes : Authentification
# ---------------------------------------------------------------------------

@app.route('/api/activate/<token>')
def activate_account(token):
    """Active le compte d'un utilisateur à partir du token reçu par e-mail."""
    try:
        email = serializer.loads(token, salt='email-activation-salt', max_age=86400)
    except SignatureExpired:
        flash("Votre lien d'activation a expiré. Veuillez vous connecter pour en demander un nouveau.", "error")
        return redirect(f"{FRONTEND_URL}/sign-in")
    except BadTimeSignature:
        flash("Lien d'activation invalide.", "error")
        return redirect(f"{FRONTEND_URL}/sign-in")
    except Exception as e:
        flash(f"Une erreur est survenue lors de l'activation : {str(e)}", "error")
        return redirect(f"{FRONTEND_URL}/sign-in")

    user = User.query.filter_by(mail=email).first()
    if not user:
        flash("Utilisateur introuvable.", "error")
        return redirect(f"{FRONTEND_URL}/sign-in")

    if user.account_activated:
        flash("Votre compte est déjà activé.", "info")
    else:
        user.account_activated = True
        db.session.commit()
        flash("Votre compte a été activé avec succès !", "success")

    return redirect(f"{FRONTEND_URL}/sign-in")


@app.route("/api/sign-up", methods=['POST'])
def sign_up():
    """
    Inscrit un nouvel utilisateur.

    Body JSON : username, mail, password, name (opt), lastname (opt), birthday (opt, YYYY-MM-DD)
    """
    data = request.get_json()
    username = data.get('username')
    name = data.get('name', '')
    lastname = data.get('lastname', '')
    mail = data.get('mail')
    password = data.get('password')
    birthday = data.get('birthday')
    picture = data.get('picture', '/static/uploads/profile_pics/defaultPic.png')

    if not all([username, mail, password]):
        return jsonify({"message": "Le nom d'utilisateur, l'e-mail et le mot de passe sont requis."}), 400

    if User.query.filter_by(username=username).first() or User.query.filter_by(mail=mail).first():
        return jsonify({"message": "Ce nom d'utilisateur ou cet e-mail est déjà utilisé."}), 400

    birthday_value = None
    if birthday:
        try:
            birthday_value = datetime.strptime(birthday, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'message': 'Date de naissance invalide (format attendu : YYYY-MM-DD).'}), 400

    new_user_data = {
        'username': username,
        'name': name or None,
        'lastname': lastname or None,
        'mail': mail,
        'hashed_password': generate_password_hash(password),
        'picture': picture,
        'account_activated': False,
    }
    if birthday_value:
        new_user_data['birthday'] = birthday_value

    try:
        db.session.add(User(**new_user_data))
        db.session.commit()
        if send_activation_email(mail, username):
            return jsonify({"message": "Inscription réussie. Vérifiez votre e-mail pour activer votre compte."}), 201
        return jsonify({"message": "Inscription réussie, mais l'envoi de l'e-mail a échoué."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Erreur lors de l'inscription : {str(e)}"}), 500


@app.route("/api/sign-in", methods=['POST'])
def sign_in():
    """
    Connecte un utilisateur existant.

    Body JSON : username, password
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return jsonify({"message": "Le nom d'utilisateur et le mot de passe sont requis."}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not check_password_hash(user.hashed_password, password):
        return jsonify({"message": "Nom d'utilisateur ou mot de passe incorrect."}), 400

    if not user.account_activated:
        return jsonify({
            "message": "Votre compte n'est pas activé. Vérifiez votre e-mail.",
            "requires_activation": True
        }), 403

    session['username'] = username
    return jsonify({"message": "Connexion réussie."}), 200


@app.route('/api/logout', methods=['POST'])
def logout():
    """Déconnecte l'utilisateur et supprime toute photo de profil temporaire."""
    if 'staged_profile_pic' in session:
        staged_file_path = os.path.join(app.root_path, session['staged_profile_pic'].lstrip('/'))
        if os.path.exists(staged_file_path):
            try:
                os.remove(staged_file_path)
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier temporaire : {e}")
        del session['staged_profile_pic']

    session.pop('username', None)
    return jsonify({"message": "Déconnexion réussie."})


@app.route('/api/check-auth')
def check_auth():
    """Vérifie si l'utilisateur est connecté."""
    if 'username' in session:
        return jsonify({"authenticated": True, "username": session['username']})
    return jsonify({"authenticated": False})


@app.route("/api/resend-activation", methods=['POST'])
def resend_activation():
    """Renvoie l'e-mail d'activation. Body JSON : username"""
    data = request.get_json()
    username = data.get('username')

    if not username:
        return jsonify({"message": "Le nom d'utilisateur est requis."}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "Utilisateur introuvable."}), 404

    if user.account_activated:
        return jsonify({"message": "Votre compte est déjà activé."}), 200

    if send_activation_email(user.mail, user.username):
        return jsonify({"message": "E-mail d'activation renvoyé avec succès."}), 200
    return jsonify({"message": "Échec de l'envoi. Veuillez réessayer."}), 500


# ---------------------------------------------------------------------------
# Routes : Réinitialisation de mot de passe
# ---------------------------------------------------------------------------

@app.route("/api/reset-password", methods=['POST'])
def reset_password_request():
    """
    Envoie un e-mail de réinitialisation si l'adresse existe.
    Répond toujours de façon neutre pour éviter l'énumération des comptes.

    Body JSON : email
    """
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"message": "L'adresse e-mail est requise."}), 400

    user = User.query.filter_by(mail=email).first()
    if not user:
        return jsonify({"message": "Si un compte est associé à cet e-mail, un lien a été envoyé."}), 200

    if send_reset_email(user.mail):
        return jsonify({"message": "Un lien de réinitialisation a été envoyé à votre adresse e-mail."}), 200
    return jsonify({"message": "Échec de l'envoi. Veuillez réessayer plus tard."}), 500


@app.route('/api/reset-password/<token>', methods=['POST'])
def reset_password_confirm(token):
    """
    Confirme la réinitialisation du mot de passe via token.

    Body JSON : new_password
    """
    try:
        email = serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except SignatureExpired:
        return jsonify({"message": "Le lien a expiré. Veuillez refaire une demande."}), 400
    except BadTimeSignature:
        return jsonify({"message": "Lien invalide."}), 400
    except Exception as e:
        return jsonify({"message": f"Erreur : {str(e)}"}), 500

    new_password = request.get_json().get('new_password')
    if not new_password:
        return jsonify({"message": "Le nouveau mot de passe est requis."}), 400

    user = User.query.filter_by(mail=email).first()
    if not user:
        return jsonify({"message": "Utilisateur introuvable."}), 404

    user.hashed_password = generate_password_hash(new_password)
    try:
        db.session.commit()
        return jsonify({"message": "Mot de passe réinitialisé avec succès."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Échec de la mise à jour : {str(e)}"}), 500


# ---------------------------------------------------------------------------
# Routes : Catégories et thèmes
# ---------------------------------------------------------------------------

@app.route("/api/categories", methods=["GET"])
def get_categories():
    """Retourne toutes les catégories avec leurs thèmes et le nombre de quiz par thème."""
    categories = Category.query.all()
    if not categories:
        return jsonify({"message": "Aucune catégorie trouvée."}), 404

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "themes": [{"name": t.name, "quizCount": len(t.quizzes)} for t in c.themes]
        }
        for c in categories
    ])


@app.route("/api/categories", methods=["POST"])
def create_category():
    """Crée une catégorie (connecté requis). Body JSON : name"""
    if 'username' not in session:
        return jsonify({"message": "Vous devez être connecté."}), 401

    name = request.get_json().get("name", "").strip()
    if not name:
        return jsonify({"message": "Le nom de la catégorie est requis."}), 400

    existing = Category.query.filter_by(name=name).first()
    if existing:
        return jsonify({"message": "Cette catégorie existe déjà.", "category_id": existing.id}), 400

    try:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
        return jsonify({"message": "Catégorie créée avec succès.", "category_id": category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la création.", "error": str(e)}), 500


@app.route("/api/themes", methods=["GET"])
def get_themes():
    """Retourne tous les thèmes disponibles."""
    themes = Theme.query.all()
    if not themes:
        return jsonify({"message": "Aucun thème trouvé."}), 404
    return jsonify([{"id": t.id, "name": t.name, "category_id": t.category_id} for t in themes])


@app.route("/api/themes", methods=["POST"])
def create_theme():
    """Crée un thème (connecté requis). Body JSON : name, category_id"""
    if 'username' not in session:
        return jsonify({"message": "Vous devez être connecté."}), 401

    data = request.get_json()
    name = data.get("name", "").strip()
    category_id = data.get("category_id")

    if not name:
        return jsonify({"message": "Le nom du thème est requis."}), 400
    if not category_id:
        return jsonify({"message": "La catégorie est requise."}), 400
    if Theme.query.filter_by(name=name).first():
        return jsonify({"message": "Ce thème existe déjà."}), 400
    if not Category.query.get(category_id):
        return jsonify({"message": "Catégorie introuvable."}), 404

    try:
        theme = Theme(name=name, category_id=category_id)
        db.session.add(theme)
        db.session.commit()
        return jsonify({"message": "Thème créé avec succès.", "theme_id": theme.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la création.", "error": str(e)}), 500


# ---------------------------------------------------------------------------
# Routes : Quiz
# ---------------------------------------------------------------------------

@app.route("/api/homeQuiz")
def get_home_quizzes():
    """Retourne 3 quiz pour la page d'accueil."""
    username = session.get('username')
    quiz_user_map = get_quiz_user_map(username)
    quizzes = Quiz.query.limit(3).all()

    if not quizzes:
        return jsonify({"message": "Aucun quiz trouvé."}), 404

    return jsonify([
        {
            "id": q.id,
            "name": q.name,
            "is_favorite": quiz_user_map.get(q.id, QuizUser(is_favorite=False)).is_favorite
        }
        for q in quizzes
    ])


@app.route("/api/quiz-by-theme")
def get_quiz_by_theme():
    """Retourne les quiz d'un thème. Query param : theme_name"""
    theme_name = request.args.get("theme_name")
    if not theme_name:
        return jsonify({"message": "Le paramètre theme_name est requis."}), 400

    theme = Theme.query.filter_by(name=theme_name).first()
    if not theme:
        return jsonify({"message": "Thème introuvable."}), 404

    quizzes = Quiz.query.filter_by(theme_id=theme.id).all()
    if not quizzes:
        return jsonify({"message": "Aucun quiz trouvé pour ce thème."}), 404

    quiz_user_map = get_quiz_user_map(session.get('username'))

    return jsonify([
        {
            "id": q.id,
            "name": q.name,
            "difficulty": q.difficulty,
            "is_favorite": quiz_user_map.get(q.id, QuizUser(is_favorite=False)).is_favorite
        }
        for q in quizzes
    ])


@app.route("/api/get_my_quizzes")
def get_my_quizzes():
    """Retourne les quiz créés par l'utilisateur connecté."""
    username = session.get('username')
    if not username:
        return jsonify({'message': 'Vous devez être connecté.'}), 401

    quizzes = Quiz.query.filter_by(created_by=username).all()
    if not quizzes:
        return jsonify({"message": "Aucun quiz trouvé."}), 404

    quiz_user_map = get_quiz_user_map(username)
    return jsonify([
        {
            "id": q.id,
            "name": q.name,
            "is_favorite": quiz_user_map.get(q.id, QuizUser(is_favorite=False)).is_favorite
        }
        for q in quizzes
    ])


@app.route("/api/get_my_favorites")
def get_fav_quizzes():
    """Retourne les quiz favoris de l'utilisateur connecté."""
    username = session.get('username')
    if not username:
        return jsonify({'message': 'Vous devez être connecté.'}), 401

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"message": "Utilisateur introuvable."}), 401

    entries = QuizUser.query.filter_by(user_id=user.username, is_favorite=True).all()
    quizzes = [q for q in (Quiz.query.get(e.quiz_id) for e in entries) if q]

    return jsonify([{"id": q.id, "name": q.name, "is_favorite": True} for q in quizzes])


@app.route('/api/get_my_scores')
def get_my_scores():
    """Retourne les scores de l'utilisateur connecté, regroupés par catégorie."""
    username = session.get('username')
    if not username:
        return jsonify({"message": "Vous devez être connecté pour accéder à vos scores."}), 401

    entries = QuizUser.query.filter_by(user_id=username).all()
    if not entries:
        return jsonify([]), 200

    result = []
    for qu in entries:
        quiz = Quiz.query.get(qu.quiz_id)
        if not quiz:
            continue
        theme = Theme.query.get(quiz.theme_id)
        category = Category.query.get(theme.category_id) if theme else None
        result.append({
            "id": quiz.id,
            "name": quiz.name,
            "is_favorite": qu.is_favorite,
            "score": qu.best_score,
            "category": category.name if category else "Autre"
        })

    return jsonify(result), 200


@app.route("/api/createQuiz", methods=["POST"])
def create_quiz():
    """
    Crée un quiz avec ses questions et réponses (connecté requis).

    Body JSON :
        title, category_name, theme_name, difficulty (1-3),
        timer (opt), questions: [{ label, answer_choices: [{ label, is_answer }] }]
    """
    if 'username' not in session:
        return jsonify({"message": "Vous devez être connecté."}), 401

    data = request.get_json()
    title = data.get("title", "").strip()
    category_name = data.get("category_name", "").strip()
    theme_name = data.get("theme_name", "").strip()
    timer = data.get("timer", 0)
    difficulty = data.get("difficulty", 1)
    questions = data.get("questions", [])

    if not title:
        return jsonify({"message": "Le titre du quiz est requis."}), 400
    if not category_name or not theme_name:
        return jsonify({"message": "Le thème et la catégorie sont requis."}), 400

    # Récupérer ou créer la catégorie
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        try:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Erreur lors de la création de la catégorie.", "error": str(e)}), 500

    # Récupérer ou créer le thème
    theme = Theme.query.filter_by(name=theme_name, category_id=category.id).first()
    if not theme:
        try:
            theme = Theme(name=theme_name, category_id=category.id)
            db.session.add(theme)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Erreur lors de la création du thème.", "error": str(e)}), 500

    # Filtrer les questions valides
    valid_questions = [
        q for q in questions
        if q.get("label", "").strip()
        and len(q.get("answer_choices", [])) >= 2
        and any(ac.get("is_answer", False) for ac in q.get("answer_choices", []))
        and all(ac.get("label", "").strip() for ac in q.get("answer_choices", []))
    ]

    if not valid_questions:
        return jsonify({"message": "Au moins une question valide est requise."}), 400

    try:
        quiz = Quiz(
            name=title,
            theme_id=theme.id,
            timer=timer,
            nb_questions=len(valid_questions),
            difficulty=difficulty,
            created_by=session['username']
        )
        db.session.add(quiz)
        db.session.flush()

        for index, q in enumerate(valid_questions, 1):
            nb_good = sum(1 for ac in q["answer_choices"] if ac.get("is_answer", False))
            question = Question(
                quiz_id=quiz.id,
                label=q["label"],
                nb_good_answers=nb_good,
                nb_answers=len(q["answer_choices"]),
                order_in_quiz=index
            )
            db.session.add(question)
            db.session.flush()

            for ac in q["answer_choices"]:
                if ac.get("label", "").strip():
                    db.session.add(AnswerChoice(
                        question_id=question.id,
                        label=ac["label"].strip(),
                        is_answer=ac.get("is_answer", False)
                    ))

        db.session.commit()
        return jsonify({"message": "Quiz créé avec succès.", "quiz_id": quiz.id}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la création du quiz.", "error": str(e)}), 500


@app.route("/api/quizzes/<int:quiz_id>/questions")
def get_quiz_questions(quiz_id):
    """Retourne les questions d'un quiz dans l'ordre."""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz introuvable."}), 404

    questions = Question.query.filter_by(quiz_id=quiz_id).order_by(Question.order_in_quiz).all()
    if not questions:
        return jsonify({"message": "Aucune question trouvée pour ce quiz."}), 404

    return jsonify([
        {
            "id": q.id,
            "label": q.label,
            "nb_good_answers": q.nb_good_answers,
            "order_in_quiz": q.order_in_quiz,
            "answer_choice": [
                {"id": ac.id, "label": ac.label, "is_answer": ac.is_answer}
                for ac in q.answer_choice
            ]
        }
        for q in questions
    ])


@app.route("/api/quizzes/<int:quiz_id>/finish", methods=["POST"])
def finish_quiz(quiz_id):
    """
    Enregistre le score et met à jour les statistiques de l'utilisateur.

    Body JSON : user_id, score (nombre de bonnes réponses)
    """
    if 'username' not in session:
        return jsonify({"message": "Vous devez être connecté."}), 401

    data = request.get_json()
    user_id = data.get("user_id")
    score = data.get("score")

    if not user_id or score is None:
        return jsonify({"message": "Données manquantes."}), 400
    if user_id != session['username']:
        return jsonify({"message": "Action non autorisée."}), 403

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({"message": "Quiz introuvable."}), 404

    nb_questions = quiz.nb_questions

    quiz_user = QuizUser.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not quiz_user:
        quiz_user = QuizUser(user_id=user_id, quiz_id=quiz_id)
        db.session.add(quiz_user)
        db.session.flush()

    score_pct = (score * 100 / nb_questions) if nb_questions != 0 else 0
    previous_best_raw = (quiz_user.best_score * nb_questions) / 100
    points_gained = max(0, score - previous_best_raw)

    quiz_user.last_score = score_pct
    quiz_user.best_score = max(quiz_user.best_score, score_pct)
    quiz_user.is_finished = True

    user = User.query.filter_by(username=user_id).first()
    if not user:
        return jsonify({"message": "Utilisateur introuvable."}), 404

    user.total_points += points_gained

    finished = QuizUser.query.filter_by(user_id=user_id, is_finished=True).all()
    user.average = sum(q.best_score for q in finished) / len(finished) if finished else 0.0

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erreur lors de la mise à jour.", "error": str(e)}), 500

    return jsonify({
        "message": "Quiz terminé.",
        "last_score": quiz_user.last_score,
        "total_points": user.total_points,
        "average": user.average
    }), 200


# ---------------------------------------------------------------------------
# Routes : Réponses utilisateur
# ---------------------------------------------------------------------------

@app.route("/api/user-answers", methods=["POST"])
def save_user_answer():
    """
    Enregistre les réponses d'un utilisateur pour une question (remplace les précédentes).

    Body JSON : user_id, answer_choice_ids (list[int])
    """
    if 'username' not in session:
        return jsonify({"message": "Vous devez être connecté."}), 401

    data = request.get_json()
    user_id = data.get("user_id")
    answer_choice_ids = data.get("answer_choice_ids")

    if not user_id or not answer_choice_ids:
        return jsonify({"message": "Données manquantes."}), 400
    if user_id != session['username']:
        return jsonify({"message": "Action non autorisée."}), 403

    question_ids = (
        db.session.query(AnswerChoice.question_id)
        .filter(AnswerChoice.id.in_(answer_choice_ids))
        .distinct()
        .all()
    )
    if len(question_ids) != 1:
        return jsonify({"message": "Tous les choix doivent appartenir à la même question."}), 400

    question_id = question_ids[0][0]

    UserAnswer.query.filter(
        UserAnswer.user_id == user_id,
        UserAnswer.answer_choice_id.in_(
            db.session.query(AnswerChoice.id).filter_by(question_id=question_id)
        )
    ).delete()

    for answer_choice_id in answer_choice_ids:
        db.session.add(UserAnswer(user_id=user_id, answer_choice_id=answer_choice_id))

    db.session.commit()
    return jsonify({"message": "Réponses enregistrées."}), 200


# ---------------------------------------------------------------------------
# Routes : Favoris
# ---------------------------------------------------------------------------

@app.route("/api/toggle-favorite", methods=["POST"])
def toggle_favorite():
    """Active/désactive le favori d'un quiz. Body JSON : quiz_id"""
    username = session.get('username')
    if not username:
        return jsonify({'message': 'Vous devez être connecté pour gérer vos favoris.'}), 401

    quiz_id = request.get_json().get('quiz_id')
    if not quiz_id:
        return jsonify({"message": "L'identifiant du quiz est requis."}), 400
    if not Quiz.query.get(quiz_id):
        return jsonify({'message': 'Quiz introuvable.'}), 404

    quiz_user = QuizUser.query.get((username, quiz_id))
    if quiz_user:
        quiz_user.is_favorite = not quiz_user.is_favorite
    else:
        quiz_user = QuizUser(
            user_id=username,
            quiz_id=quiz_id,
            is_favorite=True,
            last_score=0,
            best_score=0,
            is_finished=False,
            last_question_opened_id=None
        )
        db.session.add(quiz_user)

    db.session.commit()
    return jsonify({"message": "Favori mis à jour.", "is_favorite": quiz_user.is_favorite}), 200


# ---------------------------------------------------------------------------
# Routes : Classement
# ---------------------------------------------------------------------------

@app.route("/api/ranking")
def get_ranking():
    """Classement des utilisateurs. Query param : sort_by ('points' ou 'average')"""
    sort_by = request.args.get('sort_by', 'points')
    if sort_by not in ['points', 'average']:
        return jsonify({"message": "Paramètre sort_by invalide. Utilisez 'points' ou 'average'."}), 400

    order_column = User.total_points.desc() if sort_by == 'points' else User.average.desc()
    users = User.query.filter(User.username != 'admin').order_by(order_column).all()

    return jsonify([
        {"username": u.username, "profilePic": u.picture, "points": u.total_points, "average": u.average}
        for u in users
    ])


# ---------------------------------------------------------------------------
# Routes : Paramètres du compte
# ---------------------------------------------------------------------------

@app.route('/api/settings', methods=['GET', 'PATCH'])
def settings():
    """
    GET  : Retourne le profil de l'utilisateur connecté.
    PATCH: Met à jour le profil (name, mail, birthday, password, profilePic).
    """
    if not session.get('username'):
        return jsonify({'message': 'Vous devez être connecté.'}), 401

    user = User.query.filter_by(username=session["username"]).first()
    if not user:
        return jsonify({'message': 'Utilisateur introuvable.'}), 404

    default_pic = url_for('static', filename='uploads/profile_pics/defaultPic.png')

    if request.method == 'GET':
        return jsonify({
            'username': user.username,
            'name': user.name or '',
            'mail': user.mail or '',
            'birthday': user.birthday.strftime('%Y-%m-%d') if user.birthday else '',
            'profilePic': user.picture or default_pic
        }), 200

    data = request.get_json() or {}
    if not data:
        return jsonify({'message': 'Aucune donnée fournie.'}), 400

    if 'name' in data:
        if not isinstance(data['name'], str) or len(data['name']) > 100:
            return jsonify({'message': 'Nom invalide (max 100 caractères).'}), 400
        user.name = data['name'] or None

    if 'mail' in data:
        if not re.match(r'^\S+@\S+\.\S+$', data.get('mail', '')):
            return jsonify({'message': 'Adresse e-mail invalide.'}), 400
        if User.query.filter_by(mail=data['mail']).first() and data['mail'] != user.mail:
            return jsonify({'message': 'Cette adresse e-mail est déjà utilisée.'}), 400
        user.mail = data['mail']

    if 'birthday' in data:
        if data['birthday']:
            try:
                user.birthday = datetime.strptime(data['birthday'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'message': 'Date invalide (format attendu : YYYY-MM-DD).'}), 400
        else:
            user.birthday = None

    if 'password' in data:
        if not isinstance(data['password'], str) or len(data['password']) < 8:
            return jsonify({'message': 'Le mot de passe doit contenir au moins 8 caractères.'}), 400
        user.hashed_password = generate_password_hash(data['password'])

    if 'profilePic' in data:
        if not data.get('profilePic'):
            return jsonify({'message': 'URL de photo de profil invalide.'}), 400
        if user.picture and user.picture != default_pic:
            old_path = os.path.join(app.root_path, user.picture.lstrip('/'))
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception as e:
                    print(f"Erreur lors de la suppression de l'ancienne photo : {e}")
        user.picture = data['profilePic']
        session.pop('staged_profile_pic', None)

    try:
        db.session.commit()
        return jsonify({
            'message': 'Modifications enregistrées.',
            'username': user.username,
            'name': user.name or '',
            'mail': user.mail or '',
            'birthday': user.birthday.strftime('%Y-%m-%d') if user.birthday else '',
            'profilePic': user.picture or default_pic
        }), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Erreur : adresse e-mail déjà utilisée.'}), 400
    except Exception:
        db.session.rollback()
        return jsonify({'message': 'Erreur serveur.'}), 500


@app.route('/api/upload-profile-pic', methods=['POST'])
def upload_profile_pic():
    """
    Téléverse une photo de profil temporaire (staged).
    Elle sera confirmée lors de la sauvegarde via PATCH /api/settings.
    """
    if not session.get('username'):
        return jsonify({'message': 'Vous devez être connecté.'}), 401

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return jsonify({'message': 'Utilisateur introuvable.'}), 404

    if 'profilePic' not in request.files:
        return jsonify({'message': 'Aucun fichier fourni.'}), 400

    file = request.files['profilePic']
    if not file.filename:
        return jsonify({'message': 'Aucun fichier sélectionné.'}), 400
    if not allowed_file(file.filename):
        return jsonify({'message': 'Extension non autorisée (png, jpg, jpeg, gif).'}), 400

    # Supprimer l'ancienne photo temporaire si elle existe
    if 'staged_profile_pic' in session:
        old_path = os.path.join(app.root_path, session['staged_profile_pic'].lstrip('/'))
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"Erreur lors de la suppression du fichier temporaire précédent : {e}")

    filename = secure_filename(f"{user.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}")
    filename += os.path.splitext(file.filename)[1]
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    try:
        file.save(file_path)
        staged_url = url_for('static', filename=f'{UPLOAD_FOLDER_RELATIVE}/{filename}')
        session['staged_profile_pic'] = staged_url
        return jsonify({'message': 'Fichier téléversé, prêt à être enregistré.', 'profilePic': staged_url}), 200
    except Exception as e:
        return jsonify({'message': f'Erreur lors de la sauvegarde : {e}'}), 500


@app.route('/api/cancel-profile-pic', methods=['POST'])
def cancel_profile_pic():
    """Annule le téléversement temporaire et supprime le fichier."""
    if not session.get('username'):
        return jsonify({'message': 'Vous devez être connecté.'}), 401

    if 'staged_profile_pic' not in session:
        return jsonify({'message': 'Aucun fichier temporaire à supprimer.'}), 200

    path = os.path.join(app.root_path, session['staged_profile_pic'].lstrip('/'))
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            print(f"Erreur lors de la suppression : {e}")

    del session['staged_profile_pic']
    return jsonify({'message': 'Changement de photo annulé.'}), 200


# ---------------------------------------------------------------------------
# Routes : Messages flash
# ---------------------------------------------------------------------------

@app.route('/api/flashed-messages')
def get_flashed_messages_api():
    """Retourne les messages flash en attente."""
    return jsonify({"messages": get_flashed_messages()})


@app.route("/api/flash-404", methods=["POST"])
def flash_404_message():
    """Déclenche un message flash pour les redirections depuis une page 404."""
    flash("Page non trouvée. Vous avez été redirigé vers l'accueil.")
    return jsonify({"status": "flashed"}), 200

# Crée la base de données si elle n'existe pas
def create_database_if_not_exists():
    import pymysql
    db_name = os.getenv('DB_NAME')
    try:
        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USERNAME'),
            password=os.getenv('DB_PASSWORD'),
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        connection.close()
        print(f"Base de données '{db_name}' prête.")
    except Exception as e:
        print(f"Impossible de créer la base de données : {e}")
        raise

if __name__ == "__main__":
    create_database_if_not_exists()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
