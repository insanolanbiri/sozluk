from datetime import timedelta
from os import getenv, urandom

from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_wtf import CSRFProtect

from sozluk.authorname import AuthorName
from sozluk.entry import Entry, EntryID, EntrySketch, EntryText
from sozluk.forms import EntryForm, NukeEntryForm
from sozluk.storage import EntryAddResponse, EntryDeleteResponse
from sozluk.storage.committedmemorydb import CommittedMemoryDB
from sozluk.topicname import TopicName

timezone = timedelta(hours=3)

db = CommittedMemoryDB(getenv("DATABASE_PATH", "database.pickle"))

app = Flask(__name__)


app.secret_key = urandom(32)
csrf = CSRFProtect(app)


@app.context_processor
def inject_constants():
    return dict(
        app_name="sozluk",
        timezone=timezone,
    )


@app.errorhandler(404)
async def error404(error):
    return render_template("404.html"), 404


@app.route("/")
async def index():
    trending_topics = await db.get_latest_topics(limit=20)
    latest_authors = await db.get_latest_authors(limit=20)

    return render_template(
        "index.html",
        entry_form=EntryForm(),
        topics=trending_topics,
        authors=latest_authors,
        random_entries=await db.get_random_entries(limit=15),
    )


@app.route("/add_entry", methods=["POST"])
async def add_entry():
    entry_form = EntryForm()
    if not entry_form.validate_on_submit():
        return "nice try", 404  # FIXME: ???

    try:
        sketch = EntrySketch(
            topic=TopicName(entry_form.topic.data),
            author=AuthorName(entry_form.author.data),
            text=EntryText(entry_form.text.data),
        )
    except ValueError:
        flash("bir seyleri yanlis yapmis olmalisin")
        return redirect(url_for("index"))

    result, entry_id = await db.add_entry(sketch)

    match result:
        case EntryAddResponse.SUCCESS:
            flash("tebrikler! artik girdin yayinda.")
            return redirect(url_for("entry", entry_id=entry_id.value))
        case EntryAddResponse.DEFINITION_EXISTS:
            flash("bu tanim zaten var")
            return redirect(url_for("topic", topic_name=sketch.topic))
        case something:
            raise NotImplementedError(something)


@app.route("/del_entry", methods=["POST"])
async def del_entry():
    form = NukeEntryForm()
    if not form.validate_on_submit():
        return redirect(url_for("index"))
    try:
        entry_id = EntryID(form.entry_id.data)
    except ValueError:
        return redirect(url_for("index"))

    result = await db.del_entry(entry_id)

    match result:
        case EntryDeleteResponse.SUCCESS:
            flash("artik yok")
            return url_for("index")
        case EntryDeleteResponse.ENTRY_NOT_FOUND:
            flash("boyle bir girdi zaten yokmus, silmeme gerek kalmadi sanirim.")
            abort(404)
        case something:
            raise NotImplementedError(something)


@app.route("/entry/<entry_id>")
async def entry(entry_id: str):
    try:
        entry_id = EntryID(int(entry_id))
    except ValueError:
        flash("boyle bir girdi numarasi olamaz ki")
        return redirect(url_for("index"))

    target = await db.get_entry(entry_id)

    if not target:
        abort(404)

    return render_template(
        "entry.html", entry=target, risk=NukeEntryForm(), timezone=timezone
    )


@app.route("/topic/<name>")
async def topic(name):
    if name == "name":
        flash("asdf")
        abort(404)
    try:
        topic_name = TopicName(name)
    except ValueError:
        flash("baslik ismi kotu. boyle baslik olmaz olsun.")
        abort(404)

    entries = await db.get_topic(topic_name)

    return render_template(
        "topic.html", entries=entries, entry_form=EntryForm(), topic_name=topic_name
    )


@app.route("/author/<name>")
async def author(name):
    try:
        author_name = AuthorName(name)
    except ValueError:
        flash("yazar ismi cok kotu. boyle isim olmaz olsun")
        abort(404)

    entries = await db.get_author(author_name)

    if not entries:
        abort(404)

    return render_template("author.html", entries=entries, author=author_name)
