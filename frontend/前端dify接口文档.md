那个能让前端通过 `<iframe>` 标签直接渲染并运行 AI 编写的 HTML 代码的接口 **已完美保留**，并且针对你们最新的数据库模型（通过 `project_id` 自动定位 `exports/project_{id}_{title}/src/index.html` 物理路径）进行了重构升级。

下面是为您整理的**最新完整版接口文档（v2.0）**。其中包含了**创建项目（触发PM）**、**人机审批**以及**获取网页预览 URL** 三个核心接口的详细说明，您可以直接分享给前端同学：

---

# 📝 AI多智能体模拟系统 - 后端 API 接口文档 (v2.0)

本文件定义了前端与后端交互的 API 规范，支持分阶段步进式调用（Human-in-the-Loop 审批机制）与账号隔离的物理产物预览。

*   **测试服务器 Base URL**: `http://8.160.185.36:8000`
*   **本地开发 Base URL**: `http://127.0.0.1:8000`

---

## 1. 创建项目并启动 PM 规划 (POST)

### 1.1 接口描述
前端用户输入项目标题、核心需求，点击提交。后端会在数据库创建项目（初始状态 `INITIAL` $\rightarrow$ 后台自动流转为 `PM_WORKING`），自动创建专属磁盘文件夹，并异步触发产品经理（PM）开始规划需求。

### 1.2 请求信息
*   **请求路径**: `/api/projects/create`
*   **请求方法**: `POST`
*   **查询参数 (Query)**:
    *   `user_id` (integer, 必填)：当前登录用户的用户 ID。

### 1.3 请求体 (Request Body - JSON)
```json
{
  "title": "网页计时器",
  "description": "我需要一个带倒计时和重置功能的网页计时器，界面要有科技感。"
}
```

### 1.4 返回参数 (Response - JSON)
*   **状态码: 200**
    ```json
    {
      "success": true,
      "message": "项目创建成功，产品经理开始规划需求...",
      "project_id": 1,
      "status": "INITIAL"
    }
    ```

---

## 2. 人机协作审批接口 (POST)

### 2.1 接口描述
当项目状态流转至 `PENDING_APPROVAL`（待审批）时，前端展示产品经理写好的 `PRD.md`。用户可在网页端点击**“同意开发”**或**“驳回修改”**。
*   **若同意**：状态转为 `RUNNING`，后台自动异步触发 Dev（编码）与 QA（测试、打包）工作流。
*   **若驳回**：状态转为 `RUNNING`，后台自动将驳回意见拼接回需求描述中，重新触发 PM 重写需求。

### 2.2 请求信息
*   **请求路径**: `/api/projects/{project_id}/approve`
*   **请求方法**: `POST`
*   **路径参数 (Path)**:
    *   `project_id` (integer, 必填)：项目 ID。
*   **查询参数 (Query)**:
    *   `approved` (boolean, 必填)：`true` 代表同意进入开发，`false` 代表驳回。
    *   `feedback` (string, 选填)：当 `approved` 为 `false` 时，填入具体的驳回修改意见。

### 2.3 返回参数 (Response - JSON)
*   **状态码: 200**
    ```json
    {
      "success": true,
      "message": "审批成功，流程已向后流转。"
    }
    ```

---

## 3. 获取项目网页成果预览 URL (GET)

### 3.1 接口描述
**（核心保留接口）** 前端直接调用此接口获取成果网页的访问 URL。前端直接用 `<iframe :src="preview_url">` 即可在 Vue 3 页面中实时渲染并运行 AI 编写的计算器/倒计时器网页。
该接口拥有**智能路径探测机制**，会自动判断 `index.html` 是否在 `src/` 下或直接在根目录下；若非 Web 项目（不包含任何 HTML 文件），会自动通知前端不进行 iframe 渲染。

### 3.2 请求信息
*   **请求路径**: `/api/projects/{project_id}/preview-url`
*   **请求方法**: `GET`
*   **路径参数 (Path)**:
    *   `project_id` (integer, 必填)：项目 ID。

### 3.3 返回参数 (Response - JSON)

#### 情况 A：检测为 Web 网页项目（Status Code: 200）
```json
{
  "success": true,
  "is_web_project": true,
  "preview_url": "http://8.160.185.36:8000/previews/project_1_网页计时器/src/index.html"
}
```

#### 情况 B：检测为纯 Python 或非网页项目（Status Code: 200）
```json
{
  "success": true,
  "is_web_project": false,
  "preview_url": null,
  "message": "此项目无 HTML 文件，仅支持查看源码。"
}
```

#### 异常情况：物理文件夹尚未生成（Status Code: 404）
```json
{
  "detail": "该项目物理文件夹尚未生成"
}
```

---

### 💡 前端渲染实现建议
前端同学在 Vue 3 中可以通过判断接口返回的 `is_web_project`：
*   若为 `true`：显示预览 Tap 页，直接在页面里挂载 `<iframe :src="preview_url" class="w-full h-[600px] border-none">`。
*   若为 `false`：自动将预览 Tap 置灰或隐藏，只显示“代码树及源码查看”面板。