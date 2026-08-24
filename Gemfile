source "https://rubygems.org"

# The site is a GitHub Pages project site served from docs/ at
# https://pkic.github.io/cbom/. The github-pages gem pins Jekyll and every
# plugin to the exact versions GitHub Pages builds with, so a local preview
# matches what gets published rather than approximating it.
#
#   bundle install
#   bundle exec jekyll serve --source docs
#
# docs/README.md told contributors to run bundle exec jekyll serve before this
# file existed, which could not work: there was nothing for bundler to read.
gem "github-pages", group: :jekyll_plugins

# Ruby 3.0 dropped webrick from the standard library, and Jekyll's built-in
# server needs it. Without this, `jekyll serve` fails with a LoadError.
gem "webrick", "~> 1.8"
