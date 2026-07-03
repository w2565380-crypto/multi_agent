/**
 * calculator.js - 计算器前端状态管理与交互逻辑
 */

class Calculator {
    constructor() {
        // 状态对象
        this.state = {
            display: '0',
            firstOperand: null,
            operator: null,
            waitingSecondOperand: false,
            hasResult: false,
        };

        // DOM 元素
        this.displayEl = document.getElementById('display');
        this.buttonsContainer = document.getElementById('buttons');
    }

    /**
     * 初始化计算器：生成按钮、绑定事件、键盘支持
     */
    init() {
        this.renderButtons();
        this.bindEvents();
        this.updateDisplay();
    }

    /**
     * 动态生成按钮网格
     */
    renderButtons() {
        // 按钮配置： [text, action, value?, extraClass?]
        const buttonConfigs = [
            // 第一行
            { text: 'C', action: 'clear', extraClass: 'btn-function' },
            { text: '←', action: 'backspace', extraClass: 'btn-function' },
            { text: '÷', action: 'operator', value: '/', extraClass: 'btn-operator' },
            { text: '×', action: 'operator', value: '*', extraClass: 'btn-operator' },
            // 第二行
            { text: '7', action: 'number', value: '7', extraClass: 'btn-number' },
            { text: '8', action: 'number', value: '8', extraClass: 'btn-number' },
            { text: '9', action: 'number', value: '9', extraClass: 'btn-number' },
            { text: '−', action: 'operator', value: '-', extraClass: 'btn-operator' },
            // 第三行
            { text: '4', action: 'number', value: '4', extraClass: 'btn-number' },
            { text: '5', action: 'number', value: '5', extraClass: 'btn-number' },
            { text: '6', action: 'number', value: '6', extraClass: 'btn-number' },
            { text: '+', action: 'operator', value: '+', extraClass: 'btn-operator' },
            // 第四行
            { text: '1', action: 'number', value: '1', extraClass: 'btn-number' },
            { text: '2', action: 'number', value: '2', extraClass: 'btn-number' },
            { text: '3', action: 'number', value: '3', extraClass: 'btn-number' },
            { text: '=', action: 'equals', extraClass: 'btn-equals' },
            // 第五行
            { text: '0', action: 'number', value: '0', extraClass: 'btn-number btn-zero' },
            { text: '.', action: 'decimal', value: '.', extraClass: 'btn-number' },
            // 注意：第五行只有三个按钮，但网格为4列，需要占位
            // 我们通过CSS grid-column 让 0 占两列，. 占一列，= 占一列
            // 但 = 已在第四行，这里不再重复。所以第五行只有 0 和 . 两个按钮？
            // 标准布局需要第五行有 0 (跨2列), . (1列), = (1列) 但 = 已存在第四行。
            // 修正：将第四行的 = 移到第五行，第四行变成 1,2,3,+ ；第五行：0 (跨2列), ., =
            // 重新调整配置：
        ];

        // 重新定义更合理的布局
        const layout = [
            // 行1
            { text: 'C', action: 'clear', extraClass: 'btn-function' },
            { text: '←', action: 'backspace', extraClass: 'btn-function' },
            { text: '÷', action: 'operator', value: '/', extraClass: 'btn-operator' },
            { text: '×', action: 'operator', value: '*', extraClass: 'btn-operator' },
            // 行2
            { text: '7', action: 'number', value: '7', extraClass: 'btn-number' },
            { text: '8', action: 'number', value: '8', extraClass: 'btn-number' },
            { text: '9', action: 'number', value: '9', extraClass: 'btn-number' },
            { text: '−', action: 'operator', value: '-', extraClass: 'btn-operator' },
            // 行3
            { text: '4', action: 'number', value: '4', extraClass: 'btn-number' },
            { text: '5', action: 'number', value: '5', extraClass: 'btn-number' },
            { text: '6', action: 'number', value: '6', extraClass: 'btn-number' },
            { text: '+', action: 'operator', value: '+', extraClass: 'btn-operator' },
            // 行4
            { text: '1', action: 'number', value: '1', extraClass: 'btn-number' },
            { text: '2', action: 'number', value: '2', extraClass: 'btn-number' },
            { text: '3', action: 'number', value: '3', extraClass: 'btn-number' },
            { text: '+', action: 'operator', value: '+', extraClass: 'btn-operator' }, // 占位，实际隐藏或不用
            // 行5
            { text: '0', action: 'number', value: '0', extraClass: 'btn-number btn-zero' },
            { text: '.', action: 'decimal', value: '.', extraClass: 'btn-number' },
            { text: '=', action: 'equals', extraClass: 'btn-equals' },
        ];

        // 清空容器
        this.buttonsContainer.innerHTML = '';

        // 创建按钮并添加到容器
        layout.forEach((config, index) => {
            const btn = document.createElement('button');
            btn.textContent = config.text;
            btn.className = `btn ${config.extraClass || ''}`;
            btn.dataset.action = config.action;
            if (config.value !== undefined) {
                btn.dataset.value = config.value;
            }
            // 对于第五行的 =，它应该出现在第四列，但我们的布局中第五行只有3个按钮（0, ., =）
            // 为了让 = 出现在最右边，我们给 . 按钮添加样式使其占据一列，= 占据一列，0 占据两列
            if (config.text === '0') {
                btn.style.gridColumn = 'span 2';
            }
            if (config.text === '.') {
                btn.style.gridColumn = 'span 1';
            }
            if (config.text === '=') {
                btn.style.gridColumn = 'span 1';
            }
            // 对于第四行的最后一个 +，我们将其隐藏，因为布局中不需要两个 +
            if (index === 15) { // 第四行最后一个
                btn.style.display = 'none';
            }
            this.buttonsContainer.appendChild(btn);
        });
    }

    /**
     * 绑定事件监听
     */
    bindEvents() {
        // 按钮点击事件（事件委托）
        this.buttonsContainer.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn');
            if (!btn) return;
            const action = btn.dataset.action;
            const value = btn.dataset.value;
            this.handleAction(action, value);
        });

        // 键盘事件
        document.addEventListener('keydown', (e) => {
            const key = e.key;
            // 数字键
            if (/^[0-9]$/.test(key)) {
                e.preventDefault();
                this.handleAction('number', key);
            }
            // 运算符
            else if (key === '+') {
                e.preventDefault();
                this.handleAction('operator', '+');
            } else if (key === '-') {
                e.preventDefault();
                this.handleAction('operator', '-');
            } else if (key === '*') {
                e.preventDefault();
                this.handleAction('operator', '*');
            } else if (key === '/') {
                e.preventDefault();
                this.handleAction('operator', '/');
            }
            // 小数点
            else if (key === '.') {
                e.preventDefault();
                this.handleAction('decimal', '.');
            }
            // 等号 / 回车
            else if (key === 'Enter' || key === '=') {
                e.preventDefault();
                this.handleAction('equals');
            }
            // 退格
            else if (key === 'Backspace') {
                e.preventDefault();
                this.handleAction('backspace');
            }
            // 清除
            else if (key === 'Escape' || key === 'c' || key === 'C') {
                e.preventDefault();
                this.handleAction('clear');
            }
        });
    }

    /**
     * 处理用户动作
     * @param {string} action - 'number', 'decimal', 'operator', 'equals', 'clear', 'backspace'
     * @param {string} [value] - 数字或运算符的值
     */
    handleAction(action, value) {
        switch (action) {
            case 'number':
                this.inputNumber(value);
                break;
            case 'decimal':
                this.inputDecimal();
                break;
            case 'operator':
                this.inputOperator(value);
                break;
            case 'equals':
                this.calculate();
                break;
            case 'clear':
                this.clear();
                break;
            case 'backspace':
                this.backspace();
                break;
            default:
                break;
        }
        this.updateDisplay();
    }

    /**
     * 输入数字
     * @param {string} digit
     */
    inputNumber(digit) {
        const { display, waitingSecondOperand, hasResult } = this.state;

        // 如果刚得到结果，开始新输入
        if (hasResult) {
            this.state.display = digit;
            this.state.hasResult = false;
            this.state.firstOperand = null;
            this.state.operator = null;
            this.state.waitingSecondOperand = false;
            return;
        }

        // 如果正在等待第二操作数，替换显示
        if (waitingSecondOperand) {
            this.state.display = digit;
            this.state.waitingSecondOperand = false;
            return;
        }

        // 正常追加，但限制最大15位
        if (display.length >= 15) return;

        // 如果当前显示为 '0'，替换
        if (display === '0') {
            this.state.display = digit;
        } else {
            this.state.display += digit;
        }
    }

    /**
     * 输入小数点
     */
    inputDecimal() {
        const { display, waitingSecondOperand, hasResult } = this.state;

        // 如果刚得到结果，重置
        if (hasResult) {
            this.state.display = '0.';
            this.state.hasResult = false;
            this.state.firstOperand = null;
            this.state.operator = null;
            this.state.waitingSecondOperand = false;
            return;
        }

        // 如果正在等待第二操作数，重置显示为 "0."
        if (waitingSecondOperand) {
            this.state.display = '0.';
            this.state.waitingSecondOperand = false;
            return;
        }

        // 检查当前数字是否已包含小数点
        if (display.includes('.')) return;

        // 追加小数点
        this.state.display += '.';
    }

    /**
     * 输入运算符
     * @param {string} operator
     */
    inputOperator(operator) {
        const { firstOperand, waitingSecondOperand, hasResult } = this.state;
        const currentDisplay = parseFloat(this.state.display);

        // 如果刚得到结果，将结果作为 firstOperand
        if (hasResult) {
            this.state.firstOperand = currentDisplay;
            this.state.operator = operator;
            this.state.waitingSecondOperand = true;
            this.state.hasResult = false;
            return;
        }

        // 如果没有等待运算符，记录第一个操作数
        if (!waitingSecondOperand) {
            this.state.firstOperand = currentDisplay;
            this.state.operator = operator;
            this.state.waitingSecondOperand = true;
            return;
        }

        // 如果已有等待运算符，先执行之前的运算
        if (waitingSecondOperand && firstOperand !== null) {
            this.calculate(true); // 计算但不重置等待状态
            // 计算结果后，更新运算符
            this.state.operator = operator;
            this.state.waitingSecondOperand = true;
            this.state.hasResult = false;
        }
    }

    /**
     * 执行计算
     * @param {boolean} [keepState=false] - 是否保留等待状态（连续运算符时使用）
     */
    async calculate(keepState = false) {
        const { firstOperand, operator, waitingSecondOperand, display } = this.state;

        // 如果没有等待运算符，忽略
        if (!waitingSecondOperand || operator === null) return;

        const secondOperand = parseFloat(display);
        if (isNaN(secondOperand)) return;

        // 调用 API 或本地计算
        const result = await calculateRemote(firstOperand, secondOperand, operator);

        if (result.error) {
            // 显示错误
            this.state.display = result.error === 'Division by zero' ? 'Error' : result.error;
            this.state.firstOperand = null;
            this.state.operator = null;
            this.state.waitingSecondOperand = false;
            this.state.hasResult = true;
            return;
        }

        // 格式化结果，限制显示长度
        let resultStr = String(result.result);
        if (resultStr.length > 15) {
            resultStr = result.result.toExponential(10);
        }

        this.state.display = resultStr;
        this.state.firstOperand = result.result;
        this.state.hasResult = !keepState;
        this.state.waitingSecondOperand = keepState;
        if (!keepState) {
            this.state.operator = null;
        }
    }

    /**
     * 清除所有状态
     */
    clear() {
        this.state.display = '0';
        this.state.firstOperand = null;
        this.state.operator = null;
        this.state.waitingSecondOperand = false;
        this.state.hasResult = false;
    }

    /**
     * 退格
     */
    backspace() {
        const { display, hasResult } = this.state;

        // 如果刚得到结果或显示错误，忽略
        if (hasResult || display === 'Error' || display === 'Infinity' || display === 'NaN') return;

        // 如果显示长度为1或为 "0"，重置为 "0"
        if (display.length <= 1 || display === '0') {
            this.state.display = '0';
            return;
        }

        // 删除最后一个字符
        this.state.display = display.slice(0, -1);
        if (this.state.display === '' || this.state.display === '-') {
            this.state.display = '0';
        }
    }

    /**
     * 更新显示屏幕
     */
    updateDisplay() {
        if (this.displayEl) {
            this.displayEl.textContent = this.state.display;
        }
    }
}

// 暴露 Calculator 类（如果在模块环境中使用）
// export default Calculator;