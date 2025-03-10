import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

PUBMED_API_URL = "https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pubmed/"



PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def fetch_papers(query: str, debug: bool = False):
    """Fetch papers from PubMed API using E-utilities."""
    # Step 1: Search for PubMed IDs
    search_params = {
        "db": "pubmed",
        "term": query,
        "retmax": 10,
        "retmode": "json"
    }
    search_response = requests.get(PUBMED_SEARCH_URL, params=search_params)
    search_data = search_response.json()

    if debug:
        print(f"Search URL: {search_response.url}")
        print(f"Search Response: {search_data}")

    # Extract PubMed IDs
    pubmed_ids = search_data.get("esearchresult", {}).get("idlist", [])

    if not pubmed_ids:
        return []

    # Step 2: Fetch paper details using the IDs
    fetch_params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml"
    }
    fetch_response = requests.get(PUBMED_FETCH_URL, params=fetch_params)

    if debug:
        print(f"Fetch URL: {fetch_response.url}")

    # Parse XML response
    root = ET.fromstring(fetch_response.content)
    papers = []

    for article in root.findall(".//PubmedArticle"):
        title = article.findtext(".//ArticleTitle")
        pubmed_id = article.findtext(".//PMID")
        pub_date = article.findtext(".//PubDate/Year")
        authors = article.findall(".//Author")

        author_list = []
        for author in authors:
            name = author.findtext("LastName") + ", " + author.findtext("ForeName")
            affiliation = author.findtext("AffiliationInfo/Affiliation")
            author_list.append({"name": name, "affiliation": affiliation or "N/A"})

        papers.append({
            "PubMedID": pubmed_id,
            "Title": title,
            "Publication Date": pub_date,
            "Authors": author_list
        })

    return papers
def filter_papers(papers):
    """Filter papers to include at least one non-academic author."""
    filtered = []

    for paper in papers:
        company_authors = [
            a for a in paper["Authors"]
            if a["affiliation"] and any(keyword in a["affiliation"].lower() for keyword in ["pharma", "biotech"])
        ]

        if company_authors:
            filtered.append({
                "PubMedID": paper["PubMedID"],
                "Title": paper["Title"],
                "Publication Date": paper["Publication Date"],
                "Non-academic Author(s)": ", ".join(a["name"] for a in company_authors),
                "Company Affiliation(s)": ", ".join(a["affiliation"] for a in company_authors),
                "Corresponding Author Email": "N/A"  # PubMed API doesn't provide emails directly
            })

    return filtered



def save_to_csv(papers: List[Dict], filename: str = "papers.csv"):
    """Save filtered papers to a CSV file."""
    import csv

    with open(filename, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=papers[0].keys())
        writer.writeheader()
        writer.writerows(papers)

    print(f"Saved {len(papers)} papers to {filename}")



