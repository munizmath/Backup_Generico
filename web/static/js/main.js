/* ============================================
   Sistema de Backup Avançado - JavaScript Principal
   ============================================ */

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initMenu();
    initValidation();
    initAccessibility();
    loadTheme();
});

// Menu Mobile
function initMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    const menuDropdown = document.getElementById('menuDropdown');
    const menuDropdownContent = document.getElementById('menuDropdownContent');
    
    // Toggle menu mobile
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            overlay.classList.toggle('show');
            document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
        });
    }
    
    // Fechar menu
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        });
    }
    
    // Fechar ao clicar no overlay
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        });
    }
    
    // Menu dropdown
    if (menuDropdown && menuDropdownContent) {
        menuDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            const isExpanded = menuDropdown.getAttribute('aria-expanded') === 'true';
            menuDropdown.setAttribute('aria-expanded', !isExpanded);
            menuDropdownContent.classList.toggle('show');
        });
        
        // Fechar ao clicar fora
        document.addEventListener('click', function(e) {
            if (!menuDropdown.contains(e.target) && !menuDropdownContent.contains(e.target)) {
                menuDropdown.setAttribute('aria-expanded', 'false');
                menuDropdownContent.classList.remove('show');
            }
        });
    }
}

// Validação de Formulários
function initValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        
        inputs.forEach(input => {
            // Validação em tempo real
            input.addEventListener('blur', function() {
                validateField(input);
            });
            
            // Limpar erro ao começar a digitar
            input.addEventListener('input', function() {
                if (input.checkValidity()) {
                    clearError(input);
                }
            });
        });
        
        // Validação no submit
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                // Focar no primeiro campo inválido
                const firstInvalid = form.querySelector(':invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    });
}

function validateField(field) {
    const errorElement = field.parentElement.querySelector('.form-error');
    
    if (!field.checkValidity()) {
        showError(field, getErrorMessage(field));
        return false;
    } else {
        clearError(field);
        return true;
    }
}

function showError(field, message) {
    let errorElement = field.parentElement.querySelector('.form-error');
    
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.className = 'form-error';
        field.parentElement.appendChild(errorElement);
    }
    
    errorElement.textContent = message;
    field.setAttribute('aria-invalid', 'true');
    field.setAttribute('aria-describedby', errorElement.id || 'error-' + field.id);
    
    if (!errorElement.id) {
        errorElement.id = 'error-' + field.id;
    }
}

function clearError(field) {
    const errorElement = field.parentElement.querySelector('.form-error');
    if (errorElement) {
        errorElement.textContent = '';
    }
    field.removeAttribute('aria-invalid');
    field.removeAttribute('aria-describedby');
}

function getErrorMessage(field) {
    if (field.validity.valueMissing) {
        return `${field.getAttribute('data-label') || 'Este campo'} é obrigatório`;
    }
    if (field.validity.typeMismatch) {
        if (field.type === 'email') {
            return 'Por favor, insira um email válido';
        }
        if (field.type === 'url') {
            return 'Por favor, insira uma URL válida';
        }
    }
    if (field.validity.tooShort) {
        return `Mínimo de ${field.minLength} caracteres`;
    }
    if (field.validity.tooLong) {
        return `Máximo de ${field.maxLength} caracteres`;
    }
    if (field.validity.patternMismatch) {
        return field.getAttribute('data-pattern-error') || 'Formato inválido';
    }
    return 'Valor inválido';
}

// Acessibilidade
function initAccessibility() {
    // Skip link para navegação por teclado
    const skipLink = document.createElement('a');
    skipLink.href = '#main-content';
    skipLink.className = 'sr-only';
    skipLink.textContent = 'Pular para conteúdo principal';
    skipLink.addEventListener('focus', function() {
        this.classList.remove('sr-only');
    });
    skipLink.addEventListener('blur', function() {
        this.classList.add('sr-only');
    });
    document.body.insertBefore(skipLink, document.body.firstChild);
    
    // Anunciar mudanças dinâmicas
    const liveRegion = document.createElement('div');
    liveRegion.setAttribute('role', 'status');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    liveRegion.id = 'live-region';
    document.body.appendChild(liveRegion);
}

function announce(message) {
    const liveRegion = document.getElementById('live-region');
    if (liveRegion) {
        liveRegion.textContent = message;
        setTimeout(() => {
            liveRegion.textContent = '';
        }, 1000);
    }
}

// Funções do Menu
function openInNewTab() {
    window.open(window.location.href, '_blank');
    announce('Abrindo em nova guia');
}

function openInNewWindow() {
    const width = 1200;
    const height = 800;
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;
    window.open(
        window.location.href,
        '_blank',
        `width=${width},height=${height},left=${left},top=${top}`
    );
    announce('Abrindo em nova janela');
}

function confirmExit() {
    if (confirm('Tem certeza que deseja sair?')) {
        window.close();
        // Se não conseguir fechar (não é popup), redirecionar
        if (!document.getElementById('exit-attempt')) {
            window.location.href = 'about:blank';
        }
    }
}

// API Helpers
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Notificações
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close" aria-label="Fechar notificação">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
            </button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Fechar ao clicar
    notification.querySelector('.notification-close').addEventListener('click', () => {
        closeNotification(notification);
    });
    
    // Auto-fechar após 5 segundos
    setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}

function closeNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => {
        notification.remove();
    }, 300);
}

// Exportar funções
window.backupSystem = {
    apiRequest,
    showNotification,
    announce,
    validateField
};

