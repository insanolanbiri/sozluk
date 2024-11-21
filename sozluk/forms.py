from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import (
    AnyOf,
    DataRequired,
    InputRequired,
    Length,
    ValidationError,
)


def NotContains(substring: str, message: str = ""):
    def validator(form, field):
        if substring in field.data:
            raise ValidationError(message)

    return validator


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
            NotContains(
                " ", message="ismine bosluk koyamiyorsun maalesef. kurallar boyle."
            ),
        ],
    )
    submit = SubmitField("isiginla bizi aydinlat")

ENTRY_DELETE_CONFIRMATION = "lütfen siler misin canım benim"

class NukeEntryForm(FlaskForm):
    entry_id = IntegerField()
    text = StringField(
        f'girdiyi silmek istediginden eminsen "{ENTRY_DELETE_CONFIRMATION}" yaz',
        [
            AnyOf(
                (ENTRY_DELETE_CONFIRMATION,),
                f'"{ENTRY_DELETE_CONFIRMATION}" yazmadin, ben de silmedim kaptanim.',
            )
        ],
    )
    checkbox = BooleanField(
        "gercekten bu girdiyi karadelige gondermek istedigimden eminim",
        [AnyOf((True,), "silmedim.")],
    )
    checkbox_2 = BooleanField(
        "burayi okuyorsan bu secenegi isaretleme", [AnyOf((False,), "yemezler.")]
    )
    submit = SubmitField("kirmizi buton")
