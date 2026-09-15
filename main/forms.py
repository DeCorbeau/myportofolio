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
            "name": "Nama Skill",
            "category": "Kategori",
            "proficiency": "Tingkat Penguasaan",
            "impact": "Dampak/Pencapaian",
            "context": "Konteks (dari pengalaman mana)",
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
                    "placeholder": "Memimpin tim 8 orang mencapai target rekrutmen",
                }
            ),
            "context": TextInput(
                attrs={
                    "placeholder": "PIC, Ambassador Division — Open House 2026",
                }
            ),
        }