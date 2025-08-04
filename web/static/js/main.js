// ===== GESTORCLOUD - JAVASCRIPT PRINCIPAL =====

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Función principal de inicialización
function initializeApp() {
    initializeSidebar();
    initializeTooltips();
    initializeAnimations();
    initializeSearch();
    initializeForms();
    console.log('🚀 GestorCloud inicializado correctamente');
}

// ===== SIDEBAR FUNCTIONALITY =====
function initializeSidebar() {
    const sidebarToggle = document.querySelector('.sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    // Toggle sidebar en móviles
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
    }
    
    // Cerrar sidebar al hacer click fuera en móviles
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !e.target.matches('.sidebar-toggle')) {
                sidebar.classList.remove('show');
            }
        }
    });
    
    // Marcar enlace activo
    setActiveNavLink();
}

// Marcar el enlace de navegación activo
function setActiveNavLink() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// ===== TOOLTIPS =====
function initializeTooltips() {
    // Inicializar tooltips de Bootstrap si está disponible
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

// ===== ANIMACIONES =====
function initializeAnimations() {
    // Agregar clase fade-in a elementos cuando aparecen en el viewport
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, observerOptions);
    
    // Observar cards y elementos animables
    const animatableElements = document.querySelectorAll('.card, .stats-card');
    animatableElements.forEach(el => observer.observe(el));
}

// ===== BÚSQUEDA =====
function initializeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function(e) {
            const searchTerm = e.target.value.toLowerCase();
            performSearch(searchTerm, e.target);
        }, 300));
    });
}

// Función de búsqueda
function performSearch(searchTerm, input) {
    const targetTable = input.getAttribute('data-target') || 'table tbody tr';
    const rows = document.querySelectorAll(targetTable);
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
            row.classList.add('fade-in');
        } else {
            row.style.display = 'none';
            row.classList.remove('fade-in');
        }
    });
    
    // Mostrar mensaje si no hay resultados
    updateSearchResults(rows, searchTerm);
}

// Actualizar resultados de búsqueda
function updateSearchResults(rows, searchTerm) {
    const visibleRows = Array.from(rows).filter(row => row.style.display !== 'none');
    const resultsContainer = document.querySelector('.search-results');
    
    if (resultsContainer) {
        if (visibleRows.length === 0 && searchTerm.length > 0) {
            resultsContainer.innerHTML = `
                <div class="alert alert-info text-center">
                    <i class="fas fa-search"></i>
                    No se encontraron resultados para "${searchTerm}"
                </div>
            `;
        } else {
            resultsContainer.innerHTML = '';
        }
    }
}

// ===== FORMULARIOS =====
function initializeForms() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        // Validación en tiempo real
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
        
        // Validación al enviar
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showFormErrors();
            }
        });
    });
}

// Validar campo individual
function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    let isValid = true;
    let errorMessage = '';
    
    // Validaciones específicas
    switch (fieldName) {
        case 'correo':
        case 'email':
            if (value && !isValidEmail(value)) {
                isValid = false;
                errorMessage = 'Ingrese un correo electrónico válido';
            }
            break;
            
        case 'telefono':
            if (value && !isValidPhone(value)) {
                isValid = false;
                errorMessage = 'Ingrese un número de teléfono válido';
            }
            break;
            
        case 'edad':
            if (value && (value < 1 || value > 120)) {
                isValid = false;
                errorMessage = 'La edad debe estar entre 1 y 120 años';
            }
            break;
    }
    
    // Campos requeridos
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'Este campo es obligatorio';
    }
    
    // Mostrar/ocultar error
    if (!isValid) {
        showFieldError(field, errorMessage);
    } else {
        clearFieldError(field);
    }
    
    return isValid;
}

// Validar formulario completo
function validateForm(form) {
    const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });
    
    return isValid;
}

// Mostrar error en campo
function showFieldError(field, message) {
    clearFieldError(field);
    
    field.classList.add('is-invalid');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.textContent = message;
    field.parentNode.appendChild(errorDiv);
}

// Limpiar error de campo
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

// Mostrar errores del formulario
function showFormErrors() {
    showNotification('Por favor corrige los errores del formulario', 'error');
}

// ===== UTILIDADES =====

// Función debounce para optimizar búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Validar email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Validar teléfono
function isValidPhone(phone) {
    const phoneRegex = /^[\d\s\-\+\(\)]+$/;
    return phoneRegex.test(phone) && phone.length >= 7;
}

// Formatear números con separadores de miles
function formatNumber(num) {
    return new Intl.NumberFormat('es-CO').format(num);
}

// Formatear moneda
function formatCurrency(amount) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(amount);
}

// ===== NOTIFICACIONES =====
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification fade-in`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        ${message}
        <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
    `;
    
    // Estilos para notificación flotante
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remover después del tiempo especificado
    setTimeout(() => {
        if (notification.parentElement) {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }
    }, duration);
}

// Obtener icono para notificación
function getNotificationIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// ===== MANEJO DE ERRORES GLOBALES =====
window.addEventListener('error', function(e) {
    console.error('Error en GestorCloud:', e.error);
    showNotification('Ha ocurrido un error inesperado', 'error');
});

// ===== EXPORTAR FUNCIONES PARA USO GLOBAL =====
window.GestorCloud = {
    showNotification,
    formatNumber,
    formatCurrency,
    validateForm,
    performSearch
};