import os
import json
import argparse
import sys
import logging
import colorlog
from aiprchecker.AIPRChecker import AIPRChecker

handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)s:%(message)s'))
logger = colorlog.getLogger('file_generator')
if not logger.hasHandlers():
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Check for security issues and bugs in a PR')
    parser.add_argument('--api-key', default=None, type=str, help='Input API key')
    parser.add_argument('--model', default="gpt-4", type=str, help='Model to use')
    args = parser.parse_args()

    api_key = os.environ.get("INPUT_OPENAI_API_KEY") or args.api_key
    gh_token = os.environ["GITHUB_TOKEN"]
    model = args.model

    if not gh_token:
        logger.error("Error: Missing GitHub token in env var GITHUB_TOKEN.")
        sys.exit(1)

    if not api_key:
        logger.error("Error: Missing API key.")
        parser.print_help()
        sys.exit(1)

    # Load the GitHub event JSON
    with open(os.environ['GITHUB_EVENT_PATH']) as f:
        event = json.load(f)

    # Get the pull request number
    pr_number = event['pull_request']['number']

    # Get the repository info from the GitHub environment variables
    repo = os.environ['GITHUB_REPOSITORY']

    aiprchecker = AIPRChecker(api_key, gh_token, repo, pr_number, model)

    aiprchecker.analyze_patch()

if __name__ == "__main__":
    main()