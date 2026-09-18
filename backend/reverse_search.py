from serpapi import GoogleSearch

import os

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

def reverse_image_search(image_url):
    """
    Performs Google Lens reverse image search
    """

    params = {
        "engine": "google_lens",
        "url": image_url,
        "api_key": SERPAPI_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    return results


def analyze_reverse_search(image_url):
    """
    Processes reverse search results
    and returns clean JSON response for Flask
    """

    results = reverse_image_search(image_url)

    response = {
        "matches_found": 0,
        "digital_footprint": "LOW",
        "sources": []
    }


    if "visual_matches" in results:

        matches = results["visual_matches"]

        response["matches_found"] = len(matches)


        # Determine digital footprint
        if len(matches) >= 20:
            response["digital_footprint"] = "HIGH"

        elif len(matches) >= 5:
            response["digital_footprint"] = "MEDIUM"

        else:
            response["digital_footprint"] = "LOW"



        # Extract top 10 results only
        for match in matches[:10]:

            response["sources"].append(
                {
                    "title": match.get("title", "Unknown"),
                    "source": match.get("source", "Unknown"),
                    "link": match.get("link", "")
                }
            )


    return response



# Testing separately
if __name__ == "__main__":

    image_url = input("Image URL: ")

    result = analyze_reverse_search(image_url)


    print("\n========== REVERSE SEARCH ==========\n")

    print("Matches Found:", result["matches_found"])

    print("Digital Footprint:", result["digital_footprint"])

    print("\nTop Sources:\n")


    for i, source in enumerate(result["sources"], start=1):

        print(f"{i}. {source['title']}")
        print(f"   Source : {source['source']}")
        print(f"   Link   : {source['link']}")
        print()