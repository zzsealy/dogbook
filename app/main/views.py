from flask import render_template, redirect, url_for, abort, flash, request, current_app
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, EditProfileAdminForm, PostForm
from .. import db
from ..models import Role, User, Permission, Post
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(
            title = form.title.data,
            body = form.body.data,
            author = current_user._get_current_object()
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
                    page, per_page=current_app.config['PER_PAGE'],
                    error_out = False
                    )
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts, pagination=pagination)


@main.route('/user/<nickname>')
def user(nickname):
    user = User.query.filter_by(nickname=nickname).first_or_404()
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


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


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', posts=[post])  # 传入的是列表，为了使用局部模板。


#编辑文章的路由
@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)  # 获取文章
    if  current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash("文章已经被更新")
        return redirect(url_for('.post', id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    return render_template('edit_post.html', form=form)