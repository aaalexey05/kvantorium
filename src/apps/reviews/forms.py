from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        label="Оценка",
        coerce=int,
        choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")],
        initial=5,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["author_type"].choices = [
            ("student", "Ученик"),
            ("parent", "Родитель"),
            ("alumni", "Выпускник"),
        ]
        self.fields["author_type"].initial = "student"

    class Meta:
        model = Review
        fields = ("name", "author_type", "rating", "text")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ваше имя"}),
            "author_type": forms.Select(),
            "text": forms.Textarea(attrs={"rows": 4, "placeholder": "Поделитесь впечатлениями о курсе"}),
        }
