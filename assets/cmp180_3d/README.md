# CMP180 Blender 立體外觀模型

## 繁體中文

此資料夾提供 R&S CMP180 的可編輯 Blender 外觀模型。模型依官方產品頁、官方型錄與使用者提供的正面、背面及三分之四視角照片，以程序化硬表面方式建立。機殼採公尺單位，主要比例以官方的 2 HU × 19 吋規格與產品照片校準；`model-spec.json` 記錄建模假設。

這是展示與介面視覺化用途的外觀參考模型，不是原廠機構 CAD。照片無法確認的孔位、圓角、面板厚度與背板細節均為視覺估算，不應用於機構干涉、治具、散熱或安全設計。

產物：

- `cmp180.blend`：可編輯 Blender 原始檔。
- `renders/cmp180-hero.png`：工作室三分之四視角驗證渲染。
- `renders/cmp180-front.png`、`cmp180-rear.png`：正面與背面驗證渲染。
- `cmp180.glb`：方便 Web 或簡報使用的交換格式。
- `model-spec.json`：尺寸、零件與來源紀錄。

重新產生模型：

```powershell
uv run --python 3.13 --with bpy==5.2.1 python scripts/build_cmp180_blender.py
```

腳本只建立本機 3D 資產，不會連線 CMP180、不會送出 SCPI，也不會改變 RF 或量測狀態。

## English

This folder contains an editable Blender exterior model of the R&S CMP180. It is procedurally hard-surface modeled from the official product page, the official brochure, and the supplied front, rear, and three-quarter reference images. The scene uses metres. Its main proportions are calibrated to the official 2 HU × 19-inch format and the photographs; modeling assumptions are recorded in `model-spec.json`.

This is an exterior reference asset for presentation and interface visualization, not manufacturer mechanical CAD. Hole placement, radii, panel thickness, and rear-panel details that cannot be established from the photographs are visual estimates. Do not use the asset for mechanical interference, fixture, thermal, or safety design.

Outputs:

- `cmp180.blend`: editable Blender source.
- `renders/cmp180-hero.png`: studio three-quarter validation render.
- `renders/cmp180-front.png` and `cmp180-rear.png`: front and rear validation renders.
- `cmp180.glb`: interchange file for web or presentation use.
- `model-spec.json`: dimensions, parts, and provenance.

Regenerate the asset with:

```powershell
uv run --python 3.13 --with bpy==5.2.1 python scripts/build_cmp180_blender.py
```

The script creates local 3D assets only. It does not connect to a CMP180, transmit SCPI, or change RF or measurement state.
