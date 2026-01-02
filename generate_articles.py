#!/usr/bin/env python3
"""
优质文章篇内容生成脚本
将 /Users/barca/HFT/open_source/Ref 中的 markdown 文件转换为 VitePress 文章页面
"""

import re
import os
from pathlib import Path
from typing import List, Dict

# 文章数据结构
class Article:
    def __init__(self, date: str, title: str, link: str, source: str, summary: str, chinese_title: str = ""):
        self.date = date
        self.title = title
        self.link = link
        self.source = source
        self.summary = summary
        self.chinese_title = chinese_title

    def get_sort_key(self):
        """获取排序用的key值"""
        # 处理特殊日期格式，放到最前面（因为年份不确定，但应该是近期文章）
        if self.date == "2025 年":
            return "2025-99-99"  # 放到最前面作为近期文章
        # 标准日期格式 YYYY-MM-DD
        return self.date

    def to_slug(self) -> str:
        """将标题转换为文件名安全的 slug"""
        # 移除特殊字符，只保留字母、数字、连字符
        slug = re.sub(r'[^\w\s-]', '', self.title.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        return slug[:100]  # 限制长度

def get_chinese_title(title: str) -> str:
    """根据英文标题生成中文翻译"""
    translations = {
        # 知名公司技术博客
        "Vibe Coding With Anthropic Claude: A New Era Of AI Assisted Software Development": "Vibe Coding 与 Anthropic Claude：AI 辅助软件开发的新时代",
        "Vibe Coding Is The Future（YouTube 版）": "Vibe Coding 即将来临（YouTube 版）",
        "What Is Vibe Coding?": "什么是 Vibe Coding？",
        "Not all AI-assisted programming is vibe coding": "并非所有 AI 辅助编程都是 Vibe Coding",
        "VIBE Coding with Amazon Q CLI": "使用 Amazon Q CLI 进行 Vibe Coding",
        "Vibe Coding Explained: Tools and Guides": "Vibe Coding 详解：工具与指南",
        "Claude Code: Best practices for agentic coding": "Claude Code：代理式编码的最佳实践",
        "Vibe coding the migration of this blog from Express to Next.js": "使用 Vibe Coding 将博客从 Express 迁移到 Next.js",
        "Vibe Coding with GitHub Copilot": "使用 GitHub Copilot 进行 Vibe Coding",
        "Vibe coding is metaprogramming": "Vibe Coding 即元编程",
        "Vibe Coding Explained with v0 by Vercel": "使用 Vercel v0 详解 Vibe Coding",
        "Vibe coding case study: ScubaDuck": "Vibe Coding 案例研究：ScubaDuck",
        "Vibe Coding": "Vibe Coding：从意图到代码",
        "GitHub Copilot Vibe Coding Workshop": "GitHub Copilot Vibe Coding 工作坊",
        '"Vibe Coding" Is the Future, and It\'s Terrifying.': '"Vibe Coding" 是未来，但也令人恐惧',
        "Vibe Coding Is The Future（YouTube 版）": "Vibe Coding 即将来临（YouTube 版）",

        # 优质播客
        "Vibe Coding Is The Future": "Vibe Coding 即将来临",
        "Vibe Coding": "Vibe Coding 专题讨论",
        "#117 Vibe Coding: When AI Turns Your Ideas into Code": "第117期 Vibe Coding：当 AI 将你的想法转化为代码",
        "How to Become a Vibe Coder": "如何成为一名 Vibe Coder",
        "RIP Vibe Coding. Feb 2025-Oct 2025.": "RIP Vibe Coding：2025年2月-10月的兴衰",
        "We still need to talk about vibe coding: Reflections on 2025's word of the year": "我们仍需讨论 Vibe Coding：对2025年度词汇的反思",

        # 研究报告
        "Vibe Coding: A Mixed-Methods Case Study on Conversational AI Software Development": "Vibe Coding：对话式 AI 软件开发的混合方法案例研究",
        "Not all AI-assisted programming is vibe coding (but vibe coding rocks)": "并非所有 AI 辅助编程都是 Vibe Coding（但 Vibe Coding 很棒）",
        "Complete Guide to Vibe Coding: May 2025": "Vibe Coding 完全指南：2025年5月版",
        "Vibe Coding vs. Agentic Coding": "Vibe Coding 与 Agentic Coding 对比",
        "Securing AI-Generated Code and Vibe Coding IDEs": "保护 AI 生成代码与 Vibe Coding IDE 的安全",
        "AI | 2025 Stack Overflow Developer Survey 中的 Vibe Coding 段落": "AI | 2025 Stack Overflow 开发者调查中的 Vibe Coding 章节",
        "Vibe coding: programming through conversation with artificial intelligence": "Vibe Coding：通过与人造智能对话进行编程",
        "Vibe Coding Whitepaper": "Vibe Coding 白皮书",
        "Vibe Coding: Toward an AI‑Native Paradigm for Semantic and Intent‑Level Software Development": "Vibe Coding：迈向语义与意图级软件开发的 AI 原生范式",
        "What you need to know about vibe coding（基于 Vercel State of Vibe Coding 报告）": "关于 Vibe Coding 你需要知道的一切（基于 Vercel State of Vibe Coding 报告）",
        "A Survey of Vibe Coding with Large Language Models": "大语言模型 Vibe Coding 综述",
        "From vibe coding to context engineering: 2025 in software development": "从 Vibe Coding 到 Context Engineering：2025年软件开发回顾",
        "The 2025 State of Visual Development and Vibe Coding": "2025年可视化开发与 Vibe Coding 现状",
        "Vibe Coding a Research Probe for Exploring AI/Voice Based Code ...": "Vibe Coding：探索基于 AI/语音编码的研究探针",

        # 优质 Newsletter
        'The Reality of "Vibe Coding"': '"Vibe Coding" 的真相',
        "Vibe coding, some thoughts and predictions": "Vibe Coding：思考与预测",
        "Vibe Coding // BRXND Dispatch vol. 76": "Vibe Coding // BRXND Dispatch 第76期",
        "What is Vibe Coding?": "什么是 Vibe Coding？",
        "Vibe Coding Newsletter | Weekly Insights on AI-Powered ...": "Vibe Coding 通讯 | AI 驱动开发的每周见解",
        "I Vibe Coded an AI System to Write Substacks about AI": "我用 Vibe Coding 构建了一个自动撰写 AI 主题 Substack 的系统",
        "A New Era of Vibe Coders Has Arrived": "Vibe Coder 新时代已经到来",
        "The Past and Future of Vibe Coding": "Vibe Coding 的过去与未来",
        "Vibe engineering": "Vibe Engineering（氛围工程学）",

        # 开发者社区
        "Vibe Coding Manual": "Vibe Coding 手册",
        "cpjet64/vibecoding: A living repository for vibe coders": "vibecoding：面向 Vibe Coder 的活文档库",
        "r/vibecoding：专门讨论 Vibe Coding 的 Subreddit": "r/vibecoding：Vibe Coding 专属讨论区",
        "Vibe coding - 2025 methodoly of the year": "Vibe Coding - 2025年度方法论",
        "Interview with Vibe Coder 2025 [Vibe Coding meaning full reliance on AI]": "2025年 Vibe Coder 访谈[Vibe Coding 意味着完全依赖 AI]",
        "What's the current best and simplest vibe coding stack? What tools do you need?": "目前最佳且最简单的 Vibe Coding 技术栈是什么？你需要哪些工具？",
        "Vibe Coding Fundamentals In 33 minutes": "33分钟掌握 Vibe Coding 基础",
        "Cursor Vibe Coding Tutorial - For COMPLETE Beginners (No Experience Needed)": "Cursor Vibe Coding 教程 - 完全新手版（无需经验）",
        "What Are the Best Vibe Coding Apps in 2025? Share Your Favorites!": "2025年最好的 Vibe Coding 应用是什么？分享你的最爱！",
        "Andrej Karpathy: Software Is Changing (Again)": "Andrej Karpathy：软件正在再次变革",
        "The Ultimate Guide to Vibe Coding in 2025 (Advanced Workflow Edition)": "2025年 Vibe Coding 终极指南（高级工作流版）",
        "Vibe Coding is a trap you are setting up for yourself.": "Vibe Coding 是你为自己设下的陷阱",
        "Reddit Vibe Coding: How the Community Shares Tips, Tricks and Hilarious Coding Moments": "Reddit 上的 Vibe Coding：社区如何分享技巧、妙招和有趣的编程时刻",
        "Google's vibe coding platform deletes entire drive": "Google 的 Vibe Coding 平台删除了整个硬盘",
        "Vibe Coding: The Truth About AI-Generated Code": "Vibe Coding：AI 生成代码的真相",
        "The brutal truth about vibe coding and why you should care": "关于 Vibe Coding 的残酷真相及你为什么应该关心",

        # ========== 新增 55 篇文章翻译 ==========

        # 知名公司技术博客（新增 12 篇）
        "OpenAI for Developers in 2025": "OpenAI 2025 开发者战略",
        "Google Gemini 2.0: AI for the agentic era": "Google Gemini 2.0：代理时代的 AI",
        "Supercharging AI Coding Assistants with Massive Context": "超大上下文窗口：AI 编码助手的性能倍增器",
        "Microsoft Build 2025: The Age of AI Agents and Building the Open Agentic Web": "Microsoft Build 2025：AI 代理时代与开放代理网络",
        "Meet GitLab Duo Workflow: The Future of AI-Driven Development": "GitLab Duo Workflow：AI 驱动开发的未来",
        "GitLab Duo Agent Platform": "GitLab Duo Agent Platform：AI 代理平台",
        "Introducing Replit Agent": "Replit Agent：AI 结对编程员",
        "Leverage AI Coding Assistants to Develop Quantum Applications at Scale with NVIDIA CUDA-Q": "利用 AI 编码助手大规模开发量子应用：NVIDIA CUDA-Q 实践",
        "Benchmarking LLMs on AI-Generated CUDA Code with ComputeEval": "使用 ComputeEval 评估 LLM 生成的 CUDA 代码",
        "IBM watsonx Code Assistant: Agentic AI Capabilities for Mainframe Modernization": "IBM watsonx Code Assistant：主机现代化的代理式 AI 能力",
        "AI-Assisted Publishing and AI-Enabled Deploy Assist": "AI 辅助发布与 AI 部署助手",
        "How can we help everyone become a 10x engineer?": "如何帮助每个人成为 10 倍工程师？",

        # 优质播客（新增 9 个）
        "Vibe Coding Is a Problem - Syntax #887": "Vibe Coding 是个问题 - Syntax #887",
        "Vibe Coding and the Rise of AI Agents": "Vibe Coding 与 AI 代理的崛起",
        "Claude Code: Anthropic's Agent in Your Terminal": "Claude Code：Anthropic 的终端 AI 代理",
        "How to Use Claude Code Like the People Who Built It": "像 Claude Code 构建者一样使用它",
        "How developers (really) used AI coding tools in 2024": "2024 年开发者如何使用 AI 编码工具",
        "The Impact of Generative AI on Software Development": "生成式 AI 对软件开发的影响",
        "AI vs software devs - Practical AI #262": "AI 与软件开发者 - Practical AI #262",
        "More AI and Layoffs - Frontend Happy Hour #191": "AI 与裁员潮 - Frontend Happy Hour #191",
        "AI-assisted software development in 2025 (Inside DORA Report)": "2025 年 AI 辅助软件开发（DORA 报告深度解读）",

        # 研究报告（新增 12 份）
        "Examining the Use and Impact of an AI Code Assistant": "AI 代码助手的使用与影响研究",
        "How much does AI impact development speed?": "AI 对开发速度的影响有多大？",
        "Microsoft New Future of Work Report 2024": "微软 2024 年工作未来报告",
        "Rise of Agentic AI": "代理式 AI 的崛起",
        "The Trillion Dollar AI Software Development Stack": "万亿美元的 AI 软件开发栈",
        "AI 50: AI Agents Move Beyond Chat": "AI 50：AI 代理超越聊天",
        "Are You Generating Value from AI? The Widening Gap": "你从 AI 中获得价值了吗？差距在扩大",
        "An Empirical Study on LLM-Driven Secure Code Generation": "LLM 驱动安全代码生成的实证研究",
        "From Developer Pairs to AI Copilots: A Comparative Study": "从结对编程到 AI 副驾驶：对比研究",
        "Agentic AI Security: Threats, Defenses, Evaluation, and Future Directions": "代理式 AI 安全：威胁、防御、评估与未来方向",
        "State of Developer Ecosystem 2025": "2025 年开发者生态系统现状",
        "Technical Debt in AI-Enabled Systems": "AI 系统中的技术债务",

        # 优质 Newsletter（新增 10 个）
        "Learnings from Two Years of Using AI Tools for Software Engineering": "两年使用 AI 工具进行软件工程的经验总结",
        "Top AI Agentic Workflow Patterns": "顶级 AI 代理工作流模式",
        "TLDR AI Newsletter (December 2025 Edition)": "TLDR AI 通讯（2025年12月版）",
        "AI Agents Weekly - Software Development Edition": "AI 代理周刊：软件开发版",
        "How to Effectively Use Generative AI for Software Engineering Tasks": "如何有效使用生成式 AI 完成软件工程任务",
        "Almost Timely News: How I Code with AI": "Almost Timely News：我如何使用 AI 编程",
        "AI Dev Essentials Newsletter": "AI 开发必备通讯",
        "The State of AI Engineering (2025) - From Coding Agents to Containerized Fleets": "2025 年 AI 工程现状：从编码代理到容器化集群",
        "Claude Code: Best Practices for Agentic Coding": "Claude Code：代理式编码最佳实践",
        "Spec-driven development with AI: Get started with a new open-source toolkit": "规范驱动的 AI 开发：开源工具包入门",

        # 开发者社区（新增 12 个）
        "Vibe Coding vs. Agentic Coding: 2025 Beginner's Guide to AI-Driven Development": "Vibe Coding vs Agentic Coding：2025 年 AI 驱动开发新手指南",
        "AI Vibe Coding Tutorial + Workflow (Cursor, Best Practices)": "AI Vibe Coding 教程 + 工作流（Cursor 最佳实践）",
        "From Vibe Coding to CLI Agents: My Ultimate 2025 Developer's Guide": "从 Vibe Coding 到 CLI 代理：我的 2025 终极开发者指南",
        "How to Start Vibecoding as a Complete Beginner - Emergent": "完全新手如何开始 Vibe Coding - Emergent",
        "Essential Best Practices (💯 Must-Do) on AI Coding Platforms": "AI 编码平台的必备最佳实践",
        "Windsurf Tutorial for Beginners (AI Code Editor)": "Windsurf 初学者教程（AI 代码编辑器）",
        "Windsurf – The Best Agentic AI Code Editor (2025)": "Windsurf：2025 年最佳代理式 AI 代码编辑器",
        "The beginner's guide to coding with Cursor | Lee Robinson": "Cursor 编码初学者指南 | Lee Robinson",
        "AI Coding Best Practices in 2025": "2025 年 AI 编码最佳实践",
        "Getting Started | Zed Code Editor Documentation & Agentic Editing": "Zed 代码编辑器入门：代理式编辑",
        "Build a LOCAL AI Coding Assistant: Qwen3 + Ollama + Continue.dev Guide": "构建本地 AI 编码助手：Qwen3 + Ollama + Continue.dev 指南",
        "What is Aider AI and How to use Aider: A Beginners Guide": "Aider AI 是什么及如何使用：初学者指南",
    }

    # 特殊处理：标题中包含引号的情况
    if "Vibe Coding" in title and "Is the Future, and It's Terrifying" in title:
        return '"Vibe Coding" 是未来，但也令人恐惧'

    return translations.get(title, "")

def parse_supplement_file(file_path: Path) -> List[Article]:
    """解析补充文件中的文章列表"""
    articles = []
    content = file_path.read_text(encoding='utf-8')

    # 分割成独立的文章块
    title_pattern = r'-?\s*## .+?\|\s*题目【(.+?)】'
    matches = list(re.finditer(title_pattern, content))

    for i, match in enumerate(matches):
        title = match.group(1).strip() if match.lastindex >= 1 else ""

        # 找到当前文章块的开始位置
        start_pos = match.start()

        # 找到下一个文章块的位置，或者文件末尾
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        # 提取当前文章块的完整内容
        block = content[start_pos:end_pos]

        # 提取日期
        date_match = re.search(r'##\s*(.+?)\s*\|', block)
        date = date_match.group(1).strip() if date_match else ''

        # 提取链接
        link_match = re.search(r'链接：(.+?)(?:\n|$)', block)
        link = link_match.group(1).strip() if link_match else ''

        # 提取来源
        source_match = re.search(r'来源平台：(.+?)(?:\n|$)', block)
        source = source_match.group(1).strip() if source_match else ''

        # 提取摘要（从"摘要："到块结束）
        summary_match = re.search(r'摘要：\s*\n\s*(.+)', block, re.DOTALL)
        summary = ''
        if summary_match:
            summary = re.sub(r'\s+', ' ', summary_match.group(1).strip())

        if title and link:
            chinese_title = get_chinese_title(title)
            articles.append(Article(date, title, link, source, summary, chinese_title))

    return articles

def parse_articles_file(file_path: Path) -> List[Article]:
    """解析单个 markdown 文件，提取文章列表"""
    articles = []
    content = file_path.read_text(encoding='utf-8')

    # 分割成独立的文章块
    # 先找到所有题目位置
    title_pattern = r'-?\s*## .+?\|\s*题目【(.+?)】'
    matches = list(re.finditer(title_pattern, content))

    for i, match in enumerate(matches):
        title = match.group(1).strip()

        # 找到当前文章块的开始位置
        start_pos = match.start()

        # 找到下一个文章块的位置，或者文件末尾
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(content)

        # 提取当前文章块的完整内容
        block = content[start_pos:end_pos]

        # 提取日期
        date_match = re.search(r'##\s*(.+?)\s*\|', block)
        date = date_match.group(1).strip() if date_match else ''

        # 提取链接
        link_match = re.search(r'链接：(.+?)(?:\n|$)', block)
        link = link_match.group(1).strip() if link_match else ''

        # 提取来源
        source_match = re.search(r'来源平台：(.+?)(?:\n|$)', block)
        source = source_match.group(1).strip() if source_match else ''

        # 提取摘要（从"摘要："到块结束）
        summary_match = re.search(r'摘要：\s*\n\s*(.+)', block, re.DOTALL)
        summary = ''
        if summary_match:
            summary = re.sub(r'\s+', ' ', summary_match.group(1).strip())

        if title and link:
            chinese_title = get_chinese_title(title)
            articles.append(Article(date, title, link, source, summary, chinese_title))

    return articles

def generate_article_detail(article: Article, category: str, index: int) -> str:
    """生成文章详情页面的 markdown 内容"""
    # 清理摘要中的引号和特殊字符
    safe_summary = article.summary.replace('"', '\\"').replace('\n', ' ')
    safe_title = article.title.replace('"', '\\"')

    # 侧边栏标题：优先使用中文翻译，如果没有则使用英文
    sidebar_title = article.chinese_title if article.chinese_title else safe_title
    safe_sidebar_title = sidebar_title.replace('"', '\\"')

    # 如果有中文翻译，显示在标题下方
    chinese_subtitle = ""
    if article.chinese_title:
        chinese_subtitle = f'\n\n<div style="font-size: 16px; color: var(--vp-c-text-2); font-weight: 400; margin-top: 8px; margin-bottom: 24px;">{article.chinese_title}</div>'

    return f"""---
title: "{safe_sidebar_title}"
---

# {safe_title}{chinese_subtitle}

<div class="article-meta" style="margin-bottom: 24px;">
  <span class="article-date">{article.date}</span>
  <span style="margin: 0 12px; color: var(--vp-c-text-2);">•</span>
  <span style="color: var(--vp-c-text-2);">{article.source}</span>
</div>

## 摘要

{article.summary}

## 原文链接

[{article.title}]({article.link})

---

**返回：** [优质文章篇](/Articles/) > [{category}](./)
"""

def generate_category_index(category_name: str, articles: List[Article]) -> str:
    """生成分类首页的 markdown 内容，包含卡片布局"""
    # 文章列表 HTML
    articles_html = ""
    for article in articles:
        slug = article.to_slug()

        # 如果有中文翻译，在卡片中显示
        title_html = f"""<div class="article-title">{article.title}</div>"""
        if article.chinese_title:
            title_html = f"""<div class="article-title">{article.title}</div>
  <div class="article-title-cn">{article.chinese_title}</div>"""

        articles_html += f"""<a href="./{slug}/" class="article-card">
  <span class="article-date">{article.date}</span>
  {title_html}
  <div class="article-source">{article.source}</div>
  <div class="article-summary">{article.summary}</div>
  <span class="article-link">阅读更多</span>
</a>"""

    return f"""---
title: "{category_name}"
---

# {category_name}

精选优质学习资源，帮助你保持对行业前沿的关注。

<div class="article-grid">
{articles_html}
</div>

---

**返回：** [优质文章篇](/Articles/)
"""

def process_category(category_info: Dict[str, str], base_dir: Path):
    """处理单个分类"""
    category_name = category_info['name']
    source_file = category_info['source']
    target_dir = category_info['target']

    print(f"处理分类: {category_name}")

    # 解析文章
    articles = parse_articles_file(source_file)
    # 按日期倒序排列（最新的在前面）
    articles.sort(key=lambda x: x.get_sort_key(), reverse=True)
    print(f"  找到 {len(articles)} 篇文章")

    # 创建目标目录
    target_dir.mkdir(parents=True, exist_ok=True)

    # 生成文章详情页
    for i, article in enumerate(articles, 1):
        slug = article.to_slug()
        detail_content = generate_article_detail(article, category_name, i)
        detail_file = target_dir / f"{slug}.md"
        detail_file.write_text(detail_content, encoding='utf-8')
        print(f"    生成: {slug}.md")

    # 生成分类首页
    index_content = generate_category_index(category_name, articles)
    index_file = target_dir / "index.md"
    index_file.write_text(index_content, encoding='utf-8')
    print(f"  更新: index.md")

def main():
    """主函数"""
    base_dir = Path("/Users/barca/HFT/open_source/vibevibe/vibevibe/docs/Articles")
    ref_dir = Path("/Users/barca/HFT/open_source/Ref")
    supplement_file = Path("/Users/barca/HFT/open_source/vibevibe/vibevibe/articles_supplement.md")

    # 定义分类信息（补充文件）
    supplement_categories = [
        {
            'name': '知名公司博客',
            'section_start': '## 知名公司技术博客方向（12篇）',
            'section_end': '## 优质播客方向（9个）',
            'target': base_dir / '01-company-blogs'
        },
        {
            'name': '优质播客',
            'section_start': '## 优质播客方向（9个）',
            'section_end': '## 研究报告方向（12份）',
            'target': base_dir / '02-podcasts'
        },
        {
            'name': '研究报告',
            'section_start': '## 研究报告方向（12份）',
            'section_end': '## 优质Newsletter方向（10个）',
            'target': base_dir / '03-research-reports'
        },
        {
            'name': '优质 Newsletter',
            'section_start': '## 优质Newsletter方向（10个）',
            'section_end': '## 开发者社区方向（12个）',
            'target': base_dir / '04-newsletters'
        },
        {
            'name': '开发者社区',
            'section_start': '## 开发者社区方向（12个）',
            'section_end': None,
            'target': base_dir / '05-communities'
        },
    ]

    # 处理补充文件
    print("处理补充文章...")
    content = supplement_file.read_text(encoding='utf-8')

    for cat_info in supplement_categories:
        # 提取对应的section内容
        start_idx = content.find(cat_info['section_start'])
        end_idx = content.find(cat_info['section_end']) if cat_info['section_end'] else len(content)

        if start_idx == -1:
            continue

        section_content = content[start_idx:end_idx]

        # 创建临时文件
        temp_file = supplement_file.parent / f"temp_{cat_info['name']}.md"
        temp_file.write_text(section_content, encoding='utf-8')

        # 解析文章
        articles = parse_supplement_file(temp_file)
        # 按日期倒序排列（最新的在前面）
        articles.sort(key=lambda x: x.get_sort_key(), reverse=True)

        print(f"处理分类: {cat_info['name']}")
        print(f"  找到 {len(articles)} 篇文章")

        # 创建目标目录
        cat_info['target'].mkdir(parents=True, exist_ok=True)

        # 生成文章详情页
        for article in articles:
            slug = article.to_slug()
            detail_content = generate_article_detail(article, cat_info['name'], 0)
            detail_file = cat_info['target'] / f"{slug}.md"
            detail_file.write_text(detail_content, encoding='utf-8')

        # 生成分类首页
        index_content = generate_category_index(cat_info['name'], articles)
        index_file = cat_info['target'] / "index.md"
        index_file.write_text(index_content, encoding='utf-8')

        # 删除临时文件
        temp_file.unlink()

        print(f"  已生成 {len(articles)} 篇文章")
        print()

    print("✅ 所有补充文章生成完成！")

if __name__ == "__main__":
    main()
