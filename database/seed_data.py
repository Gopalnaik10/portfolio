"""
Seed data populated for Gopal Naik's Personal Developer & Data Science Portfolio.
"""
import json

INITIAL_PROFILE = {
    "greeting": "Hello, I'm",
    "name": "Gopal Naik",
    "title": "Computer Science & Engineering Student | Data Science",
    "tagline": "I build data-driven applications and modern web solutions.",
    "availability_status": "Available for Roles & Collaborations",
    "primary_cta_text": "View My Work →",
    "primary_cta_url": "#projects",
    "secondary_cta_text": "Contact Me",
    "secondary_cta_url": "#contact",
    "profile_image": "/uploads/profile/gopal_profile.jpg",
    "about_heading": "Turning Ideas Into Impactful Solutions",
    "about_narrative": "I'm a Computer Science & Engineering student specializing in Data Science. I enjoy building solutions that solve real-world problems using data, AI, and modern web technologies.",
    "about_focus": "Passionate about building full-stack architectures, computer vision and NLP models, and turning complex data streams into intuitive software solutions.",
    "stat_1_val": "4+",
    "stat_1_label": "Projects Built",
    "stat_2_val": "15+",
    "stat_2_label": "Technologies & Tools",
    "stat_3_val": "2026",
    "stat_3_label": "Expected Graduation",
    "stat_4_val": "Data Science",
    "stat_4_label": "Specialization",
    "email": "gopalnaik.dev@gmail.com",
    "phone": "",
    "location": "Open to Remote & On-Site"
}

INITIAL_SKILLS = [
    # Programming
    {"category": "Programming", "name": "Python", "icon": "code", "display_order": 1},
    {"category": "Programming", "name": "C", "icon": "code", "display_order": 2},

    # Data Science & AI
    {"category": "Data Science & AI", "name": "NumPy", "icon": "activity", "display_order": 3},
    {"category": "Data Science & AI", "name": "Pandas", "icon": "activity", "display_order": 4},
    {"category": "Data Science & AI", "name": "Matplotlib", "icon": "bar-chart", "display_order": 5},
    {"category": "Data Science & AI", "name": "Seaborn", "icon": "trending-up", "display_order": 6},
    {"category": "Data Science & AI", "name": "Scikit-learn", "icon": "cpu", "display_order": 7},
    {"category": "Data Science & AI", "name": "OpenCV", "icon": "eye", "display_order": 8},

    # Backend
    {"category": "Backend", "name": "Flask", "icon": "server", "display_order": 9},
    {"category": "Backend", "name": "FastAPI", "icon": "server", "display_order": 10},
    {"category": "Backend", "name": "Django", "icon": "server", "display_order": 11},

    # Database
    {"category": "Database", "name": "SQL", "icon": "database", "display_order": 12},
    {"category": "Database", "name": "PostgreSQL", "icon": "database", "display_order": 13},

    # Frontend
    {"category": "Frontend", "name": "HTML", "icon": "layout", "display_order": 14},
    {"category": "Frontend", "name": "CSS", "icon": "layout", "display_order": 15},
    {"category": "Frontend", "name": "JavaScript", "icon": "code", "display_order": 16},
    {"category": "Frontend", "name": "React", "icon": "layers", "display_order": 17},
]

INITIAL_PROJECTS = [
    {
        "title": "AI Gym Trainer",
        "category": "Machine Learning",
        "short_description": "AI-powered workout recommendation and real-time form tracking system.",
        "description": "An intelligent computer vision and machine learning fitness companion that tracks 33 skeletal body landmarks in real time. It monitors exercise posture, counts repetitions accurately, evaluates form deviation, and generates personalized training routines.",
        "problem_statement": "Gym trainees often struggle with incorrect workout posture and lack immediate feedback, leading to muscle strain or inefficient exercise routines without expensive personal trainers.",
        "key_features": json.dumps([
            "Real-time pose estimation and skeletal angle calculation via OpenCV",
            "Automatic repetition counter for bicep curls, squats, and pushups",
            "Live visual posture correction feedback with form deviation alerts",
            "Interactive Streamlit dashboard displaying workout metrics and history"
        ]),
        "technologies": "Python, OpenCV, MediaPipe, Streamlit, NumPy",
        "image": "/assets/project-gym-trainer.svg",
        "github_url": "https://github.com/gopalnaik",
        "live_url": "",
        "featured": True,
        "published": True,
        "display_order": 1
    },
    {
        "title": "Emotion Detection",
        "category": "Computer Vision",
        "short_description": "Real-time facial expression analysis and emotion classification using CNNs.",
        "description": "Deep learning convolutional neural network application capable of detecting faces in real time and classifying micro-expressions across 7 discrete emotional states with low inference latency on live video feeds.",
        "problem_statement": "Automated human-computer interaction and mental wellness monitoring require rapid, unobtrusive emotion recognition capable of operating reliably across varying lighting conditions.",
        "key_features": json.dumps([
            "Multi-face detection using Haar cascades and SSD detectors",
            "Custom CNN trained on FER2013 dataset achieving high classification accuracy",
            "Live emotion confidence probability scoring per facial bounding box",
            "Real-time video processing pipeline optimized for low-latency streaming"
        ]),
        "technologies": "Python, OpenCV, TensorFlow, Keras, NumPy",
        "image": "/assets/project-emotion-detection.svg",
        "github_url": "https://github.com/gopalnaik",
        "live_url": "",
        "featured": True,
        "published": True,
        "display_order": 2
    },
    {
        "title": "Smart Attendance System",
        "category": "AI & Web Systems",
        "short_description": "Automated biometric attendance platform with face recognition and database sync.",
        "description": "Enterprise-grade classroom and workplace attendance platform featuring instant multi-student facial recognition, automated entry/exit timestamps, PostgreSQL database synchronization, and an administrative Django analytics dashboard.",
        "problem_statement": "Manual roll calls and biometric fingerprint scanners are time-consuming and prone to proxy attendance in academic environments.",
        "key_features": json.dumps([
            "Automated multi-face identification and 128-d face encoding matching",
            "Instant attendance logging with anti-spoofing and duplicate prevention",
            "Relational PostgreSQL database schema for student and course records",
            "Django administrative control panel with exportable CSV/Excel attendance reports"
        ]),
        "technologies": "Python, OpenCV, Django, PostgreSQL, Face Recognition",
        "image": "/assets/project-smart-attendance.svg",
        "github_url": "https://github.com/gopalnaik",
        "live_url": "",
        "featured": True,
        "published": True,
        "display_order": 3
    },
    {
        "title": "AI Resume Builder",
        "category": "NLP & Full Stack",
        "short_description": "ATS-optimized resume generation system with automated NLP keyword scoring.",
        "description": "Full-stack NLP resume optimization tool that parses target job descriptions, evaluates candidate resumes against Applicant Tracking System (ATS) benchmarks, and dynamically generates keyword-rich suggestions and structured PDFs.",
        "problem_statement": "Job applicants frequently get filtered out by automated ATS scanners due to missing relevant industry keywords and suboptimal formatting.",
        "key_features": json.dumps([
            "TF-IDF and cosine similarity algorithm scoring resume alignment with job postings",
            "Intelligent keyword extraction identifying critical technical skills and requirements",
            "Dynamic PDF export engine producing clean, ATS-compliant formatted documents",
            "Lightweight Flask REST API backend with modular service architecture"
        ]),
        "technologies": "Python, NLP, Flask, Scikit-learn, ReportLab",
        "image": "/assets/project-resume-builder.svg",
        "github_url": "https://github.com/gopalnaik",
        "live_url": "",
        "featured": True,
        "published": True,
        "display_order": 4
    }
]

INITIAL_EDUCATION = [
    {
        "degree": "Computer Science & Engineering",
        "specialization": "Specialization in Data Science",
        "institution": "B.E. / B.Tech Degree Program",
        "start_year": "2022",
        "end_year": "2026",
        "expected_graduation": True,
        "description": "Focusing on data structures, algorithms, statistical data analysis, machine learning algorithms, and modern full-stack web architectures.",
        "coursework": "Data Structures & Algorithms, Machine Learning, Database Management Systems, Computer Networks, Operating Systems, Web Technologies",
        "published": True,
        "display_order": 1
    }
]

INITIAL_SOCIALS = [
    {"name": "GitHub", "url": "https://github.com/gopalnaik", "icon": "github", "display_order": 1, "enabled": True},
    {"name": "LinkedIn", "url": "https://linkedin.com/in/gopalnaik", "icon": "linkedin", "display_order": 2, "enabled": True},
    {"name": "Email", "url": "mailto:gopalnaik.dev@gmail.com", "icon": "mail", "display_order": 3, "enabled": True}
]
