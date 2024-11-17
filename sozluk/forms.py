from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import AnyOf, DataRequired, InputRequired, Length


class EntryForm(FlaskForm):
    topic = StringField(
        "baslik",
        [
            DataRequired("yokluk mu demek istedin?"),
            Length(max=50, message="baslik cok uzun ama."),
        ],
    )
    text = TextAreaField(
        "girdi",
        [DataRequired("??? cok aciklayici olmussun.")],
        render_kw={"class": "resized_text"},
    )
    author = StringField(
        "yazar",
        [
            DataRequired("bu girdi uzaylilardan gelmis olamaz diye dusunuyorum."),
            Length(max=40, message="isim cok uzun ama."),
        ],
    )
    submit = SubmitField("isiginla bizi aydinlat")


class NukeEntryForm(FlaskForm):
    entry_id = IntegerField()
    text = StringField(
        "girdiyi silmek istediginden eminsen 'sil' yaz",
        [AnyOf(("sil",), "sil yazmadin, ben de silmedim kaptanim.")],
    )
    checkbox = BooleanField(
        "gercekten bu girdiyi karadelige gondermek istedigimden eminim",
        [AnyOf((True,), "silmedim.")],
    )
    checkbox_2 = BooleanField(
        "burayi okuyorsan bu secenegi isaretleme", [AnyOf((False,), "yemezler.")]
    )
    submit = SubmitField("kirmizi buton")
