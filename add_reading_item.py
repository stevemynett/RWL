#!/usr/bin/env python3

# import argparse # No longer needed
from datetime import datetime
import os
import subprocess
import sys


def get_target_file():
    """Determines the target file based on the current year."""
    current_year = datetime.now().year
    target_file = f"{current_year}.md"
    
    if not os.path.exists(target_file):
        print(f"Error: '{target_file}' does not exist.")
        print(f"Please create the file manually before adding items for {current_year}.")
        sys.exit(1)
    
    return target_file

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

    # Determine the target file based on current year
    target_file = get_target_file()

    # Pull latest changes before reading file to minimize conflicts
    try:
        subprocess.run(
            ["git", "pull", "--no-rebase"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except Exception:
        pass  # Not a git repo or pull failed - continue anyway

    with open(target_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Ensure all lines end with a newline for consistent processing
    lines = [line if line.endswith('\n') else line + '\n' for line in lines]

    # Insert the new item directly under the title/header (first non-empty line)
    if not lines:
        lines.insert(0, new_markdown_item + "\n")
    else:
        # Find the first non-empty line as the title/header
        header_index = next((i for i, line in enumerate(lines) if line.strip() != ""), 0)
        # Determine insertion point: after any blank lines that follow the header
        insertion_index = header_index + 1
        while insertion_index < len(lines) and lines[insertion_index].strip() == "":
            insertion_index += 1
        # Insert the new item at the computed position (top of the list)
        lines.insert(insertion_index, new_markdown_item + "\n")
        # Ensure there is at least one blank line between the header and the list
        if insertion_index == header_index + 1:
            lines.insert(insertion_index, "\n")

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

    with open(target_file, "w", encoding="utf-8") as f:
        f.writelines(deduplicated_lines)

    print(f"Successfully added '{title}' to '{target_file}'.")

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
            # Check if target file has staged/unstaged changes
            status = subprocess.run(
                ["git", "status", "--porcelain", "--", target_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if status.stdout.strip():
                subprocess.run(["git", "add", target_file], check=False)
                commit_message = f"rwl: add item '{title}'"
                commit = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                if commit.returncode == 0:
                    # Use merge (not rebase) to combine changes - better for
                    # "both sides added lines at the same spot" scenarios
                    pull = subprocess.run(
                        ["git", "pull", "--no-rebase"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    if pull.returncode != 0:
                        print("Git pull failed. Resolve conflicts and push manually.")
                    else:
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
                print(f"No changes detected in {target_file}; skipping git commit/push.")
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