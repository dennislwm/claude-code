.PHONY: help setup status test plumb-install plumb-uninit
SHELL := /bin/bash
PLUMB_VERSION := 0.2.4

help:
	@echo ""
	@echo "=== Targets ==="
	@echo "  help          List targets, skills, and agents"
	@echo "  setup         Set up skills for this or a new project"
	@echo "  status        Check if the local machine has already been set up"
	@echo "  test          Run all unit tests"
	@echo "  plumb-install Install plumb-dev==$(PLUMB_VERSION) via pipx"
	@echo "  plumb-uninit  Remove Plumb hooks and data from this project"
	@echo ""
	@source ./make.sh && \
		echo "=== Skills ===" && list_items .claude/commands / 28 && echo "" && \
		echo "=== Hooks ===" && list_items .claude/hooks @ 28 && echo "" && \
		echo "=== Agents ===" && list_items .claude/agents "" 28 && echo ""

setup:
	@source ./make.sh && setup_commands

status:
	@source ./make.sh && show_status

test:
	@source ./make.sh && check_bats && bats tests/

plumb-install:
	pipx install plumb-dev==$(PLUMB_VERSION)

plumb-uninit:
	rm -f .git/hooks/pre-commit .git/hooks/post-commit
	rm -rf .plumb/
	rm -f .plumbignore
