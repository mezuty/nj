let display = document.getElementById('display');
let currentInput = '0';
let shouldResetDisplay = false;

function appendToDisplay(value) {
    if (shouldResetDisplay) {
        currentInput = '';
        shouldResetDisplay = false;
    }
    
    // Prevent multiple decimal points
    if (value === '.' && currentInput.includes('.')) {
        // Check if current number already has a decimal point
        const lastNumber = currentInput.split(/[\+\-\*\/]/).pop();
        if (lastNumber && lastNumber.includes('.')) {
            return;
        }
    }
    
    // Prevent multiple operators in a row
    if (['+', '-', '*', '/'].includes(value)) {
        const lastChar = currentInput[currentInput.length - 1];
        if (['+', '-', '*', '/'].includes(lastChar)) {
            currentInput = currentInput.slice(0, -1) + value;
            updateDisplay();
            return;
        }
    }
    
    if (currentInput === '0' && value !== '.' && !['+', '-', '*', '/'].includes(value)) {
        currentInput = value;
    } else {
        currentInput += value;
    }
    
    updateDisplay();
}

function clearDisplay() {
    currentInput = '0';
    shouldResetDisplay = false;
    updateDisplay();
}

function deleteLast() {
    if (shouldResetDisplay) {
        clearDisplay();
        return;
    }
    
    if (currentInput.length > 1) {
        currentInput = currentInput.slice(0, -1);
    } else {
        currentInput = '0';
    }
    
    updateDisplay();
}

function calculate() {
    try {
        // Replace display symbols with actual operators
        let expression = currentInput
            .replace(/×/g, '*')
            .replace(/÷/g, '/')
            .replace(/−/g, '-');
        
        // Evaluate the expression
        let result = Function('"use strict"; return (' + expression + ')')();
        
        // Handle division by zero
        if (!isFinite(result)) {
            throw new Error('Cannot divide by zero');
        }
        
        // Round to avoid floating point errors
        result = Math.round(result * 100000000) / 100000000;
        
        currentInput = result.toString();
        shouldResetDisplay = true;
        updateDisplay();
    } catch (error) {
        currentInput = 'Error';
        shouldResetDisplay = true;
        updateDisplay();
        
        // Reset after showing error
        setTimeout(() => {
            clearDisplay();
        }, 1500);
    }
}

function updateDisplay() {
    // Format the display with proper spacing
    let formatted = currentInput
        .replace(/\*/g, '×')
        .replace(/\//g, '÷')
        .replace(/-/g, '−');
    
    display.textContent = formatted;
    
    // Adjust font size if number is too long
    if (formatted.length > 12) {
        display.style.fontSize = '24px';
    } else if (formatted.length > 8) {
        display.style.fontSize = '28px';
    } else {
        display.style.fontSize = '36px';
    }
}

// Keyboard support
document.addEventListener('keydown', (event) => {
    const key = event.key;
    
    if (key >= '0' && key <= '9') {
        appendToDisplay(key);
    } else if (key === '.') {
        appendToDisplay('.');
    } else if (key === '+' || key === '-') {
        appendToDisplay(key);
    } else if (key === '*') {
        appendToDisplay('*');
    } else if (key === '/') {
        event.preventDefault();
        appendToDisplay('/');
    } else if (key === 'Enter' || key === '=') {
        event.preventDefault();
        calculate();
    } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearDisplay();
    } else if (key === 'Backspace') {
        event.preventDefault();
        deleteLast();
    }
});

