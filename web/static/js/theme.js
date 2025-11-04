/* ============================================
   Sistema de Temas (Claro/Escuro)
   ============================================ */

document.addEventListener('DOMContentLoaded', function() {
    initTheme();
});

function initTheme() {
    const themeToggle = document.getElementById('themeToggle');
    const themeToggleText = document.getElementById('themeToggleText');
    
    // Carregar tema salvo
    loadTheme();
    
    // Toggle tema
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            toggleTheme();
        });
    }
}

function loadTheme() {
    // Buscar tema do servidor
    fetch('/api/theme')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                setTheme(data.theme);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar tema:', error);
            // Fallback para tema do localStorage
            const savedTheme = localStorage.getItem('theme') || 'dark';
            setTheme(savedTheme);
        });
}

function toggleTheme() {
    const currentTheme = document.body.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.body.setAttribute('data-theme', theme);
    document.body.className = `theme-${theme}`;
    
    // Salvar no servidor
    fetch('/api/theme', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ theme: theme })
    }).catch(error => {
        console.error('Erro ao salvar tema:', error);
        // Fallback para localStorage
        localStorage.setItem('theme', theme);
    });
    
    // Atualizar texto do botão
    const themeToggleText = document.getElementById('themeToggleText');
    if (themeToggleText) {
        themeToggleText.textContent = theme === 'dark' ? 'Tema Claro' : 'Tema Escuro';
    }
    
    // Anunciar mudança
    if (window.backupSystem && window.backupSystem.announce) {
        window.backupSystem.announce(`Tema alterado para ${theme === 'dark' ? 'escuro' : 'claro'}`);
    }
}

