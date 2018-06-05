from app import create_app
from app.models import db

app=create_app()

@app.cli.command()
def init_db():
    """初始化数据库
    """
    print("sqlite3 database file is %s" % app.config['SQLALCHEMY_DATABASE_URI'])
    db.create_all()

