import { mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import matter from 'gray-matter';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkStringify from 'remark-stringify';
import { visit } from 'unist-util-visit';

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const repositoryRoot = path.resolve(siteRoot, '..');
const generatedRoot = path.join(siteRoot, 'src/content/docs');
const generatedDataRoot = path.join(siteRoot, 'src/data');
const manifest = JSON.parse(
  await readFile(path.join(siteRoot, 'content-manifest.json'), 'utf8'),
);
const sourceRef =
  process.env.SOURCE_REF ??
  process.env.VERCEL_GIT_COMMIT_SHA ??
  process.env.GITHUB_SHA ??
  manifest.repository.ref;
const editRef = process.env.SOURCE_EDIT_REF ?? manifest.repository.ref;

const sourceRoutes = new Map(
  manifest.pages
    .filter((page) => page.kind === 'source' && page.route)
    .map((page) => [page.source, page.route]),
);

function githubUrl(sourcePath) {
  return `${manifest.repository.url}/blob/${sourceRef}/${sourcePath}`;
}

function githubEditUrl(sourcePath) {
  return `${manifest.repository.url}/edit/${editRef}/${sourcePath}`;
}

function rewriteRelativeUrl(url, sourcePath) {
  if (
    !url ||
    url.startsWith('#') ||
    url.startsWith('/') ||
    /^[a-z][a-z\d+.-]*:/i.test(url)
  ) {
    return url;
  }

  const match = url.match(/^([^?#]*)([?#].*)?$/);
  const target = match?.[1] ?? url;
  const suffix = match?.[2] ?? '';
  const resolved = path.posix.normalize(
    path.posix.join(path.posix.dirname(sourcePath), target),
  );
  const projectedRoute = sourceRoutes.get(resolved);

  return projectedRoute ? `${projectedRoute}${suffix}` : `${githubUrl(resolved)}${suffix}`;
}

async function projectMarkdown(content, sourcePath) {
  const tree = unified().use(remarkParse).parse(content);
  visit(tree, ['link', 'image'], (node) => {
    node.url = rewriteRelativeUrl(node.url, sourcePath);
  });
  return unified()
    .use(remarkStringify, {
      bullet: '-',
      fences: true,
      listItemIndent: 'one',
    })
    .stringify(tree);
}

function removeLeadingTitle(content) {
  return content.replace(/^#\s+[^\n]+\n+/, '');
}

async function writeGenerated(relativePath, content) {
  const destination = path.join(generatedRoot, relativePath);
  await mkdir(path.dirname(destination), { recursive: true });
  await writeFile(destination, content, 'utf8');
}

async function renderPage(page) {
  const absoluteSource = path.join(repositoryRoot, page.source);
  const raw = await readFile(absoluteSource, 'utf8');

  if (page.kind === 'local') {
    const localPage = matter(raw);
    if (localPage.data.editUrl !== false) {
      localPage.data.editUrl = githubEditUrl(page.source);
    }
    await writeGenerated(
      page.output,
      matter.stringify(localPage.content, localPage.data),
    );
    return;
  }

  const parsed = matter(raw);
  const title = page.title ?? parsed.data.title ?? parsed.data.name;
  if (!title) {
    throw new Error(`Projected page has no title: ${page.source}`);
  }

  const projectedBody = await projectMarkdown(
    removeLeadingTitle(parsed.content),
    page.source,
  );
  const sourceNote = `> 这是 [\`${page.source}\`](${githubUrl(page.source)}) 的只读构建投影；源文件仍拥有事实与修改权。`;
  const output = matter.stringify(`${sourceNote}\n\n${projectedBody}`, {
    title,
    description: page.description ?? parsed.data.description,
    editUrl: githubEditUrl(page.source),
    source: githubUrl(page.source),
  });

  await writeGenerated(page.output, output);
}

async function readSkill(sourcePath) {
  const raw = await readFile(path.join(repositoryRoot, sourcePath), 'utf8');
  const parsed = matter(raw);
  if (typeof parsed.data.name !== 'string' || typeof parsed.data.description !== 'string') {
    throw new Error(`Skill frontmatter is incomplete: ${sourcePath}`);
  }

  return {
    name: parsed.data.name,
    description: parsed.data.description.trim().replace(/\s+/g, ' '),
    sourcePath,
    sourceUrl: githubUrl(sourcePath),
    publicPath: sourceRoutes.get(sourcePath) ?? null,
  };
}

function renderCatalog(skills) {
  const entries = skills
    .map((skill, index) => {
      const destination = skill.publicPath ?? skill.sourceUrl;
      const label = skill.publicPath ? '阅读投影' : '查看源文件';
      return `## ${String(index + 1).padStart(2, '0')} · ${skill.name}\n\n${skill.description}\n\n[${label}](${destination}) · [GitHub 源文件](${skill.sourceUrl})`;
    })
    .join('\n\n---\n\n');

  return `---
title: 技能目录
description: 当前可安装的方法，以及每种方法负责的判断。
editUrl: ${githubEditUrl('site/content-manifest.json')}
sidebar:
  order: 2
---

这里列出的技能来自检查入库的活动清单，并在构建时读取各自的结构化 frontmatter。目录帮助选择方法，不改变技能本身。

${entries}
`;
}

await rm(generatedRoot, { recursive: true, force: true });
await mkdir(generatedRoot, { recursive: true });

for (const page of manifest.pages) {
  await renderPage(page);
}

const skills = await Promise.all(manifest.catalog.skills.map(readSkill));
await writeGenerated(manifest.catalog.output, renderCatalog(skills));
await mkdir(generatedDataRoot, { recursive: true });
await writeFile(
  path.join(generatedDataRoot, 'skills.json'),
  `${JSON.stringify(skills, null, 2)}\n`,
  'utf8',
);

console.log(`Projected ${manifest.pages.length + 1} pages and ${skills.length} skills.`);
