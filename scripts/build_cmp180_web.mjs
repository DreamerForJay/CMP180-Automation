import { createHash } from 'node:crypto';
import { copyFile, mkdir, readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '../.tools/cmp180-viewer/node_modules/@gltf-transform/core/dist/index.js';
import { ALL_EXTENSIONS } from '../.tools/cmp180-viewer/node_modules/@gltf-transform/extensions/dist/index.js';
import { dedup, flatten, join, prune, quantize, weld } from '../.tools/cmp180-viewer/node_modules/@gltf-transform/functions/dist/index.js';

const root = new URL('../', import.meta.url);
const asset = new URL('src/cmp180_evm/web/static/assets/', root);
const vendor = new URL('src/cmp180_evm/web/static/vendor/model-viewer/', root);
await mkdir(asset, { recursive: true });
await mkdir(vendor, { recursive: true });
const source = new URL('assets/cmp180_3d/cmp180.glb', root);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const document = await io.read(fileURLToPath(source));
// 此模型使用純材質；只有沒有任何貼圖時才移除未使用的 UV 與 tangent。
if (document.getRoot().listTextures().length === 0) {
  for (const mesh of document.getRoot().listMeshes()) {
    for (const primitive of mesh.listPrimitives()) {
      for (const semantic of primitive.listSemantics()) {
        if (semantic.startsWith('TEXCOORD_') || semantic === 'TANGENT') primitive.setAttribute(semantic, null);
      }
    }
  }
}
// 原始 Blender／GLB 保留可編輯零件；只有 Web 副本合併同材質網格，降低 draw calls。
// 16-bit 位置量化保留公尺比例，不做簡化刪面，也不依賴外部 Draco／Meshopt 解碼器。
await document.transform(dedup(), flatten(), join(), weld(), quantize({ quantizePosition: 16 }), prune());
const target = new URL('cmp180-web.glb', asset);
await io.write(fileURLToPath(target), document);
const packageRoot = new URL('.tools/cmp180-viewer/node_modules/@google/model-viewer/', root);
const pkg = JSON.parse(await readFile(new URL('package.json', packageRoot), 'utf8'));
if (pkg.version !== '4.3.1') throw new Error('Expected model-viewer 4.3.1; install the documented pinned version.');
await copyFile(new URL('dist/model-viewer.min.js', packageRoot), new URL('model-viewer.min.js', vendor));
await copyFile(new URL('LICENSE', packageRoot), new URL('LICENSE', vendor));
// 一併保存檢視器 bundle 使用的第三方授權；minified upstream 檔案本身保持原樣。
const notices = [];
for (const name of ['three', 'lit', 'lit-element', 'lit-html', '@lit/reactive-element', '@monogrid/gainmap-js']) {
  const license = await readFile(new URL(`.tools/cmp180-viewer/node_modules/${name}/LICENSE`, root), 'utf8');
  notices.push(`${name}\n\n${license}`);
}
await writeFile(new URL('THIRD_PARTY_LICENSES.txt', vendor), notices.join('\n\n--------------------\n\n'));
const originalBytes = await readFile(source);
const webBytes = await readFile(target);
const report = {
  source: 'assets/cmp180_3d/cmp180.glb',
  source_sha256: createHash('sha256').update(originalBytes).digest('hex'),
  source_bytes: originalBytes.length,
  web_bytes: webBytes.length,
  web_sha256: createHash('sha256').update(webBytes).digest('hex'),
  meshes: document.getRoot().listMeshes().length,
  primitives: document.getRoot().listMeshes().reduce((count, mesh) => count + mesh.listPrimitives().length, 0),
  triangles: document.getRoot().listMeshes().reduce((count, mesh) => count + mesh.listPrimitives().reduce((sum, p) => sum + p.getIndices().getCount() / 3, 0), 0),
  model_viewer: pkg.version,
  model_viewer_sha256: createHash('sha256').update(await readFile(new URL('model-viewer.min.js', vendor))).digest('hex'),
  gltf_transform: '4.5.0',
  operations: ['strip-unused-uv-tangents', 'dedup', 'flatten', 'join', 'weld', 'quantize-position-16', 'prune'],
};
await writeFile(new URL('cmp180-web.manifest.json', asset), `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify(report, null, 2));
