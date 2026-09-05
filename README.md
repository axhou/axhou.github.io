# Alan Hou 的个人主页

网站：<https://axhou.github.io/>

网站使用普通 HTML，无需安装主题、Ruby、Jekyll 或前端依赖。直接在 GitHub 编辑对应文件，提交到 `main` 后会自动检查站内链接并发布。

## 去哪里修改

| 内容 | 文件或文件夹 | 网页地址 |
| --- | --- | --- |
| 主页、个人简介、论文与导航 | `index.html` | `/` |
| Everytopic Seminar | `everytopic.html`、`everytopic.png` | `/everytopic.html` |
| 教学经历、评价与指导经历 | `teaching/index.html` | `/teaching/` |
| 2024 年线性代数课程 | `teaching/la2024/` | `/teaching/la2024/` |
| 2026 年线性代数课程 | `teaching/la2026/` | `/teaching/la2026/` |
| 2026 年 Guided Reading Program | `teaching/grp2026.html` | `/teaching/grp2026.html` |
| 早期助教经历 | `teaching/ta.html` | `/teaching/ta.html` |
| 教学评价截图 | `teaching/reviews/` | — |
| Bernstein–Zelevinsky 读书班 | `seminars/bz.html` | `/seminars/bz.html` |
| Gelbart 读书班 | `seminars/gelbart.html` | `/seminars/gelbart.html` |
| Casselman 读书班 | `seminars/casselman.html` | `/seminars/casselman.html` |
| 数学笔记 | `notes/` | `/notes/algebra2.html`、`/notes/bump.html` |
| Career Panel 海报 | `events/career.pdf` | `/events/career.pdf` |
| 做饭照片与页面 | `cooking/index.html`、`cooking/images/` | `/cooking/` |
| 主页照片 | `photos/alan.jpg` | — |

每门课程的页面和资料放在一起，例如：

```text
teaching/
  index.html
  la2024/
    index.html
    syllabus.pdf
    midterm.pdf
    final.pdf
  la2026/
    index.html
    syllabus.pdf
  grp2026.html
  ta.html
  reviews/
    fall2024.png
```

`notes/archive/` 保留以前上传、目前没有在网页中链接的笔记；`photos/old/` 保留旧照片。它们不是模板文件，不会因未使用而被自动删除，也没有重新加入主页导航。

## 命名和链接

- 用简短、小写的英文名称；需要分词时使用短横线，不使用下划线或空格。
- 同一课程跨年份时用 `la2024`、`la2026` 这样的名称。
- 文件夹内的主页面统一叫 `index.html`，链接可写为 `/teaching/la2026/`。
- 课程附件统一叫 `syllabus.pdf`、`midterm.pdf`、`final.pdf`，年份由课程文件夹区分。
- 站内链接从根目录开始，例如 `href="/teaching/"`、`src="/photos/alan.jpg"`。Everytopic 现有文件、内容和路径保留原样。

新增课程时，新建 `teaching/la2027/` 之类的文件夹，放入页面和资料，再更新主页及教学页的链接即可。

## 旧地址和自动发布

旧网页、PDF 和图片地址记录在 [`.github/links.json`](.github/links.json)。网页的旧地址自动跳转；PDF 和图片在发布成品中自动生成旧地址副本。因此，别人以前收藏的链接仍可使用，仓库中只需维护新目录下的一份资料。

以后再次改名，在该文件中添加 `"旧路径": "新路径"`；如果已有映射指向被改名的文件，也把它直接更新到最新地址，避免多次跳转。不要在根目录手工添加重复文件。

发布配置集中在 `.github/`，平时更新网页内容无需修改：

- `pages.py`：整理发布成品、生成旧地址兼容文件、检查站内链接。
- `links.json`：旧地址到新地址的对应表。
- `workflows/pages.yml`：提交后自动检查和发布。Pull request 只检查，合并到 `main` 才发布。

这使用 [GitHub Pages 的静态发布流程](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。`.nojekyll` 表示无需 Jekyll 处理。旧 Dinky 主题、主题许可证与示例说明、Sass、Ruby 配置及主题开发脚本已移除；本次整理不新增个人内容的授权声明。

如需本地预览，在仓库目录运行：

```sh
python3 .github/pages.py
python3 -m http.server 8000 --directory dist
```

然后打开 <http://localhost:8000/>。`dist/` 是自动生成的发布成品，已排除在 Git 之外，请修改上表中的源文件。
