# 部署 / Deployment

`npm run build` 生成纯静态站点 `dist/`，可以放到任何静态托管（Nginx、Cloudflare Pages、Vercel、GitHub Pages）。

## 子路径

```bash
ATLAS_BASE=/words/ npm run build
```

## Nginx 示例

```nginx
location ^~ /words/ {
    alias /var/www/word-atlas/;
    try_files $uri $uri/ /words/index.html;
    expires 7d;
}
```

## GitHub Pages

本站地址：<https://kai987.github.io/IELTS-word-atlas/>。

`.github/workflows/pages.yml` 在推送到 `main` 时自动发布，也可以手动运行
“Deploy to GitHub Pages”。仓库 Settings → Pages 的发布来源需设为
“GitHub Actions”。流程安装锁定依赖，运行应用测试、日文复审工具测试及中日词库检查，
然后按 Pages 返回的子路径执行 Vite 构建，只发布 `dist/`。

请勿用默认的 Jekyll 流程直接发布源码：浏览器不能运行 `src/main.tsx`，
源码中的 `%BASE_URL%` 也需要由 Vite 转换。插画、英文音频与日文分块会随构建一并发布。

线上 `revision.txt` 记录实际构建的 Git 提交 SHA。发布完成后，核对该文件、
部署任务与日文词库内容，并在真实线上地址测试语言切换和词条加载。

## 体积

插画与音频合计约数百 MB。建议在 CDN 后部署，或按需只发布 `thumb/` 和部分音频。
