.PHONY: help setup status test
SHELL := /bin/bash

help:
	@echo ""
	@echo "=== Targets ==="
	@echo "  help     List targets, skills, and agents"
	@echo "  setup    Set up skills for this or a new project"
	@echo "  status   Check if the local machine has already been set up"
	@echo "  test     Run all unit tests"
	@echo ""
	@echo "=== Skills ==="
	@source ./make.sh && list_items .claude/commands / 28
	@echo ""
	@echo "=== Agents ==="
	@source ./make.sh && list_items .claude/agents "" 29
	@echo ""

setup:
	@source ./make.sh && setup_commands

status:
	@source ./make.sh && show_status

test:
	@bats tests/
