#!/usr/bin/env python3

# import argparse # No longer needed
from datetime import datetime, timedelta
import os
import re

README_FILE = "README.md"
MAIN_TITLE_MARKER = "# What I'm Reading, Watching, and Listening To"
WEEK_ENDING_MARKER = "### Week ending"

def get_friday_date_str():
    """Calculates the date of the upcoming or current Friday."""
    today = datetime.today()
    # Monday is 0 and Sunday is 6. Friday is 4.
    days_until_friday = (4 - today.weekday() + 7) % 7
    target_friday = today + timedelta(days=days_until_friday)
    # Format as M/D/YYYY e.g., 6/7/2024
    return f"{target_friday.month}/{target_friday.day}/{target_friday.year}"

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
    friday_date_str = get_friday_date_str()
    
    new_markdown_item = f"- {icon} [{title}]({url}) - {description}"
    target_section_header = f"{WEEK_ENDING_MARKER} {friday_date_str}"

    if not os.path.exists(README_FILE):
        # Create README.md with a basic structure if it doesn't exist
        lines = [
            f"{MAIN_TITLE_MARKER} as it pertains to my career as an Incident Response Manager.\n",
            "\n"
        ]
        print(f"'{README_FILE}' not found. Creating it with a default header.")
    else:
        with open(README_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Ensure all lines end with a newline for consistent processing
    lines = [line if line.endswith('\n') else line + '\n' for line in lines]

    section_found_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == target_section_header:
            section_found_idx = i
            break

    if section_found_idx != -1:
        # Section exists, insert new item right after the header
        # New items go at the top of the list for that week
        lines.insert(section_found_idx + 1, new_markdown_item + "\n")
    else:
        # Section does not exist, create it.
        # New week sections go at the top, after the main H1 title and any intro.
        
        new_section_block = [
            f"{target_section_header}\n",
            f"{new_markdown_item}\n",
            "\n" # Extra blank line after the new item for spacing before next section
        ]

        # Find where to insert the new week's section
        # It should go after the H1 title block and before the first existing "### Week ending"
        
        h1_index = -1
        for i, line in enumerate(lines):
            if line.startswith(MAIN_TITLE_MARKER):
                h1_index = i
                break
        
        if h1_index == -1 and not lines: # Empty file, or file created fresh without H1
             lines.insert(0, f"{MAIN_TITLE_MARKER} as it pertains to my career as an Incident Response Manager.\n")
             lines.insert(1, "\n") # Blank line after title
             h1_index = 0


        first_week_section_content_idx = -1
        # Start searching after H1 or from beginning if H1 not found/file was empty
        start_search_idx = (h1_index + 1) if h1_index != -1 else 0
        
        for i in range(start_search_idx, len(lines)):
            # Find the first line that is an actual "Week ending" header
            if lines[i].startswith(WEEK_ENDING_MARKER):
                first_week_section_content_idx = i
                break
        
        if first_week_section_content_idx != -1:
            # Insert before the first existing week section
            # Add a blank line before the new section if not already there
            if first_week_section_content_idx > 0 and lines[first_week_section_content_idx -1].strip() != "":
                 lines.insert(first_week_section_content_idx, "\n")
                 lines[first_week_section_content_idx+1 : first_week_section_content_idx+1] = new_section_block
            else:
                 lines[first_week_section_content_idx : first_week_section_content_idx] = new_section_block

        else:
            # No "Week ending" sections exist yet. Add after the H1 title block.
            # Find end of H1 block (H1 + any subsequent blank lines)
            insert_after_h1_idx = h1_index 
            if h1_index != -1: # If H1 was found
                while insert_after_h1_idx + 1 < len(lines) and lines[insert_after_h1_idx + 1].strip() == "":
                    insert_after_h1_idx += 1
            
            # Insert the new section block
            # Add a preceding newline if the line before insertion point isn't blank
            # (and not the H1 itself if it's the only thing)
            final_insert_idx = insert_after_h1_idx + 1
            if final_insert_idx > 0 and lines[final_insert_idx-1].strip() != "" and not lines[final_insert_idx-1].startswith(MAIN_TITLE_MARKER):
                lines.insert(final_insert_idx, "\n")
                lines[final_insert_idx+1 : final_insert_idx+1] = new_section_block
            elif final_insert_idx == 0: # Empty file scenario
                lines[final_insert_idx : final_insert_idx] = new_section_block
            elif lines[final_insert_idx-1].startswith(MAIN_TITLE_MARKER) and lines[final_insert_idx-1].strip() != "": # Directly after H1
                lines.insert(final_insert_idx, "\n") # Ensure a blank line after H1
                lines[final_insert_idx+1 : final_insert_idx+1] = new_section_block
            else: # Already a blank line or just after H1
                 lines[final_insert_idx : final_insert_idx] = new_section_block


    # Remove any excessive blank lines that might have been created, but keep single blank lines
    # For instance, multiple blank lines between week sections or at the end of the file.
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

    print(f"Successfully added '{title}' to '{README_FILE}' for week ending {friday_date_str}.")

if __name__ == "__main__":
    main() 