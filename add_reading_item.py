#!/usr/bin/env python3

# import argparse # No longer needed
from datetime import datetime, timedelta
import os
import re
import subprocess
import sys

README_FILE = "README.md"

def get_icon(url):
    """Determines the icon based on the URL."""
    lower_url = url.lower()
    if "youtube.com/" in lower_url or \
       "youtu.be/" in lower_url or \
       "vimeo.com/" in lower_url:
        return "📺"
    # Add more conditions here for other icons like 🎧 for podcasts, 📕 for books if needed
    return "📖"

def main():
    # parser = argparse.ArgumentParser(
    #     description="Adds a new reading/watching/listening item to the README.md file."
    # )
    # parser.add_argument("title", help="The title of the item.")
    # parser.add_argument("url", help="The URL of the item.")
    # parser.add_argument("description", help="A short description of the item.")
    # 
    # args = parser.parse_args()

    # title = args.title
    # url = args.url
    # description = args.description

    print("Enter the details for the new item:")
    title = input("Title: ")
    url = input("URL: ")
    description = input("Description: ")

    icon = get_icon(url)
    
    new_markdown_item = f"- {icon} [{title}]({url}) - {description}"

    if not os.path.exists(README_FILE):
        # Create README.md if it doesn't exist (no title/header)
        lines = []
        print(f"'{README_FILE}' not found. Creating it.")
    else:
        with open(README_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Ensure all lines end with a newline for consistent processing
    lines = [line if line.endswith('\n') else line + '\n' for line in lines]

    # Insert the new item at the very top of the file
    if not lines:
        lines.insert(0, new_markdown_item + "\n")
    else:
        lines.insert(0, new_markdown_item + "\n")
        # Ensure a blank line after the newly inserted item if the next line isn't blank
        if len(lines) > 1 and lines[1].strip() != "":
            lines.insert(1, "\n")

    # Remove any excessive blank lines that might have been created, but keep single blank lines
    # For instance, multiple blank lines between items or at the end of the file.
    deduplicated_lines = []
    for i, line in enumerate(lines):
        is_line_blank = line.strip() == ""
        is_prev_line_blank = i > 0 and deduplicated_lines[-1].strip() == ""
        if is_line_blank and is_prev_line_blank:
            # Skip adding this line if it's a consecutive blank line
            continue
        deduplicated_lines.append(line)
    
    # Ensure there's a newline at the very end of the file if there's content
    if deduplicated_lines and not deduplicated_lines[-1].endswith("\n"):
        deduplicated_lines[-1] += "\n"
    elif not deduplicated_lines and lines: # All lines were blank, restore one if original had content
        deduplicated_lines.append("\n")

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.writelines(deduplicated_lines)

    print(f"Successfully added '{title}' to '{README_FILE}'.")

    # Attempt to automatically commit and push changes if in a git repository
    try:
        # Check if we're inside a git repository
        in_repo = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if in_repo.returncode == 0:
            # Check if README has staged/unstaged changes
            status = subprocess.run(
                ["git", "status", "--porcelain", "--", README_FILE],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if status.stdout.strip():
                subprocess.run(["git", "add", README_FILE], check=False)
                commit_message = f"rwl: add item '{title}'"
                commit = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if commit.returncode == 0:
                    push = subprocess.run(
                        ["git", "push"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if push.returncode == 0:
                        print("Changes pushed to remote.")
                    else:
                        print("Git push failed. You may need to set an upstream or authenticate.")
                else:
                    print("No commit created. Git commit may have failed or there were no changes.")
            else:
                print("No changes detected in README.md; skipping git commit/push.")
        else:
            print("Not a git repository; skipping git commit/push.")
    except Exception:
        # Fail silently for git automation to avoid interrupting primary flow
        print("Skipping git operations due to an unexpected error.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        sys.exit(130)