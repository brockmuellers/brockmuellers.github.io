---
layout: page
title: Plant care
summary: Cheatsheet for plant care instructions.

full_sun_image: /assets/images/plant_care/full_sun_64.png
part_sun_image: /assets/images/plant_care/part_sun_64.png
indirect_sun_image: /assets/images/plant_care/indirect_sun_64.png
shade_image: /assets/images/plant_care/black_sun_64.png
---

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/dt-1.10.20/datatables.min.css"/>
 
<script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>
<script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.20/datatables.min.js"></script>
<script>$(document).ready(function() {
    $('#plants').DataTable({
        "paging": false
    });
} );</script>

<table id="plants" class="display">
    <thead>
        <tr>
            <th>Name</th>
            <th>Light</th>
            <th>Temp</th>
            <th>Humidity</th>
            <th>Feeding</th>
            <th>Notes</th>
        </tr>
    </thead>
    <tbody>
        {% for plant in site.data.plants %}
        <tr>
            <td>
                <i>{{plant.genus}}</i>
                {% if plant.species == "sp." %}
                    {{plant.species}}
                {% elsif plant.species %}
                    <i>{{plant.species}}</i>
                {% endif %}
                {% if plant.variety %}
                    var. <i>{{plant.variety}}</i>
                {% endif %}
                {% if plant.grex %}
                    {{plant.grex}}
                {% endif %}
                {% if plant.cultivar %}
                    '{{plant.cultivar}}'
                {% endif %}
            </td>

            <td>
                {% if plant.light contains "full" %}
                    <img src="{{page.full_sun_image}}" class="icon">
                {% endif %}
                {% if plant.light contains "part" %}
                    <img src="{{page.part_sun_image}}" class="icon">
                {% endif %}
                {% if plant.light contains "indirect" %}
                    <img src="{{page.indirect_sun_image}}" class="icon">
                {% endif %}
                {% if plant.light contains "shade" %}
                    <img src="{{page.shade_image}}" class="icon">
                {% endif %}
            </td>

            <td>{% if plant.temp %}{{plant.temp}}°{% endif %}</td>
            <td>{{plant.humidity}}</td>
            <td>{{plant.feed}}</td>
            <td>
                {{plant.notes}}
                {% if plant.link %}
                    <a href="{{plant.link}}">More info.</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

***

Key:\\
![full]({{page.full_sun_image}}){:class="icon"} Full sun\\
![part]({{page.part_sun_image}}){:class="icon"} Partial sun\\
![indirect]({{page.indirect_sun_image}}){:class="icon"} Indirect sun\\
![shade]({{page.shade_image}}){:class="icon"} Shade


[Plant troubleshooting guide](http://greenhouse.kenyon.edu/troubleshooting.htm)

[How to write botanical names](http://libanswers.nybg.org/faq/223266)\\
(Additional note: "sp." is unspecified species, "spp." is several species.)

Icon sources\\
<https://www.iconfinder.com/icons/183364/sun_icon>\\
<https://www.iconfinder.com/icons/183365/sun_icon>
