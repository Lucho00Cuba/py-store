# Variables de color (ajusta o define según sea necesario)
YELLOW = \033[33m
GREEN = \033[32m
CYAN = \033[36m
RESET = \033[0m

OUTPUT_TO_FILE := false
V := OUTPUT_TO_FILE=$(OUTPUT_TO_FILE)

TARGETS := $(basename $(notdir $(wildcard scripts/*)))

.PHONY: help

all: help

## Help
help: ## Show this help.
	@echo ''
	@echo 'Usage:'
	@echo "  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}"
	@echo ''
	@echo "${CYAN}Commands${RESET}"
	@for target in $(TARGETS); do \
	    echo "    ${YELLOW}$$target${RESET}"; \
	done
	@echo ''
	@awk 'BEGIN {FS = ":.*?## "} { \
	        if (/^[a-zA-Z_-]+:.*?##.*$$/) {printf "    ${YELLOW}%-20s${GREEN}%s${RESET}\n", $$1, $$2} \
	        else if (/^## .*$$/) {printf "  ${CYAN}%s${RESET}\n", substr($$1,4)} \
	        }' $(MAKEFILE_LIST)

$(TARGETS):
	@$(V) ./scripts/$@