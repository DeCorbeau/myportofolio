from main.models import Experience

Experience.objects.all().delete()

Experience.objects.create(
    title="Person in Charge (PIC) of Ambassador Division",
    organization="Open House Fasilkom UI 2026",
    category="committee",
    started_at="2026-02-01",
    description="\n".join([
        "Leading an 8-member Ambassador Division (1 PIC, 1 VPIC, 6 staff), holding full ownership of the division's strategic direction and day-to-day operations.",
        "Designed the division's end-to-end work timeline and workflow from the ground up, spanning recruitment (selection criteria, interview scoring rubrics, reaching 40+ staff applicants and 160+ ambassador applicants), five ambassador special programs, and daily divisional operations.",
        "Built the division's core operational infrastructure including MoUs, standard operating procedures, task guidebooks, and contingency mechanisms with defined triggers and decision flows to keep divisional operations resilient under pressure.",
        "Conceptualized and oversaw five ambassador special programs including Welcoming Ambassador, RISTEK Class, Webinar with Alumni, Mentoring 1-on-1, and Farewell Party, each with defined success metrics spanning attendance targets, satisfaction scores, and material comprehension rates.",
        "Serve as the division's point of accountability, coordinating cross-divisional collaboration and reporting to the Core Program Manager.",
    ]),
    thumbnail="/static/img/logooh26.jpeg",
)

Experience.objects.create(
    title="HR Staff of IT Development",
    organization="COMPFEST 18",
    category="committee",
    started_at="2026-03-01",
    description="\n".join([
        "Monitor the IT Development team's day-to-day performance and project progress, compiling regular progress recaps for internal reporting and review.",
        "Support recruitment for IT Development staff across both the Software Engineering and UI/UX sub-divisions.",
        "Foster a positive and cohesive team culture through bonding initiatives and engagement activities, helping maintain a comfortable and motivating work environment.",
        "Support core people-operations functions for the division including check-ins, progress tracking, and internal communication to help sustain team cohesion and productivity.",
    ]),
    thumbnail="/static/img/compfest18.jpg",
)

Experience.objects.create(
    title="Event Intern of Datathon 2026",
    organization="RISTEK Summer Event 2026: Datathon 2026",
    category="internship",
    started_at="2026-05-01",
    description="\n".join([
        "Served as PIC for Workshop 4, a national-scale workshop with 200+ participants, owning the speaker ToR, content alignment, event rundown, MC cue cards, and serving as the primary liaison with speakers throughout.",
        "During the high-school registration phase, personally reached out to 25 schools and secured engagement from 3 major communities as part of the team's broader outreach of 47 schools and 19 communities, helping drive a combined 1,200+ registrants across university and high-school levels.",
        "Served as VPIC for Final Day, the competition's 300+-attendee culminating event, handling manpower allocation, the day's rundown and cue cards (finalist pitching through partner workshops with Glair AI and GoPay), and the logistics procurement list.",
        "Worked as on-site field coordinator at the main auditorium stage on event day, overseeing run-of-show execution, stakeholder seating, live-report coverage, real-time cue card adjustments, and registration flow.",
    ]),
    thumbnail="/static/img/datathon_2026.svg",
)

Experience.objects.create(
    title="Staff of Ambassador Division",
    organization="Open House Fasilkom UI 2025",
    category="committee",
    started_at="2025-08-01",
    ended_at="2026-12-01",
    description="\n".join([
        'Served as PIC for RISTEK Class, an exclusive ambassador benefit program themed "Innovating Ideas: From Technology Concepts to Real-World Solutions," managing the full pipeline end-to-end including speaker ToR, event rundown, pre-event assignments, MC cue cards, presentation materials, and speaker appreciation certificates.',
        "Served as VPIC for Mentoring 1-on-1, a program pairing ambassadors with student mentors to build their knowledge of Open House and the Faculty of Computer Science; owned the rundown, MC cue cards, and mentor guidebook, and personally recruited approximately 15 of the 20 required mentors within 2-3 days.",
        "Acted as cross-divisional liaison with Business Development (ensuring incentives and merchandise reached speakers) and Digital Engagement & Collaboration (ensuring consistent live-report coverage across all special programs).",
        "Mentored one of three ambassador teams that collectively drove approximately 40% (~195 people) of total main event attendance, earning the division formal recognition for the achievement.",
    ]),
    thumbnail="/static/img/logooh25.jpeg",
)

print("Selesai! 4 data experience berhasil ditambahkan.")