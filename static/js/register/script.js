document.addEventListener('DOMContentLoaded', function() {
    const passwordInput = document.querySelector('input[name="password1"]');
    const passwordFeedback = document.getElementById('password-feedback');
    
    if (!passwordInput) return;
    
    // Create strength bars if they don't exist in HTML
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
    
    if (!passwordFeedback) {
        const feedbackElement = document.createElement('div');
        feedbackElement.className = 'text-sm mt-1 text-gray-600';
        feedbackElement.id = 'password-feedback';
        strengthMeter.insertAdjacentElement('afterend', feedbackElement);
    }
    
    passwordInput.addEventListener('input', function(e) {
        const password = e.target.value;
        
        // Reset state if password is empty
        if (password.length === 0) {
            resetStrengthMeter();
            resetFeedback();
            return;
        }
        
        const strength = calculatePasswordStrength(password);
        updateStrengthMeter(strength);
        updateFeedback(password, strength);
    });
    
    function calculatePasswordStrength(password) {
        let strength = 0;
        
        // Length contributes up to 3 points
        strength += Math.min(3, Math.floor(password.length / 4));
        
        // Add points for complexity
        if (/[A-Z]/.test(password)) strength += 1;
        if (/[0-9]/.test(password)) strength += 1;
        if (/[^A-Za-z0-9]/.test(password)) strength += 1;
        
        // Cap at maximum strength
        return Math.min(4, strength);
    }
    
    function updateStrengthMeter(strength) {
        for (let i = 0; i < 5; i++) {
            const bar = document.getElementById(`strength-${i}`);
            if (bar) {
                bar.className = `h-2 flex-1 rounded transition-colors duration-300 ${i <= strength ? strengthColors[strength] : 'bg-gray-200'}`;
            }
        }
    }
    
    function resetStrengthMeter() {
        for (let i = 0; i < 5; i++) {
            const bar = document.getElementById(`strength-${i}`);
            if (bar) {
                bar.className = 'h-2 flex-1 bg-gray-200 rounded transition-colors duration-300';
            }
        }
    }
    
    function updateFeedback(password, strength) {
        const feedback = document.getElementById('password-feedback');
        if (!feedback) return;
        
        let message = strengthLabels[strength];
        let colorClass = 'text-gray-600';
        
        if (strength <= 1) {
            colorClass = 'text-red-600';
            message += ' - Add more characters and variety';
        } else if (strength === 2) {
            colorClass = 'text-yellow-600';
            message += ' - Try adding numbers or symbols';
        } else if (strength === 3) {
            colorClass = 'text-blue-600';
            message += ' - Good, but could be stronger';
        } else {
            colorClass = 'text-green-600';
            message += ' - Excellent password!';
        }
        
        feedback.textContent = message;
        feedback.className = `text-sm mt-1 ${colorClass}`;
        
        // Additional specific feedback
        const suggestions = [];
        if (password.length < 8) {
            suggestions.push('Use at least 8 characters');
        }
        if (!/[A-Z]/.test(password)) {
            suggestions.push('Add uppercase letters');
        }
        if (!/[0-9]/.test(password)) {
            suggestions.push('Add numbers');
        }
        if (!/[^A-Za-z0-9]/.test(password)) {
            suggestions.push('Add special characters');
        }
        
        if (suggestions.length > 0 && strength < 4) {
            feedback.textContent += `. Suggestions: ${suggestions.join(', ')}`;
        }
    }
    
    function resetFeedback() {
        const feedback = document.getElementById('password-feedback');
        if (feedback) {
            feedback.textContent = '';
            feedback.className = 'text-sm mt-1 text-gray-600';
        }
    }
});