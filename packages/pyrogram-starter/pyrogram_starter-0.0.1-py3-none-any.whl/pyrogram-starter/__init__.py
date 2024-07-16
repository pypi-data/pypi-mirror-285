import os
import sys
import logging
from git import Repo

DEFAULT_REPO_URL = "https://github.com/nuhmanpk/pyrogram-bot"
DEFAULT_CLONE_DIR = "pyrogram-bot"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("pyrogram_starter.log", mode='w')
    ]
)

def clone_repo(repo_url, clone_dir):
    try:
        logging.info(f"Cloning repository from {repo_url} to {clone_dir}...")
        Repo.clone_from(repo_url, clone_dir)
        logging.info("Repository cloned successfully.")
    except Exception as e:
        logging.error(f"Error cloning repository: {e}")
        sys.exit(1)

def main():
    repo_url = DEFAULT_REPO_URL
    clone_dir = DEFAULT_CLONE_DIR

    if len(sys.argv) > 1:
        repo_url = sys.argv[1]

    if len(sys.argv) > 2:
        clone_dir = sys.argv[2]

    logging.info("Starting the cloning process...")
    clone_repo(repo_url, clone_dir)
    logging.info("Cloning process completed.")

if __name__ == "__main__":
    main()
