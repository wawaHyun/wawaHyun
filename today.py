"""Fetch live GitHub stats and regenerate dark_mode.svg / light_mode.svg.

Environment variables:
  ACCESS_TOKEN  a personal access token (classic: read:user; add `repo` to count
                private contributions)
  USER_NAME     your GitHub username
"""
import os
import sys
from datetime import date, datetime, timezone

import requests

API = "https://api.github.com/graphql"
HEADERS = {"Authorization": f"bearer {os.environ.get('ACCESS_TOKEN', '')}"}
USER = os.environ.get("USER_NAME", "")


def gql(query, variables=None):
    r = requests.post(API, json={"query": query, "variables": variables or {}},
                      headers=HEADERS, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]


def basic_stats():
    q = """
    query($login: String!) {
      user(login: $login) {
        createdAt
        followers { totalCount }
        repositoriesContributedTo(first: 1,
          contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY]) { totalCount }
        repositories(ownerAffiliations: OWNER) { totalCount }
      }
    }"""
    u = gql(q, {"login": USER})["user"]
    return u["createdAt"], u["followers"]["totalCount"], \
        u["repositoriesContributedTo"]["totalCount"], u["repositories"]["totalCount"]


def total_stars():
    q = """
    query($login: String!, $cursor: String) {
      user(login: $login) {
        repositories(first: 100, after: $cursor, ownerAffiliations: OWNER) {
          pageInfo { hasNextPage endCursor }
          nodes { stargazers { totalCount } }
        }
      }
    }"""
    stars, cursor = 0, None
    while True:
        repos = gql(q, {"login": USER, "cursor": cursor})["user"]["repositories"]
        stars += sum(n["stargazers"]["totalCount"] for n in repos["nodes"])
        if not repos["pageInfo"]["hasNextPage"]:
            return stars
        cursor = repos["pageInfo"]["endCursor"]


def total_commits(created_at):
    """Sum commit contributions year by year (the API caps a query at 1 year)."""
    q = """
    query($login: String!, $from: DateTime!, $to: DateTime!) {
      user(login: $login) {
        contributionsCollection(from: $from, to: $to) { totalCommitContributions }
      }
    }"""
    start = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    total = 0
    for year in range(start.year, now.year + 1):
        frm = max(start, datetime(year, 1, 1, tzinfo=timezone.utc))
        to = min(now, datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc))
        total += gql(q, {"login": USER, "from": frm.isoformat(), "to": to.isoformat()}
                     )["user"]["contributionsCollection"]["totalCommitContributions"]
    return total


def main():
    if not USER or not os.environ.get("ACCESS_TOKEN"):
        sys.exit("Set USER_NAME and ACCESS_TOKEN environment variables.")
    created, followers, contrib, repos = basic_stats()
    stats = dict(
        repos=f"{repos:,}",
        contrib=f"{contrib:,}",
        stars=f"{total_stars():,}",
        commits=f"{total_commits(created):,}",
        followers=f"{followers:,}",
    )
    print(stats)

    import build_svg
    build_svg.build(stats, today=date.today(), out_dir=os.path.dirname(os.path.abspath(__file__)))
    print("SVGs updated")


if __name__ == "__main__":
    main()
