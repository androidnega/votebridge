"""Constants for the VoteBridge presentation / demo seed."""

from apps.accounts.models import Role

SRC_ELECTION_TITLE = "TTU SRC General Elections 2026"
FASSA_ELECTION_TITLE = "FASSA Elections 2025"

STAFF_ACCOUNTS = [
    {
        "role": Role.Name.SUPER_ADMIN,
        "username": "superadmin",
        "email": "superadmin@ttu.edu.gh",
        "phone_number": "0257940791",
        "first_name": "Akua",
        "last_name": "Mensah",
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "role": Role.Name.ADMIN,
        "username": "admin",
        "email": "admin@ttu.edu.gh",
        "phone_number": "0257940792",
        "first_name": "Kofi",
        "last_name": "Asante",
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "role": Role.Name.ADMIN,
        "username": "registrar",
        "email": "registrar@ttu.edu.gh",
        "phone_number": "0257940793",
        "first_name": "Abena",
        "last_name": "Owusu",
        "is_staff": True,
        "is_superuser": False,
    },
]

# (first_name, last_name, index_number, email, department, role)
TTU_DEMO_STUDENTS = [
    ("Kwame", "Mensah", "BC/ITS/24/047", "kwame.mensah@ttu.edu.gh", "Computer Science", Role.Name.STUDENT),
    ("Ama", "Osei", "BC/ITD/24/031", "ama.osei@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Kofi", "Boateng", "BC/ITN/24/112", "kofi.boateng@ttu.edu.gh", "Information Technology", Role.Name.CANDIDATE),
    ("Abena", "Boateng", "BC/ICT/24/056", "abena.boateng@ttu.edu.gh", "Computer Technology", Role.Name.STUDENT),
    ("Yaw", "Darko", "BC/MEE/24/018", "yaw.darko@ttu.edu.gh", "Mechanical Engineering", Role.Name.STUDENT),
    ("Efua", "Adjei", "BC/ACC/24/092", "efua.adjei@ttu.edu.gh", "Accounting", Role.Name.STUDENT),
    ("Kwesi", "Appiah", "BC/ITS/24/052", "kwesi.appiah@ttu.edu.gh", "Computer Science", Role.Name.STUDENT),
    ("Akosua", "Frimpong", "BC/ITD/24/048", "akosua.frimpong@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Kojo", "Sarpong", "BC/ITN/24/118", "kojo.sarpong@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Ama", "Kwarteng", "BC/ICT/24/061", "ama.kwarteng@ttu.edu.gh", "Computer Technology", Role.Name.STUDENT),
    ("Fiifi", "Amoah", "BC/MEE/24/022", "fiifi.amoah@ttu.edu.gh", "Mechanical Engineering", Role.Name.STUDENT),
    ("Adwoa", "Mensah", "BC/ACC/24/088", "adwoa.mensah@ttu.edu.gh", "Accounting", Role.Name.STUDENT),
    ("Samuel", "Osei", "BC/ITS/24/055", "samuel.osei@ttu.edu.gh", "Computer Science", Role.Name.STUDENT),
    ("Gifty", "Asare", "BC/ITD/24/039", "gifty.asare@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Prince", "Boakye", "BC/ITN/24/105", "prince.boakye@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Naana", "Dankwa", "BC/ICT/24/070", "naana.dankwa@ttu.edu.gh", "Computer Technology", Role.Name.STUDENT),
    ("Isaac", "Tetteh", "BC/MEE/24/029", "isaac.tetteh@ttu.edu.gh", "Mechanical Engineering", Role.Name.STUDENT),
    ("Selina", "Agyeman", "BC/ACC/24/095", "selina.agyeman@ttu.edu.gh", "Accounting", Role.Name.STUDENT),
    ("Daniel", "Owusu", "BC/ITS/24/043", "daniel.owusu@ttu.edu.gh", "Computer Science", Role.Name.STUDENT),
    ("Rebecca", "Antwi", "BC/ITD/24/036", "rebecca.antwi@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Michael", "Addo", "BC/ITN/24/121", "michael.addo@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Ama", "Serwaa", "BC/ITS/24/051", "ama.serwaa@ttu.edu.gh", "Computer Science", Role.Name.STUDENT),
    ("Kwame", "Ansah", "BC/ITD/24/044", "kwame.ansah@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Nana", "Agyei", "BC/ACC/24/077", "nana.agyei@ttu.edu.gh", "Accounting", Role.Name.STUDENT),
    ("Esi", "Mensah", "BC/ICT/24/063", "esi.mensah@ttu.edu.gh", "Computer Technology", Role.Name.STUDENT),
    ("Kweku", "Annan", "BC/MEE/24/011", "kweku.annan@ttu.edu.gh", "Mechanical Engineering", Role.Name.STUDENT),
    ("Abigail", "Ofori", "BC/ITS/24/049", "abigail.ofori@ttu.edu.gh", "Computer Science", Role.Name.STUDENT),
    ("Richard", "Nyame", "BC/ITN/24/099", "richard.nyame@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("Linda", "Akoto", "BC/ITD/24/041", "linda.akoto@ttu.edu.gh", "Information Technology", Role.Name.STUDENT),
    ("George", "Mensah", "BC/MEE/24/025", "george.mensah@ttu.edu.gh", "Mechanical Engineering", Role.Name.STUDENT),
]

SRC_POSITIONS = [
    "President",
    "General Secretary",
    "Financial Secretary",
    "Women's Commissioner",
    "Sports Secretary",
    "Entertainment Secretary",
    "Organising Secretary",
]

FASSA_POSITIONS = [
    "President",
    "General Secretary",
    "Financial Secretary",
    "Women's Commissioner",
    "Organiser",
]

# name, department, index (optional), image filename under frontend/public/candidates/
SRC_CANDIDATE_ROSTER = {
    "President": [
        ("Kofi Boateng", "Information Technology", "BC/ITN/24/112", "male-1.png"),
        ("Kwame Ansah", "Information Technology", "BC/ITD/24/044", "male-2.png"),
        ("Ama Serwaa", "Computer Science", "BC/ITS/24/051", "female-1.png"),
    ],
    "General Secretary": [
        ("Efua Adjei", "Accounting", "BC/ACC/24/092", "female-2.png"),
        ("Daniel Owusu", "Computer Science", "BC/ITS/24/043", "male-3.png"),
        ("Selina Agyeman", "Accounting", "BC/ACC/24/095", "female-3.png"),
    ],
    "Financial Secretary": [
        ("Adwoa Mensah", "Accounting", "BC/ACC/24/088", "female-4.png"),
        ("Isaac Tetteh", "Mechanical Engineering", "BC/MEE/24/029", "male-4.png"),
        ("Rebecca Antwi", "Information Technology", "BC/ITD/24/036", "female-5.png"),
    ],
    "Women's Commissioner": [
        ("Akosua Frimpong", "Information Technology", "BC/ITD/24/048", "female-6.png"),
        ("Gifty Asare", "Information Technology", "BC/ITD/24/039", "female-7.png"),
        ("Naana Dankwa", "Computer Technology", "BC/ICT/24/070", "female-1.png"),
    ],
    "Sports Secretary": [
        ("Prince Boakye", "Information Technology", "BC/ITN/24/105", "male-1.png"),
        ("Samuel Osei", "Computer Science", "BC/ITS/24/055", "male-2.png"),
        ("Michael Addo", "Information Technology", "BC/ITN/24/121", "male-3.png"),
    ],
    "Entertainment Secretary": [
        ("Abena Boateng", "Computer Technology", "BC/ICT/24/056", "female-2.png"),
        ("Kojo Sarpong", "Information Technology", "BC/ITN/24/118", "male-4.png"),
        ("Ama Kwarteng", "Computer Technology", "BC/ICT/24/061", "female-3.png"),
    ],
    "Organising Secretary": [
        ("Kwesi Appiah", "Computer Science", "BC/ITS/24/052", "male-1.png"),
        ("Yaw Darko", "Mechanical Engineering", "BC/MEE/24/018", "male-2.png"),
        ("Richard Nyame", "Information Technology", "BC/ITN/24/099", "male-3.png"),
    ],
}

FASSA_CANDIDATE_ROSTER = {
    "President": [
        ("Nana Agyei", "Accounting", None, "male-4.png"),
        ("Abigail Ofori", "Computer Science", "BC/ITS/24/049", "female-4.png"),
        ("Kweku Annan", "Mechanical Engineering", "BC/MEE/24/011", "male-1.png"),
    ],
    "General Secretary": [
        ("Esi Mensah", "Computer Technology", "BC/ICT/24/063", "female-6.png"),
        ("Fiifi Amoah", "Mechanical Engineering", "BC/MEE/24/022", "male-3.png"),
    ],
    "Financial Secretary": [
        ("Joel Ampofo", "Accounting", None, "male-4.png"),
        ("Ama Osei", "Information Technology", "BC/ITD/24/031", "female-7.png"),
    ],
    "Women's Commissioner": [
        ("Yaa Serwaa", "Computer Science", None, "female-1.png"),
        ("Akosua Danso", "Computer Technology", None, "female-2.png"),
    ],
    "Organiser": [
        ("Kwabena Owusu", "Mechanical Engineering", None, "male-1.png"),
        ("Richard Nyame", "Information Technology", "BC/ITN/24/099", "male-3.png"),
    ],
}

# Hourly vote weights for FASSA historical turnout charts (sum drives believable trend).
FASSA_HOURLY_VOTE_WEIGHTS = [
    2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 18, 16, 14, 12, 10, 8, 6, 5, 4, 3, 2, 2,
]

STRONGROOM_CUSTODIAN_USERNAMES = ["admin", "registrar"]
