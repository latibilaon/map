# 🚀 START HERE — 项目总览

欢迎！这是 **2026 美西大环线行程规划系统**（行程地图 + 餐厅指南）的完整本地副本。

---

## 📍 你在这里

```
/Users/ponjuy/Desktop/Oracle/travel/
├── 00-START-HERE.md    ← 你正在读这个
├── README.md           ← 完整设计与技术文档
├── QUICKSTART.md       ← 快速开始指南
├── PROJECT_STRUCTURE.md ← 文件结构详解
├── map/                ← 行程地图页
├── food/               ← 餐厅指南页
└── scripts/            ← 数据工具脚本
```

---

## ⚡ 5 秒钟开始

### 1️⃣ 本地预览

```bash
cd /Users/ponjuy/Desktop/Oracle/travel/map
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000
```

### 2️⃣ 两个页面

- **🗺️ 地图** (`/map/`)：11 天行程 + 五张地理分区地图 + 日期点击查看当日车程/地雷/住宿/餐饮
- **🍽️ 餐厅** (`/food/`)：506 家餐厅 + 日期/场景/筛选器 + Michelin 星级 / 预订等级标记

### 3️⃣ 已上线

- https://novaisle.com/map/
- https://novaisle.com/food/

---

## 📚 文档导航

### 想快速上手？
👉 读 **[QUICKSTART.md](QUICKSTART.md)**
- 本地预览（5 分钟）
- 更新数据（餐厅变更）
- 部署到云端（一键发布）

### 想了解设计？
👉 读 **[README.md](README.md) 的前几节**
- 设计系统（字体、色彩、排版）
- 功能架构（map + food 两页的交互）
- 数据管线（docx → JSON → HTML）

### 想修改代码？
👉 读 **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 的「关键代码位置速查」**
- 改颜色、字体、间距 → 具体文件位置
- 改日期信息（车程/地雷/住宿） → DAYS 数组位置
- 改餐厅数据 → extract_food.py 或 JSON

### 想完整了解？
👉 读 **[README.md](README.md)**
- 完整设计系统说明
- 每个页面的功能与架构
- 维护与部署指南

---

## 🎨 设计高亮

### 字体系统（「现代奢华」风格）

| 用途 | 字体 | 特点 |
|------|------|------|
| 拉丁展示/数字 | **Fraunces** | 可变字体，光学尺寸自适应 |
| 中文大标题 | **Noto Serif SC** | 7539 字可变子集，优雅衬线 |
| 正文/UI | **Noto Sans SC** | 7525 字可变子集，清晰无衬线 |

✨ 全部都是**可变字体**（variable fonts），一个文件搞定多个权重

### 色彩系统（地理分区）

```
--flight: #C15B34  (陶土红 — 航班)
--park:   #3E7C58  (深绿 — 公园)
--coast:  #2E7C8F  (靛青 — 海岸)
--city:   #B08328  (古金 — 城市)
--high:   #7A67A8  (紫 — 山脉)
--transfer: #3E5C7E (深蓝 — 长途)
```

---

## 🛠️ 常见任务

### 「我要改餐厅信息」

```bash
# 1. 编辑源 Word 文件
~/Desktop/美国核心攻略/美西沿途餐厅筛选_V2_2026核实版_20260707.docx

# 2. 重跑提取脚本
cd /Users/ponjuy/Desktop/Oracle/travel
python scripts/extract_food.py

# 3. 刷新页面
python3 -m http.server 8000
# → http://localhost:8000/../food/

# 4. 部署
scp food/index.html tdb:/www/wwwroot/novaisle-static/food/
```

👉 详见 [QUICKSTART.md](QUICKSTART.md) 的「场景 A」

### 「我要改地图日期信息」

1. 编辑 `map/index.html` 末尾的 `DAYS` 数组（车程/地雷/住宿）
2. 本地测试：`python3 -m http.server 8000`
3. 部署：`scp map/index.html tdb:/www/wwwroot/novaisle-static/map/`

👉 详见 [QUICKSTART.md](QUICKSTART.md) 的「场景 B」

### 「我要改颜色/字体」

- 颜色：编辑 `<style>` 块中的 `:root` 变量
- 字体：改 `fonts.css` 或 `:root` 中的 `--serif` / `--sans`

👉 详见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) 的「关键代码位置速查」

---

## 📊 项目特点

| 特点 | 说明 |
|------|------|
| 📦 **自包含** | 两个页面各自独立，无框架无依赖 |
| ⚡ **轻量** | 总大小 6.3 MB（字体占 95%）；页面本身仅 108+196 KB |
| 🎨 **设计系统** | 统一字体/色彩/排版，高度可维护 |
| 📱 **响应式** | 桌面/平板/手机都能用 |
| 🔒 **私密** | 静态站，无数据库，私人旅程 |
| 🚀 **易部署** | scp 一个文件，nginx 直出，无 CI/CD |

---

## ✨ 最近更新（2026-07-11）

这一轮「高级美化」完成了用户的五项要求：

1. ✅ **字体全换**：Fraunces + 思源（从 Jost/Cormorant）
2. ✅ **版本号清零**：去掉所有 V1/V2/Vol.10 字样
3. ✅ **头部重排**：大标题 + 副题 + 数据带（精简美观）
4. ✅ **新增信息**：地图加住宿、餐厅加地雷红点、关键数据加链接
5. ✅ **深度美化**：渐变背景、投影效果、动画节奏、细节打磨

---

## ❓ 常见问题

**Q：本地打不开？**  
A：不要直接双击 HTML，要用 HTTP 服务器。见 [QUICKSTART.md](QUICKSTART.md)

**Q：数据没更新？**  
A：浏览器缓存。试试硬刷新（Cmd+Shift+R）或清缓存。

**Q：中文显示方块？**  
A：字体加载失败。检查 `fonts.css` 路径、浏览器控制台（F12）

**Q：想改某个颜色/字体？**  
A：找对文件和行号。详见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

---

## 📞 下一步

### 立即行动

```bash
# 1. 本地预览（感受一下）
cd /Users/ponjuy/Desktop/Oracle/travel/map
python3 -m http.server 8000

# 2. 尝试改一个小东西（如日期颜色）
# 编辑 map/index.html 的 :root { --flight: ... }

# 3. 部署到线上（需要服务器访问权）
./deploy.sh
```

### 深入了解

- 跳读 [README.md](README.md)（重点看「设计系统」和「数据管线」）
- 按需参考 [QUICKSTART.md](QUICKSTART.md)（常见任务）
- 查阅 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)（代码位置）

---

## 📋 文件清单

```
travel/ (6.3 MB)
├── 00-START-HERE.md          ← 你正在读
├── README.md                 ← 完整技术文档（18 KB）
├── QUICKSTART.md             ← 快速开始指南（8.7 KB）
├── PROJECT_STRUCTURE.md      ← 文件结构详解（8.1 KB）
├── map/
│   ├── index.html            ← 地图页（108 KB，自包含）
│   └── assets/fonts/
│       ├── fonts.css         ← 字体声明
│       ├── Fraunces-var.woff2        (120 KB)
│       ├── NotoSerifSC-var.woff2     (2.7 MB)
│       └── NotoSansSC-cjk.woff2      (2.0 MB)
├── food/
│   ├── index.html            ← 餐厅页（196 KB，自包含）
│   └── data/
│       └── food-data.json    ← 506 家餐厅数据（35 KB）
└── scripts/
    └── extract_food.py       ← docx → JSON 脚本
```

---

**开始探索吧！** 🎯

推荐先读 [QUICKSTART.md](QUICKSTART.md)，然后尝试本地预览。

---

**项目信息**
- 制作者：ponjuy
- 在线版：https://novaisle.com/
- 本地路径：`/Users/ponjuy/Desktop/Oracle/travel/`
- 最后更新：2026-07-11
- 许可：Private（个人使用）
