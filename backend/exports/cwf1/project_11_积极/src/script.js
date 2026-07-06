// DOM Elements
const display = document.getElementById('display');

// State
let currentInput = '0';
let previousValue = null;
let operator = null;
let waitingForSecondNumber = false;
let justEvaluated = false;

// Helper functions
function updateDisplay(value) {
    display.textContent = value;
}

function handleNumber(value) {
    if (waitingForSecondNumber) {
        // Start new input after operator or after result
        currentInput = value === '.' ? '0.' : value;
        waitingForSecondNumber = false;
        justEvaluated = false;
    } else {
        if (justEvaluated) {
            // If just evaluated and user presses a number, start fresh
            currentInput = value === '.' ? '0.' : value;
            justEvaluated = false;
        } else {
            // Normal input
            if (value === '.' && currentInput.includes('.')) return; // prevent multiple dots
            if (currentInput === '0' && value !== '.') {
                currentInput = value;
            } else {
                currentInput += value;
            }
        }
    }
    updateDisplay(currentInput);
}

function handleOperator(op) {
    if (operator && !waitingForSecondNumber) {
        // Evaluate previous before setting new operator
        const result = calculate();
        updateDisplay(result);
        previousValue = parseFloat(result);
        currentInput = result;
        justEvaluated = true;
    } else {
        previousValue = parseFloat(currentInput);
    }
    operator = op;
    waitingForSecondNumber = true;
}

function calculate() {
    const first = previousValue;
    const second = parseFloat(currentInput);
    let result;
    switch (operator) {
        case '+':
            result = first + second;
            break;
        case '-':
            result = first - second;
            break;
        case '*':
            result = first * second;
            break;
        case '/':
            if (second === 0) {
                return 'Error';
            }
            result = first / second;
            break;
        default:
            return currentInput;
    }
    // Format result to avoid floating point issues (limit to 10 decimal places)
    if (Number.isFinite(result)) {
        return parseFloat(result.toPrecision(10)).toString();
    }
    return 'Error';
}

function handleEquals() {
    if (operator === null) return;
    if (waitingForSecondNumber) {
        // If equals pressed after operator without second number, treat as same number
        // But to keep consistent, use currentInput (which may be 0 if reset?)
        // Actually let's allow: if waiting and user presses =, use same currentInput (like calculator)
        // No need to do anything special
    }
    const result = calculate();
    updateDisplay(result);
    if (result === 'Error') {
        // Reset state on error
        currentInput = '0';
        previousValue = null;
        operator = null;
        waitingForSecondNumber = false;
        justEvaluated = false;
    } else {
        currentInput = result;
        previousValue = null;
        operator = null;
        waitingForSecondNumber = false;
        justEvaluated = true;
    }
}

function handleClear() {
    currentInput = '0';
    previousValue = null;
    operator = null;
    waitingForSecondNumber = false;
    justEvaluated = false;
    updateDisplay('0');
}

function handleBackspace() {
    if (justEvaluated) {
        // If just evaluated, backspace should clear? Usually backspace after result starts fresh
        // To be friendly, let backspace clear current input (like starting new)
        currentInput = '0';
        justEvaluated = false;
        updateDisplay(currentInput);
        return;
    }
    if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
    } else {
        currentInput = '0';
    }
    updateDisplay(currentInput);
}

function handleToggleSign() {
    if (currentInput === '0') return;
    if (currentInput.startsWith('-')) {
        currentInput = currentInput.slice(1);
    } else {
        currentInput = '-' + currentInput;
    }
    updateDisplay(currentInput);
}

// Click event delegation
document.querySelector('.buttons').addEventListener('click', (e) => {
    const btn = e.target.closest('.btn');
    if (!btn) return;

    const action = btn.dataset.action;
    const value = btn.dataset.value;

    if (action === 'clear') { handleClear(); }
    else if (action === 'backspace') { handleBackspace(); }
    else if (action === 'toggle-sign') { handleToggleSign(); }
    else if (action === 'equals') { handleEquals(); }
    else if (value !== undefined) {
        // number or operator?
        if (btn.classList.contains('number')) {
            handleNumber(value);
        } else if (btn.classList.contains('operator')) {
            handleOperator(value);
        }
    }
});

// Keyboard support
document.addEventListener('keydown', (e) => {
    const key = e.key;
    // Numbers and decimal
    if (/^[0-9.]$/.test(key)) {
        e.preventDefault();
        handleNumber(key);
    }
    // Operators (map key to internal value)
    else if (key === '+') { e.preventDefault(); handleOperator('+'); }
    else if (key === '-') { e.preventDefault(); handleOperator('-'); }
    else if (key === '*') { e.preventDefault(); handleOperator('*'); }
    else if (key === '/') { e.preventDefault(); handleOperator('/'); }
    else if (key === 'Enter' || key === '=') {
        e.preventDefault();
        handleEquals();
    }
    else if (key === 'Backspace') {
        e.preventDefault();
        handleBackspace();
    }
    else if (key === 'Escape' || key === 'c' || key === 'C') {
        e.preventDefault();
        handleClear();
    }
});