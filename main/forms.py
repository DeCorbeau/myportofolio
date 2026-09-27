from django.forms import ModelForm, TextInput, Textarea, Select, URLInput, DateInput

from main.models import Skill, Experience


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

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "organization",
            "description",
            "category",
            "thumbnail",
            "started_at",
            "ended_at",
        ]
        labels = {
            "title": "Position / Role",
            "organization": "Organization",
            "description": "Description (one bullet point per line)",
            "category": "Category",
            "thumbnail": "Logo / Thumbnail URL",
            "started_at": "Start Date",
            "ended_at": "End Date (leave blank if ongoing)",
        }
        widgets = {
            "title": TextInput(attrs={"placeholder": "Person in Charge (PIC) of Ambassador Division"}),
            "organization": TextInput(attrs={"placeholder": "Open House Fasilkom UI 2026"}),
            "description": Textarea(attrs={"placeholder": "One achievement per line...", "rows": 5}),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://..."}),
            "started_at": DateInput(attrs={"type": "date"}),
            "ended_at": DateInput(attrs={"type": "date"}),
        }