# Scatterer Asset Library

Interactive 3D browser for generated objects intended for electromagnetic
scattering simulation from 0.1 to 15 GHz. Each asset is an assembly of closed,
material-labelled parts that fits inside a 300 mm diameter sphere.

Open `index.html` through any static web server (or the GitHub Pages site) to
browse 259 assets: orbit and zoom, x-ray exterior parts to see internals, color
by exterior/internal layer, and click parts to read their material labels.

- `assets.json` — index of assets: generic name, category, bounding box (mm),
  triangle counts, and parts with material label, layer and confidence.
- `models/*.glb` — preview meshes with normals (full detail up to 150k triangles per asset,
  smooth shading below a 35° crease angle);
  node extras carry `role`, `material_label`, `em_layer`, `confidence`, `assembly`.

Material labels are categories, not measured electromagnetic constants. The
objects are original designs inspired by real product types, not replicas.
