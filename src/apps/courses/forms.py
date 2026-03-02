from django import forms
from .models import Course, CourseModule, Lesson, LessonBlock


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "title",
            "short_description",
            "description",
            "age_group",
            "level",
            "tags",
            "status",
        ]


class ModuleForm(forms.ModelForm):
    class Meta:
        model = CourseModule
        fields = ["title", "order"]


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["title", "summary", "order", "is_published"]


class LessonBlockForm(forms.ModelForm):
    class Meta:
        model = LessonBlock
        fields = ["type", "order", "payload", "language"]
        widgets = {
            "payload": forms.Textarea(attrs={"rows": 3}),
            "language": forms.TextInput(attrs={"placeholder": "python"}),
        }
