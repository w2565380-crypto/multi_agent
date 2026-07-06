(function() {
    'use strict';

    class Calculator {
        constructor() {
            this.displayValue = '0';
            this.firstOperand = null;
            this.operator = null;
            this.waitingForSecondOperand = false;
            this.maxDigits = 15;
        }

        // 重置所有状态
        clear() {
            this.displayValue = '0';
            this.firstOperand = null;
            this.operator = null;
            this.waitingForSecondOperand = false;
        }

        // 删除最后一位
        backspace() {
            if (this.waitingForSecondOperand) return; // 如果等待第二个操作数，退格无效（或清空当前输入）——按设计如果等待中退格可清空当前输入
            // 改进：若正在输入第二个操作数，退格应该删除当前显示的数字
            if (this.displayValue.length === 1 || (this.displayValue.length === 2 && this.displayValue.startsWith('-'))) {
                this.displayValue = '0';
            } else {
                this.displayValue = this.displayValue.slice(0, -1);
            }
        }

        // 输入数字
        inputDigit(digit) {
            if (this.waitingForSecondOperand) {
                this.displayValue = digit;
                this.waitingForSecondOperand = false;
            } else {
                if (this.displayValue === '0' && digit !== '.') {
                    this.displayValue = digit;
                } else {
                    // 限制显示长度（不包括符号和小数点）
                    if (this.displayValue.replace(/[^\d]/g, '').length < this.maxDigits) {
                        this.displayValue += digit;
                    }
                }
            }
        }

        // 输入小数点
        inputDecimal() {
            if (this.waitingForSecondOperand) {
                this.displayValue = '0.';
                this.waitingForSecondOperand = false;
                return;
            }
            // 如果当前显示已经包含小数点，忽略
            if (this.displayValue.includes('.')) return;
            this.displayValue += '.';
        }

        // 处理运算符
        handleOperator(nextOperator) {
            const currentValue = parseFloat(this.displayValue);

            // 如果已经有操作符，且没有等待第二操作数，先执行计算
            if (this.operator && !this.waitingForSecondOperand) {
                const result = this.compute(this.firstOperand, currentValue, this.operator);
                this.displayValue = `${result}`;
                this.firstOperand = result;
            } else {
                // 第一次输入操作符，或刚按过等号后继续运算
                this.firstOperand = currentValue;
            }

            this.operator = nextOperator;
            this.waitingForSecondOperand = true;
        }

        // 计算
        compute(first, second, op) {
            if (op === '+') return first + second;
            if (op === '-') return first - second;
            if (op === '*') return first * second;
            if (op === '/') {
                if (second === 0) {
                    return 'Error';
                }
                return first / second;
            }
            return second;
        }

        // 执行等于
        equals() {
            // 如果没有操作符，直接返回当前值
            if (!this.operator) {
                this.firstOperand = parseFloat(this.displayValue);
                return;
            }

            const currentValue = parseFloat(this.displayValue);
            const result = this.compute(this.firstOperand, currentValue, this.operator);

            this.displayValue = `${result}`;
            this.firstOperand = result;
            this.operator = null;
            this.waitingForSecondOperand = true; // 允许继续基于结果运算
        }

        // 格式化显示（科学计数法、浮点数精度）
        formatDisplay(value) {
            if (value === 'Error') return 'Error';
            let num = parseFloat(value);
            if (isNaN(num)) return '0';

            // 检查是否需要科学计数法（整数位超过15位）
            const absNum = Math.abs(num);
            const intPartLength = Math.floor(absNum).toString().length;
            if (intPartLength > this.maxDigits) {
                return num.toExponential(10);
            }

            // 浮点数保留最多10位小数，去除多余尾部0
            if (Number.isInteger(num)) {
                return num.toString();
            } else {
                // 限制小数位数防止浮点误差
                let fixed = num.toFixed(10);
                // 去除尾随0和可能的小数点
                fixed = parseFloat(fixed).toString();
                return fixed;
            }
        }

        // 获取要显示的内容
        getDisplayText() {
            return this.formatDisplay(this.displayValue);
        }
    }

    // UI 绑定
    const displayEl = document.getElementById('display');
    const buttons = document.querySelectorAll('.btn:not(.placeholder)');
    const calculator = new Calculator();

    function updateDisplay() {
        displayEl.textContent = calculator.getDisplayText();
    }

    function handleButtonClick(e) {
        const button = e.currentTarget;
        const action = button.dataset.action;

        if (!action) return;

        // 数字按钮
        if (/^\d$/.test(action)) {
            calculator.inputDigit(action);
            updateDisplay();
            return;
        }

        // 小数点
        if (action === 'decimal') {
            calculator.inputDecimal();
            updateDisplay();
            return;
        }

        // 清空
        if (action === 'clear') {
            calculator.clear();
            updateDisplay();
            return;
        }

        // 退格
        if (action === 'backspace') {
            calculator.backspace();
            updateDisplay();
            return;
        }

        // 运算符
        const operatorMap = {
            'add': '+',
            'subtract': '-',
            'multiply': '*',
            'divide': '/'
        };
        if (operatorMap[action]) {
            calculator.handleOperator(operatorMap[action]);
            updateDisplay();
            return;
        }

        // 等于
        if (action === 'equals') {
            calculator.equals();
            updateDisplay();
            return;
        }
    }

    // 绑定事件
    buttons.forEach(btn => {
        btn.addEventListener('click', handleButtonClick);
    });

    // 键盘支持（可选，增加体验）
    document.addEventListener('keydown', (e) => {
        const key = e.key;
        let btn = null;
        if (/^\d$/.test(key)) {
            btn = document.querySelector(`[data-action="${key}"]`);
        } else if (key === '.') {
            btn = document.querySelector('[data-action="decimal"]');
        } else if (key === 'Backspace') {
            btn = document.querySelector('[data-action="backspace"]');
        } else if (key === 'Enter' || key === '=') {
            btn = document.querySelector('[data-action="equals"]');
        } else if (key === 'Escape' || key === 'c' || key === 'C') {
            btn = document.querySelector('[data-action="clear"]');
        } else if (key === '+') {
            btn = document.querySelector('[data-action="add"]');
        } else if (key === '-') {
            btn = document.querySelector('[data-action="subtract"]');
        } else if (key === '*') {
            btn = document.querySelector('[data-action="multiply"]');
        } else if (key === '/') {
            btn = document.querySelector('[data-action="divide"]');
        }
        if (btn) {
            e.preventDefault();
            btn.click();
            btn.classList.add('active');
            setTimeout(() => btn.classList.remove('active'), 100);
        }
    });

    // 初始显示
    updateDisplay();
})();