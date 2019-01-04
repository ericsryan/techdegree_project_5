# @app.route('/create-tag', methods=("GET", "POST"))
# @login_required
# def create_tag():
#     """Create a new tag for the current user."""
#     form = forms.TagForm()
#     if form.validate_on_submit():
#         try:
#             models.Tag.get(user=g.user._get_current_object(),
#                            tag=form.tag.data)
#             flash("That tag already exists")
#             return redirect(url_for('entries'))
#         except Exception:
#             models.Tag.create(user=g.user._get_current_object(),
#                               tag=form.tag.data)
#             return redirect(url_for('entries'))
#     return render_template('tags.html', form=form)





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


{% macro render_unattached_tags() %}


{% macro render_attached_tags(entry, entry_tags) %}
<div class="">
    {% if entry_tags.errors %}
        {% for error in entry_tags.errors %}
            <div class="">{{ error }}</div>
        {% endfor %}
    {% endif %}
    {% if entry_tags %}
    <p>{% for tag in entry_tags %}{% if tag.entry.id == entry.id %}• <a href="{{ url_for('entries', tag=tag.tag.tag) }}">{{ tag.tag.tag }}</a>{% endif %} {% endfor %}</p>
    {% endif %}
</div>
{% endmacro %}


{{ render_attached_tags(entry, entry_tags) }}<br><br>


, entry_tags


<p><a href="{{ url_for('edit_tags', slug=entry.slug) }}">Add/Edit Tags</a></p>


<div class="entry">
    {% if tags %}
        <h3>Tagged with: </h3>
        {{ render_attached_tags(entry, entry_tags) }}
    {% endif %}
</div>
