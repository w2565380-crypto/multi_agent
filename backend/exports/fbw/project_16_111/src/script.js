(function() {
    'use strict';

    // DOM 元素
    const expressionEl = document.getElementById('expression');
    const resultEl = document.getElementById('result');
    const buttonsContainer = document.querySelector('.buttons');

    // 状态
    let displayExpr = '';     // 显示的表达式（× 和 ÷）
    let calcExpr = '';       // 计算的表达式（* 和 /）
    let hasResult = false;   // 当前结果区是否显示计算结果

    // 更新 UI
    function updateDisplay() {
        expressionEl.textContent = displayExpr;
        // 结果区颜色：正数绿，负数红，0白色
        const resultText = resultEl.textContent;
        if (resultText === '0' || resultText === 'Error') {
            resultEl.style.color = '#fff';
        } else if (resultText.startsWith('-')) {
            resultEl.style.color = '#ff4444';
        } else {
            resultEl.style.color = '#44ff44';
        }
    }

    // 清空所有
    function clearAll() {
        displayExpr = '';
        calcExpr = '';
        hasResult = false;
        resultEl.textContent = '0';
        updateDisplay();
    }

    // 判断字符是否为运算符（内部用 * /）
    function isOperator(ch) {
        return ['+', '-', '*', '/'].includes(ch);
    }

    // 获取计算用的运算符
    function calcOp(op) {
        if (op === '×') return '*';
        if (op === '÷') return '/';
        return op;
    }

    // 显示用的运算符
    function displayOp(op) {
        if (op === '*') return '×';
        if (op === '/') return '÷';
        return op;
    }

    // 判断当前输入的数字是否已有小数点
    function lastNumberHasDecimal(expr) {
        // 从末尾向前提取最后一个数字（包括小数点）
        let i = expr.length - 1;
        while (i >= 0 && /[\d.]/.test(expr[i])) i--;
        const lastNum = expr.slice(i + 1);
        return lastNum.includes('.');
    }

    // 处理数字输入
    function handleDigit(digit) {
        if (hasResult) {
            // 有结果时，数字重置输入
            clearAll();
        }
        displayExpr += digit;
        calcExpr += digit;
        updateDisplay();
        // 结果区暂时置空
        resultEl.textContent = '';
    }

    // 处理小数点
    function handleDecimal() {
        if (hasResult) {
            clearAll();
            // 重置后输入 "0."
            displayExpr = '0.';
            calcExpr = '0.';
            updateDisplay();
            resultEl.textContent = '';
            return;
        }
        // 当前无结果，检查最后数字是否已有小数点
        if (lastNumberHasDecimal(calcExpr)) {
            return; // 已存在小数点，忽略
        }
        // 如果表达式为空或末尾是运算符，补 "0."
        if (calcExpr === '' || isOperator(calcExpr[calcExpr.length - 1])) {
            displayExpr += '0.';
            calcExpr += '0.';
        } else {
            displayExpr += '.';
            calcExpr += '.';
        }
        updateDisplay();
    }

    // 处理运算符
    function handleOperator(op) {
        const calcOpChar = calcOp(op);
        const displayOpChar = displayOp(calcOpChar);

        if (hasResult) {
            // 有结果时，将结果作为表达式开始
            const currentResult = resultEl.textContent;
            if (currentResult !== '0' && currentResult !== 'Error' && currentResult !== '') {
                displayExpr = currentResult;
                calcExpr = currentResult;
                hasResult = false;
                resultEl.textContent = '';
            } else {
                clearAll();
            }
        }

        // 如果表达式为空，忽略（不允许以运算符开始）
        if (calcExpr === '') {
            return;
        }

        // 如果末尾是运算符，替换
        const lastChar = calcExpr[calcExpr.length - 1];
        if (isOperator(lastChar)) {
            // 替换
            displayExpr = displayExpr.slice(0, -1) + displayOpChar;
            calcExpr = calcExpr.slice(0, -1) + calcOpChar;
        } else {
            displayExpr += displayOpChar;
            calcExpr += calcOpChar;
        }
        updateDisplay();
    }

    // 执行计算
    function calculate() {
        if (calcExpr === '') {
            resultEl.textContent = '0';
            hasResult = false;
            updateDisplay();
            return;
        }
        // 安全检查：只允许数字、运算符、小数点
        if (!/^[\d+\-*/.]+$/.test(calcExpr)) {
            resultEl.textContent = 'Error';
            hasResult = true;
            updateDisplay();
            return;
        }
        try {
            const result = new Function('return ' + calcExpr)();
            if (!isFinite(result)) {
                resultEl.textContent = 'Error';
            } else {
                // 处理浮点精度
                const formatted = parseFloat(result.toFixed(10)).toString();
                resultEl.textContent = formatted;
                hasResult = true;
            }
        } catch (e) {
            resultEl.textContent = 'Error';
            hasResult = true;
        }
        updateDisplay();
    }

    // 退格
    function backspace() {
        // 如果结果区有非零值或Error，重置
        if (resultEl.textContent !== '0' && resultEl.textContent !== '') {
            clearAll();
            return;
        }
        // 删除最后一个字符
        if (displayExpr.length > 0) {
            const lastChar = calcExpr[calcExpr.length - 1];
            displayExpr = displayExpr.slice(0, -1);
            calcExpr = calcExpr.slice(0, -1);
            // 如果表达式变空，结果区恢复0
            if (calcExpr === '') {
                resultEl.textContent = '0';
            }
            updateDisplay();
        }
    }

    // 主按钮处理函数
    function handleButton(value) {
        // 如果当前结果是Error，除C和⌫外，先清除再处理
        if (resultEl.textContent === 'Error' && value !== 'C' && value !== '⌫') {
            clearAll();
            // 继续执行下面的逻辑，此时状态已重置
        }

        if (value === 'C') {
            clearAll();
        } else if (value === '⌫') {
            backspace();
        } else if (value === '=') {
            calculate();
        } else if (value === '.') {
            handleDecimal();
        } else if (['+', '-', '×', '÷'].includes(value)) {
            handleOperator(value);
        } else if (/^\d$/.test(value)) {
            handleDigit(value);
        }
    }

    // 绑定按钮点击事件（事件委托）
    buttonsContainer.addEventListener('click', function(e) {
        const btn = e.target.closest('.btn');
        if (!btn) return;
        const value = btn.getAttribute('data-value');
        if (!value) return;
        handleButton(value);
    });

    // 键盘支持
    document.addEventListener('keydown', function(e) {
        const key = e.key;
        // 数字
        if (/^\d$/.test(key)) {
            e.preventDefault();
            handleButton(key);
            return;
        }
        // 运算符映射
        if (key === '+') {
            e.preventDefault();
            handleButton('+');
            return;
        }
        if (key === '-') {
            e.preventDefault();
            handleButton('-');
            return;
        }
        if (key === '*') {
            e.preventDefault();
            handleButton('×');
            return;
        }
        if (key === '/') {
            e.preventDefault();
            handleButton('÷');
            return;
        }
        // 小数点
        if (key === '.') {
            e.preventDefault();
            handleButton('.');
            return;
        }
        // 等号（Enter）
        if (key === 'Enter') {
            e.preventDefault();
            handleButton('=');
            return;
        }
        // 清除（Escape）
        if (key === 'Escape') {
            e.preventDefault();
            handleButton('C');
            return;
        }
        // 退格（Backspace）
        if (key === 'Backspace') {
            e.preventDefault();
            handleButton('⌫');
            return;
        }
    });

    // 初始化显示
    updateDisplay();
})();