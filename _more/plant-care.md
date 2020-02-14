---
layout: page
title: Plant care
summary: Cheatsheet for plant care instructions.

full_sun_image: /assets/images/plant_care/full_sun_64.png
part_sun_image: /assets/images/plant_care/part_sun_64.png
indirect_sun_image: /assets/images/plant_care/indirect_sun_64.png
shade_image: /assets/images/plant_care/black_sun_64.png

show_dead_plants: false
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
            <th>Count</th>
        </tr>
    </thead>
    <tbody>
        {% for plant in site.data.plants %}
           {% if page.show_dead_plants or plant.count != "0" %}
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
                        {% assign light_amounts = plant.light | split: ";" %}
                        {% for amount in light_amounts %}
                            {% if amount == "full" %}
                                <img src="{{page.full_sun_image}}" class="icon">
                            {% endif %}
                            {% if amount == "part" %}
                                <img src="{{page.part_sun_image}}" class="icon">
                            {% endif %}
                            {% if amount == "indirect" %}
                                <img src="{{page.indirect_sun_image}}" class="icon">
                            {% endif %}
                            {% if amount == "shade" %}
                                <img src="{{page.shade_image}}" class="icon">
                            {% endif %}
                        {% endfor %}
                    </td>

                    <td>{% if plant.temp %}{{plant.temp}}°{% endif %}</td>

                    <td>{{plant.humidity}}</td>

                    <td>{{plant.feed}}</td>

                    <td>
                        {{plant.notes}}
                        {% assign links = plant.links | split: ";" %}
                        {% for link in links %}
                            <a href="{{link}}">More info.</a>
                        {% endfor %}
                    </td>

                    <td>{{plant.count}}</td>
                </tr>
            {% endif %}
        {% endfor %}
    </tbody>
</table>

***

### Stats

{% assign species_count = 0 %}
{% assign specimen_count = 0 %}
{% for plant in site.data.plants %}
    {% if plant.count != "0" %}
        {% assign species_count = species_count | plus: 1 %}
        {% assign specimen_count = specimen_count | plus: plant.count %}
    {% endif %}
{% endfor %}

Current species count: {{species_count}}\\
Current specimen count: {{specimen_count}}

### Key

**Light**\\
![full]({{page.full_sun_image}}){:class="icon"} Full sun\\
![part]({{page.part_sun_image}}){:class="icon"} Partial sun\\
![indirect]({{page.indirect_sun_image}}){:class="icon"} Indirect sun\\
![shade]({{page.shade_image}}){:class="icon"} Shade

**Water**\\
Surface dry: water when top 1/4-1/2" of soil is dry.\\
Partly dry: water when at least the top 1" of soil is dry.\\
Mostly dry: water when more than half of the soil is dry; should not be bone dry.\\
Fully dry: don't water unless the soil is completely dry. Especially in cooler conditions, these can wait several weeks between watering.

**Temperatures**: if a ">" range is given, it specifies the minimum temperature the plant can survive at, as well as the minimum preferred temperature.

**Feeding**: wait this amount of time between feeding. Stop feeding in winter, unless the plant is actively growing.

### Resources

[Plant troubleshooting guide](http://greenhouse.kenyon.edu/troubleshooting.htm)

[How to write botanical names](http://libanswers.nybg.org/faq/223266)\\
(Additional note: "sp." is unspecified species, "spp." is several species.)

Icon sources\\
<https://www.iconfinder.com/icons/183364/sun_icon>\\
<https://www.iconfinder.com/icons/183365/sun_icon>
