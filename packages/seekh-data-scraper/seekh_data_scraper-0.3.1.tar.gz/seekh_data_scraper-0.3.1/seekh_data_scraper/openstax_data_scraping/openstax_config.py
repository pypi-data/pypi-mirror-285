# config.py


# Terms for grouping URLs
KEY_TERM = "key-terms"
GROUP_2_TERMS = ["questions", "problems", "exercises", "assessment-questions", "practice", "quiz", "short-answer", "fill-in-the-blank", "multiple-choice", "critical-thinking"]

# Terms to remove from content URLs
TERMS_TO_REMOVE = [
    "references", "preface-and-foreword", "chapter", "suggested-resources",
    "problem-set-a", "problem-set-b", "summary-of-learning-outcomes", "key-equations",
    "test-prep-for-ap-r-courses", "exercise-set-c", "exercise-set-d", "problems",
    "further-research", "index", "bibliography", "introduction", "thought-provokers",
    "suggested-readings", "suggestions-for-further-study", "chapter-review",
    "exercise-set-a", "exercise-set-b", "preface", "review", "homework", "solutions",
    "bringing-it-together-homework", "true-false", "matching", "glossary", "endnotes",
    "video-activity", "why-it-matters"
]

# Additional summary terms
ADDITIONAL_SUMMARY_TERMS = ["chapter-review", "summary-of-learning-outcomes"]

# Titles to skip when scraping content
SKIP_TITLES = ["learning objectives", "learning outcomes", "suggested readings"]

# Default output file names
DEFAULT_KEYWORD_OUTPUT = "keywords.csv"
DEFAULT_CONTENT_OUTPUT = "content.csv"
DEFAULT_QUESTIONS_OUTPUT = "questions.csv"
DEFAULT_SUMMARY_OUTPUT = "summary.json"