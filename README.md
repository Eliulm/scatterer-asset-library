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

## Wavefront OBJ exports

Every asset has a matching `models/<ID>.obj` and `models/<ID>.mtl` alongside
its GLB. Each OBJ contains the assembly as separately named objects with
normals and material assignments. Coordinates are in metres and use the same
axes as the GLB. `obj-parts.json` maps the OBJ object names back to the GLB
part roles, material labels, electromagnetic layers, and confidence notes.

The OBJs are conversions of the published GLB previews, not the original
builder OBJ files. They therefore have the same triangle counts as the GLBs;
17 previews were simplified compared with the original asset triangle count.
MTL colours approximate the GLB base colours, but the OBJ/MTL format cannot
preserve all glTF PBR material and rendering properties. The GLBs remain the
reference for appearance.

To regenerate the OBJ, MTL and part index files, install Python dependencies
`numpy` and `trimesh` (the current export was made with `trimesh==5.2.1`) and
run `python scripts/export_glb_to_obj.py` from the repository root.
