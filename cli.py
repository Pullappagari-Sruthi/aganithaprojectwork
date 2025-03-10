import argparse
from api import fetch_papers, filter_papers, save_to_csv


def main():
    parser = argparse.ArgumentParser(description="Fetch research papers from PubMed.")
    parser.add_argument("query", type=str, help="Search query for PubMed API")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("-f", "--file", type=str, help="Output CSV file", default="papers.csv")

    args = parser.parse_args()

    papers = fetch_papers(args.query, args.debug)
    filtered_papers = filter_papers(papers)

    if filtered_papers:
        save_to_csv(filtered_papers, args.file)
        print(f"Saved {len(filtered_papers)} papers to {args.file}")
    else:
        print("No relevant papers found.")


if __name__ == "__main__":
    main()
