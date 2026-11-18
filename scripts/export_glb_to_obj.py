#!/usr/bin/env python3
"""Export the library's GLB preview geometry to Wavefront OBJ and MTL.

Requires Python 3, numpy, and trimesh. Run from the repository root:
  python scripts/export_glb_to_obj.py
The GLBs remain the source of truth. Exported coordinates use metres and the
same axes as the GLBs. OBJ/MTL cannot preserve all glTF PBR properties.
"""
import json
import re
import struct
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]

def gltf_json(path):
    with path.open('rb') as f:
        magic, version, length, size, kind = struct.unpack('<IIIII', f.read(20))
        if magic != 0x46546c67 or version != 2 or kind != 0x4e4f534a:
            raise ValueError(f'Not a GLB 2.0 JSON chunk: {path}')
        return json.loads(f.read(size))

def name_safe(name):
    return re.sub(r'[^A-Za-z0-9_.-]+', '_', name).strip('_') or 'part'

def export_one(entry):
    item = entry['id']
    src = ROOT / entry['file']
    gltf = gltf_json(src)
    scene = trimesh.load(str(src), force='scene', process=False)
    if gltf.get('images'):
        raise ValueError(f'{item}: textured image requires explicit conversion')
    extras = {n.get('name'): n.get('extras', {}) for n in gltf.get('nodes', []) if 'mesh' in n}
    mats = {m.get('name', f'material_{i}'): m for i, m in enumerate(gltf.get('materials', []))}
    obj = ROOT / 'models' / f'{item}.obj'
    mtl = ROOT / 'models' / f'{item}.mtl'
    groups, materials, vertices, triangles, offset = [], {}, 0, 0, 0
    with obj.open('w', encoding='utf-8', newline='\n') as f:
        f.write(f'# Converted from {entry["file"]}; coordinates in metres, GLB axes.\n')
        f.write(f'# Part names and material labels: obj-parts.json.\nmtllib {item}.mtl\n')
        for i, node in enumerate(scene.graph.nodes_geometry):
            transform, geom = scene.graph[node]
            mesh = scene.geometry[geom]
            base = node if node in extras else re.sub(r'_[0-9a-f]{6}$', '', node)
            ex = extras.get(base)
            if ex is None:
                raise ValueError(f'{item}: missing metadata for {node}')
            verts = trimesh.transform_points(mesh.vertices, transform)
            faces = np.asarray(mesh.faces)
            if not np.isfinite(verts).all() or faces.ndim != 2 or faces.shape[1] != 3 or len(faces)==0:
                raise ValueError(f'{item}: invalid geometry in {node}')
            if faces.min() < 0 or faces.max() >= len(verts):
                raise ValueError(f'{item}: invalid face index in {node}')
            normals = mesh._cache.cache.get('vertex_normals')
            if normals is None or normals.shape != verts.shape or not np.isfinite(normals).all():
                raise ValueError(f'{item}: missing or invalid GLB normals in {node}')
            normal_matrix = np.linalg.inv(transform[:3, :3]).T
            normals = np.asarray(normals) @ normal_matrix.T
            sizes = np.linalg.norm(normals, axis=1)
            if (sizes <= 0).any():
                raise ValueError(f'{item}: zero GLB normals in {node}')
            normals = normals / sizes[:,None]
            mat = getattr(mesh.visual, 'material', None)
            original_material = getattr(mat, 'name', None)
            if original_material is None:
                mat_id = 'mat_default'
                materials[mat_id] = {}
            elif original_material in mats:
                mat_id = f'mat_{list(mats).index(original_material):03d}'
                materials[mat_id] = mats[original_material]
            else:
                raise ValueError(f'{item}: unknown GLB material {original_material}')
            group = f'part_{i:03d}_{name_safe(base)}'
            f.write(f'\no {group}\nusemtl {mat_id}\n')
            np.savetxt(f, verts, fmt='v %.9g %.9g %.9g')
            np.savetxt(f, normals, fmt='vn %.9g %.9g %.9g')
            face_index = faces + offset + 1
            pairs = np.repeat(face_index, 2, axis=1)
            np.savetxt(f, pairs, fmt='f %d//%d %d//%d %d//%d')
            groups.append({'obj_object': group, 'source_node': base, 'source_primitive_node': node,
                           'role': ex.get('role'), 'material_label': ex.get('material_label'),
                           'em_layer': ex.get('em_layer'), 'confidence': ex.get('confidence'),
                           'assembly': ex.get('assembly'), 'obj_material': mat_id,
                           'source_material': original_material, 'vertices': len(verts), 'triangles': len(faces)})
            offset += len(verts); vertices += len(verts); triangles += len(faces)
    if triangles != entry['preview_tris']:
        raise ValueError(f'{item}: {triangles} faces vs GLB index {entry["preview_tris"]}')
    with mtl.open('w', encoding='utf-8', newline='\n') as f:
        f.write('# Approximate GLB base colours; glTF PBR material properties are not fully represented in MTL.\n')
        for name, source in sorted(materials.items()):
            pbr=source.get('pbrMetallicRoughness', {}); color=pbr.get('baseColorFactor',[1,1,1,1]); alpha=float(color[3])
            f.write(f'\nnewmtl {name}\nKd {color[0]:.8g} {color[1]:.8g} {color[2]:.8g}\nd {alpha:.8g}\nillum 2\n')
    return {'id':item,'obj':str(obj.relative_to(ROOT)), 'mtl':str(mtl.relative_to(ROOT)),
            'source_glb':entry['file'],'units':'metres','axes':'same as GLB',
            'original_triangles':entry['tris'],'preview_triangles':entry['preview_tris'],
            'vertices':vertices,'triangles':triangles,'parts':groups}

def main():
    entries=json.loads((ROOT/'assets.json').read_text())
    result=[]
    for i,entry in enumerate(entries,1):
        result.append(export_one(entry))
        if i%10==0 or i==len(entries):print(f'{i}/{len(entries)} {entry["id"]}', flush=True)
    (ROOT/'obj-parts.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
