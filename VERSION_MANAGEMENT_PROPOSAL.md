# 股票分析系统版本管理方案

## 问题分析

### 当前版本号分布情况

| 文件位置 | 当前版本 | 最后更新 | 说明 |
|---------|---------|---------|------|
| CLAUDE.md | v1.5.5 | 2025-06-29 | ✅ 最新 |
| docs/project_status/CURRENT_STATUS.md | v1.5.5 | 2025-06-29 | ✅ 最新 |
| test-guide.md | v1.5.5 | 2025-06-29 | ✅ 最新 |
| api/main.py | v1.4.1 | 较早 | ❌ 过时 |
| setup.py | v1.3.0 | 较早 | ❌ 过时 |
| frontend/package.json | 0.0.0 | 未设置 | ❌ 未管理 |

### 核心问题

1. **版本号分散**：6个不同位置维护版本号
2. **更新不同步**：文档版本与代码版本相差多个版本
3. **缺乏规范**：没有统一的版本管理流程
4. **前后端分离**：前端和后端版本独立管理

## 解决方案

### 方案一：统一版本管理（推荐）

#### 1. 创建中央版本文件

```python
# version.py (项目根目录)
"""
股票分析系统版本管理
"""

# 主版本号 - 整个系统的统一版本
SYSTEM_VERSION = "1.5.5"

# 组件版本号 - 可选，用于独立组件版本管理
BACKEND_VERSION = SYSTEM_VERSION  # 后端API版本
FRONTEND_VERSION = SYSTEM_VERSION  # 前端版本
API_VERSION = "v1"  # API接口版本（用于URL）

# 版本信息
VERSION_INFO = {
    "version": SYSTEM_VERSION,
    "release_date": "2025-06-29",
    "codename": "Unified Validator",
    "description": "统一股票验证器大幅优化"
}

# 版本历史
VERSION_HISTORY = [
    ("1.5.5", "2025-06-29", "统一股票验证器大幅优化"),
    ("1.5.4", "2025-06-28", "流式响应完整实现"),
    ("1.5.3", "2025-06-27", "React前端Phase 1完成"),
    # ... 更多历史
]
```

#### 2. 自动同步脚本

```python
# scripts/sync_version.py
"""
版本号同步脚本
使用方法: python scripts/sync_version.py
"""

import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from version import SYSTEM_VERSION, BACKEND_VERSION, FRONTEND_VERSION

def update_file_version(filepath, pattern, replacement):
    """更新文件中的版本号"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = re.sub(pattern, replacement, content)
    
    if content != new_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ 更新 {filepath}")
    else:
        print(f"⏭️  跳过 {filepath} (已是最新)")

def main():
    """同步所有版本号"""
    print(f"同步版本号到: {SYSTEM_VERSION}")
    print("=" * 50)
    
    # 更新规则
    updates = [
        # 文档文件
        ("CLAUDE.md", 
         r"Stock Analysis System \(v[\d.]+\)", 
         f"Stock Analysis System (v{SYSTEM_VERSION})"),
        
        ("docs/project_status/CURRENT_STATUS.md",
         r"\*\*版本\*\*: v[\d.]+",
         f"**版本**: v{SYSTEM_VERSION}"),
        
        ("test-guide.md",
         r"\*\*版本\*\*: v[\d.]+",
         f"**版本**: v{SYSTEM_VERSION}"),
        
        # Python文件
        ("setup.py",
         r'version="[\d.]+"',
         f'version="{BACKEND_VERSION}"'),
        
        ("api/main.py",
         r'version="[\d.]+"',
         f'version="{BACKEND_VERSION}"'),
        
        # 前端文件
        ("frontend/package.json",
         r'"version": "[\d.]+"',
         f'"version": "{FRONTEND_VERSION}"'),
    ]
    
    # 执行更新
    for filepath, pattern, replacement in updates:
        if os.path.exists(filepath):
            update_file_version(filepath, pattern, replacement)
        else:
            print(f"❌ 文件不存在: {filepath}")
    
    print("\n✅ 版本同步完成！")

if __name__ == "__main__":
    main()
```

#### 3. 版本管理流程

```bash
# 1. 更新版本号
编辑 version.py 中的 SYSTEM_VERSION

# 2. 同步版本号到所有文件
python scripts/sync_version.py

# 3. 提交更改
git add -A
git commit -m "chore: bump version to vX.X.X"

# 4. 创建版本标签
git tag -a vX.X.X -m "Release vX.X.X: 版本描述"

# 5. 推送
git push origin dev-react-frontend-v2 --tags
```

### 方案二：前后端独立版本管理

如果需要前后端独立发版，可以采用：

1. **后端版本**：`version.py` 管理 Python 相关版本
2. **前端版本**：`frontend/version.json` 管理前端版本
3. **系统版本**：文档中记录整体系统版本

```json
// frontend/version.json
{
  "version": "1.5.5",
  "apiVersion": "1.4.1",
  "buildDate": "2025-06-29",
  "features": ["streaming", "darkMode", "validator"]
}
```

### 方案三：使用版本管理工具

使用 `bump2version` 或 `poetry` 等工具自动管理版本：

```ini
# .bumpversion.cfg
[bumpversion]
current_version = 1.5.5
commit = True
tag = True

[bumpversion:file:version.py]
[bumpversion:file:setup.py]
[bumpversion:file:api/main.py]
[bumpversion:file:frontend/package.json]
[bumpversion:file:CLAUDE.md]
[bumpversion:file:docs/project_status/CURRENT_STATUS.md]
```

## 建议采用方案

**推荐方案一：统一版本管理**

理由：
1. 简单直观，易于维护
2. 确保版本号一致性
3. 支持自动化同步
4. 可扩展到CI/CD流程

## 实施步骤

1. **立即执行**：
   - 创建 `version.py` 文件
   - 创建 `scripts/sync_version.py` 同步脚本
   - 运行同步脚本统一当前版本号

2. **后续改进**：
   - 集成到 Git hooks（pre-commit）
   - 添加版本检查到 CI/CD
   - 创建自动发布脚本

3. **文档更新**：
   - 在 README 中说明版本管理策略
   - 在贡献指南中添加版本更新流程

## 版本号规范

采用语义化版本 2.0.0：

- **主版本号（MAJOR）**：不兼容的API修改
- **次版本号（MINOR）**：向下兼容的功能性新增
- **修订号（PATCH）**：向下兼容的问题修正

示例：
- 1.5.5 → 1.5.6：修复bug
- 1.5.5 → 1.6.0：新增功能
- 1.5.5 → 2.0.0：重大改版