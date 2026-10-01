from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput, Textarea, Select, URLInput, DateInput
from django.utils.html import strip_tags

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
    # Second line of defence: strip HTML tags from text the moment it comes in.
    # Escaping when displaying (escapeHtml) is still the main protection.
    def clean_name(self):
        name = strip_tags(self.cleaned_data["name"]).strip()
        if not name:
            raise ValidationError("Skill name cannot consist of HTML tags only.")
        return name

    def clean_impact(self):
        return strip_tags(self.cleaned_data["impact"]).strip()

    def clean_context(self):
        return strip_tags(self.cleaned_data["context"]).strip()    

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

    # Second line of defence: strip HTML tags from text the moment it comes in.
    # Escaping when displaying (escapeHtml) is still the main protection.
    def clean_title(self):
        title = strip_tags(self.cleaned_data["title"]).strip()
        if not title:
            raise ValidationError("Title cannot consist of HTML tags only.")
        return title

    def clean_organization(self):
        return strip_tags(self.cleaned_data["organization"]).strip()

    def clean_description(self):
        description = strip_tags(self.cleaned_data["description"]).strip()
        if not description:
            raise ValidationError("Description cannot consist of HTML tags only.")
        return description

    def clean(self):
        cleaned_data = super().clean()
        started_at = cleaned_data.get("started_at")
        ended_at = cleaned_data.get("ended_at")
        if started_at and ended_at and ended_at.date() < started_at:
            self.add_error("ended_at", "End date cannot be earlier than the start date.")
        return cleaned_data