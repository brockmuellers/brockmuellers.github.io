---
layout: page
title: Plants
permalink: /plants/

image: /assets/images/botanical_gardens.jpg

# Icon for each value in the plants.csv light column
light_icons:
  full: /assets/images/plant_care/full_sun_64.png
  part: /assets/images/plant_care/part_sun_64.png
  indirect: /assets/images/plant_care/indirect_sun_64.png
  shade: /assets/images/plant_care/black_sun_64.png

show_dead_plants: false
---

<link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/dt-1.10.20/datatables.min.css"/>
 
<script src="https://code.jquery.com/jquery-3.4.1.min.js" integrity="sha256-CSXorXvZcTkaix6Yvo6HppcZGetbYMGWSFlBw8HfCJo=" crossorigin="anonymous"></script>
<script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.20/datatables.min.js"></script>
<script type="module">
$('#plants').DataTable({ paging: false });
</script>

{% include sourced_image.html image=page.image image_class="large-img"%}

<table id="plants" class="display">
    <thead>
        <tr>
            <th>Name</th>
            <th>Light</th>
            <th>Temp</th>
            <th>Water</th>
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

                    <!-- data-order is the sort key DataTables uses for the column -->
                    <td data-order="{{ plant.light | replace: "full", "0" | replace: "part", "1" | replace: "indirect", "2" | replace: "shade", "3" }}">
                        {% assign light_amounts = plant.light | split: ";" %}
                        {% for amount in light_amounts %}
                            <img src="{{ page.light_icons[amount] }}" alt="{{ amount }}" class="icon">
                        {% endfor %}
                    </td>

                    <td>{% if plant.temp %}{{plant.temp}}°{% endif %}</td>

                    <td data-order="{{ plant.water | replace: "evenly moist", "0" | replace: "surface dry", "1" | replace: "partly dry", "2" | replace: "mostly dry", "3" | replace: "fully dry", "4" }}">{{plant.water}}</td>

                    <td>{{plant.humidity}}</td>

                    <!-- assumes only "wk" or "mo" as time values -->
                    <td data-order="{% if plant.feed contains "wk" %}0{% else %}1{% endif %}">{{plant.feed}}</td>

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
![full]({{page.light_icons.full}}){:class="icon"} Full sun (S window; prefer 50000+ lux)\\
![part]({{page.light_icons.part}}){:class="icon"} Partial sun (direct morning/afternoon sun in E/W window; prefer 20000-50000 lux, can survive at 4000 lux)\\
![indirect]({{page.light_icons.indirect}}){:class="icon"} Indirect sun (near a S/E/W window; prefer 10000-20000 lux, can survive at 2000 lux)\\
![shade]({{page.light_icons.shade}}){:class="icon"} Shade (N window or interior; prefer <10000 lux, can survive at 1000 lux)\\
Listed lux values are very rough estimations.\\
Most plants can tolerate 2-3 hours of indoor direct sun per day, if properly acclimatized.

**Water**\\
Evenly moist: do not allow the soil to dry.\\
Surface dry: water when top 1/4-1/2" of soil is dry.\\
Partly dry: water when at least the top 1" of soil is dry.\\
Mostly dry: water when more than half of the soil is dry; should not be bone dry.\\
Fully dry: don't water unless the soil is completely dry. To avoid root rot in cooler conditions, these can wait several weeks between watering.

**Temperatures**: if a ">" range is given, it specifies the minimum temperature the plant can survive at, as well as the minimum preferred temperature.

**Feeding**: wait this amount of time between feeding. Stop feeding in winter, unless the plant is actively growing.

### Supplements and sprays

* Iron chlorosis: Yellowing leaves may be a sign of iron chlorosis. This can be caused by a deficiency of iron in the soil, but more often is due to the plant failing to take up enough iron. This can be due to problems with the root system (compacted old soil, root rot, etc), because the soil is too alkaline, or because the soil does not have enough organic material. Repotting will often solve the problem, but if that doesn't work or is not possible, one can acidify the soil or provide an iron supplement. To acidify the soil, water with a solution of 1 Tbs vinegar in 1 gal water (or 1/4 tsp vinegar in 1 1/3 cups water). Iron supplementation can be provided monthly with chelated liquid iron, as a foliar spray or soil supplement.

### Resources

[Plant troubleshooting guide](http://greenhouse.kenyon.edu/troubleshooting.htm)

[How to write botanical names](http://libanswers.nybg.org/faq/223266)\\
(Additional note: "sp." is unspecified species, "spp." is several species.)

[Light requirements ranges](https://smartgardenguide.com/light-requirements-for-indoor-plants/)\\

[Specific light requirements for common indoor plants](https://www.houseplantjournal.com/bright-indirect-light-requirements-by-plant/)

Icon sources\\
<https://www.iconfinder.com/icons/183364/sun_icon>\\
<https://www.iconfinder.com/icons/183365/sun_icon>
