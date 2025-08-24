import os

from django.conf import settings
from django.core.management.base import BaseCommand

from api.chromadb_utils import add_or_update_node, get_collection

# Import all your models and utilities
from api.models import Achievement, Certification, Experience, Project, Publication, Resume
from api.utils import clean_html, extract_pdf_text  # Import clean_html


class Command(BaseCommand):
    help = "Indexes all existing content into the ChromaDB knowledge base."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reindex",
            action="store_true",
            help="Clear the entire collection before indexing new content.",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting content indexing..."))
        collection = get_collection()

        if options["reindex"]:
            self.stdout.write(self.style.WARNING("Clearing existing collection..."))
            # This is a bit of a workaround as Chroma's delete_collection is sometimes tricky.
            # We'll get all items and delete them by ID.
            existing_items = collection.get()
            if existing_items and existing_items["ids"]:
                collection.delete(ids=existing_items["ids"])
            self.stdout.write(self.style.SUCCESS("Collection cleared."))

        # --- 1. Index Static Content ---
        self.stdout.write(self.style.NOTICE("Indexing static content..."))

        # About Me Content (taken from your About.tsx)
        about_me_text = """
        Hello! I'm Md Mushfiqur Rahman, a full-stack data scientist with around 3 years of professional experience. \
        I strive to tackle real-world challenges using my technical expertise in Data Science. \
        I thrive in environments where research work is valued alongside routine tasks, \
        constantly motivated to learn and stay updated with the latest tools and technologies in the ever-evolving data-driven world. \
        Currently, I serve as an AI/ML Team Lead, focusing on designing and implementing advanced Machine Learning and Generative AI systems. \
        My work involves leading the development of innovative AI solutions, \
        including architecting and deploying complex agentic AI systems and solutions built upon Large Language Models (LLMs). \
        I contribute to system design and ensure the smooth execution and deployment of AI-powered projects. \
        My core areas of interest include Statistics, Data Science, Machine Learning, Deep Learning, Generative AI, and Cryptocurrency. \
        I possess a solid understanding of various machine learning and deep learning algorithms, \
        always making an effort to keep pace with new tools and technologies in the AI domain. \
        I believe in "Learning is Surviving!" – a philosophy that guides my proactive approach to continuous professional development. \
        As an active learner, I constantly keep myself updated with AI trends and innovations by reading LinkedIn posts from top AI figures. \
        I participate in Kaggle contests and maintain a strong presence on LinkedIn and GitHub, \
        alongside conducting research work utilizing my knowledge in machine learning and deep learning. \
        I think like a Software Engineer and work like a Data Scientist, with a particular passion for collecting and analyzing datasets. \
        I am very passionate about my work, adhering strictly to schedules to ensure projects are completed before deadlines.
        I believe in ultimate professionalism in my work ethic.
        """
        add_or_update_node(
            doc_id="static-about-me",
            content=f"About Md Mushfiqur Rahman: {about_me_text}",
            metadata={"type": "about", "title": "About Md Mushfiqur Rahman"},
        )
        self.stdout.write(self.style.SUCCESS("Indexed 'About Me' content."))

        # Skills Content (UPDATED to match frontend)
        skills_list = [
            "Python",
            "SQL",
            "Go",
            "HTML / CSS",
            "C / C++",
            "Flask / FastAPI / Streamlit",
            "Django",
            "React",
            "Scikit-learn",
            "TensorFlow",
            "PyTorch",
            "Keras",
            "Langchain",
            "LangGraph",
            "Exploratory Data Analysis",
            "Natural Language Processing (NLP)",
            "Computer Vision",
            "Statistics",
            "Supervised ML",
            "Unsupervised ML",
            "Generative AI",
            "Time-Series Forecasting",
            "Hypothesis Testing",
            "MLOps",
            "MLflow",
            "DVC",
            "Airflow",
            "AWS",
            "Docker",
            "Git & GitHub",
            "CI/CD (GitHub Actions, CircleCI)",
            "Nginx",
            "Monitoring (Prometheus, Grafana)",
            "Caching (Redis)",
            "n8n",
            "Web-scrapping (BeautifulSoup, Selenium)",
        ]
        skills_text = f"Md Mushfiqur Rahman's skills include: {', '.join(skills_list)}."
        add_or_update_node(doc_id="static-skills", content=skills_text, metadata={"type": "skills", "title": "Skills"})
        self.stdout.write(self.style.SUCCESS("Indexed 'Skills' content."))

        # NEW: Index Contact Information
        contact_info_text = """
        Contact Information for Md Mushfiqur Rahman:
        - Email: mushfiqur.rahman.robin@gmail.com
        - LinkedIn: https://linkedin.com/in/mushfiqur--rahman
        - GitHub: https://github.com/Mushfiqur-Rahman-Robin
        He can be reached for collaborations, inquiries, or general contact through these professional channels.
        """
        add_or_update_node(doc_id="static-contact-info", content=contact_info_text, metadata={"type": "contact", "title": "Contact Information"})
        self.stdout.write(self.style.SUCCESS("Indexed 'Contact' content."))

        # --- 2. Index Dynamic Content from Database ---
        self.stdout.write(self.style.NOTICE("\nIndexing dynamic content from database..."))

        # Index Projects (description is RichTextUploadingField, so clean it)
        for project in Project.objects.all():
            cleaned_description = clean_html(project.description)
            content = f"Project Title: {project.title}\nDescription: {cleaned_description}"
            add_or_update_node(f"project-{project.id}", content, {"type": "project", "title": project.title})
        self.stdout.write(self.style.SUCCESS(f"Indexed {Project.objects.count()} projects."))

        # Index Experiences (work_details now stores HTML, so clean it)
        for exp in Experience.objects.all():
            cleaned_work_details = clean_html(exp.work_details)
            content = f"Experience at {exp.company_name} as {exp.job_title}\nDetails: {cleaned_work_details}"
            add_or_update_node(f"experience-{exp.id}", content, {"type": "experience", "title": f"{exp.job_title} at {exp.company_name}"})
        self.stdout.write(self.style.SUCCESS(f"Indexed {Experience.objects.count()} experiences."))

        # Index Certifications
        for cert in Certification.objects.all():
            content = f"Certification: {cert.name}\nIssued by: {cert.issuing_organization}"
            add_or_update_node(f"certification-{cert.id}", content, {"type": "certification", "title": cert.name})
        self.stdout.write(self.style.SUCCESS(f"Indexed {Certification.objects.count()} certifications."))

        # Index Publications
        for pub in Publication.objects.all():
            content = f"Publication: {pub.title}\nAuthors: {pub.authors}\nConference: {pub.conference}"
            add_or_update_node(f"publication-{pub.id}", content, {"type": "publication", "title": pub.title})
        self.stdout.write(self.style.SUCCESS(f"Indexed {Publication.objects.count()} publications."))

        # Index Achievements
        for ach in Achievement.objects.all():
            content = f"Achievement: {ach.title}\nDescription: {ach.description}"
            add_or_update_node(f"achievement-{ach.id}", content, {"type": "achievement", "title": ach.title})
        self.stdout.write(self.style.SUCCESS(f"Indexed {Achievement.objects.count()} achievements."))

        # Index latest Resume
        latest_resume = Resume.objects.order_by("-uploaded_at").first()
        if latest_resume:
            pdf_path = os.path.join(settings.MEDIA_ROOT, latest_resume.pdf_file.name)
            if os.path.exists(pdf_path):
                content = extract_pdf_text(pdf_path)
                if content:
                    add_or_update_node(f"resume-{latest_resume.id}", content, {"type": "resume", "title": latest_resume.title})
                    self.stdout.write(self.style.SUCCESS("Indexed latest resume."))
            else:
                self.stdout.write(self.style.WARNING(f"Resume PDF not found at path: {pdf_path}"))
        else:
            self.stdout.write(self.style.WARNING("No resume found in database to index."))

        self.stdout.write(self.style.SUCCESS("\nContent indexing complete!"))
