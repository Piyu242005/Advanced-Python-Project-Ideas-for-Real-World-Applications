# 🤖 Automated Resume Screening

## Purpose
Automatically rank job applicants by how well their resume matches a given job description — saving manual review time.

## Use Case
HR teams or hiring tools that need to shortlist candidates fast from a large pool of resumes.

## Tech Used
| Library | Role |
|:---|:---|
| `scikit-learn` | TF-IDF vectorization + cosine similarity scoring |
| `NLTK` | Text tokenization and preprocessing |
| `spaCy` | NLP pipeline support |

## Run
```bash
pip install -r requirements.txt
python main.py
```
