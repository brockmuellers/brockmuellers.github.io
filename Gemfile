source "https://rubygems.org"

# Run Jekyll with `bundle exec jekyll serve`
gem "minima", "~> 2.5.1"
gem "github-pages", group: :jekyll_plugins

# Windows and JRuby don't include zoneinfo files
install_if -> { RUBY_PLATFORM =~ %r!mingw|mswin|java! } do
  gem "tzinfo", "~> 2.0"
  gem "tzinfo-data", "~> 1.2025"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.2.0", :install_if => Gem.win_platform?
