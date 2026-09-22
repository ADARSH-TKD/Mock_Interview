"""Constants, dictionaries, and wordlists for the Resume Analyzer."""

from typing import Dict, List, Set

# Essential sections that ATS and human recruiters expect
ESSENTIAL_SECTIONS = [
    "experience",
    "education",
    "summary",
    "skills",
    "projects",
]

# Section aliases for intelligent heading recognition
SECTION_ALIASES: Dict[str, Set[str]] = {
    "summary": {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career objective",
        "objective",
        "about me",
        "executive summary",
        "personal statement",
        "career summary",
    },
    "education": {
        "education",
        "academic background",
        "qualifications",
        "educational background",
        "academics",
        "degrees",
        "academic qualifications",
        "education and training",
    },
    "experience": {
        "experience",
        "work experience",
        "professional experience",
        "employment",
        "employment history",
        "work history",
        "internships",
        "internship experience",
        "relevant experience",
        "practical experience",
    },
    "skills": {
        "skills",
        "technical skills",
        "technologies",
        "core competencies",
        "areas of expertise",
        "skillset",
        "tools & technologies",
        "tools and technologies",
        "technical proficiencies",
        "programming skills",
    },
    "projects": {
        "projects",
        "personal projects",
        "academic projects",
        "key projects",
        "notable projects",
        "technical projects",
        "software projects",
        "selected projects",
    },
    "certifications": {
        "certifications",
        "certificates",
        "courses",
        "licenses & certifications",
        "professional certifications",
        "accreditations",
    },
    "achievements": {
        "achievements",
        "awards",
        "accomplishments",
        "honors",
        "awards & honors",
        "recognitions",
        "key achievements",
    },
    "publications": {
        "publications",
        "research papers",
        "patents",
        "articles",
        "conference papers",
    },
}

# Skill ontology grouping
SKILL_GROUPS: Dict[str, Set[str]] = {
    # Programming Languages
    "Python": {"python", "py"},
    "Java": {"java"},
    "C++": {"c++", "cpp"},
    "C": {"c language", "c programming"},
    "C#": {"c#", "csharp", "c sharp"},
    "JavaScript": {"javascript", "js", "ecmascript"},
    "TypeScript": {"typescript", "ts"},
    "Go / Golang": {"go", "golang"},
    "Rust": {"rust"},
    "Ruby": {"ruby"},
    "PHP": {"php"},
    "Kotlin": {"kotlin"},
    "Swift": {"swift"},
    "SQL": {"sql", "mysql", "postgresql", "postgres", "sqlite", "plsql", "t-sql"},
    # AI / Data Science / ML
    "Machine Learning": {"machine learning", "ml"},
    "Deep Learning": {"deep learning", "dl"},
    "NLP": {"nlp", "natural language processing"},
    "Computer Vision": {"computer vision", "cv", "opencv"},
    "TensorFlow": {"tensorflow", "tf"},
    "PyTorch": {"pytorch"},
    "Keras": {"keras"},
    "Hugging Face": {"hugging face", "transformers"},
    "Scikit-learn": {"scikit-learn", "sklearn"},
    "Pandas": {"pandas"},
    "NumPy": {"numpy"},
    "SciPy": {"scipy"},
    "Matplotlib": {"matplotlib"},
    "Seaborn": {"seaborn"},
    "LLMs / GenAI": {"llm", "llms", "large language models", "generative ai", "genai", "prompt engineering", "langchain", "llamaindex", "rag"},
    # Web & Frameworks
    "React": {"react", "reactjs", "react.js"},
    "Next.js": {"next.js", "nextjs"},
    "Node.js": {"node.js", "nodejs", "node"},
    "Express": {"express", "expressjs"},
    "Django": {"django"},
    "Flask": {"flask"},
    "FastAPI": {"fastapi"},
    "Streamlit": {"streamlit"},
    "Spring Boot": {"spring boot", "spring framework"},
    "HTML/CSS": {"html", "html5", "css", "css3"},
    "Tailwind CSS": {"tailwind", "tailwindcss"},
    "GraphQL": {"graphql"},
    "RESTful APIs": {"rest api", "restful api", "rest", "apis"},
    # Databases & Big Data
    "MongoDB": {"mongodb", "mongo"},
    "Redis": {"redis"},
    "Elasticsearch": {"elasticsearch"},
    "Cassandra": {"cassandra"},
    "Kafka": {"kafka", "apache kafka"},
    "Spark": {"spark", "pyspark", "apache spark"},
    "Hadoop": {"hadoop"},
    "Snowflake": {"snowflake"},
    "BigQuery": {"bigquery"},
    # Cloud & DevOps
    "AWS": {"aws", "amazon web services", "ec2", "s3", "lambda"},
    "Azure": {"azure", "microsoft azure"},
    "GCP": {"gcp", "google cloud platform", "google cloud"},
    "Docker": {"docker", "containerization"},
    "Kubernetes": {"kubernetes", "k8s"},
    "Terraform": {"terraform"},
    "CI/CD": {"ci/cd", "ci cd", "github actions", "jenkins", "gitlab ci"},
    "Linux / Bash": {"linux", "unix", "bash", "shell scripting"},
    "Git": {"git", "github", "gitlab", "version control"},
    # CS Fundamentals
    "DBMS": {"dbms", "database management", "relational database"},
    "Computer Networks": {"computer networks", "networking", "tcp/ip"},
    "Operating Systems": {"operating systems", "operating system", "os"},
    "Data Structures": {"data structures", "dsa"},
    "Algorithms": {"algorithms", "algorithm design"},
    "System Design": {"system design", "distributed systems"},
    "OOP": {"object oriented programming", "oop", "oops"},
}

# Strong Action Verbs for bullet point evaluation
ACTION_VERBS: Set[str] = {
    # Leadership & Management
    "led", "directed", "spearheaded", "orchestrated", "supervised", "managed",
    "guided", "mentored", "coached", "coordinated", "oversaw", "championed",
    "steered", "empowered", "cultivated",
    # Technical & Engineering
    "developed", "engineered", "architected", "implemented", "built", "designed",
    "coded", "programmed", "constructed", "deployed", "scaled", "automated",
    "configured", "integrated", "refactored", "debugged", "optimized", "enhanced",
    "migrated", "upgraded", "maintained", "containerized", "instrumented",
    # Innovation & Research
    "pioneered", "formulated", "researched", "investigated", "devised", "invented",
    "conceived", "initiated", "established", "modeled", "simulated", "trained",
    "fine-tuned", "evaluated", "benchmarked",
    # Impact & Optimization
    "increased", "boosted", "accelerated", "maximized", "reduced", "minimized",
    "slashed", "saved", "cut", "decreased", "eliminated", "streamlined",
    "revamped", "modernized", "transformed", "strengthened", "expedited",
    # Collaboration & Delivery
    "collaborated", "partnered", "delivered", "executed", "launched", "produced",
    "published", "authored", "presented", "negotiated", "resolved", "facilitated",
}

# Synonyms for overused or repetitive action verbs
ACTION_VERB_SYNONYMS: Dict[str, List[str]] = {
    "managed": ["spearheaded", "orchestrated", "guided", "directed", "supervised", "steered"],
    "helped": ["facilitated", "assisted", "supported", "collaborated on", "expedited"],
    "worked": ["engineered", "developed", "executed", "implemented", "constructed"],
    "created": ["architected", "formulated", "designed", "pioneered", "devised"],
    "handled": ["resolved", "navigated", "executed", "remediated", "dispatched"],
    "improved": ["enhanced", "optimized", "streamlined", "revamped", "elevated"],
    "led": ["spearheaded", "orchestrated", "championed", "directed", "guided"],
    "used": ["leveraged", "utilized", "deployed", "implemented", "applied"],
    "made": ["produced", "generated", "constructed", "crafted", "delivered"],
    "did": ["executed", "performed", "accomplished", "conducted", "realized"],
}

# Overused buzzwords & resume clichés to flag
BUZZWORDS_AND_CLICHES: List[str] = [
    "responsible for",
    "duties included",
    "team player",
    "hardworking",
    "go-getter",
    "self-starter",
    "detail-oriented",
    "results-driven",
    "think outside the box",
    "fast-paced environment",
    "proven track record",
    "synergy",
    "dynamic",
    "hard worker",
    "problem solver",
    "work ethic",
    "people person",
    "value-add",
    "strategic thinker",
    "hit the ground running",
]

# Technical dictionary of words that must NEVER be flagged as spelling errors
TECH_DICTIONARY: Set[str] = {
    # Frameworks, libs, technologies
    "pytorch", "tensorflow", "keras", "scikit", "sklearn", "pandas", "numpy", "scipy",
    "matplotlib", "seaborn", "plotly", "streamlit", "gradio", "opencv", "spacy", "nltk",
    "gensim", "transformers", "huggingface", "bert", "roberta", "gpt", "llm", "llms",
    "langchain", "llamaindex", "faiss", "chromadb", "pinecone", "milvus",
    "docker", "kubernetes", "k8s", "ansible", "terraform", "helm", "grafana", "prometheus",
    "fastapi", "flask", "django", "celery", "rabbitmq", "kafka", "redis", "elasticsearch",
    "mongodb", "postgresql", "postgres", "mysql", "sqlite", "mariadb", "dynamodb",
    "react", "reactjs", "nextjs", "vue", "vuejs", "angular", "angularjs", "svelte",
    "nodejs", "expressjs", "express", "tailwind", "tailwindcss", "bootstrap",
    "graphql", "restful", "grpc", "protobuf", "websocket", "websockets", "oauth", "jwt",
    "github", "gitlab", "bitbucket", "jira", "confluence", "jenkins", "circleci",
    "aws", "gcp", "azure", "ec2", "s3", "lambda", "cloudfront", "sagemaker", "cloudwatch",
    "linux", "ubuntu", "debian", "centos", "redhat", "bash", "powershell", "zsh",
    "devops", "mlops", "ci", "cd", "cicd", "etl", "elt", "bi", "dwh", "saas", "paas", "iaas",
    "api", "apis", "sdk", "sdks", "cli", "crud", "orm", "nosql", "rdbms", "dbms",
    "json", "yaml", "xml", "csv", "tsv", "html", "css", "sql", "nosql",
    "frontend", "backend", "fullstack", "microservices", "serverless", "monolith",
    "agile", "scrum", "kanban", "sprint", "standup", "okrs", "kpis",
    "blockchain", "crypto", "solidity", "web3", "iot", "vr", "ar",
    "bachelor", "bachelors", "master", "masters", "phd", "btech", "mtech", "bsc", "msc",
    "gpa", "cgpa", "honors", "cum", "laude",
    "linkedin", "github", "leetcode", "hackerrank", "kaggle", "stackoverflow",
    "intern", "internship", "internships", "freelance", "fulltime", "parttime",
    "cert", "certified", "certification", "credential", "coursera", "udemy", "edx",
    "pdfplumber", "pypdf", "docx", "regex", "regexes",
}

# CS core subjects for interview questions
CORE_SUBJECTS: List[str] = [
    "Data Structures",
    "Algorithms",
    "DBMS",
    "SQL",
    "Operating Systems",
    "Computer Networks",
    "System Design",
]

# Section-specific interview questions
FIXED_QUESTIONS: Dict[str, List[str]] = {
    "summary": [
        "Give me a brief elevator pitch about yourself based on your resume summary.",
        "What specific career trajectory are you aiming for, and why does this role align with it?",
    ],
    "education": [
        "How did your academic coursework prepare you for solving complex real-world technical problems?",
        "What was the most challenging technical project or research paper during your degree?",
    ],
    "experience": [
        "Walk me through a high-impact project from your work experience, focusing on your specific contribution.",
        "Tell me about a difficult technical roadblock you encountered on the job and how you diagnosed and resolved it.",
    ],
    "projects": [
        "Explain the end-to-end architecture of your strongest project, including trade-offs you made.",
        "If you had another 3 months and a larger budget, what would you re-architect in your project?",
    ],
    "skills": [
        "Which technical skill on your resume do you consider your superpower, and where have you pushed its limits?",
        "How do you quickly master a new library, framework, or paradigm when an urgent business need arises?",
    ],
    "certifications": [
        "Which certification or specialization taught you practical skills that you actively apply?",
        "How do you evaluate whether a new technology or certification is worth investing time into?",
    ],
    "achievements": [
        "Tell me about a competition, award, or milestone you earned and the perseverance it demanded.",
        "How do you define success in your engineering endeavors?",
    ],
}
