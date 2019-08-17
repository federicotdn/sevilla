from flask_sqlalchemy import SQLAlchemy

SESSION_ID_BITS = 256

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.String(SESSION_ID_BITS / 4), primary_key=True)
    expiration = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return "<User %r>" % self.username
