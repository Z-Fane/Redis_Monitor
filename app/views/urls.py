from flask import Blueprint

from app.views.views import IndexView

api = Blueprint('api', __name__)

api.add_url_rule('/', view_func=IndexView.as_view('index'))