# 前后端独立版本管理方案

## 概述

前后端独立版本管理允许前端和后端按照各自的开发节奏独立发布，适合以下场景：
- 前后端团队独立开发
- 前端UI频繁更新，后端API相对稳定
- 需要支持多个前端版本对接同一后端API

## 版本体系设计

### 1. 三层版本结构

```
系统版本 (System Version)
    ├── 后端版本 (Backend Version)
    │   ├── API版本 (API Version)
    │   └── 服务版本 (Service Version)
    └── 前端版本 (Frontend Version)
        ├── UI版本 (UI Version)
        └── 兼容API版本 (Compatible API Version)
```

### 2. 版本号规范

#### 系统版本（用于整体发布）
- 格式：`vX.Y.Z`
- 示例：`v2.0.0`
- 用途：标记系统重大里程碑，通常在前后端都有重大更新时使用

#### 后端版本
- 格式：`X.Y.Z`
- 示例：`1.6.0`
- 规则：
  - 主版本(X)：API不兼容变更
  - 次版本(Y)：新增功能，向后兼容
  - 修订版(Z)：Bug修复

#### 前端版本
- 格式：`X.Y.Z`
- 示例：`2.1.0`
- 规则：
  - 主版本(X)：UI重大改版或不兼容变更
  - 次版本(Y)：新增功能或UI改进
  - 修订版(Z)：Bug修复和小优化

#### API版本（URL路径版本）
- 格式：`v1`, `v2`
- 示例：`/api/v1/query`, `/api/v2/query`
- 用途：API接口版本控制，支持多版本并存

## 具体实施方案

### 1. 后端版本管理

#### 创建后端版本文件
```python
# backend_version.py
"""
后端版本管理
"""

# 后端服务版本
BACKEND_VERSION = "1.6.0"

# API版本（用于URL路径）
API_VERSION = "v1"

# API兼容性版本范围
API_COMPATIBILITY = {
    "min_version": "1.4.0",  # 最低兼容版本
    "max_version": "1.6.x"   # 最高兼容版本
}

# 功能特性标记
BACKEND_FEATURES = {
    "financial_analysis": True,
    "money_flow": True,
    "streaming": True,
    "unified_validator": True,
    "date_intelligence_v2": True
}

# 版本信息
VERSION_INFO = {
    "version": BACKEND_VERSION,
    "api_version": API_VERSION,
    "release_date": "2025-06-29",
    "description": "统一股票验证器优化"
}
```

#### 更新 api/main.py
```python
from backend_version import BACKEND_VERSION, API_VERSION, VERSION_INFO

app = FastAPI(
    title="股票分析系统API",
    version=BACKEND_VERSION,
    description=f"API Version: {API_VERSION}"
)

# API版本路由
api_router = APIRouter(prefix=f"/api/{API_VERSION}")

# 版本信息端点
@app.get("/version")
async def get_version():
    return VERSION_INFO

# 健康检查包含版本
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "backend_version": BACKEND_VERSION,
        "api_version": API_VERSION,
        "features": BACKEND_FEATURES
    }
```

### 2. 前端版本管理

#### 创建前端版本配置
```json
// frontend/version.json
{
  "version": "2.1.0",
  "name": "Stock Analysis Frontend",
  "releaseDate": "2025-06-29",
  "apiCompatibility": {
    "requiredApiVersion": "v1",
    "minBackendVersion": "1.4.0",
    "maxBackendVersion": "1.6.x"
  },
  "features": {
    "streaming": true,
    "darkMode": true,
    "splitView": true,
    "stopButton": true
  },
  "buildInfo": {
    "buildTime": "2025-06-29T14:00:00Z",
    "commitHash": "e2f895c",
    "environment": "production"
  }
}
```

#### 前端版本检查组件
```typescript
// frontend/src/utils/versionManager.ts
import versionInfo from '../../version.json';

export class VersionManager {
  static async checkCompatibility(): Promise<{
    compatible: boolean;
    message?: string;
  }> {
    try {
      // 获取后端版本信息
      const response = await fetch('/api/version');
      const backendInfo = await response.json();
      
      // 检查API版本
      if (backendInfo.api_version !== versionInfo.apiCompatibility.requiredApiVersion) {
        return {
          compatible: false,
          message: `API版本不兼容。需要: ${versionInfo.apiCompatibility.requiredApiVersion}, 
                   当前: ${backendInfo.api_version}`
        };
      }
      
      // 检查后端版本范围
      const backendVersion = backendInfo.version;
      if (!this.isVersionInRange(backendVersion, 
          versionInfo.apiCompatibility.minBackendVersion,
          versionInfo.apiCompatibility.maxBackendVersion)) {
        return {
          compatible: false,
          message: `后端版本不兼容。需要: ${versionInfo.apiCompatibility.minBackendVersion} - 
                   ${versionInfo.apiCompatibility.maxBackendVersion}, 当前: ${backendVersion}`
        };
      }
      
      return { compatible: true };
    } catch (error) {
      return {
        compatible: false,
        message: '无法连接到后端服务'
      };
    }
  }
  
  static getVersion(): string {
    return versionInfo.version;
  }
  
  static getFeatures(): Record<string, boolean> {
    return versionInfo.features;
  }
}
```

#### 在应用启动时检查兼容性
```typescript
// frontend/src/App.tsx
import { VersionManager } from './utils/versionManager';

function App() {
  const [versionCheck, setVersionCheck] = useState<{
    checked: boolean;
    compatible: boolean;
    message?: string;
  }>({ checked: false, compatible: true });

  useEffect(() => {
    VersionManager.checkCompatibility().then(result => {
      setVersionCheck({
        checked: true,
        ...result
      });
    });
  }, []);

  if (versionCheck.checked && !versionCheck.compatible) {
    return (
      <div className="version-error">
        <h2>版本不兼容</h2>
        <p>{versionCheck.message}</p>
        <p>请联系管理员更新系统。</p>
      </div>
    );
  }

  // 正常渲染应用...
}
```

### 3. 版本同步脚本

#### 后端版本同步脚本
```python
# scripts/sync_backend_version.py
import os
import re
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_version import BACKEND_VERSION

def update_backend_files():
    """更新后端相关文件的版本号"""
    updates = [
        ("setup.py", r'version="[\d.]+"', f'version="{BACKEND_VERSION}"'),
        ("api/main.py", r'version="[\d.]+"', f'version="{BACKEND_VERSION}"'),
        ("CLAUDE.md", r'后端API版本: v[\d.]+', f'后端API版本: v{BACKEND_VERSION}'),
    ]
    
    for filepath, pattern, replacement in updates:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            new_content = re.sub(pattern, replacement, content)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"✅ 更新 {filepath}")

if __name__ == "__main__":
    print(f"同步后端版本到: {BACKEND_VERSION}")
    update_backend_files()
```

#### 前端版本同步脚本
```javascript
// frontend/scripts/sync-version.js
const fs = require('fs');
const path = require('path');

const versionInfo = require('../version.json');
const packageJsonPath = path.join(__dirname, '../package.json');

// 更新 package.json
const packageJson = require(packageJsonPath);
packageJson.version = versionInfo.version;

fs.writeFileSync(
  packageJsonPath,
  JSON.stringify(packageJson, null, 2) + '\n'
);

console.log(`✅ 前端版本已同步到: ${versionInfo.version}`);
```

### 4. 发布流程

#### 后端发布流程
```bash
# 1. 更新后端版本
编辑 backend_version.py 中的 BACKEND_VERSION

# 2. 同步版本号
python scripts/sync_backend_version.py

# 3. 运行测试
python test_agents_consistency.py

# 4. 提交和标记
git add -A
git commit -m "chore(backend): bump version to v1.6.0"
git tag -a backend-v1.6.0 -m "Backend Release v1.6.0"

# 5. 推送
git push origin main --tags
```

#### 前端发布流程
```bash
# 1. 更新前端版本
编辑 frontend/version.json

# 2. 同步版本号
cd frontend
npm run sync-version

# 3. 构建和测试
npm run build
npm test

# 4. 提交和标记
git add -A
git commit -m "chore(frontend): bump version to v2.1.0"
git tag -a frontend-v2.1.0 -m "Frontend Release v2.1.0"

# 5. 推送
git push origin main --tags
```

### 5. 版本兼容性矩阵

| 前端版本 | 兼容后端版本 | API版本 | 说明 |
|---------|-------------|---------|------|
| 2.1.x | 1.4.0 - 1.6.x | v1 | 当前版本 |
| 2.0.x | 1.4.0 - 1.5.x | v1 | 支持流式响应 |
| 1.x.x | 1.0.0 - 1.3.x | v1 | 旧版本（已废弃） |

### 6. CI/CD 集成

#### GitHub Actions 示例
```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'backend-v*'
      - 'frontend-v*'

jobs:
  backend-release:
    if: startsWith(github.ref, 'refs/tags/backend-v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Extract version
        run: echo "VERSION=${GITHUB_REF#refs/tags/backend-v}" >> $GITHUB_ENV
      - name: Build and publish backend
        run: |
          python setup.py sdist bdist_wheel
          # 发布到 PyPI 或私有仓库

  frontend-release:
    if: startsWith(github.ref, 'refs/tags/frontend-v')
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Extract version
        run: echo "VERSION=${GITHUB_REF#refs/tags/frontend-v}" >> $GITHUB_ENV
      - name: Build and publish frontend
        run: |
          cd frontend
          npm install
          npm run build
          # 部署到 CDN 或静态服务器
```

## 优势与注意事项

### 优势
1. **独立发布周期**：前后端可以按需发布，不相互阻塞
2. **版本兼容性管理**：明确的兼容性检查机制
3. **多版本支持**：可以同时运行多个API版本
4. **清晰的版本追踪**：每个组件都有独立的版本历史

### 注意事项
1. **兼容性测试**：每次发布需要测试版本兼容性
2. **文档同步**：需要维护版本兼容性矩阵文档
3. **通信协议**：前后端需要约定好版本协商机制
4. **回滚策略**：需要考虑版本回滚的影响

## 迁移计划

1. **第一阶段**：建立版本文件和检查机制
2. **第二阶段**：实施版本兼容性检查
3. **第三阶段**：建立自动化发布流程
4. **第四阶段**：完善监控和告警机制