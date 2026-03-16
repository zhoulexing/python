// Markdown实时渲染器JavaScript逻辑

class MarkdownRenderer {
    constructor() {
        this.initElements();
        this.initMarked();
        this.initEventListeners();
        this.loadInitialContent();
        this.updateStats();
        
        // 功能状态
        this.syncScrollEnabled = true;
        this.isFullscreenEditor = false;
        this.isFullscreenPreview = false;
        
        // 防抖渲染
        this.renderTimeout = null;
    }
    
    initElements() {
        this.editor = document.getElementById('editor');
        this.preview = document.getElementById('preview');
        this.wordCount = document.getElementById('word-count');
        this.lineCount = document.getElementById('line-count');
        this.toggleSyncBtn = document.getElementById('toggle-sync');
        this.fullscreenEditorBtn = document.getElementById('fullscreen-editor');
        this.fullscreenPreviewBtn = document.getElementById('fullscreen-preview');
        this.exportHtmlBtn = document.getElementById('export-html');
        this.clearEditorBtn = document.getElementById('clear-editor');
        this.loadExampleBtn = document.getElementById('load-example');
        this.copyRichTextBtn = document.getElementById('copy-rich-text');
        this.copyXiaohongshuBtn = document.getElementById('copy-xiaohongshu');
        this.copyHtmlBtn = document.getElementById('copy-html');
        this.printPreviewBtn = document.getElementById('print-preview');
        this.app = document.querySelector('.app');
    }
    
    initMarked() {
        // 自定义renderer，只渲染明确的markdown链接语法
        const renderer = new marked.Renderer();
        
        // 重写link方法，保持markdown链接语法的正常渲染
        renderer.link = function(href, title, text) {
            return `<a href="${href}"${title ? ` title="${title}"` : ''}>${text}</a>`;
        };
        
        // 重写text方法，不自动转换URL为链接
        renderer.text = function(text) {
            return text;
        };
        
        // 配置marked.js
        marked.setOptions({
            renderer: renderer,
            highlight: function(code, lang) {
                if (lang && hljs.getLanguage(lang)) {
                    try {
                        return hljs.highlight(code, { language: lang }).value;
                    } catch (err) {}
                }
                return hljs.highlightAuto(code).value;
            },
            breaks: true,
            gfm: false, // 禁用GitHub风格自动链接
            tables: true,
            sanitize: false
        });
    }
    
    initEventListeners() {
        // 编辑器输入事件
        this.editor.addEventListener('input', () => {
            this.debouncedRender();
            this.updateStats();
        });
        
        // 编辑器滚动事件
        this.editor.addEventListener('scroll', () => {
            if (this.syncScrollEnabled) {
                this.syncScroll('editor');
            }
        });
        
        // 预览滚动事件
        this.preview.addEventListener('scroll', () => {
            if (this.syncScrollEnabled) {
                this.syncScroll('preview');
            }
        });
        
        // 工具栏按钮事件
        this.toggleSyncBtn.addEventListener('click', () => this.toggleSyncScroll());
        this.fullscreenEditorBtn.addEventListener('click', () => this.toggleFullscreenEditor());
        this.fullscreenPreviewBtn.addEventListener('click', () => this.toggleFullscreenPreview());
        this.exportHtmlBtn.addEventListener('click', () => this.exportHtml());
        this.clearEditorBtn.addEventListener('click', () => this.clearEditor());
        this.loadExampleBtn.addEventListener('click', () => this.loadExample());
        this.copyRichTextBtn.addEventListener('click', () => this.copyRichText());
        this.copyXiaohongshuBtn.addEventListener('click', () => this.copyXiaohongshu());
        this.copyHtmlBtn.addEventListener('click', () => this.copyHtml());
        this.printPreviewBtn.addEventListener('click', () => this.printPreview());
        
        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveToLocalStorage();
                        this.showMessage('内容已保存到本地存储', 'success');
                        break;
                    case 'e':
                        e.preventDefault();
                        this.toggleFullscreenEditor();
                        break;
                    case 'p':
                        e.preventDefault();
                        this.toggleFullscreenPreview();
                        break;
                }
            }
        });
        
        // 窗口大小变化事件
        window.addEventListener('resize', () => {
            this.syncScroll();
        });
    }
    
    loadInitialContent() {
        // 从本地存储加载内容
        const savedContent = localStorage.getItem('markdown-content');
        if (savedContent) {
            this.editor.value = savedContent;
            this.renderMarkdown();
        } else {
            // 使用默认示例内容
            this.renderMarkdown();
        }
    }
    
    debouncedRender() {
        clearTimeout(this.renderTimeout);
        this.renderTimeout = setTimeout(() => {
            this.renderMarkdown();
            this.saveToLocalStorage();
        }, 300);
    }
    
    renderMarkdown() {
        try {
            const markdownText = this.editor.value;
            const htmlContent = marked.parse(markdownText);
            this.preview.innerHTML = htmlContent;
            
            // 重新应用代码高亮
            this.preview.querySelectorAll('pre code').forEach((block) => {
                hljs.highlightElement(block);
            });
            
            // 添加markdown-body类名
            this.preview.className = 'markdown-body';
            
        } catch (error) {
            console.error('Markdown渲染错误:', error);
            this.preview.innerHTML = `<div class="error-message">渲染错误: ${error.message}</div>`;
        }
    }
    
    updateStats() {
        const text = this.editor.value;
        const charCount = text.length;
        const lineCount = text.split('\n').length;
        
        this.wordCount.textContent = `字符数: ${charCount}`;
        this.lineCount.textContent = `行数: ${lineCount}`;
    }
    
    syncScroll(source = 'editor') {
        if (!this.syncScrollEnabled) return;
        
        if (source === 'editor') {
            const editorScrollRatio = this.editor.scrollTop / (this.editor.scrollHeight - this.editor.clientHeight);
            const previewScrollTop = editorScrollRatio * (this.preview.scrollHeight - this.preview.clientHeight);
            this.preview.scrollTop = previewScrollTop;
        } else {
            const previewScrollRatio = this.preview.scrollTop / (this.preview.scrollHeight - this.preview.clientHeight);
            const editorScrollTop = previewScrollRatio * (this.editor.scrollHeight - this.editor.clientHeight);
            this.editor.scrollTop = editorScrollTop;
        }
    }
    
    toggleSyncScroll() {
        this.syncScrollEnabled = !this.syncScrollEnabled;
        if (this.syncScrollEnabled) {
            this.toggleSyncBtn.classList.add('sync-active');
            this.toggleSyncBtn.textContent = '同步滚动 ✓';
        } else {
            this.toggleSyncBtn.classList.remove('sync-active');
            this.toggleSyncBtn.textContent = '同步滚动';
        }
    }
    
    toggleFullscreenEditor() {
        this.isFullscreenEditor = !this.isFullscreenEditor;
        if (this.isFullscreenEditor) {
            this.app.classList.add('fullscreen-editor');
            this.app.classList.remove('fullscreen-preview');
            this.fullscreenEditorBtn.textContent = '退出全屏';
            this.isFullscreenPreview = false;
            this.fullscreenPreviewBtn.textContent = '全屏预览';
        } else {
            this.app.classList.remove('fullscreen-editor');
            this.fullscreenEditorBtn.textContent = '全屏编辑';
        }
        this.editor.focus();
    }
    
    toggleFullscreenPreview() {
        this.isFullscreenPreview = !this.isFullscreenPreview;
        if (this.isFullscreenPreview) {
            this.app.classList.add('fullscreen-preview');
            this.app.classList.remove('fullscreen-editor');
            this.fullscreenPreviewBtn.textContent = '退出全屏';
            this.isFullscreenEditor = false;
            this.fullscreenEditorBtn.textContent = '全屏编辑';
        } else {
            this.app.classList.remove('fullscreen-preview');
            this.fullscreenPreviewBtn.textContent = '全屏预览';
        }
    }
    
    exportHtml() {
        try {
            const htmlContent = this.generateFullHtml();
            const blob = new Blob([htmlContent], { type: 'text/html;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'markdown-export.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            this.showMessage('HTML文件已导出', 'success');
        } catch (error) {
            console.error('导出错误:', error);
            this.showMessage('导出失败: ' + error.message, 'error');
        }
    }
    
    generateFullHtml() {
        const markdownText = this.editor.value;
        const htmlContent = marked.parse(markdownText);
        
        return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Markdown导出</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/highlight.js@11.8.0/styles/github.min.css">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            color: #1e293b;
        }
        .markdown-body {
            font-size: 16px;
            line-height: 1.6;
        }
        ${this.getMarkdownStyles()}
    </style>
</head>
<body>
    <div class="markdown-body">
        ${htmlContent}
    </div>
</body>
</html>`;
    }
    
    getMarkdownStyles() {
        // 返回markdown样式的简化版本
        return `
        .markdown-body h1, .markdown-body h2, .markdown-body h3, 
        .markdown-body h4, .markdown-body h5, .markdown-body h6 {
            margin-top: 1.5rem;
            margin-bottom: 0.5rem;
            font-weight: 600;
            line-height: 1.25;
        }
        .markdown-body h1 { font-size: 2rem; border-bottom: 2px solid #e2e8f0; padding-bottom: 0.3rem; }
        .markdown-body h2 { font-size: 1.5rem; }
        .markdown-body h3 { font-size: 1.25rem; }
        .markdown-body p { margin-bottom: 1rem; }
        .markdown-body ul, .markdown-body ol { margin-bottom: 1rem; padding-left: 2rem; }
        .markdown-body blockquote {
            margin: 1rem 0; padding: 0.5rem 1rem;
            border-left: 4px solid #2563eb; background: #f8fafc;
        }
        .markdown-body code {
            background: #f8fafc; padding: 0.125rem 0.25rem;
            border-radius: 4px; font-family: monospace;
        }
        .markdown-body pre {
            background: #f6f8fa; padding: 1rem; border-radius: 8px;
            overflow-x: auto; margin: 1rem 0;
        }
        .markdown-body table { width: 100%; border-collapse: collapse; margin: 1rem 0; }
        .markdown-body th, .markdown-body td { padding: 0.5rem; border: 1px solid #e2e8f0; }
        .markdown-body th { background: #f8fafc; font-weight: 600; }
        `;
    }
    
    clearEditor() {
        if (confirm('确定要清空编辑器内容吗？')) {
            this.editor.value = '';
            this.renderMarkdown();
            this.updateStats();
            this.saveToLocalStorage();
            this.showMessage('编辑器已清空', 'success');
        }
    }
    
    loadExample() {
        const exampleMarkdown = `# Markdown语法示例

## 标题
使用 \`#\` 来创建标题，支持1-6级标题。

## 文本格式
- **粗体文本**
- *斜体文本*
- ~~删除线~~
- \`行内代码\`

## 列表
### 无序列表
- 项目1
- 项目2
  - 子项目2.1
  - 子项目2.2

### 有序列表
1. 第一项
2. 第二项
3. 第三项

## 链接和图片
[访问GitHub](https://github.com)

## 引用
> 这是一个引用块
> 
> 可以包含多行内容
> 
> > 嵌套引用

## 代码块
\`\`\`javascript
function hello() {
    console.log('Hello, Markdown!');
    return 'world';
}

const message = hello();
console.log(message);
\`\`\`

\`\`\`python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print([fibonacci(i) for i in range(10)])
\`\`\`

## 表格
| 功能 | 状态 | 描述 |
|------|------|------|
| 实时预览 | ✅ | 支持 |
| 语法高亮 | ✅ | 支持 |
| 同步滚动 | ✅ | 支持 |
| 导出HTML | ✅ | 支持 |

## 分割线
---

## 任务列表
- [x] 完成基础功能
- [x] 添加样式优化
- [ ] 添加更多主题
- [ ] 支持插件扩展

## 数学公式（如果支持）
行内公式: $E = mc^2$

块级公式:
$$
\\sum_{i=1}^{n} i = \\frac{n(n+1)}{2}
$$

## 脚注
这是一个有脚注的句子[^1]。

[^1]: 这是脚注的内容。

---
*最后更新：${new Date().toLocaleDateString('zh-CN')}*`;

        this.editor.value = exampleMarkdown;
        this.renderMarkdown();
        this.updateStats();
        this.saveToLocalStorage();
        this.showMessage('示例内容已加载', 'success');
    }
    
    async copyRichText() {
        try {
            // 获取预览内容
            const previewContent = this.preview.innerHTML;
            
            // 创建临时容器应用微信公众号兼容样式
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = previewContent;
            
            // 应用微信公众号兼容的内联样式
            this.applyWeChatStyles(tempDiv);
            
            // 创建富文本剪贴板数据
            const htmlBlob = new Blob([tempDiv.innerHTML], { type: 'text/html' });
            const textBlob = new Blob([tempDiv.textContent || tempDiv.innerText || ''], { type: 'text/plain' });
            
            const clipboardItem = new ClipboardItem({
                'text/html': htmlBlob,
                'text/plain': textBlob
            });
            
            // 复制到剪贴板
            await navigator.clipboard.write([clipboardItem]);
            this.showMessage('富文本样式已复制，可直接粘贴到微信公众号编辑器', 'success');
            
        } catch (error) {
            console.error('复制富文本失败:', error);
            // 降级方案：选择内容让用户手动复制
            this.fallbackCopyRichText();
        }
    }
    
    applyWeChatStyles(container) {
        // 微信公众号兼容的样式配置
        const wechatStyles = {
            // 基础文本样式
            body: 'font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; line-height: 1.75; color: #333; font-size: 17px;',
            
            // 标题样式
            h1: 'font-size: 24px; font-weight: bold; margin: 20px 0 10px 0; padding: 0; color: #333; line-height: 1.5;',
            h2: 'font-size: 20px; font-weight: bold; margin: 18px 0 8px 0; padding: 0; color: #333; line-height: 1.5;',
            h3: 'font-size: 18px; font-weight: bold; margin: 16px 0 8px 0; padding: 0; color: #333; line-height: 1.5;',
            h4: 'font-size: 16px; font-weight: bold; margin: 14px 0 6px 0; padding: 0; color: #333; line-height: 1.5;',
            h5: 'font-size: 14px; font-weight: bold; margin: 12px 0 6px 0; padding: 0; color: #333; line-height: 1.5;',
            h6: 'font-size: 14px; font-weight: bold; margin: 10px 0 6px 0; padding: 0; color: #666; line-height: 1.5;',
            
            // 段落和文本
            p: 'margin: 15px 0; padding: 0; line-height: 1.75; color: #333; font-size: 17px;',
            
            // 列表样式
            ul: 'margin: 15px 0; padding-left: 20px;',
            ol: 'margin: 15px 0; padding-left: 20px;',
            li: 'margin: 6px 0; line-height: 1.75; color: #333; font-size: 17px;',
            
            // 引用块
            blockquote: 'margin: 20px 0; padding: 15px 20px; background-color: #f7f7f7; border-left: 4px solid #1e90ff; color: #666; font-style: italic; line-height: 1.75; font-size: 17px;',
            
            // 代码样式
            code: 'background-color: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; color: #e96900;',
            pre: 'background-color: #f8f8f8; padding: 15px; border-radius: 6px; overflow-x: auto; margin: 15px 0; border: 1px solid #e1e4e8;',
            
            // 表格样式
            table: 'border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px;',
            th: 'border: 1px solid #dfe2e5; padding: 8px 12px; background-color: #f6f8fa; font-weight: bold; text-align: left;',
            td: 'border: 1px solid #dfe2e5; padding: 8px 12px; text-align: left;',
            
            // 加粗元素样式 - 确保公众号兼容性
            strong: 'font-weight: 700; color: #333;',
            b: 'font-weight: 700; color: #333;',
            
            // 链接
            a: 'color: #1e90ff; text-decoration: none; border-bottom: 1px solid transparent;',
            
            // 图片
            img: 'max-width: 100%; height: auto; border-radius: 4px; margin: 10px 0;',
            
            // 分割线
            hr: 'border: none; height: 1px; background-color: #e1e4e8; margin: 30px 0;'
        };
        
        // 应用样式到所有匹配的元素
        Object.keys(wechatStyles).forEach(tag => {
            const elements = container.querySelectorAll(tag);
            elements.forEach(element => {
                element.style.cssText = wechatStyles[tag];
                
                // 特殊处理
                if (tag === 'pre') {
                    const codeElement = element.querySelector('code');
                    if (codeElement) {
                        codeElement.style.cssText = 'background: none; padding: 0; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 13px; line-height: 1.5; color: #333;';
                    }
                }
                
                if (tag === 'a') {
                    element.addEventListener('mouseover', function() {
                        this.style.borderBottomColor = '#1e90ff';
                    });
                }
                
                // 为标题添加底部边框（仅h1）
                if (tag === 'h1') {
                    element.style.borderBottom = '2px solid #eaecef';
                    element.style.paddingBottom = '10px';
                }
                // h2标题不添加底部边框，保持简洁
            });
        });
        
        // 为整个容器设置基础样式
        container.style.cssText = wechatStyles.body;
        
        // 处理加粗元素，确保在公众号中正确显示
        this.fixBoldForWeChat(container);
        
        // 移除可能影响微信显示的类名和属性
        this.cleanupForWeChat(container);
    }
    
    fixBoldForWeChat(container) {
        // 处理所有可能的加粗元素，确保在公众号中显示正确
        const boldSelectors = ['strong', 'b', '[style*="font-weight"]'];
        
        boldSelectors.forEach(selector => {
            const boldElements = container.querySelectorAll(selector);
            boldElements.forEach(element => {
                // 设置强的加粗效果，兼容公众号编辑器
                element.style.fontWeight = '700'; // 使用数值而不是bold关键字
                element.style.color = element.style.color || '#333'; // 确保有足够对比度
                
                // 如果不是strong或b标签，转换为strong标签
                if (!['STRONG', 'B'].includes(element.tagName)) {
                    const strongElement = document.createElement('strong');
                    strongElement.innerHTML = element.innerHTML;
                    strongElement.style.cssText = element.style.cssText;
                    strongElement.style.fontWeight = '700';
                    element.parentNode.replaceChild(strongElement, element);
                }
            });
        });
        
        // 特别处理Markdown中的**粗体**文本
        const allTextNodes = this.getTextNodesIn(container);
        allTextNodes.forEach(textNode => {
            if (textNode.parentElement && textNode.parentElement.tagName === 'STRONG') {
                textNode.parentElement.style.fontWeight = '700';
                textNode.parentElement.style.color = textNode.parentElement.style.color || '#333';
            }
        });
        
        // 确保标题的加粗效果
        const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach(heading => {
            heading.style.fontWeight = '700';
        });
    }
    
    cleanupForWeChat(container) {
        // 移除所有类名（微信不支持外部CSS）
        const allElements = container.querySelectorAll('*');
        allElements.forEach(element => {
            element.removeAttribute('class');
            // 移除可能导致问题的属性
            element.removeAttribute('id');
            element.removeAttribute('data-line');
            element.removeAttribute('contenteditable');
        });
        
        // 处理语法高亮的span标签，转换为合适的样式
        const highlightSpans = container.querySelectorAll('span[class]');
        highlightSpans.forEach(span => {
            const classList = span.className;
            // 根据语法高亮的类名设置颜色
            if (classList.includes('hljs-keyword')) {
                span.style.color = '#d73a49';
                span.style.fontWeight = 'bold';
            } else if (classList.includes('hljs-string')) {
                span.style.color = '#032f62';
            } else if (classList.includes('hljs-number')) {
                span.style.color = '#005cc5';
            } else if (classList.includes('hljs-comment')) {
                span.style.color = '#6a737d';
                span.style.fontStyle = 'italic';
            } else if (classList.includes('hljs-function')) {
                span.style.color = '#6f42c1';
            } else if (classList.includes('hljs-variable')) {
                span.style.color = '#e36209';
            }
            span.removeAttribute('class');
        });
    }
    
    fallbackCopyRichText() {
        try {
            // 降级方案：创建临时可选择的div
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = this.preview.innerHTML;
            this.applyWeChatStyles(tempDiv);
            
            tempDiv.style.cssText += '; position: fixed; left: -9999px; top: -9999px; opacity: 0;';
            document.body.appendChild(tempDiv);
            
            // 选择内容
            const range = document.createRange();
            range.selectNodeContents(tempDiv);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            
            // 尝试执行复制命令
            const success = document.execCommand('copy');
            
            // 清理
            selection.removeAllRanges();
            document.body.removeChild(tempDiv);
            
            if (success) {
                this.showMessage('富文本样式已复制（兼容模式），可直接粘贴到微信公众号编辑器', 'success');
            } else {
                this.showMessage('复制失败，请手动选择内容复制', 'error');
            }
        } catch (error) {
            console.error('降级复制也失败:', error);
            this.showMessage('复制功能不可用，请手动选择内容复制', 'error');
        }
    }
    
    async copyXiaohongshu() {
        try {
            // 获取预览内容
            const previewContent = this.preview.innerHTML;
            
            // 创建临时容器应用小红书兼容样式
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = previewContent;
            
            // 应用小红书兼容的内联样式
            this.applyXiaohongshuStyles(tempDiv);
            
            // 创建富文本剪贴板数据
            const htmlBlob = new Blob([tempDiv.innerHTML], { type: 'text/html' });
            const textBlob = new Blob([tempDiv.textContent || tempDiv.innerText || ''], { type: 'text/plain' });
            
            const clipboardItem = new ClipboardItem({
                'text/html': htmlBlob,
                'text/plain': textBlob
            });
            
            // 复制到剪贴板
            await navigator.clipboard.write([clipboardItem]);
            this.showMessage('富文本样式已复制，可直接粘贴到小红书编辑器', 'success');
            
        } catch (error) {
            console.error('复制富文本失败:', error);
            // 降级方案：选择内容让用户手动复制
            this.fallbackCopyXiaohongshu();
        }
    }
    
    applyXiaohongshuStyles(container) {
        // 小红书兼容的样式配置
        const xiaohongshuStyles = {
            // 基础文本样式 - 小红书偏向活泼年轻的风格
            body: 'font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif; line-height: 1.8; color: #333; font-size: 16px;',
            
            // 标题样式 - 小红书标题通常更加醒目
            h1: 'font-size: 28px; font-weight: 700; margin: 24px 0 12px 0; padding: 0; color: #222; line-height: 1.4; text-align: center;',
            h2: 'font-size: 24px; font-weight: 700; margin: 20px 0 10px 0; padding: 0; color: #222; line-height: 1.4;',
            h3: 'font-size: 20px; font-weight: 700; margin: 18px 0 9px 0; padding: 0; color: #333; line-height: 1.4;',
            h4: 'font-size: 18px; font-weight: 700; margin: 16px 0 8px 0; padding: 0; color: #333; line-height: 1.4;',
            h5: 'font-size: 16px; font-weight: 700; margin: 14px 0 7px 0; padding: 0; color: #333; line-height: 1.4;',
            h6: 'font-size: 14px; font-weight: 700; margin: 12px 0 6px 0; padding: 0; color: #666; line-height: 1.4;',
            
            // 段落和文本 - 小红书用16px比较合适，行距稍大
            p: 'margin: 16px 0; padding: 0; line-height: 1.8; color: #333; font-size: 16px;',
            
            // 列表样式 - 小红书的列表通常更简洁
            ul: 'margin: 16px 0; padding-left: 24px;',
            ol: 'margin: 16px 0; padding-left: 24px;',
            li: 'margin: 8px 0; line-height: 1.8; color: #333; font-size: 16px;',
            
            // 引用块 - 小红书风格的引用块，更加时尚
            blockquote: 'margin: 20px 0; padding: 16px 20px; background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%); border-left: 4px solid #ff6b6b; color: #555; font-style: italic; line-height: 1.8; border-radius: 8px; font-size: 16px;',
            
            // 代码样式 - 小红书的代码块样式
            code: 'background-color: #f8f9fa; padding: 3px 8px; border-radius: 4px; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; color: #e83e8c; border: 1px solid #e9ecef;',
            pre: 'background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 20px; border-radius: 8px; overflow-x: auto; margin: 20px 0; border: 1px solid #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.1);',
            
            // 表格样式 - 小红书风格的表格
            table: 'border-collapse: collapse; width: 100%; margin: 24px 0; font-size: 14px; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1);',
            th: 'border: 1px solid #e9ecef; padding: 12px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: 700; text-align: left;',
            td: 'border: 1px solid #e9ecef; padding: 12px 16px; text-align: left; background-color: #fff;',
            
            // 加粗元素样式 - 确保小红书兼容性
            strong: 'font-weight: 700; color: #222;',
            b: 'font-weight: 700; color: #222;',
            
            // 链接 - 小红书风格的链接
            a: 'color: #ff6b6b; text-decoration: none; border-bottom: 1px solid transparent; font-weight: 500;',
            
            // 图片 - 小红书喜欢圆角
            img: 'max-width: 100%; height: auto; border-radius: 8px; margin: 16px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);',
            
            // 分割线 - 小红书风格的分割线
            hr: 'border: none; height: 2px; background: linear-gradient(to right, #ff6b6b, #feca57, #48dbfb, #ff9ff3); margin: 32px 0; border-radius: 1px;'
        };
        
        // 应用样式到所有匹配的元素
        Object.keys(xiaohongshuStyles).forEach(tag => {
            const elements = container.querySelectorAll(tag);
            elements.forEach(element => {
                element.style.cssText = xiaohongshuStyles[tag];
                
                // 特殊处理
                if (tag === 'pre') {
                    const codeElement = element.querySelector('code');
                    if (codeElement) {
                        codeElement.style.cssText = 'background: none; padding: 0; font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; font-size: 14px; line-height: 1.6; color: #495057; border: none;';
                    }
                }
                
                if (tag === 'a') {
                    element.addEventListener('mouseover', function() {
                        this.style.borderBottomColor = '#ff6b6b';
                        this.style.color = '#ff5252';
                    });
                }
                
                // 为标题添加特殊效果
                if (tag === 'h1') {
                    element.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                    element.style.webkitBackgroundClip = 'text';
                    element.style.webkitTextFillColor = 'transparent';
                    element.style.backgroundClip = 'text';
                    element.style.borderBottom = '3px solid #667eea';
                    element.style.paddingBottom = '12px';
                } else if (tag === 'h2') {
                    element.style.color = '#667eea';
                    element.style.borderBottom = '2px solid #f093fb';
                    element.style.paddingBottom = '8px';
                } else if (tag === 'h3') {
                    element.style.color = '#764ba2';
                }
                
                // 无序列表保持原有样式，不添加emoji装饰
                if (tag === 'li' && element.parentElement.tagName.toLowerCase() === 'ul') {
                    // 保持小红书风格但不添加emoji，使用更简洁的列表样式
                    element.style.marginBottom = '8px';
                }
            });
        });
        
        // 为整个容器设置基础样式
        container.style.cssText = xiaohongshuStyles.body;
        
        // 处理加粗元素，确保在小红书中正确显示
        this.fixBoldForXiaohongshu(container);
        
        // 移除可能影响小红书显示的类名和属性
        this.cleanupForXiaohongshu(container);
    }
    
    fixBoldForXiaohongshu(container) {
        // 处理所有可能的加粗元素，确保在小红书中显示正确
        const boldSelectors = ['strong', 'b', '[style*="font-weight"]'];
        
        boldSelectors.forEach(selector => {
            const boldElements = container.querySelectorAll(selector);
            boldElements.forEach(element => {
                // 设置更强的加粗效果，兼容小红书编辑器
                element.style.fontWeight = '700'; // 使用数值而不是bold关键字
                element.style.color = element.style.color || '#222'; // 确保有足够对比度
                
                // 如果不是strong或b标签，转换为strong标签
                if (!['STRONG', 'B'].includes(element.tagName)) {
                    const strongElement = document.createElement('strong');
                    strongElement.innerHTML = element.innerHTML;
                    strongElement.style.cssText = element.style.cssText;
                    strongElement.style.fontWeight = '700';
                    element.parentNode.replaceChild(strongElement, element);
                }
            });
        });
        
        // 特别处理Markdown中的**粗体**文本
        const allTextNodes = this.getTextNodesIn(container);
        allTextNodes.forEach(textNode => {
            if (textNode.parentElement && textNode.parentElement.tagName === 'STRONG') {
                textNode.parentElement.style.fontWeight = '700';
                textNode.parentElement.style.color = textNode.parentElement.style.color || '#222';
            }
        });
        
        // 确保标题的加粗效果
        const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
        headings.forEach(heading => {
            heading.style.fontWeight = '700';
        });
    }
    
    getTextNodesIn(element) {
        const textNodes = [];
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );
        
        let node;
        while (node = walker.nextNode()) {
            textNodes.push(node);
        }
        
        return textNodes;
    }
    
    cleanupForXiaohongshu(container) {
        // 移除所有类名（小红书可能不支持外部CSS）
        const allElements = container.querySelectorAll('*');
        allElements.forEach(element => {
            element.removeAttribute('class');
            // 移除可能导致问题的属性
            element.removeAttribute('id');
            element.removeAttribute('data-line');
            element.removeAttribute('contenteditable');
        });
        
        // 处理语法高亮的span标签，转换为适合小红书的颜色
        const highlightSpans = container.querySelectorAll('span[class]');
        highlightSpans.forEach(span => {
            const classList = span.className;
            // 根据语法高亮的类名设置颜色 - 小红书风格的配色
            if (classList.includes('hljs-keyword')) {
                span.style.color = '#ff6b6b';
                span.style.fontWeight = '700';
            } else if (classList.includes('hljs-string')) {
                span.style.color = '#4ecdc4';
            } else if (classList.includes('hljs-number')) {
                span.style.color = '#45b7d1';
            } else if (classList.includes('hljs-comment')) {
                span.style.color = '#96ceb4';
                span.style.fontStyle = 'italic';
            } else if (classList.includes('hljs-function')) {
                span.style.color = '#a29bfe';
            } else if (classList.includes('hljs-variable')) {
                span.style.color = '#fd79a8';
            }
            span.removeAttribute('class');
        });
    }
    
    fallbackCopyXiaohongshu() {
        try {
            // 降级方案：创建临时可选择的div
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = this.preview.innerHTML;
            this.applyXiaohongshuStyles(tempDiv);
            
            tempDiv.style.cssText += '; position: fixed; left: -9999px; top: -9999px; opacity: 0;';
            document.body.appendChild(tempDiv);
            
            // 选择内容
            const range = document.createRange();
            range.selectNodeContents(tempDiv);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            
            // 尝试执行复制命令
            const success = document.execCommand('copy');
            
            // 清理
            selection.removeAllRanges();
            document.body.removeChild(tempDiv);
            
            if (success) {
                this.showMessage('富文本样式已复制（兼容模式），可直接粘贴到小红书编辑器', 'success');
            } else {
                this.showMessage('复制失败，请手动选择内容复制', 'error');
            }
        } catch (error) {
            console.error('降级复制也失败:', error);
            this.showMessage('复制功能不可用，请手动选择内容复制', 'error');
        }
    }
    
    async copyHtml() {
        try {
            const htmlContent = this.preview.innerHTML;
            await navigator.clipboard.writeText(htmlContent);
            this.showMessage('HTML内容已复制到剪贴板', 'success');
        } catch (error) {
            console.error('复制失败:', error);
            this.showMessage('复制失败，请手动选择复制', 'error');
        }
    }
    
    printPreview() {
        const printWindow = window.open('', '', 'width=800,height=600');
        const htmlContent = this.generateFullHtml();
        printWindow.document.write(htmlContent);
        printWindow.document.close();
        printWindow.print();
    }
    
    saveToLocalStorage() {
        try {
            localStorage.setItem('markdown-content', this.editor.value);
        } catch (error) {
            console.warn('无法保存到本地存储:', error);
        }
    }
    
    showMessage(text, type = 'success') {
        // 移除现有的消息
        const existingMessage = document.querySelector('.success-message, .error-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // 创建新消息
        const message = document.createElement('div');
        message.className = type === 'success' ? 'success-message' : 'error-message';
        message.textContent = text;
        
        // 插入到预览面板顶部
        this.preview.insertBefore(message, this.preview.firstChild);
        
        // 3秒后自动消失
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 3000);
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    new MarkdownRenderer();
});

// 页面卸载前保存内容
window.addEventListener('beforeunload', () => {
    const editor = document.getElementById('editor');
    if (editor) {
        localStorage.setItem('markdown-content', editor.value);
    }
});
