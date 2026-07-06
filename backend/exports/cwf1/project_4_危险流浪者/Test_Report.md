---
# 📋 软件系统 - 自动化静态与逻辑测试报告

## 1. 测试概要
- **静态审查结果**: [存在语法漏洞 / 资源引用冗余]
- **业务逻辑验证**: [部分实现 / 存在状态管理缺陷]
- **核心测试状态**: **[FAIL]**

## 2. 需求覆盖率与逻辑对照表 (Logic & Requirements Alignment)
- **[PRD功能模块: 计算器主界面布局]**: [🟡 部分实现] — 代码中同时存在 `index.html` 中的硬编码按钮和 `calculator.js` 中的动态生成逻辑，且 `index.html` 中存在重复的 `<div class="buttons">` 结构，导致 DOM 渲染混乱。
- **[PRD功能模块: 数字与小数点输入]**: [🟢 逻辑闭合] — `inputNumber` 和 `inputDecimal` 方法正确实现了替换、追加及小数点唯一性校验。
- **[PRD功能模块: 连续运算与运算符处理]**: [🔴 未完全实现/逻辑缺陷] — `inputOperator` 在 `waitingSecondOperand` 为 true 时调用了 `calculate(true)`，但 `calculate` 内部对 `keepState=true` 的处理逻辑未能正确更新 `firstOperand` 为最新计算结果，导致连续运算（如 `1+2+3`）时第二个操作数可能取错值或状态不一致。
- **[PRD功能模块: 清除与退格]**: [🟢 逻辑闭合] — `clear` 重置所有状态；`backspace` 正确处理了 `hasResult` 锁定及长度限制。
- **[PRD功能模块: 键盘支持]**: [🟢 逻辑闭合] — `keydown` 事件监听器覆盖了数字、运算符、Enter、Backspace、Escape 等关键键，并正确阻止了默认行为。

## 3. 静态代码审查明细 (Static Code Review)
- **HTML 语义与规范**: 
    - **严重问题**: `index.html` 中包含两个 `<div class="buttons">` 容器。第一个是静态写的（虽然注释说会被 JS 覆盖），第二个是空的并被 JS 初始化。这违反了单一数据源原则，且如果 JS 执行失败，用户将看到错误的静态布局。
    - **冗余代码**: `index.html` 中保留了大量关于布局调整的 HTML 注释和废弃的按钮结构，增加了维护成本。
    - **脚本加载顺序**: 脚本位于 body 底部，符合规范，但 `api.js` 和 `calculator.js` 依赖关系明确，无循环依赖。
- **CSS 表现力与响应式**: 
    - **媒体查询健全**: `style.css` 针对 480px 和 360px 设置了合理的断点，字体大小和内边距适配良好。
    - **触摸友好**: 按钮最小高度设为 44px (在小屏下)，符合移动端触控要求。
    - **视觉反馈**: `:active` 和 `:focus-visible` 伪类使用得当，提供了清晰的交互反馈。
- **JavaScript 运行安全**: 
    - **空指针风险**: `renderButtons` 中通过 `document.getElementById('buttons')` 获取容器，若 HTML 结构变更可能导致 null 引用，但在当前 `index.html` 结构下是安全的。
    - **异步处理**: `calculate` 函数是 `async` 的，但在 `handleAction` 中被同步调用。由于 `calculateRemote` 内部大部分时间走同步回退 (`calculateLocal`)，或者即使走 fetch 也是微任务，UI 不会阻塞，但 `updateDisplay` 在 `handleAction` 末尾立即执行，可能在异步计算完成前显示中间状态（虽然当前逻辑中 `calculate` 内部已更新 state，所以显示是正确的）。*注：此处逻辑看似没问题，因为 `calculate` 更新了 `this.state.display`，随后 `handleAction` 调用 `updateDisplay`，时序上是正确的。*

## 4. 缺陷清单 (Bug List)

1. **[Bug ID: 01] HTML 结构冗余与冲突**
   - **严重程度**: [严重]
   - **静态/逻辑分类**: [静态代码审查]
   - **具体表现**: `index.html` 文件中定义了两个 `<div class="buttons">`。第一个包含硬编码的按钮（其中第四行最后一个按钮是重复的 '+' 且被注释说明），第二个是空的 `<div class="buttons" id="buttons">`。`calculator.js` 的 `init()` 会清空 `id="buttons"` 的元素。这种双重定义极易导致开发者误解，且如果 JS 加载失败，页面显示的是错误的静态布局。此外，`index.html` 中第一个 `.buttons` 容器内的按钮没有 `id` 或特定标记，容易被误认为是最终 UI。
   - **修改建议**: 删除 `index.html` 中第一个 `<div class="buttons">` 及其所有内容，仅保留第二个空的 `<div class="buttons" id="buttons">`，并确保其注释清晰。

2. **[Bug ID: 02] 连续运算状态更新错误**
   - **严重程度**: [严重]
   - **静态/逻辑分类**: [业务逻辑测试]
   - **具体表现**: 在 `inputOperator` 方法中，当 `waitingSecondOperand` 为 `true` 时（即用户刚按过运算符，现在按另一个运算符），代码执行 `this.calculate(true)`。然而，查看 `calculate(keepState = true)` 的实现：
     ```javascript
     this.state.firstOperand = result.result; // 更新 firstOperand
     this.state.hasResult = !keepState;       // false
     this.state.waitingSecondOperand = keepState; // true
     if (!keepState) {
         this.state.operator = null;          // 不执行，operator 保持旧值
     }
     ```
     这里有一个微妙的问题：`calculate` 使用了传入的 `operator`（来自闭包或参数？注意 `calculate` 签名是 `async calculate(keepState = false)`，它从 `this.state.operator` 读取当前的运算符进行计算）。
     
     让我们推演 `1 + 2 + 3 =`：
     1. 输入 1, +, 2。状态: `first=1`, `op='+'`, `wait=true`, `display='2'`.
     2. 点击 `+`。进入 `inputOperator('+')`。`waitingSecondOperand` 为 true。
     3. 调用 `calculate(true)`。此时 `this.state.operator` 是 `'+'`。
     4. `calculate` 取出 `secondOperand` (2)，计算 `1+2=3`。
     5. `calculate` 设置 `firstOperand = 3`, `display = '3'`, `waitingSecondOperand = true`, `operator` 保持 `'+'` (因为 `!keepState` 为假)。
     6. 回到 `inputOperator`，接着执行 `this.state.operator = operator` (即新的 `'+'`)。
     7. 状态变为: `first=3`, `op='+'`, `wait=true`, `display='3'`.
     8. 输入 3。状态: `display='3'`, `wait=false` (在 `inputNumber` 中重置).
     9. 点击 `=`。调用 `calculate()`。`first=3`, `op='+'`, `second=3`. 结果 6。
     
     *修正分析*: 上述推演似乎能跑通。但是，如果在 `calculate(true)` 之后，`inputOperator` 中没有显式更新 `this.state.operator` 为新传入的 `operator`，则会出错。代码中有 `this.state.operator = operator;`。
     
     **真正的 Bug 在于浮点数精度与显示格式**: 
     在 `calculate` 中：
     ```javascript
     let resultStr = String(result.result);
     if (resultStr.length > 15) {
         resultStr = result.result.toExponential(10);
     }
     this.state.display = resultStr;
     ```
     如果结果是整数，`String(3)` 是 `"3"`。但如果结果是 `0.1 + 0.2 = 0.30000000000000004`。
     `api.js` 中的 `calculateLocal` 做了 `parseFloat(result.toPrecision(12))`。
     `0.1 + 0.2` -> `0.30000000000000004` -> `toPrecision(12)` -> `"0.300000000000"` -> `parseFloat` -> `0.3`。
     这部分处理得不错。
     
     **重新审视 Bug ID 02 的逻辑**: 
     如果在 `inputOperator` 中，`firstOperand` 是 `null` 怎么办？
     PRD 要求：“如果已有等待运算符...则先执行之前的运算”。
     代码中 `if (waitingSecondOperand && firstOperand !== null)` 检查了非空。
     
     **发现真正严重的逻辑 Bug**: 
     在 `inputOperator` 的最后一段：
     ```javascript
     if (waitingSecondOperand && firstOperand !== null) {
         this.calculate(true); 
         this.state.operator = operator;
         this.state.waitingSecondOperand = true;
         this.state.hasResult = false;
     }
     ```
     这里调用了 `this.calculate(true)`。注意 `calculate` 是 `async` 函数。
     `this.calculate(true)` 返回一个 Promise。
     紧接着执行 `this.state.operator = operator;`。
     **这是竞态条件！** 
     如果后端 API 启用（虽然当前注释掉了，但架构上允许），`calculate` 是异步的。在 `calculate` 完成之前，`this.state.operator` 已经被修改为新运算符，而 `this.state.firstOperand` 还是旧值（或者未更新）。
     即使当前使用本地计算（同步回退），`calculateLocal` 是同步的，但 `calculate` 函数本身是 `async`，这意味着它总是返回 Promise。
     **关键点**: `calculateRemote` 调用 `calculateLocal` 是直接返回结果吗？
     `return calculateLocal(...)` 在 async 函数中会包装成 resolved Promise。
     但是 `calculateLocal` 本身是同步的。
     然而，`calculate` 函数体中有 `await calculateRemote(...)`。
     即使 `calculateRemote` 立即 resolve，`await` 也会将其放入微任务队列。
     因此，`this.calculate(true)` 之后的语句会在计算完成**之前**执行。
     
     **后果**: 
     1. `inputOperator` 设置 `this.state.operator = newOperator`。
     2. 微任务触发 `calculate` 内部逻辑：读取 `this.state.operator` (此时已是新运算符！)。
     3. `calculate` 使用**新运算符**和旧的 `firstOperand` 以及当前的 `display` (第二个操作数) 进行计算。
     4. 计算使用的运算符是错误的（应该是上一个运算符，而不是刚刚输入的这个）。
     
     **示例**: `1 + 2 × =`
     1. 输入 1, +, 2。状态: `f=1, op='+', wait=T, disp='2'`.
     2. 点击 `×`。
     3. `inputOperator('*')`:
        - `waitingSecondOperand` is true.
        - Call `calculate(true)`. (Async, waits for promise).
        - Immediately sets `this.state.operator = '*'`.
        - Sets `this.state.waitingSecondOperand = true`.
     4. Microtask runs `calculate`:
        - Reads `this.state.operator` which is now `'*'`.
        - Calculates `1 * 2 = 2`.
        - Sets `display = '2'`, `firstOperand = 2`.
     5. 用户点击 `=`。
        - `calculate()`: `first=2`, `op='*'`, `second=?` (假设用户没输数字，直接等于，或者输了3).
        - 如果用户直接等于，`second` 是 `display` ('2'). `2 * 2 = 4`.
        - 正确逻辑应该是 `1 + 2 = 3`, then `3 × ...`? 不，通常是 `1+2` 暂存，按 `×` 变成 `3` (作为 first), 然后等待第二操作数。
        
     **结论**: 异步导致的竞态条件使得连续运算符切换时，计算使用的是**后一个**运算符而非**前一个**运算符，导致计算结果完全错误。

   - **修改建议**: 
     将 `calculate` 改为同步逻辑（因为当前核心计算是纯数学且无网络延迟，或确保在 `inputOperator` 中等待 Promise 解析后再更新状态）。
     最简单的修复是将 `calculate` 中的 `await` 移除（如果确定后端不可用或同步），或者在 `inputOperator` 中使用 `await this.calculate(true)` 并等待其完成后才更新 `this.state.operator`。鉴于这是一个前端演示，建议将 `calculate` 改造为同步函数，或者在 `inputOperator` 中处理同步逻辑。
     
     *推荐修复方案*: 重构 `calculate` 为同步函数（移除 `async/await`，直接调用 `calculateLocal`），因为 PRD 并未强制要求实时后端计算，且前端计算器通常要求即时响应。

3. **[Bug ID: 03] 除零错误显示不一致**
   - **严重程度**: [一般]
   - **静态/逻辑分类**: [业务逻辑测试]
   - **具体表现**: 
     - 在 `api.js` 的 `calculateLocal` 中，除零返回 `{ error: 'Division by zero' }`。
     - 在 `calculator.js` 的 `calculate` 中，判断 `result.error === 'Division by zero'` 时显示 `'Error'`。
     - 在 `calculator.py` (后端) 中，抛出 `ValueError("Division by zero")`，FastAPI 捕获后返回 `error: "Division by zero"`。
     - 如果未来启用后端，前端收到的 error 字符串是 `"Division by zero"`，前端代码能正确映射为 `"Error"`。
     - 但是，`api.js` 中还有一处：`return { error: 'Infinity' };` 和 `return { error: 'NaN' };`。
     - 在 `calculator.js` 中：`this.state.display = result.error === 'Division by zero' ? 'Error' : result.error;`。
     - 这意味着如果是 Infinity，显示 "Infinity"；如果是 NaN，显示 "NaN"。这符合 PRD 要求。
     - **潜在问题**: 如果 `calculateRemote` 发生网络异常，catch 块调用 `calculateLocal`。如果 `calculateLocal` 也失败（极不可能），则返回 undefined？不，switch default 返回 `{ error: 'Invalid operator' }`。
     - 此 Bug 实际较轻微，主要在于代码路径分散。

## 5. 体验改进与性能建议 (Recommendations)
- **移除异步开销**: 既然核心计算逻辑 `calculateLocal` 是同步且确定的，建议将 `Calculator.prototype.calculate` 改为普通函数（移除 `async`），并直接调用 `calculateLocal`。这样可以消除 `inputOperator` 中的竞态条件，简化代码逻辑，并提高响应速度（尽管差异微小，但逻辑更严谨）。
- **清理 HTML 结构**: 彻底清理 `index.html` 中的冗余按钮和注释，只保留干净的容器占位符，避免误导后续维护者。

---