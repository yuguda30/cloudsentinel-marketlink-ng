import os
from datetime import datetime

from flask import Flask
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO, join_room, emit

from config import Config
from models import db, User, Message


# -----------------------------
# Extensions
# -----------------------------

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Please login to continue."
login_manager.login_message_category = "warning"

socketio = SocketIO(
    cors_allowed_origins="*",
    async_mode="threading"
)

online_users = set()


# -----------------------------
# User Loader
# -----------------------------

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None


# -----------------------------
# App Factory
# -----------------------------

def create_app():

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # ---------------------------------
    # Update User Last Seen
    # ---------------------------------

    @app.before_request
    def update_last_seen():

        if current_user.is_authenticated:

            try:
                current_user.last_seen = datetime.utcnow()
                db.session.commit()
            except Exception:
                db.session.rollback()

    # ---------------------------------
    # Notification Count
    # ---------------------------------

    @app.context_processor
    def inject_notifications():

        if current_user.is_authenticated:

            unread_count = Message.query.filter_by(
                receiver_id=current_user.id,
                is_read=False
            ).count()

            return dict(
                unread_count=unread_count,
                unread_messages=unread_count
            )

        return dict(
            unread_count=0,
            unread_messages=0
        )

    # ---------------------------------
    # Blueprints
    # ---------------------------------

    from routes.auth_routes import auth_bp
    from routes.main_routes import main_bp
    from routes.listing_routes import listing_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.chat_routes import chat_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(listing_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(chat_bp)

    # ---------------------------------
    # Create Database Tables
    # ---------------------------------

    with app.app_context():
        db.create_all()

    return app


# -----------------------------
# Socket Events
# -----------------------------

@socketio.on("user_online")
def user_online(data):

    user_id = str(data.get("user_id"))

    if user_id:

        online_users.add(user_id)

        join_room(f"user-{user_id}")

        emit(
            "online_users",
            list(online_users),
            broadcast=True
        )


@socketio.on("join_chat")
def join_chat(data):

    room = data.get("room")
    user_id = str(data.get("user_id"))

    if room:
        join_room(room)

    if user_id:

        online_users.add(user_id)

        join_room(f"user-{user_id}")

        emit(
            "online_users",
            list(online_users),
            broadcast=True
        )


@socketio.on("send_message")
def send_message(data):

    try:

        room = data.get("room")

        sender_id = int(data.get("sender_id"))
        receiver_id = int(data.get("receiver_id"))
        listing_id = int(data.get("listing_id"))

        content = data.get("content", "").strip()

        if not content:
            return

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            listing_id=listing_id,
            content=content
        )

        db.session.add(message)
        db.session.commit()

        payload = {
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "listing_id": listing_id,
            "content": content,
            "time": message.created_at.strftime("%H:%M")
        }

        emit(
            "receive_message",
            payload,
            room=room
        )

        emit(
            "new_message_notification",
            payload,
            room=f"user-{receiver_id}"
        )

    except Exception as e:

        db.session.rollback()

        print("Socket Message Error:", e)


# -----------------------------
# Run App
# -----------------------------

app = create_app()

if __name__ == "__main__":
    socketio.run(
        app,
        debug=True
    )
