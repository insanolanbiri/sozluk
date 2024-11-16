from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import AnyOf, InputRequired


class EntryForm(FlaskForm):
    topic = StringField("baslik", [InputRequired("bkz: yokluk")])
    text = TextAreaField(
        "girdi",
        [InputRequired("[                      ]")],
        render_kw={"class": "resized_text"},
    )
    author = StringField(
        "yazar", [InputRequired("bir girdi uzaylilardan gelmis olamaz.")]
    )
    submit = SubmitField("yolla")


class NukeEntryForm(FlaskForm):
    entry_id = IntegerField()
    text = StringField(
        "girdiyi silmek istediginden eminsen 'sil' yaz", [AnyOf(("sil"))]
    )
    checkbox = BooleanField(
        "gercekten bu girdiyi karadelige gondermek istedigimden eminim",
        [AnyOf((True,))],
    )
    checkbox_2 = BooleanField(
        "burayi okuyorsan bu secenegi isaretleme", [AnyOf((False,))]
    )
    submit = SubmitField("yok et")
