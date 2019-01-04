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


def get_tags(user):
    """Get all tags that have been created by the current user."""
    return Tag.select().where(Tag.user == user.user).order_by(Tag.tag)


def get_entry_tags(entry):
    """Get all tags attached to the current entry."""
    return EntryTag.select().where(EntryTag.entry_id == entry.id)


def get_entries_by_tag(tag):
    """Get all entries with the selected tag."""
    return EntryTag.select().where(EntryTag.tag_id == tag.id)


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by = ('-joined_at',)


    def get_entries(self):
        """Get entries created by the logged in user from the database."""
        return (Entry.select().where(Entry.user == self).
                order_by(Entry.timestamp.desc()))

    def get_index_entries(self):
        """Get the most recent entries to display on the home page."""
        return (Entry.select().where(Entry.user == self).
                limit(4).order_by(Entry.timestamp.desc()))

    def get_entry_count(self):
        """Return the number of entries by the logged in user."""
        return Entry.select().where(Entry.user == self).count()

    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError("A user with that username or "
                             "email address already exists.")


class Entry(Model):
    user = ForeignKeyField(User, backref='entries')
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
    user = ForeignKeyField(User)
    tag = CharField()

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
