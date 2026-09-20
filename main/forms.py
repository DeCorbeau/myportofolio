from django.forms import ModelForm, TextInput, Textarea, Select, NumberInput

from main.models import Skill


class SkillForm(ModelForm):
    class Meta:
        model = Skill
        fields = [
            "name",
            "category",
            "proficiency",
            "impact",
            "context",
        ]
        labels = {
            "name": "Skill Name",
            "category": "Category",
            "proficiency": "Proficiency Level",
            "impact": "Impact/Achievement",
            "context": "Context (from which experience)",
        }
        widgets = {
            "name": TextInput(
                attrs={
                    "placeholder": "Team Leadership",
                    "maxlength": 100,
                }
            ),
            "category": Select(),
            "proficiency": Select(),
            "impact": TextInput(
                attrs={
                    "placeholder": "Led a team of 8 to hit the division target",
                }
            ),
            "context": TextInput(
                attrs={
                    "placeholder": "PIC of Ambassador Division — Open House Fasilkom UI 2026",
                }
            ),
        }