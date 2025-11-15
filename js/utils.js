/**
 * Moduł pomocniczy - funkcje utilities
 */

// Formatowanie liczb
const formatNumber = (num, decimals = 2) => {
    if (!num && num !== 0) return '-';
    return new Intl.NumberFormat('pl-PL', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(num);
};

// Formatowanie walut
const formatCurrency = (amount, currency = 'USD') => {
    if (!amount && amount !== 0) return '-';
    return new Intl.NumberFormat('pl-PL', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
};

// Formatowanie dużych liczb (K, M, B)
const formatLargeNumber = (num) => {
    if (!num && num !== 0) return '-';
    
    const absNum = Math.abs(num);
    if (absNum >= 1e9) {
        return (num / 1e9).toFixed(2) + 'B';
    } else if (absNum >= 1e6) {
        return (num / 1e6).toFixed(2) + 'M';
    } else if (absNum >= 1e3) {
        return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toFixed(2);
};

// Formatowanie daty
const formatDate = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('pl-PL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    }).format(date);
};

// Formatowanie daty i czasu
const formatDateTime = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return new Intl.DateTimeFormat('pl-PL', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    }).format(date);
};

// Obliczanie dni temu
const daysAgo = (dateStr) => {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Dziś';
    if (diffDays === 1) return 'Wczoraj';
    if (diffDays < 7) return `${diffDays} dni temu`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} tyg. temu`;
    return `${Math.floor(diffDays / 30)} mies. temu`;
};

// Klasyfikacja zmian (positive/negative/neutral)
const getChangeClass = (value) => {
    if (!value) return 'neutral';
    return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral';
};

// Ikona dla typu transakcji
const getTransactionIcon = (type) => {
    const types = {
        'purchase': '🟢',
        'buy': '🟢',
        'BUY': '🟢',
        'sale': '🔴',
        'sell': '🔴',
        'SELL': '🔴',
        'exchange': '🔄'
    };
    return types[type] || '⚪';
};

// Kolor dla wartości
const getValueColor = (value, thresholds = { high: 1000000, medium: 100000 }) => {
    if (value >= thresholds.high) return 'red';
    if (value >= thresholds.medium) return 'orange';
    return 'gray';
};

// Debounce function
const debounce = (func, wait) => {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};

// Toast notification
const showToast = (message, type = 'info') => {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
};

// Loading spinner
const showLoading = (element) => {
    if (element) {
        element.innerHTML = '<div class="loading-spinner"></div>';
    }
};

const hideLoading = (element) => {
    if (element) {
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) spinner.remove();
    }
};

// Sort array by property
const sortBy = (array, property, direction = 'asc') => {
    return array.sort((a, b) => {
        const aVal = a[property];
        const bVal = b[property];
        
        if (direction === 'asc') {
            return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
        } else {
            return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
        }
    });
};

// Filter array by search term
const filterBySearch = (array, searchTerm, properties) => {
    if (!searchTerm) return array;
    
    const term = searchTerm.toLowerCase();
    return array.filter(item => {
        return properties.some(prop => {
            const value = item[prop];
            return value && value.toString().toLowerCase().includes(term);
        });
    });
};

// LocalStorage helpers
const storage = {
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return defaultValue;
        }
    },
    
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error writing to localStorage:', e);
            return false;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Error removing from localStorage:', e);
            return false;
        }
    }
};

// Export dla użycia w innych modułach
window.Utils = {
    formatNumber,
    formatCurrency,
    formatLargeNumber,
    formatDate,
    formatDateTime,
    daysAgo,
    getChangeClass,
    getTransactionIcon,
    getValueColor,
    debounce,
    showToast,
    showLoading,
    hideLoading,
    sortBy,
    filterBySearch,
    storage
};
