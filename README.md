# AI 互动闯关学习助手（Phase 1 收敛版）

本仓库已实现你确认的范围：

- 前端：Taro 4 + React + TypeScript 小程序工程（核心 6 页面 + 错题本/学习记录占位页）
- 后端：FastAPI + LangChain + DeepSeek（核心 3 接口）
- 测试：后端 TDD 测试通过（pytest）

## 目录结构

- `miniapp/`：小程序前端
- `backend/`：Python 后端
- `prototypes/claudeCode开发的原型图/`：UI 原型源文件

## 已实现能力

### 前端（严格映射原型）

- 首页（开始学习、错题本/学习记录入口）
- 输入页（文本输入、题量/难度设置）
- 题目页（进度、选项、即时反馈覆盖层、左滑下一题）
- 结算页（得分、正确/错误、查看分析）
- 分析页（整体评价、薄弱点、下一步建议）
- 错题本占位页、学习记录占位页

### 后端

- `GET /api/health`
- `POST /api/generate-questions`
- `POST /api/generate-analysis`

并包含：

- 参数校验与统一错误结构
- LangChain + ChatDeepSeek 集成（`deepseek-chat`）
- JSON 解析与题目结构校验
- Token 消耗记录器（jsonl）

## 启动后端

```powershell
cd backend
# 首次（已创建 .venv 时可跳过）
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt

# 配置环境变量
copy .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY

# 启动
.\.venv\Scripts\python main.py
```

接口文档：`http://127.0.0.1:8000/docs`

## 启动前端（小程序）

```powershell
cd miniapp
npm install
npm run dev:weapp
```

构建校验：

```powershell
npm run build:weapp
```

## 后端测试（TDD）

```powershell
cd backend
.\.venv\Scripts\python -m pytest -q
```

当前结果：`6 passed`

## 说明

- 登录能力按确认不纳入 Phase 1。
- 数据库持久化按确认暂不接入。
- URL 解析与文件上传在输入页保留入口，当前显示 Phase 1 提示（未启用）。
- 错题本和学习记录按确认提供占位页。
