---
# TODO: develop header dropdown menu for these items
layout: page
title: More
permalink: /more/
---
{% for item in site.more limit:33 %}
## [{{ item.title }}]({{ item.url }})
{{ item.summary }}
{% endfor %}
