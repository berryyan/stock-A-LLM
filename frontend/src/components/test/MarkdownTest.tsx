import React, { useEffect, useState } from 'react';
import { MarkdownRenderer } from '../common/MarkdownRenderer';

export const MarkdownTest: React.FC = () => {
  const [content, setContent] = useState('');
  
  useEffect(() => {
    // 加载测试Markdown内容
    fetch('/src/test-markdown.md')
      .then(res => res.text())
      .then(text => setContent(text))
      .catch(() => {
        // 如果无法加载文件，使用内置测试内容
        setContent(`# Markdown渲染测试

## 代码块测试

### Python示例
\`\`\`python
def analyze_stock(stock_code):
    """分析股票数据"""
    data = fetch_data(stock_code)
    return data
\`\`\`

### JavaScript示例
\`\`\`javascript
const query = async (code) => {
  return await fetch(\`/api/stock/\${code}\`);
};
\`\`\`

## 表格测试

| 股票代码 | 公司名称 | 最新价格 |
|---------|---------|---------|
| 600519.SH | 贵州茅台 | 1,680.00 |
| 000858.SZ | 五粮液 | 180.50 |

## 链接测试

查看 [股票分析文档](https://example.com)

## 引用测试

> 投资有风险，入市需谨慎。

## 列表测试

- 实时查询
- 数据分析
- AI推荐

1. 第一步
2. 第二步
3. 第三步`);
      });
  }, []);
  
  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="mb-8 p-4 bg-gray-100 rounded">
        <h2 className="text-lg font-semibold mb-2">Markdown渲染器测试页面</h2>
        <p className="text-sm text-gray-600">测试各种Markdown元素的渲染效果</p>
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow">
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
};