---
layout: page
title: Resume
permalink: /resume/
---

([Link to PDF]({{ site.baseurl }}/assets/resume/resume.pdf))

---

---

---

Summary
=======

{{site.data.resume.summary}}

*Code priorities: {{site.data.resume.code-priorities}}*

*Culture priorities: {{site.data.resume.culture-priorities}}*

---

---

---

Education
=========

**{{site.data.resume.education.school}}, {{site.data.resume.education.year}}**

{{site.data.resume.education.major}}, minor in {{site.data.resume.education.minor}}

---

---

---

Skills
======

{% for skill in site.data.resume.skills %}

**{{skill.name}}**

{{skill.value}}
{% endfor %}

---

---

---

Experience
==========

{% for job in site.data.resume.experience.jobs %}

**{{job.company}}**: {{job.role}}; *{{job.start}} - {{job.end}}*

{% for item in job.items %}
* {{item.description}}

{% for subitem in item.subitems %}
  * {{subitem}}
{% endfor %}

{% endfor %}

{% endfor %}

**Internships**

{% for internship in site.data.resume.experience.internships %}
* {{internship.company}}, *{{internship.start}} - {{internship.end}}*: {{internship.description}}
{% endfor %}


---

---

---

Interests
=========

{{site.data.resume.interests}}
