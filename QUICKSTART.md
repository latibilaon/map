# 快速开始 · Quick Start

## ⚡ 本地预览（5 分钟）

### 1. 启动本地服务器

```bash
cd /Users/ponjuy/Desktop/Oracle/travel/map
python3 -m http.server 8000
```

或用 Node.js：
```bash
npx http-server . -p 8000
```

### 2. 打开浏览器

- 地图：http://localhost:8000
- 餐厅：http://localhost:8000/../food/

或者直接用 Finder 打开 `map/index.html` / `food/index.html`（只读模式，无交互限制）

---

## 📊 数据更新流程

### 场景 A：餐厅信息变化

**步骤**：

1. **编辑源文件**
   ```
   ~/Desktop/美国核心攻略/美西沿途餐厅筛选_V2_2026核实版_20260707.docx
   ```
   - 添加新餐厅、删除闭店店铺、修改地址或评级

2. **运行提取脚本**
   ```bash
   cd /Users/ponjuy/Desktop/Oracle/travel
   python scripts/extract_food.py
   # 输出：food/data/food-data.json
   ```

3. **手工注入数据**（临时方案）
   ```bash
   # 编辑 food/index.html，找到 window.foodData = {...}
   # 替换为新的 JSON（从 food-data.json 复制粘贴）
   ```
   
   或运行自动化脚本：
   ```bash
   cat > build_food.py << 'EOF'
   import json
   data = json.load(open('food/data/food-data.json'))
   html = open('food/index-template.html').read()
   html = html.replace('/*__DATA__*/null', 'window.foodData=' + json.dumps(data, ensure_ascii=False))
   open('food/index.html', 'w').write(html)
   print("✓ food/index.html 已更新")
   EOF
   python build_food.py
   ```

4. **本地测试**
   ```bash
   python3 -m http.server 8000  # 在 map/ 目录
   # 打开 http://localhost:8000/../food/
   ```

5. **上线部署**
   ```bash
   scp /Users/ponjuy/Desktop/Oracle/travel/food/index.html tdb:/www/wwwroot/novaisle-static/food/
   ssh tdb "chown www:www /www/wwwroot/novaisle-static/food/index.html"
   ```

### 场景 B：地图信息变化（车程、地雷、住宿）

**步骤**：

1. **编辑 `map/index.html`** 末尾的 JavaScript：
   ```html
   <script>
   const DAYS = [
     {
       date: "8/13",
       route: "SFO → Emeryville",
       segs: [{from: "SFO", to: "Hyatt", time: "22-28m"}],  // ← 改这里
       mine: "周四返还费用...",  // ← 改这里
       stay: "Hyatt Place...",  // ← 改这里
       food: {a: "Sun Moon Studio", p: "West Oakland", n: "Michelin 二星"}
     },
     // ... 10 more days
   ];
   </script>
   ```

2. **本地测试**
   ```bash
   python3 -m http.server 8000
   # 打开 http://localhost:8000
   # 点击日期，验证抽屉信息是否更新
   ```

3. **上线部署**
   ```bash
   scp /Users/ponjuy/Desktop/Oracle/travel/map/index.html tdb:/www/wwwroot/novaisle-static/map/
   ssh tdb "chown www:www /www/wwwroot/novaisle-static/map/index.html"
   ```

### 场景 C：设计调整（颜色、字体、间距）

**颜色**：

```html
<!-- 在 <style> 块里改 :root 变量 -->
<style>
:root {
  --flight: #C15B34;  /* 航班红 → 改成 #FF6B6B 等 */
  --park: #3E7C58;
  --coast: #2E7C8F;
  --city: #B08328;
  --high: #7A67A8;
  --transfer: #3E5C7E;
}
</style>
```

**字体**：

```css
/* 在 map/assets/fonts/fonts.css 改 @font-face 或字体栈 */
:root {
  --serif: "Fraunces", "Noto Serif SC", serif;   /* 改左边字体名 */
  --sans: "Noto Sans SC", "Hiragino Sans GB", sans-serif;
}
```

**间距/排版**：

```css
/* 改类定义 */
h1 { font-size: 88px; }  /* → 改成 72px 等 */
.hero-band { margin-top: 34px; }  /* → 改成 20px 等 */
```

---

## 🚀 部署到云端

### 前置条件

- SSH 连接腾讯云服务器（已设 `tdb` 别名）
- 服务器路径：`/www/wwwroot/novaisle-static/`
- Nginx 已配置 gzip + cache-control

### 一键部署脚本

保存为 `deploy.sh`：

```bash
#!/bin/bash
set -e  # 失败则中止

LOCAL="/Users/ponjuy/Desktop/Oracle/travel"
REMOTE="tdb:/www/wwwroot/novaisle-static"

echo "📦 备份远程文件..."
ssh tdb "cp $REMOTE/map/index.html $REMOTE/map/index.html.bak-$(date +%Y%m%d-%H%M%S)"
ssh tdb "cp $REMOTE/food/index.html $REMOTE/food/index.html.bak-$(date +%Y%m%d-%H%M%S)"

echo "📤 上传文件..."
scp $LOCAL/map/index.html $REMOTE/map/
scp $LOCAL/food/index.html $REMOTE/food/
scp $LOCAL/map/assets/fonts/* $REMOTE/map/assets/fonts/

echo "🔐 设置权限..."
ssh tdb "chown -R www:www $REMOTE"

echo "✅ 验证部署..."
MAP_CODE=$(curl -so /dev/null -w "%{http_code}" https://novaisle.com/map/)
FOOD_CODE=$(curl -so /dev/null -w "%{http_code}" https://novaisle.com/food/)

if [ "$MAP_CODE" = "200" ] && [ "$FOOD_CODE" = "200" ]; then
  echo "✨ 部署成功！"
  echo "🗺️  https://novaisle.com/map/"
  echo "🍽️  https://novaisle.com/food/"
else
  echo "❌ 部署失败（map=$MAP_CODE, food=$FOOD_CODE）"
  echo "尝试回滚..."
  ssh tdb "cp $REMOTE/map/index.html.bak-* $REMOTE/map/index.html"
  ssh tdb "cp $REMOTE/food/index.html.bak-* $REMOTE/food/index.html"
  exit 1
fi
```

**使用**：

```bash
chmod +x deploy.sh
./deploy.sh
```

### 手工部署（以防万一）

```bash
# 1. 备份
ssh tdb 'cp /www/wwwroot/novaisle-static/map/index.html \
         /www/wwwroot/novaisle-static/map/index.html.bak'

# 2. 上传 map
scp /Users/ponjuy/Desktop/Oracle/travel/map/index.html \
    tdb:/www/wwwroot/novaisle-static/map/

# 3. 上传 food
scp /Users/ponjuy/Desktop/Oracle/travel/food/index.html \
    tdb:/www/wwwroot/novaisle-static/food/

# 4. 上传字体
scp /Users/ponjuy/Desktop/Oracle/travel/map/assets/fonts/* \
    tdb:/www/wwwroot/novaisle-static/map/assets/fonts/

# 5. 权限
ssh tdb 'chown -R www:www /www/wwwroot/novaisle-static'

# 6. 验证
curl -I https://novaisle.com/map/
curl -I https://novaisle.com/food/
```

---

## 🐛 问题排查

### Q：本地打开 food/index.html 后筛选不工作

**A**：浏览器同源策略限制。改用 HTTP 服务器启动：
```bash
cd /Users/ponjuy/Desktop/Oracle/travel
python3 -m http.server 8000
```
然后访问 `http://localhost:8000/map/index.html` 或 `http://localhost:8000/food/index.html`

### Q：餐厅数据没更新

**A**：可能是缓存。试试：
1. 浏览器硬刷新：`Cmd+Shift+R`（Mac）或 `Ctrl+Shift+R`（Windows/Linux）
2. 清空浏览器缓存（Settings → Privacy → Clear browsing data）
3. 或在 DevTools 里禁用缓存（F12 → Settings → Network → "Disable cache"）

### Q：地图抽屉点击后不出现

**A**：
1. 打开 DevTools（F12），看控制台是否有 JS 错误
2. 检查 DAYS 数组格式是否正确（特别是引号、逗号）
3. 检查 HTML 中是否有 `id="drawer"` 的 div

### Q：字体显示成方块（中文 / 特殊字符）

**A**：
1. 检查 `fonts.css` 是否正确加载（DevTools → Network → 搜索 fonts.css）
2. 检查 `.woff2` 文件大小（应该 2–3 MB）
3. 如果在服务器上，检查 nginx gzip 配置是否包含 `font/woff2`（某些旧版本会压坏可变字体）

### Q：线上 map 或 food 显示 404

**A**：
```bash
# 检查文件是否存在
ssh tdb 'ls -la /www/wwwroot/novaisle-static/map/index.html'
ssh tdb 'ls -la /www/wwwroot/novaisle-static/food/index.html'

# 检查权限
ssh tdb 'stat /www/wwwroot/novaisle-static/map/index.html'
# 应该显示 644 权限，www 用户可读

# 检查 nginx 日志
ssh tdb 'tail -50 /var/log/nginx/error.log'
```

---

## 📋 检查清单

部署前：
- [ ] `map/index.html` 本地已测试（所有日期可点击）
- [ ] `food/index.html` 本地已测试（筛选器工作）
- [ ] 字体文件都在 `map/assets/fonts/`
- [ ] 无浏览器控制台错误
- [ ] 数据（DAYS 数组、JSON）已最新

部署后：
- [ ] `curl -I https://novaisle.com/map/` 返回 200
- [ ] `curl -I https://novaisle.com/food/` 返回 200
- [ ] 打开两个页面，验证日期/筛选可交互
- [ ] 检查 DevTools 无 404 或 CORS 错误
- [ ] 用不同设备（手机/平板）测试响应式

---

## 💡 小贴士

1. **定期备份**
   ```bash
   # 每次部署前自动备份
   tar -czf backup-$(date +%Y%m%d).tar.gz /Users/ponjuy/Desktop/Oracle/travel/
   ```

2. **版本控制**（可选）
   ```bash
   cd /Users/ponjuy/Desktop/Oracle/travel
   git init
   git add .
   git commit -m "initial: map + food pages with Fraunces + Noto fonts"
   ```

3. **监控线上页面**
   ```bash
   # 设置 cron 每小时检查一次
   0 * * * * curl -f https://novaisle.com/map/ || mail -s "Map page down!" user@example.com
   ```

4. **性能优化**
   - 图片压缩（SVG 已内联，无额外请求）
   - gzip 启用（nginx 配置已含）
   - 字体缓存（`.woff2` 设置 immutable 缓存 1 年）
   - 减少 DOM 节点（两页都 < 500 nodes）

---

## 📞 支持

遇到问题？按以下顺序排查：

1. **本地测试** → 问题在代码，改本地文件
2. **部署测试** → 问题在服务器配置，检查 nginx
3. **数据问题** → 更新 JSON 或 DAYS 数组
4. **浏览器缓存** → 硬刷新 + 清缓存

---

**最后更新**：2026-07-11  
**维护者**：ponjuy
