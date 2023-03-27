from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, \
    EmptyForm, PostForm, TodoForm, EditTodoStatusForm
from app.models import User, Post, Todo

# Übernommen aus den Beispielen von Miguel Grinberg
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='Explore', posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

# Eigenentwicklung
@app.route('/todos', methods=['GET', 'POST'])
@login_required
def todos():
    todo_form = TodoForm()
    todo_form.assigned_to.choices = [(user.id, user.username) for user in User.query.all()]
    if todo_form.validate_on_submit():
        todo = Todo(task=todo_form.task.data, due_date=todo_form.due_date.data, status=todo_form.status.data
        , assigned_to_id=todo_form.assigned_to.data, user_id=current_user.id)
        db.session.add(todo)
        db.session.commit()
        flash('Todo created successfully', 'success')
        return redirect(url_for('todos'))
    users = User.query.all()
    page = request.args.get('page', 1, type=int)
    todos = Todo.query.order_by(Todo.due_date.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('todos', page=todos.next_num) \
        if todos.has_next else None
    prev_url = url_for('todos', page=todos.prev_num) \
        if todos.has_prev else None
    return render_template('todos.html', title='All Tasks', users=users, todos=todos.items, todo_form=todo_form, next_url=next_url, prev_url=prev_url)

# Eigenentwicklung   
@app.route('/todos/<int:todo_id>/edit_status', methods=['GET', 'POST'])
@login_required
def edit_todo_status(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first_or_404()
    if current_user.id != todo.assigned_to_id:
        abort(403)
    form = EditTodoStatusForm()
    if form.validate_on_submit():
        todo.status = form.status.data
        db.session.commit()
        flash('Todo status has been updated!', 'success')
        return redirect(url_for('todos'))
    elif request.method == 'GET':
        form.status.data = todo.status
    return render_template('edit_todo_status.html', title='Edit Todo Status', form=form, todo=todo)

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    form = EmptyForm()
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url, form=form)

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)

# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash('You are following {}!'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))


# Übernommen aus den Beispielen von Miguel Grinberg
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash('User {} not found.'.format(username))
            return redirect(url_for('index'))
        if user == current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash('You are not following {}.'.format(username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))

# Eigenentwicklung
@app.route('/admin_posts')
@login_required
def admin_posts():
    # Check if the user is an admin or not and abort with 403 if not
    if current_user.is_admin is False:
        abort(403)
    users = User.query.all()
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('admin_posts', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('admin_posts', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('admin_posts.html', title='Admin Posts', posts=posts.items, current_user=current_user, users=users,
                           next_url=next_url, prev_url=prev_url)

# Eigenentwicklung
@app.route('/admin_delete_post/<int:id>', methods=['POST'])
@login_required
def admin_delete_post(id):
    # Check if the user is an admin or not and abort with 403 if not
    post = Post.query.get_or_404(id)
    if current_user.is_admin is False:
            abort(403)
    
    # Delete the user from the database
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.')
    return redirect(url_for('admin_posts'))


# Eigenentwicklung
@app.route('/admin_users')
@login_required
def admin_users():
    # Check if the user is an admin or not and abort with 403 if not
    if current_user.is_admin is False:
        abort(403)
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.id.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('admin_users', username=current_user.username, page=users.next_num) \
        if users.has_next else None
    prev_url = url_for('admin_users', username=current_user.username, page=users.prev_num) \
        if users.has_prev else None
    return render_template('admin_users.html', title='Users Admin', current_user=current_user, users=users,
                           next_url=next_url, prev_url=prev_url)

# Eigenentwicklung
@app.route('/admin_delete_user/<int:id>', methods=['POST'])
@login_required
def admin_delete_user(id):
    # Check if the user is an admin or not and abort with 403 if not
    user = User.query.get_or_404(id)
    if current_user.is_admin is False:
            abort(403)
    
    # Delete the user from the database
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.')
    return redirect(url_for('admin_users'))

# Eigenentwicklung
@app.route('/admin_todos')
@login_required
def admin_todos():
    # Check if the user is an admin or not and abort with 403 if not
    if current_user.is_admin is False:
        abort(403)
    page = request.args.get('page', 1, type=int)
    todos = Todo.query.order_by(Todo.id.desc()).paginate(
        page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('admin_todos', username=current_user.username, page=todos.next_num) \
        if todos.has_next else None
    prev_url = url_for('admin_todos', username=current_user.username, page=todos.prev_num) \
        if todos.has_prev else None
    return render_template('admin_todos.html', title='Todos Admin', current_user=current_user, todos=todos,
                           next_url=next_url, prev_url=prev_url)

# Eigenentwicklung
@app.route('/admin_delete_todo/<int:id>', methods=['POST'])
@login_required
def admin_delete_todo(id):
    # Check if the user is an admin or not and abort with 403 if not
    todo = Todo.query.get_or_404(id)
    if current_user.is_admin is False:
            abort(403)
    
    # Delete the user from the database
    db.session.delete(todo)
    db.session.commit()
    flash('Todo deleted.')
    return redirect(url_for('admin_todos'))
