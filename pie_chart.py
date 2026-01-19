import requests
import matplotlib.pyplot as plt

API_URL = "http://localhost:8000"

def fetch_reviews(job_id):
    response = requests.get(f"{API_URL}/reviews/{job_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch reviews")
        return []

def plot_reviews_chart(job_id):
    reviews = fetch_reviews(job_id)

    if not reviews:
        print("No reviews available to plot.")
        return
    
    rating_counts = {}
    for review in reviews:
        rating = review['rating']
        if rating in rating_counts:
            rating_counts[rating] += 1
        else:
            rating_counts[rating] = 1

    labels = [f"{rating} ★" for rating in rating_counts.keys()]
    sizes = rating_counts.values()
    colors = plt.cm.Set3(range(len(rating_counts)))

    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors,
        startangle=0
    )
    
    plt.legend(wedges, labels, title="Ratings", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

    plt.title('Distribution of Reviews by Rating')
    plt.axis('equal')

    plt.show()
