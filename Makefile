# ==============================================================
# Hatsik Makefile
# ==============================================================

TAILWIND_BIN = ./tailwindcss

.PHONY: tailwind-watch tailwind-build help

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

tailwind-watch: ## Run Tailwind in watch mode (local dev)
	$(TAILWIND_BIN) -i static/css/input.css -o static/css/main.css --watch

tailwind-build: ## Compile and minify Tailwind CSS (production)
	$(TAILWIND_BIN) -i static/css/input.css -o static/css/main.css --minify

tailwind-install: ## Download Tailwind CLI standalone binary (macOS arm64)
	curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
	chmod +x tailwindcss-macos-arm64
	mv tailwindcss-macos-arm64 tailwindcss
