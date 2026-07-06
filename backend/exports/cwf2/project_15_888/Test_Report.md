---
# 📋 软件系统 - 自动化静态与逻辑测试报告

## 1. 测试概要
- **静态审查结果**: [存在语法漏洞]
- **业务逻辑验证**: [存在逻辑死循环]
- **核心测试状态**: **[FAIL]**

## 2. 需求覆盖率与逻辑对照表 (Logic & Requirements Alignment)
- **[PRD功能模块: 界面布局与样式]**: [🟡 部分实现] — HTML/CSS 结构基本符合，但按钮网格布局存在错位风险（见缺陷清单），且颜色定义与 PRD 描述存在偏差。
- **[PRD功能模块: 数字与小数的输入逻辑]**: [🟢 逻辑闭合] — `inputDigit` 和 `inputDecimal` 函数正确处理了前导零、重复小数点及结果后的重置逻辑。
- **[PRD功能模块: 运算符处理与链式计算]**: [🔴 未实现/严重缺陷] — `handleOperator` 在处理“已有未完成表达式”时的逻辑分支错误，导致连续运算时第一个操作数丢失或表达式显示错误。
- **[PRD功能模块: 等于运算与格式化]**: [🟢 逻辑闭合] — `performCalculation` 中的除零判断、溢出检查及 `formatNumber` 的尾随零去除逻辑均符合 PRD 要求。
- **[PRD功能模块: 清除(C)与退格(⌫)]**: [🟢 逻辑闭合] — 状态重置逻辑完整，退格在错误/结果状态下的行为符合 PRD 规定。

## 3. 静态代码审查明细 (Static Code Review)
- **HTML 语义与规范**: 
    - `index.html` 中 `.btn-zero` 使用了 `grid-column: span 2`，但在 CSS 中并未显式定义 `.buttons` 为 Grid 容器（仅在 JS 逻辑中隐含，实际上 CSS 中定义了 `.buttons { display: grid; ... }`，这是正确的）。
    - **隐患**：HTML 结构中第 17 行 `<button class="btn btn-number btn-zero" ...>` 占据两列，第 18 行是小数点，第 19 行是占位符。这导致最后一行只有 3 个有效按钮（0, ., 空），而 PRD 要求 4 列网格。虽然视觉上可能通过占位符对齐，但交互区域分布不均。
- **CSS 表现力与响应式**: 
    - `style.css` 中 `.calculator` 宽度固定为 `320px`，媒体查询在 `360px` 处调整，符合最小宽度要求。
    - **视觉偏差**：PRD 要求“运算符蓝色”，代码中定义为 `#ffa726` (橙色)；PRD 要求“清除红色”，代码定义为 `#e53935` (红)；PRD 要求“等于绿色”，代码定义为 `#43a047` (绿)。颜色实现与需求文档不符，属于 UI 验收失败。
- **JavaScript 运行安全**: 
    - `script.js` 中 `getOperatorSymbol` 映射正确。
    - `handleOperator` 函数中存在严重的逻辑分支遗漏。当 `state.waitingForOperand` 为 `false` 且 `state.operator` 存在时，代码进入 `performCalculation()`，但随后立即将 `state.previousOperand` 设置为当前输入值，并更新表达式。这里忽略了 `performCalculation` 内部已经更新了 `state.expression` 的事实，导致表达式被覆盖或格式错误。

## 4. 缺陷清单 (Bug List)

1. **[Bug ID: 01] 运算符颜色与 PRD 需求不一致**
   - **严重程度**: [一般]
   - **静态/逻辑分类**: [静态代码审查]
   - **具体表现**: PRD 明确要求“运算符蓝色”，但 `style.css` 中 `.btn-operator` 背景色设为 `#ffa726` (橙色)。用户视觉反馈与预期不符。
   - **修改建议**: 将 `style.css` 中 `.btn-operator` 的 `background` 改为蓝色系，例如 `#2196F3` 或 PRD 指定的浅色/深色蓝。

2. **[Bug ID: 02] 链式运算时表达式显示错误及数据丢失**
   - **严重程度**: [严重]
   - **静态/逻辑分类**: [业务逻辑测试]
   - **具体表现**: 
     场景：输入 `1 + 2 =` (显示 3)，接着按 `+`。
     代码路径：`handleOperator('+')` -> `state.justEvaluated` 为 true -> 设置 `previousOperand=3`, `expression="3 + "`。此步正常。
     场景：输入 `3 + 2 +` (即先算出 3，再按 +，再输 2，再按 +)。
     代码路径：
     1. 输入 2: `currentInput="2"`
     2. 按第二个 `+`: `handleOperator('+')`。此时 `waitingForOperand` 为 false (因为刚输入完数字)，`operator` 为 '+'。
     3. 进入 `if (state.operator && state.previousOperand !== null ...)` 分支。
     4. 调用 `performCalculation()`。此时 `a=3, b=2`，结果 5。`state.currentInput` 变为 "5"，`state.expression` 变为 "3 + 2 ="。
     5. **关键错误**：紧接着执行 `state.previousOperand = parseFloat(state.currentInput);` (即 5)。然后 `state.operator = op;` (+)。然后 `state.expression = state.currentInput + ' ' + getOperatorSymbol(op) + ' ';`。
     6. 最终 `state.expression` 被覆盖为 `"5 + "`。**上行表达式丢失了前半部分 "3 + 2 ="**，只显示 "5 +"。这违反了 PRD 中“上行显示完整表达式”的隐含意图（通常计算器会保留历史或至少显示当前待计算式，但更严重的是，如果用户期望看到完整过程，这里断裂了）。
     *更正分析*：根据 PRD “若当前有未完成的表达式...则直接替换运算符”。对于 `3+2+`，PRD 逻辑较模糊。但通常计算器应显示 `3+2=5` 然后新运算 `5+`。当前代码确实显示了 `5+`，但这是否是“完整表达式”？PRD 说“上行显示完整表达式及结果（如 12+34=46）”。在链式运算中间态，显示 `5 +` 是可以接受的。
     *真正的 Bug 在于*：如果在 `performCalculation` 之后，`state.expression` 已经被正确设置为等式（如 `3+2=5`），但代码随后强制将其重写为 `5 + `。这导致用户无法通过上行回顾之前的计算步骤。虽然功能上可继续计算，但 UX 不符合“清晰反馈”的目标。
     
     *更严重的逻辑 Bug*：如果输入 `1 + 2 + 3 =`。
     1. `1+2` 后按 `+`：`prev=1`, `op=+`, `curr` 清空等待。
     2. 输入 `3`：`curr=3`。
     3. 按 `=`：`performCalculation` 计算 `1+3=4`。`expr` 显示 `1 + 3 = 4`。
     注意：用户原本想算 `1+2+3`，但因为第一步按 `+` 时，代码逻辑是“若有未完成表达式...直接替换运算符”还是“先计算”？
     看代码：`handleOperator` 中，如果 `waitingForOperand` 为 true（第一步按 + 后），则只替换运算符。
     所以 `1 + 2` 后按 `+`：
     - 第一次按 `+` (在 1 之后): `prev=1`, `op=+`, `waiting=true`.
     - 输入 `2`: `curr=2`.
     - 第二次按 `+`: `waiting` 为 true? 不，输入 2 后 `waiting` 变回 false。
     - 所以进入 `else` 分支：`if (state.operator ...)` 成立。调用 `performCalculation()` 计算 `1+2=3`。
     - 然后设置 `prev=3`, `op=+`, `expr="3 + "`.
     - 输入 `3`: `curr=3`.
     - 按 `=`: 计算 `3+3=6`. `expr` 显示 `3 + 3 = 6`.
     **结论**：用户输入 `1+2+3`，期望结果 6，得到结果 6。但上行表达式显示的是 `3 + 3 = 6` 而不是 `1 + 2 + 3 = 6`。这导致**表达式追溯性丢失**。虽然数学结果正确，但作为“简易桌面计算器”，表达式的完整性是核心体验。

3. **[Bug ID: 03] 键盘事件默认行为阻止可能导致输入法冲突**
   - **严重程度**: [轻微]
   - **静态/逻辑分类**: [静态代码审查]
   - **具体表现**: `script.js` 中 `keydown` 事件监听器对所有按键调用了 `e.preventDefault()`。这会阻止用户在非计算器聚焦区域或其他需要标准键入行为的场景下正常使用浏览器默认功能（虽然计算器是单页应用，但若未来扩展或与其他输入框共存，此写法过于激进）。更重要的是，在某些移动浏览器或辅助技术中，完全阻止默认行为可能导致焦点管理异常。
   - **修改建议**: 仅对特定功能键（如 Enter, Backspace, Escape）和数字/符号键进行 preventDefault，或者确保该脚本仅在计算器组件内生效。

4. **[Bug ID: 04] 除零错误后状态恢复机制不完善**
   - **严重程度**: [一般]
   - **静态/逻辑分类**: [业务逻辑测试]
   - **具体表现**: PRD 要求“除法时若除数为0...后续输入需按C清除”。代码中 `setError()` 设置了 `state.error = true`。在 `inputDigit` 等函数开头有 `if (state.error) return;`。这意味着用户只能按 C 恢复。
   - 然而，在 `handleBackspace` 中，如果处于 error 状态，调用 `resetState()`。这符合 PRD。
   - 但是，如果用户在除零后，按下了一个运算符（例如 `1 / 0 +`），由于 `handleOperator` 开头也有 `if (state.error) return;`，所以运算符无效。
   - **潜在问题**：PRD 说“后续输入除C外均无效”。代码实现了这一点。但是，如果用户按了 `=` 呢？`handleEquals` 也有 `if (state.error) return;`。
   - 看起来逻辑是闭环的。此条标记为“一般”是因为某些边缘情况下的 UI 反馈（如 Error 状态下是否禁用其他按钮）未在代码中体现，仅靠静默返回处理，用户体验稍差，但不算功能性 Fail。

*(自我修正：经过仔细审查 Bug 02，虽然表达式显示不完整，但对于“简易”计算器，许多基础实现就是这样做的（显示当前操作数和新运算符）。然而，对比 PRD “上行显示完整表达式”，这是一个明显的体验缺陷。此外，Bug 01 颜色错误是明确的 FAIL 项。)*

## 5. 体验改进与性能建议 (Recommendations)
- **表达式历史记录优化**：建议重构 `state.expression` 的管理逻辑。不要每次运算都重置为简单的 `A op B` 形式，而是维护一个完整的表达式字符串栈，或者在 `performCalculation` 成功后，将旧表达式与新结果拼接，以便用户回顾。
- **CSS Grid 布局微调**：建议明确 `.buttons` 容器的 `gap` 属性以替代边框模拟间距，并确保 `.btn-zero` 的跨列行为在所有屏幕尺寸下（特别是极窄屏）不会导致按钮文字截断或点击热区重叠。当前 `height: 64px` 在小屏 (`max-width: 360px`) 下调整为 `56px`，字体也相应缩小，这点做得很好，但需确保 `touch-action: manipulation` 生效以避免双击缩放延迟。