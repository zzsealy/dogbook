import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Role

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)




@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.cli.command()
@click.argument('test_names', nargs=-1)
def test(test_names):
    """Run the unit tests."""
    import unittest
    if test_names:
        tests = unittest.TestLoader().loadTestsFromNames(test_names)
    else:
        tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
@click.option('--drop', is_flag=True, help='create after drop.')
def initdb(drop):
    """ 初始化数据库 """
    if drop:
        click.confirm('这个操作会删除数据库并且重新创建数据库， 你确定要继续吗？', abort=True)
        db.drop_all()
        click.echo('数据库已经删除。')
    db.create_all()
    click.echo('数据库重新创建。')
