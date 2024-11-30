from datetime import timedelta
from os import getenv, urandom

import psutil
from flask import (
    Flask,
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_wtf import CSRFProtect
from sqlalchemy import create_engine

from sozluk.authorname import AuthorName
from sozluk.entry import EntryID, EntrySketch, EntryText
from sozluk.forms import EntryForm, NukeEntryForm, SearchForm
from sozluk.storage import EntryAddResponse, EntryDeleteResponse
from sozluk.storage.sqlalchemydatabase import SQLAlchemyDatabase
from sozluk.topicname import TopicName
from sozluk.turkishlowercasedstring import TurkishLowercasedString

timezone = timedelta(hours=3)

BUILD_COMMIT = getenv("VCS_TAG", "")

url = getenv("DATABASE_URL", "sqlite:///sozluk.sqlite")
engine = create_engine(url)
db = SQLAlchemyDatabase(engine)

app = Flask(__name__)


app.secret_key = urandom(32)
csrf = CSRFProtect(app)


@app.context_processor
def inject_constants():
    return dict(
        app_name="sozluk",
        timezone=timezone,
        commit=BUILD_COMMIT,
    )


@app.errorhandler(404)
async def error404(error):
    return render_template("404.html"), 404


@app.route("/robots.txt")
async def robots():
    return send_from_directory(app.static_folder, "robots.txt")


@app.route("/")
async def index():
    return render_template(
        "index.html",
        entry_form=EntryForm(),
        search_form=SearchForm(),
    )


@app.route("/add_entry", methods=["POST"])
async def add_entry():
    entry_form = EntryForm()
    if not entry_form.validate_on_submit():
        for _, error in entry_form.errors.items():
            flash(" ".join(error))
        return redirect(url_for("index"))

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
            flash("bu tanim zaten var.")
            return redirect(url_for("topic", name=sketch.topic))
        case something:
            raise NotImplementedError(something)


@app.route("/del_entry", methods=["POST"])
async def del_entry():
    form = NukeEntryForm()
    if not form.validate_on_submit():
        for _, error in form.errors.items():
            flash(" ".join(error))
        return redirect(url_for("index"))
    try:
        entry_id = EntryID(form.entry_id.data)
    except ValueError:
        flash("bir seyler ters gitti, silemedim.")
        return redirect(url_for("index"))

    result = await db.del_entry(entry_id)

    match result:
        case EntryDeleteResponse.SUCCESS:
            flash("artik yok.")
            return redirect(url_for("index"))
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
    try:
        topic_name = TopicName(name)
    except ValueError:
        flash("baslik ismi kotu. boyle baslik olmaz olsun.")
        abort(404)

    entries = await db.get_topic(topic_name)

    # do not throw 404 even if there are no entries.
    # since page shows an entry input field.

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


@app.route("/stats")
async def stats():
    topic_list = await db.get_latest_topics()
    if not topic_list:
        first_entry = None
        last_entry = None
    else:
        first_topic = topic_list[-1]
        first_entry = (await db.get_topic(first_topic))[0]

        last_topic = topic_list[0]
        last_entry = (await db.get_topic(last_topic))[-1]

    cpu_percentage = psutil.cpu_percent(interval=0.2)
    cpu_count = psutil.cpu_count()

    mem = psutil.virtual_memory()
    ram_total_megabytes = int(mem.total / 1024 / 1024)
    ram_used_megabytes = ram_total_megabytes - int(mem.available / 1024 / 1024)
    ram_percentage = mem.percent
    load_average = psutil.getloadavg()

    total_entry_count = db.entry_count
    total_topic_count = db.topic_count
    total_author_count = db.author_count
    return render_template(
        "stats.html",
        first_entry=first_entry,
        last_entry=last_entry,
        total_entry_count=await total_entry_count,
        total_topic_count=await total_topic_count,
        total_author_count=await total_author_count,
        cpu_percentage=cpu_percentage,
        cpu_count=cpu_count,
        ram_total_megabytes=ram_total_megabytes,
        ram_used_megabytes=ram_used_megabytes,
        ram_percentage=ram_percentage,
        load_average=load_average,
    )


@app.route("/theemoji")
async def theemoji():
    return render_template("theemoji.html")


@app.route("/about")
async def about():
    return render_template("about.html")


@app.route("/random")
async def random():
    random_entries = db.get_random_entries(limit=10)

    return render_template("random.html", random_entries=await random_entries)


@app.route("/search")
async def search():
    form = SearchForm(request.args)

    if form.query.data is not None:
        form.query.data = form.query.data.strip()

    if not form.validate():
        for _, error in form.errors.items():
            flash(" ".join(error))
        return redirect(url_for("index"))

    query = TurkishLowercasedString(form.query.data)

    topics = db.topic_search_basic(query)

    return render_template(
        "search.html", result_topics=await topics, query=query, search_form=form
    )


@app.route("/authors")
async def authors():
    latest_authors = db.get_latest_authors(limit=None)

    return render_template("authors.html", authors=await latest_authors)


@app.route("/topics")
async def topics():
    page = request.args.get("page", "1")

    try:
        page = int(page)
    except ValueError:
        flash("kotu sayfa")
        return redirect(url_for("topics"))

    if page <= 0:
        flash("kucuk sayfa. seni gidi seni!")
        return redirect(url_for("topics"))

    topics_per_page = 10

    latest_topics = await db.get_latest_topics(
        offset=(page - 1) * topics_per_page, limit=topics_per_page
    )

    if not latest_topics:
        flash("cok gittin")
        abort(404)

    return render_template("topics.html", topics=latest_topics, page=page)
