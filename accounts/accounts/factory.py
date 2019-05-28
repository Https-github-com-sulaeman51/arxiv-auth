"""Application factory for accounts app."""

from flask import Flask

from arxiv import vault
from arxiv.base import Base
from arxiv.base.middleware import wrap
from arxiv.users import auth

from accounts.routes import ui
from accounts.services import SessionStore, legacy, users


def create_web_app() -> Flask:
    """Initialize and configure the accounts application."""
    app = Flask('accounts')
    app.config.from_pyfile('config.py')

    SessionStore.init_app(app)
    legacy.init_app(app)
    users.init_app(app)

    app.register_blueprint(ui.blueprint)
    Base(app)    # Gives us access to the base UI templates and resources.
    auth.Auth(app)  # Handless sessions and authn/z.

    middleware = [auth.middleware.AuthMiddleware]
    if app.config['VAULT_ENABLED']:
        middleware.insert(0, vault.middleware.VaultMiddleware)
    wrap(app, middleware)
    if app.config['VAULT_ENABLED']:
        app.middlewares['VaultMiddleware'].update_secrets({})

    if app.config['CREATE_DB']:
        legacy.create_all()
        users.create_all()
    return app
