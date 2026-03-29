"""
Automated Resume Screening
Uses TF-IDF vectorization + cosine similarity to rank resumes
against a job description — no external APIs required.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Sample data (replace with real file I/O as needed) ─────────────────────

JOB_DESCRIPTION = """
We are looking for a Python Developer with experience in machine learning,
data analysis, and building REST APIs. The candidate should know scikit-learn,
pandas, NumPy, and Flask. Knowledge of SQL databases and Git is a plus.
"""

RESUMES = {
    "Piyush": """
        Python developer with 3 years of experience. Skilled in scikit-learn,
        pandas, NumPy and Flask. Built multiple RESTful APIs. Familiar with
        PostgreSQL and version control with Git.
    """,
    "Tippsy": """
        Front-end developer experienced in React, JavaScript, HTML and CSS.
        Some Python scripting knowledge. No machine learning background.
    """,
    "Carol": """
        Data scientist with expertise in machine learning, TensorFlow, pandas,
        and NumPy. Published research in NLP. Comfortable with Python and Git.
    """,
    "Dave": """
        Java backend developer with Spring Boot. Limited Python experience.
        Worked with SQL databases and REST APIs extensively.
    """,
    "Eva": """
        Full-stack Python developer. Uses Flask, scikit-learn, pandas, and NumPy
        daily. Strong SQL skills, active Git user, builds data pipelines.
    """,
}


def rank_resumes(job_desc: str, resumes: dict[str, str]) -> list[tuple[str, float]]:
    """Return candidates ranked by cosine similarity to the job description."""
    names = list(resumes.keys())
    corpus = [job_desc] + [resumes[n] for n in names]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # Row 0 = job description; rows 1..N = resumes
    scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    ranked = sorted(zip(names, scores), key=lambda x: x[1], reverse=True)
    return ranked


def display_results(ranked: list[tuple[str, float]]) -> None:
    print("\n" + "═" * 50)
    print("  🤖  AUTOMATED RESUME SCREENING RESULTS")
    print("═" * 50)
    print(f"  {'Rank':<6}{'Candidate':<12}{'Match Score':>12}")
    print("─" * 50)
    for rank, (name, score) in enumerate(ranked, start=1):
        bar = "█" * int(score * 30)
        print(f"  #{rank:<5}{name:<12}{score:>10.2%}  {bar}")
    print("═" * 50)
    print(f"\n  ✅  Top candidate: {ranked[0][0]}\n")


def main():
    print("Running Automated Resume Screening …")
    ranked = rank_resumes(JOB_DESCRIPTION, RESUMES)
    display_results(ranked)


if __name__ == "__main__":
    main()
