import os
import sys

# Ensure repository root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from github import Github
import openai
from app.core.logger import log_event

REPO = os.getenv("GITHUB_REPOSITORY")
PR_NUMBER = os.getenv("PR_NUMBER") or os.getenv("GITHUB_REF", "refs/pull/0").split("/")[-2]
TOKEN = os.getenv("GITHUB_TOKEN")
API_KEY = os.getenv("INPUT_OPENAI_API_KEY")


def get_pr_diff() -> str:
    """Return aggregated diff text for the pull request."""
    g = Github(TOKEN)
    repo = g.get_repo(REPO)
    pr = repo.get_pull(int(PR_NUMBER))
    diff_text = ""
    for file in pr.get_files():
        if file.patch:
            diff_text += f"\n--- {file.filename} ---\n{file.patch}\n"
    return diff_text


def run_review(diff: str) -> str:
    """Submit diff to OpenAI and return the review."""
    openai.api_key = API_KEY
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "你是一位資安工程師，請審查這段 diff 內容是否有安全性或程式設計問題，並提出具體建議。請以繁體中文回答。",
            },
            {"role": "user", "content": diff[:4000]},
        ],
    )
    return response["choices"][0]["message"]["content"]


def main() -> None:
    log_event("CodexReview", "fetch_diff", {}, "INFO")
    diff = get_pr_diff()
    log_event("CodexReview", "send_to_openai", {}, "INFO")
    result = run_review(diff)
    log_event("CodexReview", "review_result", {"result": result}, "INFO")

    if "\u91cd\u5927\u5b89\u5168\u554f\u984c" in result or "\u4e0d\u8981\u5408\u4f75" in result:
        log_event("CodexReview", "critical_issue_found", {}, "ERROR")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
