document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('responder-form');
    const submitBtn = document.getElementById('submit-btn');
    const formSection = document.querySelector('.form-section');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');
    const resetBtn = document.getElementById('reset-btn');
    const answersContainer = document.getElementById('answers-container');
    const resultTitle = document.getElementById('result-title');
    const resultDesc = document.getElementById('result-desc');
    
    const personasContainer = document.getElementById('personas-container');
    const addPersonaBtn = document.getElementById('add-persona-btn');

    // Add Persona Event Listener
    addPersonaBtn.addEventListener('click', () => {
        const firstGroup = personasContainer.querySelector('.persona-group');
        const newGroup = firstGroup.cloneNode(true);
        newGroup.querySelector('.persona-input').value = '';
        newGroup.querySelector('.submission-count').value = '1';
        newGroup.querySelector('.remove-persona-btn').classList.remove('hidden');
        personasContainer.appendChild(newGroup);
    });

    // Remove Persona Event Listener using Event Delegation
    personasContainer.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-persona-btn')) {
            e.target.closest('.persona-group').remove();
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const url = document.getElementById('form-url').value;
        
        // Build personas array
        const personas = [];
        let totalCount = 0;
        document.querySelectorAll('.persona-group').forEach(group => {
            const count = parseInt(group.querySelector('.submission-count').value) || 1;
            totalCount += count;
            personas.push({
                description: group.querySelector('.persona-input').value,
                count: count
            });
        });
        
        if (totalCount > 100) {
            errorMessage.textContent = "The maximum allowed number of overall submissions is 100.";
            errorMessage.classList.remove('hidden');
            return;
        }
        
        // UI Loading state
        submitBtn.classList.add('btn-loading');
        submitBtn.disabled = true;
        errorMessage.classList.add('hidden');
        
        try {
            const response = await fetch('/api/process-form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, personas })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'An error occurred while processing the form.');
            }
            
            displayResults(data);
            
        } catch (error) {
            errorMessage.textContent = error.message;
            errorMessage.classList.remove('hidden');
        } finally {
            submitBtn.classList.remove('btn-loading');
            submitBtn.disabled = false;
        }
    });

    resetBtn.addEventListener('click', () => {
        resultsSection.classList.add('hidden');
        formSection.classList.remove('hidden');
        form.reset();
        answersContainer.innerHTML = '';
        errorMessage.classList.add('hidden');
    });

    function displayResults(data) {
        formSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');
        
        resultTitle.textContent = data.form_title || 'Processed Form';
        
        let descHtml = data.form_description || '';
        
        if (data.status === 'processing') {
            descHtml += '<br><br><strong style="color: var(--accent-1);">⏳ ' + escapeHtml(data.message) + '</strong>';
        } else {
            if (data.submitted) {
                descHtml += '<br><br><strong style="color: var(--success-color);">✓ Successfully submitted answers to the Google Form.</strong>';
            } else if (data.submitted === false) {
                descHtml += '<br><br><strong style="color: var(--error-color);">✗ Failed to submit answers to the Google Form.</strong>';
            }
        }
        
        resultDesc.innerHTML = descHtml;
        
        answersContainer.innerHTML = '';
        
        if (data.results && data.results.length > 0) {
            data.results.forEach((item, index) => {
                const card = document.createElement('div');
                card.className = 'answer-card';
                card.style.animationDelay = `${index * 0.1}s`;
                card.style.animation = 'slideDown 0.5s ease-out forwards';
                card.style.opacity = '0';
                
                const questionHtml = `
                    <div class="question-text">Q: ${escapeHtml(item.title)}</div>
                    <div class="answer-text"><strong>A:</strong> ${escapeHtml(item.answer)}</div>
                `;
                card.innerHTML = questionHtml;
                answersContainer.appendChild(card);
            });
        } else if (data.status === 'processing') {
            answersContainer.innerHTML = '<p>The backend is generating and submitting answers in parallel. You can check your Google Form responses shortly.</p>';
        } else {
            answersContainer.innerHTML = '<p>No questions could be extracted or answered from this form.</p>';
        }
    }

    function escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
             .toString()
             .replace(/&/g, "&amp;")
             .replace(/</g, "&lt;")
             .replace(/>/g, "&gt;")
             .replace(/"/g, "&quot;")
             .replace(/'/g, "&#039;");
    }
});
