# 项目结构详解

```
travel/
│
├── README.md                   # 完整项目文档（设计系统、架构、维护指南）
├── QUICKSTART.md              # 快速开始与常见任务（本地预览、更新数据、部署）
├── PROJECT_STRUCTURE.md       # 本文件
│
├── map/                        # 行程地图页面
│   ├── index.html             # 自包含单页（SVG 地图 + 时间轴 + 抽屉）
│   └── assets/
│       └── fonts/
│           ├── fonts.css      # 字体声明 + 全局样式（当前在用：Fraunces + 思源宋体/黑体）
│           ├── Fraunces-var.woff2           # ✨ 拉丁展示字体（120 KB，可变）
│           ├── NotoSerifSC-var.woff2        # ✨ 中文大标题字体（2.7 MB，可变）
│           ├── NotoSansSC-cjk.woff2         # ✨ 正文/UI 字体（2.0 MB，可变）
│           │
│           └── [旧字体，已弃用，可删除]
│               ├── Jost-*.woff2
│               ├── Cormorant Garamond-*.woff2
│               └── EBGaramond-*.woff2
│
├── food/                       # 餐厅指南页面
│   ├── index.html             # 自包含单页（506 家餐厅，日期 + 筛选器）
│   └── data/
│       └── food-data.json     # 数据文件（提取脚本的输出，与 index.html 同步）
│
└── scripts/
    └── extract_food.py        # 数据提取脚本（docx → JSON）

```

---

## 文件职责速查表

| 文件 | 大小 | 用途 | 修改频率 |
|------|------|------|---------|
| `README.md` | 15 KB | 完整文档（设计、架构、维护） | 低（更新重大功能时） |
| `QUICKSTART.md` | 8 KB | 快速上手指南 + 常见任务 | 低（工作流稳定后） |
| `map/index.html` | 108 KB | 地图页的 HTML + CSS + JS | 中（车程/地雷/住宿变更） |
| `food/index.html` | 196 KB | 餐厅页的 HTML + CSS + JS + JSON | 高（餐厅信息频繁变更） |
| `fonts.css` | 1 KB | 字体声明 + 全局样式 | 低（字体升级时） |
| `Fraunces-var.woff2` | 120 KB | 拉丁字体 | 无（除非升级版本） |
| `NotoSerifSC-var.woff2` | 2.7 MB | 中文宋体 | 无 |
| `NotoSansSC-cjk.woff2` | 2.0 MB | 中文黑体 | 无 |
| `food-data.json` | ~35 KB | 506 家餐厅的结构化数据 | 高（提取脚本自动生成） |
| `extract_food.py` | 6 KB | docx → JSON 提取脚本 | 低（通常无需改） |

**总体大小**：~7.5 MB（字体占 95%）

---

## 构建与部署流程

### 数据流

```
美西沿途餐厅筛选_V2_2026核实版_20260707.docx
            ↓ (Python 提取)
        extract_food.py
            ↓
    food-data.json (本地)
            ↓ (手工或脚本注入)
    food/index.html (含 JSON 内联)
            ↓ (scp)
  tdb:/www/wwwroot/novaisle-static/food/
            ↓ (nginx 直出)
    https://novaisle.com/food/
```

### 编辑与发布流程

```
LOCAL WORK
├─ map/index.html        (编辑 DAYS 数组 / CSS / JS)
├─ food/index.html       (编辑筛选器 / 样式)
├─ fonts.css             (改字体 / 全局样式)
│
↓ (本地测试)
python3 -m http.server 8000
→ http://localhost:8000
→ 验证交互 / 数据 / 样式 ✓
│
↓ (部署)
./deploy.sh
或手工 scp
│
↓ (线上验证)
https://novaisle.com/map/
https://novaisle.com/food/
```

---

## 关键代码位置速查

### 改日期时间轴颜色

**文件**：`map/index.html` 或 `food/index.html`  
**位置**：`<style>` 块中的 `:root` 变量  
**搜索**：`--flight:` / `--park:` / `--coast:` / `--city:` 等

```css
:root {
  --flight: #C15B34;  ← 改这里
  /* ... */
}
```

### 改地图日期信息（车程 / 地雷 / 住宿）

**文件**：`map/index.html`  
**位置**：页尾 `<script>` 块中的 `const DAYS = [...]`  
**搜索**：`date: "8/13"` 开始的对象

```javascript
const DAYS = [
  {
    date: "8/13",
    route: "...",
    segs: [{from: "...", to: "...", time: "..."}],  ← 车程分段
    mine: "...",  ← 地雷提示
    stay: "...",  ← 住宿信息
    food: {...}
  },
  // ...
];
```

### 改餐厅数据

**文件**：`scripts/extract_food.py`（如需改提取逻辑）  
**或**：`food/data/food-data.json`（直接改 JSON）  
**或**：重跑 `python extract_food.py` 后在 `food/index.html` 中注入

### 改全局字体栈

**文件**：`map/assets/fonts/fonts.css` 或 `<style>` 块  
**搜索**：`:root` 中的 `--serif:` 和 `--sans:`

```css
:root {
  --serif: "Fraunces", "Noto Serif SC", serif;  ← 改这里
  --sans: "Noto Sans SC", "Hiragino Sans GB", sans-serif;  ← 或改这里
}
```

### 改排版大小（标题、正文、间距）

**文件**：`map/index.html` 或 `food/index.html` 的 `<style>` 块  
**搜索**：具体类名（如 `h1`、`.intro`、`.panel`）

```css
h1 { font-size: 88px; }  ← 改这里
.intro { font-size: 15.5px; }  ← 或改这里
```

---

## 数据结构快速参考

### map/index.html 中的 DAYS 数组

```javascript
{
  date: "8/13",              // 日期（MMDD 格式）
  weekday: "Thu",            // 英文星期（3 字）
  route: "SFO → Hyatt...",   // 行程摘要
  segs: [                    // 车程分段
    {
      from: "SFO",
      to: "Hyatt",
      time: "22–28m"
    }
  ],
  mine: "周四晚返还费用...",   // 地雷提示（当日必读）
  stay: "Hyatt Place...",    // 住宿（今晚住哪儿）
  food: {                    // 餐饮锚点（餐厅推荐）
    a: "Sun Moon Studio",    // 餐厅名
    p: "West Oakland",       // 位置
    n: "Michelin 二星 · ..."  // 描述
  }
}
```

### food/data/food-data.json 顶层结构

```json
{
  "preamble": ["11 天、506 家..."],
  "booking_tiers": [{"tier": "A 优先锁定", "list": "..."}],
  "days": [
    {
      "date": "8/13",
      "weekday": "Thu",
      "route": "拜达渔港",
      "pool": [
        {
          "tier": "A",
          "name": "Chez Panisse",
          "loc": "North Berkeley",
          "kind": "Michelin Selected / 加州厨房",
          "meal": "早午餐 / 正餐",
          "price": "￥320–220",
          "book": "必须预订",
          "tip": "每日菜单...",
          "star": "Selected",
          "cat": "fine",
          "bk": "must"
        }
        // ... 30+ more
      ]
    }
    // ... 10 more days
  ],
  "anchors": [...],
  "checklist_done": [...],
  "checklist_todo": [...]
}
```

---

## 依赖与工具链

| 工具 | 用途 | 是否必需 |
|------|------|---------|
| Python 3 | 运行 `extract_food.py` | 有（更新数据时） |
| python-docx | 解析 .docx 文件 | 有（更新数据时） |
| HTTP 服务器 | 本地测试 | 有（开发时） |
| scp / ssh | 部署到服务器 | 有（线上部署时） |
| nginx | 服务器（已配置） | 有（生产环境） |

**安装依赖**：
```bash
pip install python-docx  # 一次性，用于数据提取
```

---

## 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| map 页面大小 | 108 KB | HTML + CSS + JS + SVG（不含字体） |
| food 页面大小 | 196 KB | HTML + CSS + JS + JSON（不含字体） |
| 字体总大小 | ~4.8 MB | 3 个可变字体 |
| 首屏加载 | ~1 s | 含字体加载（LTE 网络模拟） |
| DOM 节点数 | <500 | 两页都保持精简 |
| 交互延迟 | <50 ms | Vanilla JS，无框架开销 |

**优化已应用**：
- ✅ 字体 gzip 压缩
- ✅ `immutable` 缓存头（字体 31536000s）
- ✅ SVG 内联（无额外请求）
- ✅ CSS 内联（无额外请求）
- ✅ JS 内联（无额外请求）
- ✅ JSON 内联（无额外请求）

---

## 已知限制与未来计划

### 现有限制

- ❌ 不支持离线（依赖浏览器加载字体）
- ❌ 无搜索引擎优化（私密旅程规划）
- ❌ 无移动端专项优化（但响应式设计兼容）
- ❌ 数据更新需要手工重建 HTML（无 CMS）

### 未来可选优化

- 🔄 **自动更新流程**：webpack 或 esbuild 自动注入 JSON
- 🔍 **全文搜索**：Lunr.js 或 Algolia
- 📱 **PWA 支持**：离线工作 + 字体缓存
- 🔐 **访问控制**：HTTP 基础认证
- 📊 **统计追踪**：Plausible 或 Fathom（隐私优先）
- 🌐 **多语言**：英文翻译版本

---

**最后更新**：2026-07-11
