"""
E-commerce Recommendation Engine
User-item collaborative filtering using cosine similarity on a
purchase/rating matrix — no external services required.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# ── Sample purchase/rating matrix (rows=users, cols=products) ──────────────
# Rating scale: 0 = not purchased/rated, 1-5 = rating
DATA = {
    "Laptop":     [5, 4, 0, 0, 1, 0],
    "Headphones": [4, 5, 0, 0, 2, 1],
    "Monitor":    [5, 0, 0, 0, 0, 0],
    "Keyboard":   [3, 4, 0, 0, 0, 0],
    "Mouse":      [0, 4, 5, 4, 0, 2],
    "Webcam":     [0, 0, 5, 4, 0, 3],
    "Desk Chair": [0, 0, 4, 5, 0, 0],
    "Notebook":   [0, 0, 0, 0, 5, 4],
    "Pen Set":    [0, 0, 0, 0, 5, 5],
    "Backpack":   [0, 0, 0, 0, 4, 3],
}
USERS = ["Piyush", "Tippsy", "Carol", "Dave", "Eva", "Frank"]

ratings_df = pd.DataFrame(DATA, index=USERS)


def get_user_similarity(df: pd.DataFrame) -> pd.DataFrame:
    """Compute cosine similarity between all users."""
    sim = cosine_similarity(df.values)
    return pd.DataFrame(sim, index=df.index, columns=df.index)


def recommend_for_user(
    user: str,
    ratings: pd.DataFrame,
    top_n: int = 5,
) -> list[tuple[str, float]]:
    """Return top-N product recommendations for a given user."""
    sim_df = get_user_similarity(ratings)
    user_sim = sim_df[user].drop(user)           # similarity to others
    user_ratings = ratings.loc[user]

    # Products the user hasn't rated yet
    unrated = user_ratings[user_ratings == 0].index.tolist()

    scores: dict[str, float] = {}
    for product in unrated:
        # Weighted average of similar users' ratings for this product
        others_rated = ratings[product]
        weighted = sum(
            sim * others_rated[other]
            for other, sim in user_sim.items()
            if others_rated[other] > 0
        )
        total_sim = sum(
            abs(sim)
            for other, sim in user_sim.items()
            if others_rated[other] > 0
        )
        if total_sim > 0:
            scores[product] = weighted / total_sim

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_n]


def display_recommendations(user: str, recs: list[tuple[str, float]]) -> None:
    print("\n" + "═" * 52)
    print(f"  🛒  RECOMMENDATIONS FOR: {user.upper()}")
    print("═" * 52)
    if not recs:
        print("  No new recommendations — user has rated everything!")
    else:
        print(f"  {'#':<4}{'Product':<18}{'Predicted Rating':>16}")
        print("─" * 52)
        for i, (product, score) in enumerate(recs, 1):
            stars = "★" * round(score) + "☆" * (5 - round(score))
            print(f"  {i:<4}{product:<18}{score:>8.2f} / 5   {stars}")
    print("═" * 52)


def main():
    print("Running E-commerce Recommendation Engine …\n")
    print("User-Item Rating Matrix:")
    print(ratings_df.to_string())

    for user in USERS:
        recs = recommend_for_user(user, ratings_df, top_n=3)
        display_recommendations(user, recs)


if __name__ == "__main__":
    main()
