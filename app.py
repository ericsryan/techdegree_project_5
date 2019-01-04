from flask import Flask, flash, g, redirect, render_template, url_for
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)

import forms
import models

DEBUG = True

app = Flask(__name__)
app.secret_key = 'bfe345^789IkjHgfrE34%6&8iJhgfDwe3$5^&8IJ'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(userid):
    """Lookup user."""
    try:
        return models.User.get(models.User.id == userid)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.user = current_user
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user."""
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You registered and are now logged in as "
              "{}".format(form.username.data), "success")
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        login_user(models.User.get(models.User.username == form.username.data))
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Login existing user."""
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.username == form.username.data)
        except models.DoesNotExist:
            flash("Your username or password doesn't match.", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("You have been logged in.", "success")
                return redirect(url_for('index'))
            else:
                flash("Your email or password doesn't match.", "error")
    return render_template('login.html', form=form)


@app.route('/entry', methods=('GET', 'POST'))
@login_required
def add():
    """Create a new journal entry."""
    form = forms.EntryForm()
    if form.validate_on_submit():
        flash("Your entry has been saved.", "success")
        models.Entry.create(
            user=g.user._get_current_object(),
            slug=models.generate_slug(form.title.data),
            title=form.title.data,
            timestamp=form.timestamp.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data,
            resources=form.resources.data
        )
        return redirect(url_for('index'))
    return render_template('add.html', form=form)


@app.route('/entries/edit/<slug>', methods=('GET', 'POST'))
@login_required
def edit(slug):
    """Edit an existing journal entry."""
    entry = models.Entry.get(models.Entry.slug == slug)
    form = forms.EntryForm(obj=entry)
    if form.validate_on_submit():
        flash("Your entry has been saved.", "success")
        models.Entry.update(
            slug=models.generate_slug(form.title.data),
            title=form.title.data,
            timestamp=form.timestamp.data,
            time_spent=form.time_spent.data,
            learned=form.learned.data,
            resources=form.resources.data
        ).where(models.Entry.slug == slug).execute()
        return redirect(url_for('index'))
    return render_template('edit.html', form=form)


@app.route('/entries', methods=('GET', 'POST'))
def entries():
    entries = current_user.get_entries()
    entry_tags = models.EntryTag.select()
    entry_count = current_user.get_entry_count()
    return render_template('entries.html',
                           entries=entries,
                           entry_tags=entry_tags,
                           entry_count=entry_count)


@app.route('/entries/<slug>')
@login_required
def details(slug):
    entry = models.Entry.get(models.Entry.slug == slug)
    entry_tags = models.EntryTag.select()
    tags = models.get_entry_tags(entry)
    return render_template('detail.html',
                           entry=entry,
                           entry_tags=entry_tags,
                           tags=tags)


@app.route('/create-tag', methods=("GET", "POST"))
@login_required
def create_tag():
    """Create a new tag for the current user."""
    form = forms.TagForm()
    if form.validate_on_submit():
        try:
            models.Tag.get(user=g.user._get_current_object(),
                           tag=form.tag.data)
            flash("That tag already exists")
            return redirect(url_for('entries'))
        except Exception:
            models.Tag.create(user=g.user._get_current_object(),
                              tag=form.tag.data)
            return redirect(url_for('entries'))
    return render_template('new_tag.html', form=form)


@app.route('/delete-tag', methods=("GET", "POST"))
@login_required
def delete_tag():
    pass


@app.route('/attach-tag/<entry_slug>/<tag>')
@login_required
def attach_tag(entry_slug, tag):
    try:
        entry = models.Entry.get(models.Entry.slug**entry_slug)
        tag = models.Tag.get(models.Tag.tag**tag)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.EntryTag.create(
                entry=entry,
                tag=tag
            )
        except models.IntegrityError:
            pass
    return redirect(url_for('index'))


@app.route('/remove-tag/<entry_slug>/<tag>')
@login_required
def remove_tag(entry_slug, tag):
    try:
        entry = models.Entry.get(models.Entry.slug**entry_slug)
        tag = models.Tag.get(models.Tag.tag**tag)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.EntryTag.get(
                entry=entry,
                tag=tag
            ).delete_instance()
        except models.IntegrityError:
            pass
    return redirect(url_for('index'))



@app.route('/delete/<slug>')
@login_required
def delete(slug):
    entry = models.Entry.get(models.Entry.slug == slug)
    entry.delete_instance()
    flash("The entry has been deleted")
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('index'))


@app.route('/')
def index():
    """Display the main page."""
    if current_user.is_authenticated:
        entries = current_user.get_index_entries()
        entry_tags = models.EntryTag.select()
        entry_count = current_user.get_entry_count()
        return render_template('index.html',
                               entries=entries,
                               entry_tags=entry_tags,
                               entry_count=entry_count)
    else:
        return render_template('index.html')


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='test_user',
            email='test@test.com',
            password='password'
        )
    except ValueError:
        pass
    app.run(debug=DEBUG)
