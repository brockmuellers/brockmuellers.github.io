---
layout: page
title:  "Fun markdown tricks"
summary: "Markdown tricks, specific to my setup using github pages and kramdown."
---

These are tricks specific to my setup using github pages and kramdown.

***

### Putting markdown in HTML

If you want markdown to be processed inside HTML tags, use the attribute `markdown="1"`.

```html
<div>
**I should be bold but am not**
</div>

<div markdown="1">
**I am bold**
</div>
```
<div>
**I should be bold but am not**
</div>
<div markdown="1">
**I am bold**
</div>


Source [here](https://stackoverflow.com/questions/29368902/how-can-i-wrap-my-markdown-in-an-html-div)

***

### Accordion

```html
<details markdown="1">
<summary>Click to expand!</summary>

1. A list item
2. Another list item

</details>
```

<details markdown="1">
<summary>Click to expand!</summary>

1. A list item
2. Another list item

</details>

***

### Footnotes

```html
This is a text with a
footnote[^1].

Here's some more text.

[^1]: And here is the definition.
```

This is a text with a
footnote[^1].

Here's some more text.

[^1]: And here is the definition.
