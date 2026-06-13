// Search functionality
const SearchManager = {
    products: [
        { id: 'prod1', name: 'Router Gigabit Empresarial', category: 'Networking', price: 129990 },
        { id: 'prod2', name: 'Switch PoE 24 Puertos', category: 'Switches', price: 624900 },
        { id: 'prod3', name: 'Antena Parabólica PtP', category: 'Inalámbrico', price: 385500 },
        { id: 'prod4', name: 'Bobina UTP Cat 6', category: 'Infraestructura', price: 95000 },
        { id: 'prod5', name: 'Servidor Rackeable 1U', category: 'Data Center', price: 1250000 },
    ],

    search(query) {
        if (!query.trim()) return [];
        const lowerQuery = query.toLowerCase();
        return this.products.filter(p =>
            p.name.toLowerCase().includes(lowerQuery) ||
            p.category.toLowerCase().includes(lowerQuery)
        );
    },

    showResults(query) {
        const results = this.search(query);
        const container = document.querySelector('.search-results');

        if (!container) {
            const input = document.querySelector('.search-input');
            const resultsDiv = document.createElement('div');
            resultsDiv.className = 'search-results position-absolute bg-white border rounded shadow-lg mt-2';
            resultsDiv.style.width = '100%';
            resultsDiv.style.zIndex = '1000';
            resultsDiv.style.maxHeight = '400px';
            resultsDiv.style.overflowY = 'auto';
            input.parentElement.appendChild(resultsDiv);
        }

        const resultsContainer = document.querySelector('.search-results');

        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="p-3 text-muted text-center">No se encontraron productos</div>';
            return;
        }

        resultsContainer.innerHTML = results.map(p => `
            <div class="p-3 border-bottom cursor-pointer hover-bg-light" style="cursor: pointer;" onclick="window.location.href='{% url 'web:productos' %}'">
                <div class="fw-bold text-dark">${p.name}</div>
                <small class="text-muted">${p.category}</small>
                <div class="text-primary fw-bold">$${p.price.toLocaleString('es-CL')}</div>
            </div>
        `).join('');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.querySelector('.search-input');

    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            SearchManager.showResults(e.target.value);
        });

        searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                const resultsContainer = document.querySelector('.search-results');
                if (resultsContainer) resultsContainer.remove();
            }, 200);
        });

        searchInput.addEventListener('focus', (e) => {
            if (e.target.value.trim()) {
                SearchManager.showResults(e.target.value);
            }
        });
    }
});
