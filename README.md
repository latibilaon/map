# 2026 美西大环线 · 旅行图集

> 行程规划 + 餐厅指南的交互式双页系统  
> **在线访问**：[novaisle.com/map](https://novaisle.com/map/) | [novaisle.com/food](https://novaisle.com/food/)  
> **部署架构**：腾讯云静态站 (nginx)  
> **最后更新**：2026-07-11

---

## 📖 项目概览

这是一个针对 2026 年美西 11 天自驾旅程的**自包含双页系统**，包含：

- **[/map](#map-行程地图)**：5 张地理分区的交互式地图 + 11 天时间轴 + 底部抽屉（车程 / 地雷 / 住宿 / 餐饮锚点）
- **[/food](#food-餐厅指南)**：506 家餐厅的日期联动选择器 + 三层筛选（日期 → 场景 → 完整池）

两页通过顶部 tab 导航互连，共享统一的**设计系统**（字体、色彩、排版）。

---

## 🎨 设计系统

### 字体栈（现代奢华）

**三层字体体系**，针对不同内容角色：

| 字体 | 角色 | 参数 | 文件 |
|------|------|------|------|
| **Fraunces** | 拉丁展示 / 数字（大标题、时间戳、统计数字） | 可变 opsz + wght 100–900 | `Fraunces-var.woff2` (120 KB) |
| **Noto Serif SC** | 中文大标题（主标题、小节标题） | 可变 wght 400–900 | `NotoSerifSC-var.woff2` (2.7 MB) |
| **Noto Sans SC** | 正文 / UI（段落、导航、标签） | 可变 wght 100–900 | `NotoSansSC-cjk.woff2` (2.0 MB) |

**关键决策**：
- Fraunces 的**光学尺寸自适应**（`opsz` 轴）让大标题自动调整笔画粗细比，视觉更生动
- 思源黑体用作正文字体（非衬线），较 Jost 合成字更扎实真实
- 全部是**可变字体**（variable fonts），减少加载文件数量同时保留字重灵活性

**字重调校**：思源系列的真实字重比前代 Jost 合成粗，页面 CSS 全局下调一档（原 800→700、750→650 等）

**字符覆盖**：两个中文子集共 7500+ 字符，覆盖 GB2312 + 补充符号；四个不支持的特殊符号已替换（◈→◆、☑→★、☐→○、✕→×）

### 色彩系统

**六色分区体系**（用于地图线路与时间轴）：

```css
--flight: #C15B34  /* 陶土红 — 航班路线 */
--park:   #3E7C58  /* 深绿 — 公园园区 */
--coast:  #2E7C8F  /* 靛青 — 沿海线路 */
--city:   #B08328  /* 古金 — 城市短途 */
--high:   #7A67A8  /* 紫 — 高点/山脉 */
--transfer: #3E5C7E /* 深蓝 — 长途转场 */
```

**衬托色**：
- 背景纸质白 `#F6F1E7`（略偏黄，温暖）
- 正文墨色 `#212B36`（非纯黑，易读）
- 淡灰 `#8A8375`（标签、备注）
- 警告红 `#B23B2E`（地雷标记）

**应用原则**：
- map 页的 SVG 线路 + food 页的日期条 chip 各用对应分色
- 地雷日期 chip 加红点警示
- 选中状态用分色的渐变背景 + 投影

### 排版节奏

**尺度系统**（rem 基准 15px）：
- **特大标题**：clamp(46px, 4.8vw, 88px) —— 响应式主标题
- **大标题**：26–38px —— 副标题、分段标题
- **正文**：15–16.5px —— 段落、导航
- **小字**：11–13px —— 标签、备注、图例

**间距**（基于 8px 网格）：
- 页间距：30–40px
- 板块间距：26–30px
- 元素内间距：10–18px

**行高**：
- 大标题：1.02–1.05（紧凑）
- 正文：1.9–1.95（舒展）
- 列表项：1.35–1.4（中等）

---

## 🗺️ Map · 行程地图

### 功能

**静态内容**：
- 五张分区地图（SVG），每张展示特定地域的车程分段、地标、营地
- 图例卡说明线路颜色含义与时间胶囊格式
- 底部分区索引（5 个地区的关键信息汇总）

**交互**：
- **日期时间轴**（吸顶）：11 个日期 chip，可点击切换
- **底部抽屉**：当点击某日期时弹出抽屉，包含：
  - 📍 当日路线（Google Maps 时间复查）
  - 🚗 车程分段（起点→终点 + 时长）
  - ⚠️ 当日地雷（闭店、道路工事等必读）
  - 🏨 **今晚住宿**（酒店名 + 地点）
  - 🍽️ 今晚吃什么（餐饮锚点 + 小节选择）
  - 🔗 快速入口（跳到 /food 页当日餐厅）

**SVG 地图交互**：
- 图钉悬停显示浮层（景点名 + 备注）
- 点击图钉脉冲 key-item 卡片
- key-item 列表点击联动图钉高亮

### 架构

```
map/
├── index.html          (自包含单页)
└── assets/fonts/       (字体文件)
    ├── fonts.css       (字体声明 + 全局样式)
    ├── Fraunces-var.woff2
    ├── NotoSerifSC-var.woff2
    └── NotoSansSC-cjk.woff2
```

**页面结构**（HTML）：
```
<header class="hero">
  <!-- 标题、导语、数据带（11 天 / 2 航班 / 5 区域 / 最长驾驶段 / 506 餐厅入口） -->
</header>
<nav class="topnav">
  <!-- 品牌 + tab 导航 -->
</nav>
<div class="day-rail">
  <!-- 吸顶日期时间轴 -->
</div>
<section class="master-map">
  <!-- SVG 地图 -->
</section>
<div id="drawer">
  <!-- 底部抽屉（JS 动态渲染） -->
</div>
```

**数据**（JS）：
```javascript
const DAYS = [
  {
    date: "8/13", weekday: "Thu",
    route: "SFO → Hyatt Place Emeryville",
    segs: [{from: "SFO", to: "Hyatt", time: "22–28m"}],
    mine: "☑️ 周四晚 19:00 后返还车辆费用…",
    food: {a: "Sun Moon Studio", p: "West Oakland", n: "Michelin 二星 · 当日首选"}
    stay: "Hyatt Place Emeryville（湾区东岸）"
  },
  // ... 10 more days
]
```

**CSS 关键类**：
- `.topnav`：吸顶导航栏
- `.day-rail`：吸顶日期时间轴（`top: 76px`）
- `.day-chip`：日期卡片，有色顶边框 + hover 动效
- `.drawer`：抽屉（slide-up 动画 + cubic-bezier）
- `#map-canvas`：SVG 容器

**JS 交互**：
```javascript
// 日期 chip 点击 → 渲染抽屉
document.querySelectorAll('.day-chip').forEach(chip => {
  chip.addEventListener('click', () => renderDrawer(DAYS[index]));
});

// SVG 图钉悬停 → 显示浮层
pin.addEventListener('mouseenter', () => showTooltip(pin.dataset));
```

### 样式亮点

- **数据带**（hero-band）：统计数字与"餐厅指南"链接用 `┆` 竖线分隔，间距均匀
- **日期 chip 渐变**：选中时用分色渐变 `linear-gradient(168deg, rgba(c, 92%), rgba(c, 100%))`
- **抽屉动效**：`cubic-bezier(.22,.68,.34,1)` 更自然的滑入曲线
- **卡片投影**：`box-shadow: 0 12px 26px rgba(color, 38%)`，色彩一致

---

## 🍽️ Food · 餐厅指南

### 功能

**三层体系**：
1. **No.01 当日总推荐 Top 5** —— 5 家金章最优选（各日不同）
2. **No.02 按场景选** —— 5 张场景卡（Michelin / 本地特色 / 平价餐厅 / 平价咖啡 / Berkeley 近郊）
3. **No.03 完整候选池** —— 全日（30–50 家）的可筛选卡片网格

**筛选交互**：
- **日期选择器**（吸顶）：11 个日期 chip，标记有闭店地雷的日子（红点 ⚠️）
- **水平筛选栏**：类别 (Michelin / 本地特色 / 平价 / 早餐 / 补给) ✕ 预订等级 (必订 / 强烈 / 建议 / walk-in)
- **搜索框**：店名 / 位置 / 菜系实时查找

**展示**：
- **星级徽章**：三星 / 二星 / 一星 / Bib Gourmand / Selected / JBF 等 Michelin 认证
- **力度指数**：A 级（优先锁定）/ B 级（好用备选）/ C 级（保底补给）
- **预订等级**：必须提前预订（红）/ 强烈建议（橙）/ 建议预留位置（黄）/ walk-in 可行（绿）
- **价格与评分**：人均（未税）+ Google/Michelin 评分
- **位置 / 餐次**：精确地点 + 早餐/午餐/晚餐适配

### 架构

```
food/
├── index.html          (注入 JSON 数据的自包含单页)
└── data/
    ├── food-data.json  (506 家餐厅的结构化数据)
    └── (food-index-template.html 模板已内联)
```

**数据源与处理管线**：

1. **源数据**：`~/Desktop/美国核心攻略/美西沿途餐厅筛选_V2_2026核实版_20260707.docx`
   - 11 张日期表，每张包含「总推荐」「场景推荐」「完整候选」三类
   - 506 家餐厅，手工核实与评级

2. **提取脚本**（`scripts/extract_food.py`）：
   ```bash
   python extract_food.py
   # → food-data.json (506 条记录 + 元数据)
   ```
   - 按日期分割表格
   - 识别 top5（排序表）、场景卡（类型表）、完整池（候选表）
   - 修复 docx 表格的行错位（6 处）
   - 分类：星级（`star`）、餐厅类型（`cat`）、预订等级（`bk`）

3. **数据结构**（JSON）：
   ```json
   {
     "preamble": ["11 天、506 家候选…"],
     "booking_tiers": [
       {"tier": "A 优先锁定", "list": "餐厅名 1, 餐厅名 2…"},
       // ...
     ],
     "days": [
       {
         "date": "8/13",
         "weekday": "Thu",
         "route": "拜达渔港",
         "notes": ["【联网核实与校订】必读…"],
         "top5": ["Chez Panisse", "Great China", "Ippuku", "Vik's Chaat", "Sun Moon Studio"],
         "types": [
           {"type": "Michelin/高端", "pick": "Sun Moon Studio / Commis", "tip": "顶级品尝菜…"},
           // ... 4 more
         ],
         "pool": [
           {
             "tier": "A",
             "name": "Chez Panisse",
             "loc": "North Berkeley",
             "kind": "Michelin Selected / 加州厨房核心",
             "meal": "早午餐 / 正餐",
             "price": "￥320–220 / ¥450–4",
             "book": "必须预订；正餐位置紧张",
             "tip": "正式菜单每日一新；让 maitre d' 引导…",
             "star": "Selected",
             "cat": "fine",
             "bk": "must"
           },
           // ... 30–50 more
         ],
         "pool_count": 37
       },
       // ... 10 more days
     ],
     "anchors": [
       {"date": "8/13", "anchor": "Chez Panisse", "platform": "预订官网", "window": "2–4 周前", "note": "加州菜之源…"},
       // ...
     ],
     "checklist_done": ["Yellowstone 2026 订阅版 RSS…"],
     "checklist_todo": ["临行 1 周逐店电话确认…"]
   }
   ```

4. **页面生成**：
   - 模板 HTML（`food-index-template.html`）中的占位符 `/*__DATA__*/null`
   - 脚本注入：`tpl.replace('/*__DATA__*/null', JSON.stringify(data))`
   - 输出 `index.html`（自包含，无外部 JSON 请求）

### 样式亮点

- **日期 chip 地雷警示**：有闭店的日子在 chip 上加小红点 `<u class="minedot">`
- **分层卡片**：
  - **Top5 卡**：金色序号章 + 高亮背景
  - **场景卡**：6 色对应（Michelin / 本地 / 平价 / 早餐 / 补给）
  - **完整池卡**：收敛风格，重点突出【星级】【等级】【价格】三要素
- **地雷标记**（V2 alert）：红色边框框 + 闭店警示内容
- **筛选器**：6 个 toggle + 搜索框，选中的 tag 加色 + 点击高亮
- **响应式**：卡片网格 3 列（桌面）→ 2 列（平板）→ 1 列（手机）

### 交互逻辑（JavaScript）

```javascript
// 日期 chip 点击
day_chip.onclick = () => {
  filterPoolByDay(chip.dataset.day);
  showAlert(data.days[i].notes);
};

// 筛选器点击
filter_tag.onclick = () => {
  updatePoolDisplay(
    filterBy.category,
    filterBy.booking_level,
    search_text
  );
};

// 搜索实时更新
search_input.oninput = () => {
  updatePoolDisplay(...);
};
```

---

## 📦 部署架构

### 本地开发

```bash
# 预览（Python 简易 HTTP 服务器）
cd /Users/ponjuy/Desktop/Oracle/travel/map
python3 -m http.server 8000

# 访问 http://localhost:8000
```

### 云服务器（腾讯云）

**目录结构**：
```
/www/wwwroot/novaisle-static/
├── map/
│   ├── index.html
│   └── assets/fonts/
│       ├── fonts.css
│       ├── Fraunces-var.woff2
│       ├── NotoSerifSC-var.woff2
│       └── NotoSansSC-cjk.woff2
└── food/
    ├── index.html
    └── data/  (仅本地工作目录；云端不需要单独文件)
```

**nginx 配置**（HTTPS + gzip）：
```nginx
server {
    listen 443 ssl http2;
    server_name novaisle.com;
    ssl_certificate /path/to/cert;
    ssl_certificate_key /path/to/key;
    
    root /www/wwwroot/novaisle-static;
    gzip on;
    gzip_types text/html text/css application/json font/woff2;
    gzip_min_length 1000;
    
    location / {
        try_files $uri $uri/ =404;
        add_header Cache-Control "public, max-age=3600";
    }
    location ~ \.(woff2|woff)$ {
        add_header Cache-Control "public, max-age=31536000, immutable";
    }
}
```

**部署脚本**（一键更新）：
```bash
#!/bin/bash
LOCAL="/Users/ponjuy/Desktop/Oracle/travel"
REMOTE="tdb:/www/wwwroot/novaisle-static"

# 备份
ssh tdb "cp -r $REMOTE/map/index.html $REMOTE/map/index.html.bak-$(date +%Y%m%d)"
ssh tdb "cp -r $REMOTE/food/index.html $REMOTE/food/index.html.bak-$(date +%Y%m%d)"

# 上传
scp $LOCAL/map/index.html $REMOTE/map/
scp $LOCAL/food/index.html $REMOTE/food/
scp $LOCAL/map/assets/fonts/* $REMOTE/map/assets/fonts/

# 权限
ssh tdb "chown -R www:www $REMOTE"

# 验证
curl -so /dev/null -w "%{http_code}\n" https://novaisle.com/map/
curl -so /dev/null -w "%{http_code}\n" https://novaisle.com/food/
```

---

## 🔧 维护指南

### 更新数据（餐厅信息）

当 docx 源文件更新（新餐厅、闭店、地址变更）：

1. **编辑 docx**：`~/Desktop/美国核心攻略/美西沿途餐厅筛选_V2_2026核实版_20260707.docx`
   - 按日期维护表格结构（不改表头、不改表格顺序）
   - 修复发现的错位行

2. **重新提取**：
   ```bash
   cd /Users/ponjuy/Desktop/Oracle/travel
   python scripts/extract_food.py
   # → food/data/food-data.json (更新)
   ```

3. **重建页面**：
   ```bash
   python build.py  # 伪代码；实际用模板注入脚本
   # → food/index.html (刷新 JSON 数据)
   ```

4. **部署**：
   ```bash
   scp food/index.html tdb:/www/wwwroot/novaisle-static/food/
   ```

### 更新地图信息

map 页的 DAYS 数组手写在页尾 script，更新步骤：

1. **编辑 `map/index.html`** 的 DAYS 数组：
   - 修改车程时间（Google Maps 重新复查）
   - 修改地雷提示、住宿、餐饮锚点

2. **部署**：
   ```bash
   scp map/index.html tdb:/www/wwwroot/novaisle-static/map/
   ```

### 更新字体

若想更换字体（如升级可变字体版本）：

1. **替换文件** `map/assets/fonts/*.woff2`
2. **更新 `fonts.css`** 的 `@font-face` 声明
3. **部署**：
   ```bash
   scp map/assets/fonts/* tdb:/www/wwwroot/novaisle-static/map/assets/fonts/
   ```

### 调整设计

**色彩系统**：编辑 HTML 的 `:root` CSS 变量
```css
:root {
  --flight: #C15B34;  /* 改这里 */
  --park: #3E7C58;
  /* ... */
}
```

**排版参数**：编辑 HTML 内 `<style>` 块中的类定义（`h1 { font-size: ... }`）

**间距**：统一使用 8px 网格倍数，改 padding/margin 类定义即可

---

## 📋 技术栈速览

| 层面 | 技术 | 备注 |
|------|------|------|
| **页面** | 原生 HTML5 + CSS3 + Vanilla JS | 无框架，完全自包含 |
| **字体** | 可变字体 (woff2) | Fraunces + 思源黑体 / 思源宋体 |
| **地图** | SVG (inline) | 手绘路线、点位、分区 |
| **数据** | JSON (inline) | 506 条餐厅 + 11 天时间轴 |
| **构建** | Python (docx → JSON 提取) | 手工 JSON 注入 |
| **部署** | 腾讯云 (nginx) | 静态站，无数据库 |
| **性能** | gzip + 缓存头 | 字体文件 immutable 缓存 31536000s |

---

## ✨ 设计决策记录

### 为什么用可变字体？

- **单一文件** vs 多重坯体：Fraunces-var 120 KB = 原来 4 个单重文件的 1/3
- **光学尺寸自适应**：同一个「8/13」数字在大标题用 opsz=72、在正文用 opsz=15，系统自动调笔画粗细比
- **灵活性**：CSS 中 `font-weight: 560` 这样的细微权重控制，单重字体做不到

### 为什么不用框架？

- **项目规模**：两个独立单页，无复杂状态管理
- **性能**：Vanilla JS 无额外加载；整个 food 页只有 196 KB（含 JSON 数据）
- **可维护性**：5 年后想改个颜色，不必担心框架版本已死；HTML/CSS/JS 永恒稳定
- **用户体验**：首屏加载 ~1s（包括字体加载）

### 为什么数据 inline？

- **减少请求**：一个 HTTP 请求 = 一整个页面
- **可靠性**：无网络延迟或 JSON 加载失败的风险
- **简化部署**：scp 一个 HTML 文件，完全搞定

### 为什么分别部署 map 和 food？

- **独立更新**：餐厅信息变更不影响地图；反之亦然
- **加载优化**：用户进 map 不加载 506 家餐厅数据
- **URL 清晰**：`novaisle.com/map` vs `/food` 语义明确

---

## 🎯 使用指南

### 作为用户

1. **进 `/map`** 看行程概览 + 五张地图
2. **点选某天** 看当日车程、地雷、住宿、餐厅锚点
3. **点「沿途餐厅指南」** 跳到 `/food`
4. **在 /food 选日期** → 按场景或完整池筛选餐厅
5. **查 Michelin 星级 + 预订等级** 决策是否早订

### 作为维护者

1. **餐厅有新信息**？编辑 docx → 重跑 `extract_food.py` → scp `index.html`
2. **地图车程有变**？编辑 `map/index.html` 的 DAYS 数组 → scp
3. **想改颜色**？编辑 `:root` CSS 变量 → scp
4. **字体升级**？替换 `.woff2` 文件 + 更新 `fonts.css` → scp

---

## 📞 问题排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 中文显示方块 | 字体文件未加载 | 检查 `fonts.css` 路径、浏览器缓存（Cmd+Shift+R） |
| 日期 chip 不响应 | JS 错误 | 打开控制台看报错；检查 DAYS 数组格式 |
| 抽屉不滑出 | CSS `display: none` 或动画未触发 | 检查 `.drawer.active` 类是否加上 |
| 餐厅数据未更新 | JSON inline 过期 | 清浏览器缓存；硬刷新（Cmd+Shift+R） |
| 线上字体显示模糊 | gzip 导致变量字体损坏 | 检查 nginx `gzip_types` 是否包含 `font/woff2`；改用 `deflate` |

---

## 📚 相关资源

- **Fraunces 字体**：https://github.com/undercasetype/Fraunces（开源，Google Fonts）
- **Noto Sans/Serif SC**：https://github.com/noto-project（开源，中文覆盖完整）
- **可变字体指南**：https://variablefonts.io/
- **SVG 地图手绘工具**：Adobe Illustrator / Figma
- **Nginx 配置参考**：https://nginx.org/en/docs/

---

## 📝 更新日志

**2026-07-11**
- ✨ 字体栈升级：Fraunces + 思源（可变字体）+ 字重全局调校
- 🗺️ map 页新增底部抽屉：车程分段、当日地雷、住宿信息
- 🍽️ food 页加地雷红点标记 + 日期 chip 优化
- 🎯 全站去除版本号（V1/V2/Vol.10 清零）
- 🚀 部署腾讯云：https://novaisle.com/map + /food

---

**制作者**：ponjuy  
**许可**：Private（个人旅程规划，非商业）  
**最后修改**：2026-07-11  
