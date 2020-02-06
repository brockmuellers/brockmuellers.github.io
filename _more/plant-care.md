---
layout: page
title: Plant care
summary: Cheatsheet for plant care instructions.
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
                <i>{{plant.species}}</i>
                {% if plant.variety %}'{{plant.variety}}'{% endif %}
            </td>
            <td>{{plant.light}}</td>
            <td>{{plant.temp}}</td>
            <td>{{plant.humidity}}</td>
            <td>{{plant.feed}}</td>
            <td>{{plant.notes}}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
