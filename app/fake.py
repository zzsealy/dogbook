from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Post


def users(count=100):
    fake = Faker(locale='zh_CN')
    i = 0
    while i < count:
        u = User(
            email=fake.email(),
            nickname=fake.name(),  # 昵称
            password='123456',
            about_me=fake.text(),
            member_since=fake.past_date()
        )
        db.session.add(u)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker(locale='zh_CN')
    user_count = User.query.count()
    for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(
                title=fake.sentence(),  # 随机生成一句话
                body=fake.text(),
                timestamp=fake.past_date(),
                author=u)
            db.session.add(p)
    db.session.commit()
