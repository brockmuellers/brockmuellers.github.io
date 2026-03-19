# brockmuellers.github.io

My personal site.

This is built on github pages with jekyll. There's some odd lualatex in here that generates a pdf resume. Wildly unnecessary, but it was fun to write.

Disclaimer: I'm not a front-end dev and this site reflects that fact.

Find me at [brockmuellers.com](https://self.brockmuellers.com).

## References for myself

#### Jekyll

https://help.github.com/en/github/working-with-github-pages/about-github-pages-and-jekyll

https://github.com/jekyll/minima/tree/v2.5.1

https://jekyllrb.com/docs/

#### Markdown processor

https://kramdown.gettalong.org/syntax.html

https://kramdown.gettalong.org/quickref.html

#### Building locally

`bundle exec jekyll serve --trace --drafts`
(at localhost:4000)

For local dev with local API overrides, create `_config.local.yml` (gitignored) and run:

`bundle exec jekyll serve --trace --drafts --config _config.yml,_config.local.yml`

To enable waypoint photo thumbnails locally, serve your photos directory and set `travel_log_photos_base_url` in `_config.local.yml`:

```bash
python3 -m http.server 8082 --directory /path/to/photos
```

```yaml
# _config.local.yml
travel_log_photos_base_url: "http://localhost:8082"
```

#### Other

Image sources can be recorded and loaded from `_data/image_source.yml`.

[Favicon source](https://www.iconfinder.com/icons/3561781/flower_garden_green_nature_plant_tree_icon)
