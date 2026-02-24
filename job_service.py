import requests

def fetch_remoteok_jobs(keyword, max_results=5):
    """
    Fetch remote jobs from RemoteOK API matching a keyword.
    
    Parameters:
        keyword (str): Skill or keyword to search for (e.g., "Python", "Java").
        max_results (int): Maximum number of job listings to return (default 5).
        
    Returns:
        List[dict]: List of job dictionaries with title, company, mode, apply_link.
    """
    url = "https://remoteok.com/api"
    
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("Job fetch error:", e)
        return []

    listings = []

    # Normalize keyword for matching
    keyword = keyword.lower().strip()
    keyword_words = keyword.split()  # handle multi-word like "data science"

    for job in data:
        # Skip metadata (first element) and non-dict entries
        if not isinstance(job, dict):
            continue

        title = job.get("position") or job.get("role") or job.get("title") or ""
        company = job.get("company") or ""
        tags = job.get("tags", [])
        apply_link = job.get("url") or ""

        # Combine searchable text
        searchable_text = f"{title} {company} {' '.join(tags)}".lower()

        # Check if any keyword matches
        if any(k in searchable_text for k in keyword_words):
            listings.append({
                "title": title,
                "company": company,
                "mode": ", ".join(tags),
                "apply_link": apply_link
            })

    # Return top N results
    return listings[:max_results]
