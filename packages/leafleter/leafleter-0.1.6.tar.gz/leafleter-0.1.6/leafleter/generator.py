import json

def openstreetmap_copyright_notice():
    return 'data: &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

def get_grayscale_tile_layer():
    return get_positron_tile_layer

def get_positron_tile_layer():
    return """L.tileLayer('https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png', {
        attribution: '""" + openstreetmap_copyright_notice() + """', basemap: &copy; <a href="http://cartodb.com/attributions">CartoDB</a>',
        subdomains: 'abcd',
        maxZoom: 19
    })"""

def get_gray_transformed_osm_carto_tile_layer():
    return """L.tileLayer('https://tiles.wmflabs.org/bw-mapnik/${z}/${x}/${y}.png', {
    attribution: '""" + openstreetmap_copyright_notice() + """',
    subdomains: 'abcd',
    maxZoom: 19
})"""

def get_standard_OSM_tile_layer():
    return """L.tileLayer('http://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '""" + openstreetmap_copyright_notice() + """, basemap made by <a href=\"https://github.com/gravitystorm/openstreetmap-carto/\">openstreetmap-carto project</a>',
    maxZoom: 19
})"""

def get_standard_prefix_of_any_html_page(title):
    return """<!DOCTYPE html>
    <html>
    <head>
        <title>""" + title + """</title>
        <meta charset=\"utf-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">"""

def get_leaflet_dependencies():
    # see https://leafletjs.com/download.html for updates
    return """<link rel="stylesheet" href="https://unpkg.com/leaflet@1.4.0/dist/leaflet.css"
  integrity="sha512-puBpdR0798OZvTTbP4A8Ix/l+A4dHDD0DGqYW6RQ+9jxkRFclaxxQb/SJAWZfWAkuyeQUytO7+7N4QKrDh+drA=="
  crossorigin=""/>
<script src="https://unpkg.com/leaflet@1.4.0/dist/leaflet.js"
  integrity="sha512-QVftwZFqvtRNi0ZyCtsznlKSWOStnDORoefr1enyq5mVL4tmKB3S/EnC3rRJcxCPavG10IcrVGSmPh6Qw5lwrg=="
  crossorigin=""></script>"""

def map_area_part_of_styling(width_percent):
    return """        body {
      padding: 0;
      margin: 0;
  }
  html, body {
      height: 100%;
      width: 100%;
  }
  #map {
      height: 100%;
      width: """ + str(width_percent) + """%;
      float: left;
  }"""
    if width_percent != 100:
      returned += """
#pane {
height: 100%;
width: """ + str(100 - width_percent) + """%;
float: right;
}"""

def internal_leaflet_styling_part():
    # workaround for https://github.com/Leaflet/Leaflet/issues/4686
    return "\n .leaflet-fade-anim .leaflet-tile,.leaflet-zoom-anim .leaflet-zoom-animated { will-change:auto !important; }"


def recoloured_markers_styling():
    return """
img.huechange_purple_marker { filter: hue-rotate(50deg); }
img.huechange_pinkish_marker { filter: hue-rotate(120deg); }
img.huechange_red_marker { filter: hue-rotate(158deg); }
img.huechange_green_marker { filter: hue-rotate(250deg); }
"""

def get_html_page_prefix(title, lat_centered, lon_centered, zlevel_centered=13, tile_layer=get_standard_OSM_tile_layer(), width_percent=100, sidebar_content="", css=None):
    # asserts for parameters, I wasted over 1 hour on bug that would be caught by this
    float(zlevel_centered)
    float(lat_centered)
    float(lon_centered)
    float(width_percent)
    if width_percent > 100:
        raise Exception("map cannot cover more than entire width of screen - width_percent was set to " + str(width_percent))
    if width_percent <= 0:
        raise Exception("map cannot cover less than nothing - width_percent was set to " + str(width_percent))
    if zlevel_centered <= 0:
        raise Exception("zlevel cannot be negative - zlevel_centered was set to " + str(zlevel_centered))
    ######

    returned = """
    """ + get_standard_prefix_of_any_html_page(title) + """
    """ + get_leaflet_dependencies() + """
"""
    if css != None:
      returned += '<link rel="stylesheet" type="text/css" href="' + css + '" />'
    returned += "<style>"
    returned += "\n"
    returned += map_area_part_of_styling(width_percent)
    returned += internal_leaflet_styling_part()
    returned += recoloured_markers_styling()
    returned +="""\n    </style>
      </head>
      <body>
        <div id=\"map\"></div><div id=\"pane\">""" + sidebar_content + """</div>

        <script>
          // added for GeoJson adding support
          function onEachFeaturePopupAddingForGeojsonCallback(feature, layer) {
              // does this feature have a property named popupContent?
              if (feature.properties && feature.properties.popupContent) {
                  layer.bindPopup(feature.properties.popupContent);
              }
          }
          var map = L.map('map').setView(['""" + str(lat_centered) + "', '" + str(lon_centered) + "'], '" + str(zlevel_centered) + """');
          mapLink = '<a href=\"http://openstreetmap.org\">OpenStreetMap</a>';
          """ + tile_layer + """.addTo(map);
"""
    return returned

def get_html_page_suffix():
    return """
</script>
</body>
</html>
"""

def get_bind_popup(text):
    if '"' in text and "'" not in text:
        return "bindPopup('" + text + "')"
    elif '"' not in text:
        return "bindPopup(\"" + text + "\"')"
    else:
        raise Exception("both \" and ' in text: " + text)

def get_location(lat, lon):
    return "[" + str(lat) + ", " + str(lon) + "]"

def get_marker(text, lat, lon, color=None):
    # idea from https://stackoverflow.com/a/61982880/4130619 - thanks!
    stylings = {'pink': "._icon.classList.add(\"huechange_pinkish_marker\")",
     'green': "._icon.classList.add(\"huechange_green_marker\")",
     'blue': "",
     None: "",
     'red': "._icon.classList.add(\"huechange_red_marker\")",
     'purple': "._icon.classList.add(\"huechange_purple_marker\")",
     }
    location = get_location(lat, lon)
    returned = "L.marker(" + location + ").addTo(map)." + get_bind_popup(text)
    returned += stylings[color]
    return returned + ";\n"

def get_circle_marker(text, lat, lon, radius_in_px = 10, options = {}):
    location = get_location(lat, lon)
    option_string = ""
    if options != {}:
        option_string = ", {"
        for pair in options:
            option_string += "\t"+ pair + ": " + options[pair] + ","
            option_string += "\n}"
    # docs at https://leafletjs.com/reference-1.4.0.html#circlemarker
    return "L.circleMarker(" + location + option_string + ").setRadius(" + str(radius_in_px) + ").addTo(map)." + get_bind_popup(text) + "\n"

def get_line(lat1, lon1, lat2, lon2, color = 'red', weight = 3, opacity = 0.7):
    dummy_color = "black"
    return get_polyline([[lat1, lon1], [lat2, lon2]], color, dummy_color, weight, opacity)

def get_polygon(positions, color = 'red', fill_color = 'red', weight = 3, opacity = 0.7):
    return get_polyline(positions, color, fill_color, weight, opacity)

def get_polyline(positions, color = 'red', fill_color = 'red', weight = 3, opacity = 0.7):
    locations_string = ""
    for position in positions:
        if locations_string != "":
            locations_string += ", "
        locations_string += get_location(position[0], position[1])
    styling = " {color: '" + str(color) + "', fill: '" + str(fill_color) + "', weight: " + str(weight) + ", opacity: " + str(opacity) + ", lineJoin: 'round'}"
    return "L.polyline([" + locations_string + "]," + styling + ").addTo(map);\n"

def get_geojson_placing(geojson_dictionary):
    json_str = json.dumps(geojson_dictionary, indent=4)
    return "L.geoJSON(" + json_str + """, {
    onEachFeature: onEachFeaturePopupAddingForGeojsonCallback
}).addTo(map);"""

