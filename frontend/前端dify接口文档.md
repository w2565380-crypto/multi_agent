# 🌈 AI多智能体模拟系统 - 前后端联调 API 接口文档 (v3.0 完备版)
---

## 📂 接口体系全局一览

```text
├── 1. 项目生命周期与控制
│   ├── POST /api/projects/create            # 1. 创建项目并异步触发 PM 规划
│   ├── POST /api/projects/{id}/approve      # 2. 人机交互审批 (同意/驳回)
│   ├── POST /api/projects/{id}/revise       # 3. 提交修改建议，重新迭代重构代码
│   └── DELETE /api/projects/{id}            # 4. 一键彻底物理抹除项目
│
├── 2. 项目列表与状态恢复 (刷新防丢失)
│   ├── GET  /api/projects/                  # 5. 获取指定用户名下的所有项目列表
│   └── GET  /api/projects/{id}              # 6. 获取单个项目最新的基础信息 (高频状态轮询)
│
└── 3. 智能体物理成果精准调取 (支持 Markdown 渲染 & 代码树生成)
    ├── GET  /api/projects/{id}/prd          # 7. 【PM成果】读取需求规格说明书文本
    ├── GET  /api/projects/{id}/qa-report    # 8. 【QA成果】读取静态代码审查报告文本
    ├── GET  /api/projects/{id}/code-files   # 9. 【Dev成果】读取程序员生成的所有源码文件列表与正文
    ├── GET  /api/projects/{id}/preview-url  # 10.【成果运行】自适应探测并生成 HTML 网页预览链接
    └── GET  /api/projects/{id}/download     # 11.【物理交付】一键触发 ZIP 压缩包浏览器物理下载
```

---

## 一、 项目生命周期与流转控制

### 1. 创建项目并启动仿真 (POST)
*   **路径**: `/api/projects/create`
*   **方法**: `POST`
*   **Query 参数**:
    *   `user_id` (integer, 必填): 客户的老板账号 ID（例如 `5`）。
*   **Body 参数 (JSON)**:
    ```json
    {
      "title": "网页计时器",
      "description": "我需要一个带倒计时和重置功能的网页计时器，界面要有科技感。"
    }
    ```
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "message": "项目创建成功，产品经理开始规划需求...",
      "project_id": 16,
      "status": "INITIAL"
    }
    ```
*   **流转反应**: 后台将异步拉起产品经理（PM）工作流。前端应展示“产品经理正在规划中”状态，并启动对 **`接口 6`** 的高频轮询，直到状态变更为 `PENDING_APPROVAL`。

---

### 2. 人机协作审批控制 (POST)
*   **路径**: `/api/projects/{project_id}/approve`
*   **方法**: `POST`
*   **Query 参数**:
    *   `approved` (boolean, 必填): `true` 代表批准进入开发；`false` 代表不满意驳回。
    *   `feedback` (string, 选填): 当 `approved` 为 `false` 时，必填此字段传入修改意见。
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "message": "审批指令已下达，流程开始流转。"
    }
    ```
*   **流转反应**: 
    *   若批准，后台任务（Dev $\rightarrow$ QA $\rightarrow$ 打包）会依次自动执行。
    *   若驳回，后台会将修改反馈拼接入需求，重新交由 PM 规划。前端重新展示加载动画。

---

### 3. 代码不满意打回重新修改 (POST)
*   **路径**: `/api/projects/{project_id}/revise`
*   **方法**: `POST`
*   **Query 参数**:
    *   `feedback` (string, 必填): 老板给程序员提出的具体代码调整建议。
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "message": "代码重构指令已下达，程序员正在根据您的建议修改代码，请耐心等待并轮询状态..."
    }
    ```
*   **流转反应**: 后端会在物理内存中自动合成“原PRD + 历史QA报错 + 本次修改意见”的大文本，拉起 Dev 重构代码。完成后自动触发 QA 重新测试和 ZIP 打包。前端应展示“程序员正在重构中”并重新对 **`接口 6`** 进行轮询直到状态变回 `COMPLETED`。

---

### 4. 一键彻底物理删除项目 (DELETE)
*   **路径**: `/api/projects/{project_id}`
*   **方法**: `DELETE`
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "message": "项目 ID: 16 及其本地源码、打包 ZIP、关联 AI 记录已全部成功安全彻底清理！"
    }
    ```
*   **流转反应**: 接口会自动删除项目的数据库记录，联级清理 `project_agents` 记录，并强行物理擦除服务器硬盘上的项目源码目录以及 ZIP 包。

---

## 二、 历史恢复与看板状态管理

### 5. 获取用户的项目历史列表 (GET)
*   **路径**: `/api/projects/`
*   **方法**: `GET`
*   **Query 参数**:
    *   `user_id` (integer, 必填): 用户 ID。
*   **成功返回示例 (200)**:
    ```json
    [
      {
        "id": 16,
        "title": "网页计时器",
        "status": "PENDING_APPROVAL",
        "zip_path": null
      },
      {
        "id": 15,
        "title": "888",
        "status": "COMPLETED",
        "zip_path": "exports/cwf2/project_15.zip"
      }
    ]
    ```

---

### 6. 获取单个项目最新状态 (GET)
*   **路径**: `/api/projects/{project_id}`
*   **方法**: `GET`
*   **成功返回示例 (200)**:
    ```json
    {
      "id": 16,
      "user_id": 5,
      "title": "网页计时器",
      "description": "我需要一个带倒计时和重置功能的网页计时器，界面要有科技感。",
      "status": "RUNNING",
      "zip_path": null
    }
    ```
*   **状态值对照表**:
    *   `INITIAL`：初始状态。
    *   `RUNNING`：后台工作流运行中（无论是 PM、Dev 还是 QA 在干活都属于此状态）。
    *   `PENDING_APPROVAL`：产品经理干完活了，PRD 已生成，强制挂起等待用户点击通过或驳回。
    *   `COMPLETED`：测试通过且打包压缩完成。
    *   `FAILED`：智能体执行错误或超时失败。

---

## 三、 智能体生成成果读取与展示

### 7. 【PM成果】获取 PRD 说明书 Markdown (GET)
*   **路径**: `/api/projects/{project_id}/prd`
*   **方法**: `GET`
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "project_id": 16,
      "prd_content": "# 1. 项目概述\n- **项目名称**: 网页计时器\n## 2. 核心功能需求\n- 包含重置按钮...\n"
    }
    ```

---

### 8. 【QA成果】获取 QA 测试报告 Markdown (GET)
*   **路径**: `/api/projects/{project_id}/qa-report`
*   **方法**: `GET`
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "project_id": 16,
      "qa_report": "---# 📋 软件系统 - 自动化测试报告\n## 1. 测试概要\n- 静态代码审查结果: [PASS]\n..."
    }
    ```

---

### 9. 【Dev成果】获取源码文件树列表与正文 (GET)
*   **路径**: `/api/projects/{project_id}/code-files`
*   **方法**: `GET`
*   **成功返回示例 (200)**:
    ```json
    {
      "success": true,
      "project_id": 16,
      "files": [
        {
          "file_name": "index.html",
          "file_path": "index.html",
          "code_content": "<!DOCTYPE html>\n<html>\n..."
        },
        {
          "file_name": "style.css",
          "file_path": "style.css",
          "code_content": "body { background: #1e1e1e; }"
        },
        {
          "file_name": "script.js",
          "file_path": "script.js",
          "code_content": "class Timer { ... }"
        }
      ]
    }
    ```

---

### 10. 【成果运行】获取网页的预览渲染地址 (GET)
*   **路径**: `/api/projects/{project_id}/preview-url`
*   **方法**: `GET`
*   **成功返回示例 - 情况 A (网页项目, 200)**:
    ```json
    {
      "success": true,
      "is_web_project": true,
      "preview_url": "http://8.160.185.36:8000/previews/cwf2/project_16_网页计时器/src/index.html"
    }
    ```
*   **成功返回示例 - 情况 B (纯代码无 HTML 项目, 200)**:
    ```json
    {
      "success": true,
      "is_web_project": false,
      "preview_url": null,
      "message": "此项目无 HTML 文件，仅支持查看源码。"
    }
    ```
*   **前端处理方案**:
    如果 `is_web_project` 字段返回 `true`，前端即可点亮“成果预览”Tab，并将 `preview_url` 塞入原生的 `<iframe>` 标签中，用户即可立即在 Vue 网页中操纵生成的计算器/计时器应用！

---

### 11. 【物理交付】一键下载成果 ZIP 包 (GET)
*   **路径**: `/api/projects/{project_id}/download`
*   **方法**: `GET`
*   **处理机制**: 直接返回二进制二进制数据流。
*   **浏览器效果**: 触发原生的下载任务，下载到本地硬盘。
*   **解压后结构**:
    ```text
    Project_16_网页计时器.zip
    ├── PRD.md                   # 产品经理需求规格书
    ├── Test_Report.md           # 测试工程师静态代码审查报告
    └── src/                     # 源码文件夹
        ├── index.html
        ├── style.css
        └── script.js
    ```

### 12. 获取指定用户下特定类型的历史文档汇总 (GET)
*  请求路径: /api/users/{user_id}/files
*  请求方法: GET
*  路径参数 (Path):
*  user_id (integer, 必填)：当前登录用户的 ID。
*  查询参数 (Query):
*  type (string, 必填)：要查询的产物类型。只支持 pm（查询所有 PRD 需求文档）或 qa（查询所有 QA 测试报告），不区分大小写。
*  成功返回示例 (Response - JSON):
  ```json
  {
    "success": true,
    "files": [
      {
        "project_id": 14,
        "project_title": "网页计时器",
        "file_name": "PRD.md",
        "content": "# 1. 项目概述\n- **项目名称**: 网页计时器..."
      },
      {
        "project_id": 15,
        "project_title": "计算器项目",
        "file_name": "PRD.md",
        "content": "# 1. 项目概述\n- **项目名称**: 计算器项目..."
      }
    ]
  }