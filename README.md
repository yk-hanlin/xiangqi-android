# 中国象棋 · 安卓版（云构建 APK）

用 Capacitor 把单文件象棋游戏封装成原生安卓应用，APK 由 GitHub Actions 在云端编译，**本机无需安装 JDK / Android SDK**。

## 目录结构

```
xiangqi-android/
├─ www/                     ← 网页资源（唯一需要改的地方）
│  ├─ index.html            游戏本体（已做平板适配 + PWA）
│  ├─ manifest.webmanifest  PWA 清单
│  ├─ sw.js                 离线缓存
│  └─ icons/                应用图标（脚本生成）
├─ tools/make_icons.py      图标生成脚本（Pillow）
├─ capacitor.config.json    App ID / 名称 / 资源配置
├─ package.json
└─ .github/workflows/build-apk.yml   云端构建流程
```

`android/` 目录不进仓库，由 CI 用 `npx cap add android` 现场生成。

## 一、上传到 GitHub

```bash
cd xiangqi-android
git init
git add .
git commit -m "中国象棋安卓版"
git branch -M main
git remote add origin https://github.com/<你的账号>/xiangqi-android.git
git push -u origin main
```

> 若 `android/`、`node_modules/` 被误加，`.gitignore` 已排除。

## 二、触发云端构建

两种方式，任选：

1. **手动触发**：GitHub 仓库 → `Actions` → 左侧「构建安卓 APK」→ `Run workflow`。
2. **打 tag 自动构建并发布**：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
   构建完成后 APK 会直接挂到 Release 页面。

构建约 3～6 分钟。产物下载位置：

- Actions 页面 → 该次运行 → `Artifacts` → `xiangqi-debug-apk`
- 或 Release 页面（打 tag 时）

## 三、安装到平板

1. 把 `app-debug.apk` 传到平板（微信/QQ 传文件、数据线、网盘均可）。
2. 平板打开「设置 → 安全 → 允许安装未知来源应用」，给文件管理器或浏览器授权。
3. 点击 APK 安装，桌面出现「中国象棋」图标。

> 这是 **debug 签名**的 APK，可正常安装使用；只有上架应用商店才需要正式签名证书（可在 workflow 里接入 secrets 扩展）。

## 四、改代码后重新出包

改 `www/` 里的文件 → commit → push → 再跑一次 workflow 即可（或推新 tag）。

## 五、只想在平板上用，不想装 APK？

直接用浏览器也行，访问网页后点 Chrome 菜单「安装应用 / 添加到主屏幕」：

- 全屏运行、桌面有图标、断网也能玩（`sw.js` 已缓存全部资源）。

## 六、本地直接预览（可选）

```bash
cd xiangqi-android/www
python -m http.server 8080
# 浏览器打开 http://localhost:8080
```

> 离线缓存（Service Worker）只在 `http://localhost` 或 https 下生效，直接双击 index.html（file://）不会注册。

## 七、配置速查

| 项 | 值 |
|---|---|
| App ID | `com.yunke.xiangqi` |
| 应用名 | 中国象棋 |
| webDir | `www` |
| Capacitor | 7.6.9 |
| AGP / compileSdk / minSdk | 8.7.2 / 35 / 23 |
| CI 环境 | Node 20 + JDK 17 + Android SDK 35 |

改应用名/包名：编辑 `capacitor.config.json` 的 `appName` / `appId`（改 `appId` 后需删除仓库里的 `android/` 重新生成）。
