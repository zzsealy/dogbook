from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, ResetForm, ChangePasswordForm
from .. import mail
from flask import current_app
from flask_mail import Message
import os
from ..setting import redirect_back


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(u'你已经登陆了！', 'info')
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):    # 把原url保存在next参数里，如果没有就重定向到首页。
                next = url_for('main.index')
            return redirect(next)
        flash('用户名或密码错误！')
    return render_template('auth/login.html', form=form)

@auth.route('/reset', methods=['GET', 'POST'])
def reset():
    app = current_app._get_current_object() # 获取当前的对象
    form = ResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if not user:
            flash("用户不存在！")
        else:
            msg = Message('重置密码', sender=os.environ.get('MAIL_USERNAME'), recipients=[user.email])
            msg.body = '重置密码'
            new_password = '666666'
            msg.html = '新密码是:{}'.format(new_password)
            try:
                with app.app_context():
                    mail.send(msg)
                user.password = new_password
                db.session.add(user)
                db.session.commit()
                flash('已发送邮件!')
                return redirect(url_for('auth.login'))
            except :
                flash('发生错误！')
        
    return render_template('auth/reset.html', form=form)


@auth.route('/logout')
def logout():
    logout_user()
    flash("退出登录！")
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data.lower(),
                    nickname=form.nickname.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('你现在可以登陆了！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash("你的密码已经被更新！")
            return redirect(url_for('main.index'))
        else:
            flash("旧密码错误！")
    return render_template("auth/changepassword.html", form=form)