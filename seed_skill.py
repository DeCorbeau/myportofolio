from main.models import Skill

Skill.objects.all().delete()

Skill.objects.create(name="People Management", category="leadership", proficiency=4,
    impact="Led an 8-member Ambassador Division, holding full ownership of strategic direction and daily operations; also monitored team performance and fostered team culture as HR Staff.",
    context="PIC of Ambassador Division — Open House Fasilkom UI 2026; HR Staff of IT Development — COMPFEST 18")

Skill.objects.create(name="Strategic Planning", category="leadership", proficiency=3,
    impact="Designed the division's end-to-end work timeline and workflow from the ground up, spanning recruitment (selection criteria, interview rubrics), five ambassador special programs with defined success metrics, and daily divisional operations.",
    context="PIC of Ambassador Division — Open House Fasilkom UI 2026")

Skill.objects.create(name="Recruitment & Selection", category="leadership", proficiency=4,
    impact="Built the recruitment mechanism for staff and ambassadors, reaching 40+ staff and 160+ ambassador applicants; also supported recruitment for IT Development staff.",
    context="PIC of Ambassador Division — Open House Fasilkom UI 2026; HR Staff of IT Development — COMPFEST 18")

Skill.objects.create(name="Crisis Management", category="leadership", proficiency=2,
    impact="Built the division's core operational infrastructure including MoUs, standard operating procedures, task guidebooks, and contingency mechanisms with defined triggers and decision flows to keep divisional operations resilient under pressure.",
    context="PIC of Ambassador Division — Open House Fasilkom UI 2026")

Skill.objects.create(name="Event Planning & Execution", category="event", proficiency=4,
    impact="Served as PIC for a national-scale workshop with 200+ participants, owning ToR, content, and rundown; also managed an ambassador program end-to-end including speaker ToR, rundown, and pre-event assignments.",
    context="Event Intern — RISTEK Summer Event 2026: Datathon 2026; Ambassador Division Staff — Open House Fasilkom UI 2025")

Skill.objects.create(name="On-site Field Coordination", category="event", proficiency=4,
    impact="Oversaw run-of-show execution, stakeholder seating, and real-time cue card adjustments as field coordinator.",
    context="Event Intern — RISTEK Summer Event 2026: Datathon 2026")

Skill.objects.create(name="Logistics Coordination", category="event", proficiency=3,
    impact="Handled manpower allocation and logistics procurement for a 300+-attendee culminating event.",
    context="VPIC, Final Day — RISTEK Summer Event 2026: Datathon 2026")

Skill.objects.create(name="Cross-divisional Liaison", category="communication", proficiency=3,
    impact="Served as the division's point of accountability, coordinating cross-divisional collaboration; also acted as liaison with Business Development and Digital Engagement teams.",
    context="PIC of Ambassador Division — Open House Fasilkom UI 2026; Ambassador Division Staff — Open House Fasilkom UI 2025")

Skill.objects.create(name="Speaker & Partner Relations", category="communication", proficiency=3,
    impact="Owned speaker ToR and served as primary liaison with speakers and partners including Glair AI and GoPay; also managed speaker materials and appreciation certificates for an ambassador program.",
    context="Event Intern — RISTEK Summer Event 2026: Datathon 2026; Ambassador Division Staff — Open House Fasilkom UI 2025")

Skill.objects.create(name="Outreach & Networking", category="communication", proficiency=3,
    impact="Personally reached out to 25 schools and secured engagement from 3 major communities as part of a broader outreach effort.",
    context="Event Intern — RISTEK Summer Event 2026: Datathon 2026")

Skill.objects.create(name="Persuasion & Negotiation", category="communication", proficiency=3,
    impact="Personally recruited approximately 15 of the 20 required mentors within 2-3 days.",
    context="Ambassador Division Staff — Open House Fasilkom UI 2025")

Skill.objects.create(name="Python", category="technical", proficiency=3,
    context="Learned through Programming Foundations 1 course, now being applied further in Django-based coursework.")

Skill.objects.create(name="Java", category="technical", proficiency=2,
    context="Learned through Programming Foundations 2 course.")

Skill.objects.create(name="C & Systems Programming", category="technical", proficiency=2,
    context="Learned through Introduction to Operating Systems course, applying C to explore operating system concepts.")

Skill.objects.create(name="Web Development (Django)", category="technical", proficiency=3,
    context="Learned through Platform Based Programming course, currently applied to build this portfolio website.")

print("Selesai! 15 skill berhasil ditambahkan.")