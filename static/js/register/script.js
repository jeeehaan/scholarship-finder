document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[name="password1"]');
    const passwordFeedback = document.getElementById('password-feedback');
    
    if (!passwordInput) return;
    
    // Create strength meter
    const strengthMeter = document.createElement('div');
    strengthMeter.className = 'flex gap-1 mt-2';
    strengthMeter.id = 'password-strength-meter';
    
    const strengthLabels = ['Very weak', 'Weak', 'Medium', 'Strong', 'Very strong'];
    const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500'];
    
    for (let i = 0; i < 5; i++) {
        const bar = document.createElement('div');
        bar.className = 'h-2 flex-1 bg-gray-200 rounded transition-colors duration-300';
        bar.id = `strength-${i}`;
        strengthMeter.appendChild(bar);
    }
    
    passwordInput.insertAdjacentElement('afterend', strengthMeter);
    
    // Create feedback element if not exists
    if (!passwordFeedback) {
        const feedbackElement = document.createElement('div');
        feedbackElement.className = 'text-sm mt-1 text-gray-600';
        feedbackElement.id = 'password-feedback';
        strengthMeter.insertAdjacentElement('afterend', feedbackElement);
    }
    
    passwordInput.addEventListener('input', function(e) {
        const password = e.target.value;
        
        if (password.length === 0) {
            resetStrengthMeter();
            resetFeedback();
            return;
        }
        
        const result = calculatePasswordStrength(password);
        updateStrengthMeter(result.strength);
        updateFeedback(password, result);
    });

    function calculatePasswordStrength(password) {
        let strength = 0;
        let isCommon = false;
        let hasSequential = false;
        let hasRepeats = false;

        // Length is the primary factor
        if (password.length < 4) {
            return { strength: 0, isCommon, hasSequential, hasRepeats };
        }

        // Complexity checks
        const hasLower = /[a-z]/.test(password);
        const hasUpper = /[A-Z]/.test(password);
        const hasNumber = /\d/.test(password);
        const hasSymbol = /[\W_]/.test(password);

        // Length score (0-3 points)
        if (password.length >= 4) strength = 1; // Weak
        if (password.length >= 8) strength = 2; // Medium
        if (password.length >= 12) strength = 3; // Strong

        // Complexity boosts (only if length is sufficient)
        if (strength > 0) {
            // Add points for complexity (max 2 points)
            const complexityPoints = [hasUpper, hasNumber, hasSymbol].filter(Boolean).length;
            strength += Math.min(2, Math.floor(complexityPoints / 2));
        }

        // Common password check
        const commonPasswords = [
            'password', '123456', '12345678', 'qwerty', 'abc123', 'letmein',
            'monkey', 'password1', 'admin', 'welcome', 'sunshine', 'football'
        ];
        isCommon = commonPasswords.includes(password.toLowerCase());
        if (isCommon && strength > 1) strength = 1; // Downgrade to weak if common

        // Sequential characters check
        hasSequential = hasSequentialChars(password, 3);
        if (hasSequential && strength > 2) strength = 2; // Downgrade to medium

        // Repeated characters check
        hasRepeats = hasRepeatedChars(password, 3);
        if (hasRepeats && strength > 2) strength = 2; // Downgrade to medium

        strength = Math.max(0, Math.min(4, strength));
        console.log(strength)

        return { 
            strength, 
            isCommon, 
            hasSequential, 
            hasRepeats,
            hasUpper,
            hasNumber,
            hasSymbol,
            hasLower
        };
    }

    function hasSequentialChars(password, minLength) {
        for (let i = 0; i <= password.length - minLength; i++) {
            const slice = password.substr(i, minLength);
            const codes = [...slice].map(c => c.charCodeAt(0));
            
            const increasing = codes.every((c, i) => i === 0 || c === codes[i-1] + 1);
            const decreasing = codes.every((c, i) => i === 0 || c === codes[i-1] - 1);
            
            if (increasing || decreasing) return true;
        }
        return false;
    }

    function hasRepeatedChars(password, minRepeat) {
        return new RegExp(`(.)\\1{${minRepeat -1}}`).test(password);
    }

    function updateStrengthMeter(strength) {
        // Always show at least one red bar if there's any input
        const visibleStrength = passwordInput.value.length > 0 ? Math.max(1, strength) : 0;
        
        for (let i = 0; i < 5; i++) {
            const bar = document.getElementById(`strength-${i}`);
            if (i <= visibleStrength - 1) {
                bar.className = `h-2 flex-1 rounded transition-colors duration-300 ${strengthColors[visibleStrength - 1]}`;
            } else {
                bar.className = 'h-2 flex-1 bg-gray-200 rounded transition-colors duration-300';
            }
        }
    }

    function resetStrengthMeter() {
        for (let i = 0; i < 5; i++) {
            document.getElementById(`strength-${i}`).className = 
                'h-2 flex-1 bg-gray-200 rounded transition-colors duration-300';
        }
    }

    function updateFeedback(password, result) {
        const feedback = document.getElementById('password-feedback');
        if (!feedback) return;

        const { strength, isCommon, hasSequential, hasRepeats, hasUpper, hasNumber, hasSymbol } = result;
        let message = strengthLabels[strength];
        let colorClass = 'text-red-600'; // Default to red for any input
        const suggestions = [];

        // Update color based on strength
        if (strength >= 1) colorClass = 'text-orange-600';
        if (strength >= 2) colorClass = 'text-yellow-600';
        if (strength >= 3) colorClass = 'text-blue-600';
        if (strength >= 4) colorClass = 'text-green-600';

        // Base messages
        if (password.length === 0) {
            message = '';
        } else if (password.length < 4) {
            message = 'Very weak - Needs at least 4 characters';
        } else {
            // Add specific warnings
            if (isCommon) suggestions.push('avoid common passwords');
            if (hasSequential) suggestions.push('avoid sequential characters');
            if (hasRepeats) suggestions.push('avoid repeated characters');

            // Complexity requirements
            if (password.length < 8) suggestions.push('use 8+ characters');
            if (!hasUpper) suggestions.push('add uppercase letters');
            if (!hasNumber) suggestions.push('add numbers');
            if (!hasSymbol) suggestions.push('add symbols');
        }

        // Combine suggestions
        if (suggestions.length > 0) {
            message += `. Suggestions: ${suggestions.join(', ')}`;
        }

        feedback.textContent = message;
        feedback.className = `text-sm mt-1 ${colorClass}`;
    }

    function resetFeedback() {
        const feedback = document.getElementById('password-feedback');
        if (feedback) {
            feedback.textContent = '';
            feedback.className = 'text-sm mt-1 text-gray-600';
        }
    }
});