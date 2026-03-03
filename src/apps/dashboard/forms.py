from django import forms
from django.utils.text import slugify

from apps.accounts.models import User
from apps.achievements.models import Achievement
from apps.core.models import ContactInfo
from apps.courses.models import Course, CourseModule, Lesson, LessonBlock
from apps.news.models import NewsPost


class TeacherCourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "short_description",
            "description",
            "age_group",
            "level",
            "tags",
            "cover",
            "status",
        ]
        widgets = {
            "short_description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Коротко о курсе: для кого и чему учит"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 7,
                    "placeholder": "Подробное описание. Можно использовать HTML теги: <p>, <h3>, <ul>, <li>...",
                }
            ),
            "age_group": forms.TextInput(attrs={"placeholder": "10-14"}),
            "level": forms.TextInput(attrs={"placeholder": "Начальный / Средний"}),
            "tags": forms.TextInput(attrs={"placeholder": "Python, Scratch, Web"}),
        }


class TeacherCourseStructureForm(forms.Form):
    module_titles = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Модуль 1\nМодуль 2\nМодуль 3",
            }
        ),
        label="Модули",
        help_text="Каждая строка - название модуля.",
    )
    lesson_titles = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Урок 1\nУрок 2\nУрок 3",
            }
        ),
        label="Уроки первого модуля",
        help_text="Каждая строка - название урока в первом модуле.",
    )


class TeacherModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        fields = ["title", "order"]


class TeacherLessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "summary", "order", "is_published"]
        widgets = {"summary": forms.Textarea(attrs={"rows": 3})}


class TeacherLessonBlockForm(forms.Form):
    type = forms.ChoiceField(choices=LessonBlock.BLOCK_TYPES, label="Тип блока")
    language = forms.CharField(required=False, label="Язык кода")
    text_content = forms.CharField(
        required=False,
        label="Текст/код",
        widget=forms.Textarea(attrs={"rows": 4}),
    )
    resource_url = forms.CharField(
        required=False,
        label="URL ресурса (изображение/видео/файл)",
        widget=forms.TextInput(attrs={"placeholder": "https://... или /static/..."}),
    )
    caption = forms.CharField(required=False, label="Подпись")
    order = forms.IntegerField(required=False, min_value=1, label="Порядок")

    def clean(self):
        cleaned_data = super().clean()
        block_type = cleaned_data.get("type")
        text_content = cleaned_data.get("text_content")
        resource_url = cleaned_data.get("resource_url")
        if block_type in {"text", "code"} and not text_content:
            self.add_error("text_content", "Для этого типа блока нужен текст.")
        if block_type in {"image", "video", "file"} and not resource_url:
            self.add_error("resource_url", "Для этого типа блока нужен URL ресурса.")
        return cleaned_data


class AdminCourseForm(forms.ModelForm):
    created_by = forms.ModelChoiceField(
        queryset=User.objects.filter(role__in=[User.Role.TEACHER, User.Role.ADMIN]).order_by("email"),
        required=False,
        label="Преподаватель",
    )

    class Meta:
        model = Course
        fields = ["title", "short_description", "status", "created_by"]
        widgets = {"short_description": forms.Textarea(attrs={"rows": 3})}


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "role", "is_active", "is_staff"]
        widgets = {
            "email": forms.EmailInput(attrs={"readonly": "readonly"}),
        }


class AdminNewsForm(forms.ModelForm):
    slug = forms.SlugField(required=False)

    class Meta:
        model = NewsPost
        fields = ["title", "slug", "summary", "body", "status", "image"]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "body": forms.Textarea(attrs={"rows": 6}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug", "").strip()
        title = self.cleaned_data.get("title", "").strip()
        base = slug or slugify(title) or "news-post"
        candidate = base
        counter = 2
        while NewsPost.objects.filter(slug=candidate).exists():
            candidate = f"{base}-{counter}"
            counter += 1
        return candidate


class AdminAchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ["title", "year", "category", "description", "media"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class AdminContactForm(forms.ModelForm):
    city = forms.CharField(
        required=False,
        label="Город",
        widget=forms.TextInput(attrs={"placeholder": "Барнаул"}),
    )
    street = forms.CharField(
        required=False,
        label="Улица / проспект",
        widget=forms.TextInput(attrs={"placeholder": "проспект Социалистический"}),
    )
    house = forms.CharField(
        required=False,
        label="Дом / корпус / офис",
        widget=forms.TextInput(attrs={"placeholder": "126Б"}),
    )

    class Meta:
        model = ContactInfo
        fields = ["phone", "email", "schedule", "map_url"]
        widgets = {
            "phone": forms.TextInput(attrs={"placeholder": "+7 (999) 123-45-67"}),
            "schedule": forms.TextInput(attrs={"placeholder": "Пн-Пт 09:00-18:00"}),
            "map_url": forms.URLInput(
                attrs={"placeholder": "Опционально: ссылка Google Maps или embed URL"}
            ),
        }

    @staticmethod
    def compose_address(city: str, street: str, house: str):
        parts = [part.strip() for part in [city, street, house] if (part or "").strip()]
        return ", ".join(parts)

    @staticmethod
    def split_address(address: str):
        parts = [part.strip() for part in (address or "").split(",") if part.strip()]
        city = parts[0] if len(parts) > 0 else ""
        street = parts[1] if len(parts) > 1 else ""
        house = ", ".join(parts[2:]) if len(parts) > 2 else ""
        return city, street, house

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and not self.is_bound:
            city, street, house = self.split_address(self.instance.address)
            self.fields["city"].initial = city
            self.fields["street"].initial = street
            self.fields["house"].initial = house

    def clean(self):
        cleaned_data = super().clean()
        address = self.compose_address(
            cleaned_data.get("city", ""),
            cleaned_data.get("street", ""),
            cleaned_data.get("house", ""),
        )
        cleaned_data["address"] = address
        if not address and not cleaned_data.get("map_url"):
            raise forms.ValidationError(
                "Укажите адрес (город + улица) или добавьте ссылку на карту."
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.address = self.cleaned_data.get("address", "")
        if commit:
            instance.save()
        return instance
