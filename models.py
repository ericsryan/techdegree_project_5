import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *
from slugify import UniqueSlugify

DATABASE = SqliteDatabase('journal.db')


def generate_slug(title):
    """Generate unique slug from entry title."""
    slug = UniqueSlugify(to_lower=True)
    while True:
        new_slug = slug(title)
        if Entry.get_or_none(Entry.slug == new_slug):
            continue
        else:
            return new_slug


def get_entry_tags(entry):
    """Get all tags attached to the current entry."""
    return EntryTag.select().where(EntryTag.entry_id == entry.id)


def get_attach_tags(slug, tags):
    """Get tags that may be added to the current entry."""
    attach_tags = []
    entry = Entry.get(Entry.slug == slug)
    for tag in tags:
        if EntryTag.get_or_none((EntryTag.tag_id == tag.id) & (EntryTag.entry_id == entry.id)):
            continue
        else:
            attach_tags.append(tag)
    return attach_tags


def get_remove_tags(slug, tags):
    """Get tags that may be removed to the current entry."""
    remove_tags = []
    entry = Entry.get(Entry.slug == slug)
    for tag in tags:
        if EntryTag.get_or_none((EntryTag.tag_id == tag.id) & (EntryTag.entry_id == entry.id)):
            remove_tags.append(tag)
        else:
            continue
    return remove_tags


def get_delete_tags(slug, tags):
    """Get tags that are not attached to any entry."""
    delete_tags = []
    for tag in tags:
        if EntryTag.get_or_none(EntryTag.tag_id == tag.id):
            continue
        else:
            delete_tags.append(tag)
    return delete_tags

def get_entries_by_tag(url_tag):
    """Get all entries with the selected tag."""
    tag = Tag.get(Tag.tag == url_tag)
    return (
        Entry.select().join(
            EntryTag, on=EntryTag.entry
        ).where(
            (EntryTag.tag == tag)
        )
    )


class User(UserMixin, Model):
    username = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)


    def get_entries(self):
        """Get entries created by the logged in user from the database."""
        return Entry.select().order_by(Entry.timestamp.desc())

    def get_index_entries(self):
        """Get the most recent entries to display on the home page."""
        return Entry.select().limit(3).order_by(Entry.timestamp.desc())

    def get_entry_count(self):
        """Return the number of entries by the logged in user."""
        return Entry.select().count()

    @classmethod
    def create_user(cls, username, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("A user with that username or "
                             "email address already exists.")


class Entry(Model):
    slug = CharField(unique=True)
    title = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)
    time_spent = CharField()
    learned = TextField()
    resources = TextField()

    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)


class Tag(Model):
    tag = CharField(unique=True)

    class Meta:
        database = DATABASE

class EntryTag(Model):
    entry = ForeignKeyField(Entry, backref='entries')
    tag = ForeignKeyField(Tag, backref='tags')

    class Meta:
        database = DATABASE
        indexes = (
            (('entry', 'tag'), True),
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Entry, EntryTag, Tag], safe=True)
    DATABASE.close()
