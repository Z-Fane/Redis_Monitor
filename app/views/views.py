from flask import render_template
from flask.views import MethodView


class IndexView(MethodView):
    """首页视图
    """

    def get(self):
        """渲染模板
        """
        return render_template('index.html')