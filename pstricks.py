import re

# Example: \newrgbcolor{xdxdff}{0.49019607843137253 0.49019607843137253 1}
pattern_color = re.compile(r'\\newrgbcolor\s*\{\s*(\w+)\s*}\s*\{\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s*}')
# Example: \pspolygon[linewidth=0.8pt,linecolor=zzttqq,fillcolor=zzttqq,fillstyle=solid,opacity=0.1](-0.4,0)(-0.4,-0.2)
pattern_polygon = re.compile(r'\\pspolygon\s*\[.*fillcolor=(\w+).*]\s*([(\-0-9., )]+)$')
pattern_vertex = re.compile(r'\(\s*([\-0-9.]+)\s*,\s*([\-0-9.]+)\s*\)')


# Utility to read PSTricks - https://en.wikipedia.org/wiki/PSTricks
# files and extract the polygons with colors.
#
# This can be used to load polygins created using - https://www.geogebra.org/m/vtZwe6c6
# and downloaded as PSTricks format.
def load_polygons(filename):
    colors = {}
    polygons = []
    f = open(filename, "r")
    for line in f.readlines():
        line = line.strip()
        # Color
        m = pattern_color.match(line)
        if m:
            name = m.group(1)
            r = int(float(m.group(2)) * 255)
            g = int(float(m.group(3)) * 255)
            b = int(float(m.group(4)) * 255)
            rgb = "#%02X%02X%02X" % (r, g, b)
            # print("Color[%s]: %s = (%d, %d, %d) - %s" % (filename, name, r, g, b, rgb))
            colors[name] = rgb
        # Polygon
        m = pattern_polygon.match(line)
        if m:
            color_name = m.group(1)
            vertices_set = m.group(2)
            # print("Polygon[%s]: color = %s, vertices_set = %s" % (filename, color_name, vertices_set))
            vertices = []
            ms = pattern_vertex.finditer(vertices_set)
            for m in ms:
                x = float(m.group(1))
                y = float(m.group(2)) * -1.0
                vertices.append((x, y))
            # print("Vertices[%s]: %s" % (filename, str(vertices)))
            polygons.append({
                "color": colors[color_name],
                "vertices": vertices
            })

    f.close()
    return polygons
