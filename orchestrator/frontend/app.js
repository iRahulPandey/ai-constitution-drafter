const createForm = document.getElementById('create-form');
const topicInput = document.getElementById('topic-input');
const createButton = document.getElementById('create-button');
const progressContainer = document.getElementById('progress-container');
const statusText = document.getElementById('status-text');

const sessionId = 'session-' + Math.random().toString(36).substring(2, 15);

function showProgress() {
    createForm.classList.add('hidden');
    topicInput.disabled = true;
    createButton.disabled = true;
    createButton.innerHTML = 'Drafting...';
    progressContainer.classList.remove('hidden');
}

function updateStatus(text) {
    statusText.textContent = text;
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    
    // Updated keywords to match backend agent names
    if (text.toLowerCase().includes('research') || text.toLowerCase().includes('gather')) {
        document.getElementById('step-researcher').classList.add('active');
    } else if (text.toLowerCase().includes('judge') || text.toLowerCase().includes('verdict')) {
        document.getElementById('step-judge').classList.add('active');
    } else if (text.toLowerCase().includes('writ') || text.toLowerCase().includes('builder')) {
        document.getElementById('step-builder').classList.add('active');
    }
}

createForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const topic = topicInput.value.trim();
    if (!topic) return;

    showProgress();

    try {
        const response = await fetch('/api/chat_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                // Updated Prompt to align with Agent Instructions
                message: `Draft a binding AI Constitution for this use case: ${topic}`,
                session_id: sessionId
            })
        });

        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const data = JSON.parse(line);
                    if (data.type === 'progress') {
                        updateStatus(data.text);
                    } else if (data.type === 'result') {
                        // Backend returns a JSON string, so we save it directly
                        localStorage.setItem('currentConstitution', data.text);
                        // Redirect to the new constitution viewer
                        window.location.href = '/constitution.html';
                        return;
                    }
                } catch (e) {
                    console.error('Error parsing JSON:', e, line);
                }
            }
        }

    } catch (error) {
        console.error('Error:', error);
        statusText.textContent = 'Connection error. Please try again.';
    }
});