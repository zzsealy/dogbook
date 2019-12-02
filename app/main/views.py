from flask import render_template, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import Role, User
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    return render_template('user.html', user=user)


# 个人用户的资料编辑路由
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()    
    if form.validate_on_submit():
        current_user.nickname = form.nickname.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('你的个人资料已经更新')
        return redirect(url_for('.user', nickname=current_user.nickname))
    form.nickname.data = current_user.nickname
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


# 管理员用户的资料编辑路由
@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.nickname = form.nickname.data
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("个人资料已被更新", 'warning')
        return redirect(url_for('.user', nickname=user.nickname))
    form.email.data = user.email
    form.nickname.data = user.nickname
    # 因为choice属性中设置的元组列表使用数字标识符表示各选项。
    form.role.data = user.role_id
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)