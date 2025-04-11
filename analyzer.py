from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(text):
    if not text.strip():
        return []

    vectorizer = TfidfVectorizer(stop_words='english')
    try:
        X = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out()
    except ValueError:
        return []

def analyze_resume(jd_text, resume_text):
    jd_keywords = extract_keywords(jd_text)
    resume_keywords = extract_keywords(resume_text)

    matched = list(set(jd_keywords).intersection(set(resume_keywords)))
    missing = list(set(jd_keywords) - set(resume_keywords))

    match_score = round((len(matched) / len(jd_keywords)) * 100, 2) if len(jd_keywords) > 0 else 0.0

    return {
        "match_score": match_score,
        "jd_keywords": jd_keywords,
        "matched_keywords": matched,
        "missing_keywords": missing,
    }
