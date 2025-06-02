# Default target to run the script
add:
	./add_reading_item.py

# Typing 'make' or 'make add' will execute the script.
# .PHONY ensures these targets run even if files named 'add' or 'all' exist.
.PHONY: add 