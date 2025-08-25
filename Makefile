# Default target to run the script
add:
	./add_reading_item.py

# Typing 'make' or 'make add' will execute the script.
# .PHONY ensures these targets run even if files named 'add' or 'all' exist.
.PHONY: add install

# Installation settings
PREFIX ?= /usr/local
BINDIR ?= $(PREFIX)/bin
USER_BINDIR ?= $(HOME)/.local/bin
SCRIPT := add_reading_item.py
TARGET := rwl

# Install the script as 'rwl' to a standard bin directory
install:
	@chmod +x $(SCRIPT)
	@dest="$(BINDIR)"; \
	project_dir="$(CURDIR)"; \
	if [ -d "$$dest" ] && [ -w "$$dest" ]; then \
	  echo "Installing $(TARGET) to $$dest"; \
	  tmp_file="$$(mktemp -t rwlwrap)"; \
	  printf '#!/bin/sh\nPROJECT_DIR="%s"\ncd "$$PROJECT_DIR" || exit 1\nexec ./add_reading_item.py "$$@"\n' "$$project_dir" > "$$tmp_file"; \
	  install -m 0755 "$$tmp_file" "$$dest/$(TARGET)"; \
	  rm -f "$$tmp_file"; \
	elif install -d "$$dest" >/dev/null 2>&1 && [ -w "$$dest" ]; then \
	  echo "Installing $(TARGET) to $$dest"; \
	  tmp_file="$$(mktemp -t rwlwrap)"; \
	  printf '#!/bin/sh\nPROJECT_DIR="%s"\ncd "$$PROJECT_DIR" || exit 1\nexec ./add_reading_item.py "$$@"\n' "$$project_dir" > "$$tmp_file"; \
	  install -m 0755 "$$tmp_file" "$$dest/$(TARGET)"; \
	  rm -f "$$tmp_file"; \
	else \
	  dest="$(USER_BINDIR)"; \
	  echo "No permission for $(BINDIR). Installing to $$dest"; \
	  install -d "$$dest"; \
	  tmp_file="$$(mktemp -t rwlwrap)"; \
	  printf '#!/bin/sh\nPROJECT_DIR="%s"\ncd "$$PROJECT_DIR" || exit 1\nexec ./add_reading_item.py "$$@"\n' "$$project_dir" > "$$tmp_file"; \
	  install -m 0755 "$$tmp_file" "$$dest/$(TARGET)"; \
	  rm -f "$$tmp_file"; \
	  case ":$$PATH:" in *":$$dest:"*) ;; * ) echo "Consider adding $$dest to your PATH" ;; esac; \
	fi