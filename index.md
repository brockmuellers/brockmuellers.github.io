---
layout: default
title: Welcome
image: /assets/images/kings_canyon_sunset.jpg
---

<header><h1 class="page-heading">Hi! I'm Sara Brockmueller.</h1></header>

I'm a software engineer with over 10 years of experience in backend development, focused on building cloud-based platforms/frameworks and scaling systems.
I'm passionate about climate change and sustainability, as well as music, plants, hiking, and learning new skills.

---

## Quick links

* [About me]({% link about.md %})

* [Professional experience]({% link resume.md %})

* [My github](https://github.com/{{ site.github_username }})

* [LinkedIn](https://www.linkedin.com/in/{{ site.linkedin_username }})

{% if jekyll.environment == "development" %}

* Featured projects:
	* [Travel log]({% link about.md %}) exploring my sabbatical travels ([github](https://github.com/brockmuellers/travel-log))
	* ACB tracker for doing Canadian taxes ([github](https://github.com/brockmuellers/acb-tracker-ca))
	* OCR transcription of handwritten letters ([github](https://github.com/brockmuellers/family-history))
	* Birdnet

{% endif %}

---

{% include sourced_image.html image=page.image image_class="large-img"%}
