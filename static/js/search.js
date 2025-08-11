// Advanced Search Functionality with Autocomplete and Filtering
class ToolSearch {
    constructor() {
        this.tools = [];
        this.filteredTools = [];
        this.searchInput = document.getElementById('searchInput');
        this.searchResults = document.getElementById('searchResults');
        this.searchResultsList = document.getElementById('searchResultsList');
        this.categoryFilter = document.getElementById('categoryFilter');
        this.priceFilter = document.getElementById('priceFilter');
        this.ratingFilter = document.getElementById('ratingFilter');
        this.resetFilters = document.getElementById('resetFilters');
        this.clearSearch = document.getElementById('clearSearch');
        
        this.isLoading = false;
        this.currentQuery = '';
        
        this.init();
    }
    
    async init() {
        await this.loadTools();
        this.bindEvents();
        this.trackSearchEvents();
    }
    
    async loadTools() {
        try {
            // Load tools data from Hugo's JSON output
            const response = await fetch('/index.json');
            if (response.ok) {
                const data = await response.json();
                this.tools = data.tools || [];
                console.log(`Loaded ${this.tools.length} tools for search`);
            } else {
                // Fallback: extract from page content if JSON not available
                this.extractToolsFromPage();
            }
        } catch (error) {
            console.warn('Could not load tools JSON, extracting from page:', error);
            this.extractToolsFromPage();
        }
    }
    
    extractToolsFromPage() {
        // Extract tool data from existing page elements
        const toolCards = document.querySelectorAll('.tool-card, .category-card');
        this.tools = Array.from(toolCards).map((card, index) => {
            const titleEl = card.querySelector('h3 a, h2 a');
            const taglineEl = card.querySelector('.tool-tagline, .category-description');
            const categoryEl = card.querySelector('.category-tag');
            
            return {
                id: index,
                title: titleEl ? titleEl.textContent.trim() : 'Unknown Tool',
                tagline: taglineEl ? taglineEl.textContent.trim() : '',
                category: categoryEl ? categoryEl.textContent.trim() : '',
                url: titleEl ? titleEl.href : '#',
                rating: 4.3, // Default rating
                price: 29 // Default price
            };
        });
        
        console.log(`Extracted ${this.tools.length} tools from page content`);
    }
    
    bindEvents() {
        // Search input events
        this.searchInput.addEventListener('input', this.debounce(this.handleSearch.bind(this), 300));
        this.searchInput.addEventListener('focus', this.showResults.bind(this));
        
        // Filter events
        this.categoryFilter.addEventListener('change', this.applyFilters.bind(this));
        this.priceFilter.addEventListener('change', this.applyFilters.bind(this));
        this.ratingFilter.addEventListener('change', this.applyFilters.bind(this));
        
        // Clear and reset events
        this.clearSearch.addEventListener('click', this.clearSearch.bind(this));
        this.resetFilters.addEventListener('click', this.resetAllFilters.bind(this));
        
        // Click outside to hide results
        document.addEventListener('click', (e) => {
            if (!document.getElementById('searchContainer').contains(e.target)) {
                this.hideResults();
            }
        });
        
        // Keyboard navigation
        this.searchInput.addEventListener('keydown', this.handleKeyNavigation.bind(this));
    }
    
    debounce(func, wait) {
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
    
    handleSearch(e) {
        const query = e.target.value.trim().toLowerCase();
        this.currentQuery = query;
        
        if (query.length === 0) {
            this.hideResults();
            return;
        }
        
        if (query.length < 2) {
            return; // Wait for at least 2 characters
        }
        
        this.performSearch(query);
    }
    
    performSearch(query) {
        this.isLoading = true;
        this.showLoadingState();
        
        // Search algorithm with multiple criteria
        const results = this.tools.filter(tool => {
            const titleMatch = tool.title.toLowerCase().includes(query);
            const taglineMatch = tool.tagline.toLowerCase().includes(query);
            const categoryMatch = tool.category.toLowerCase().includes(query);
            
            // Keyword matching for common terms
            const keywordMatch = this.matchKeywords(query, tool);
            
            return titleMatch || taglineMatch || categoryMatch || keywordMatch;
        });
        
        // Sort results by relevance
        results.sort((a, b) => {
            const aScore = this.calculateRelevanceScore(query, a);
            const bScore = this.calculateRelevanceScore(query, b);
            return bScore - aScore;
        });
        
        this.filteredTools = results.slice(0, 50); // Limit to top 50 results
        this.displayResults();
        this.isLoading = false;
    }
    
    matchKeywords(query, tool) {
        const keywords = {
            'crm': ['customer', 'relationship', 'management', 'sales', 'leads'],
            'email': ['marketing', 'newsletter', 'campaigns', 'automation'],
            'design': ['creative', 'graphics', 'ui', 'ux', 'visual'],
            'analytics': ['data', 'tracking', 'metrics', 'insights', 'reporting'],
            'ecommerce': ['store', 'shop', 'selling', 'retail', 'commerce'],
            'project': ['management', 'planning', 'tasks', 'collaboration'],
            'communication': ['chat', 'messaging', 'video', 'meetings', 'collaboration'],
            'productivity': ['tasks', 'workflow', 'efficiency', 'organization']
        };
        
        for (const [key, terms] of Object.entries(keywords)) {
            if (query.includes(key) || terms.some(term => query.includes(term))) {
                const toolText = `${tool.title} ${tool.tagline} ${tool.category}`.toLowerCase();
                if (terms.some(term => toolText.includes(term)) || toolText.includes(key)) {
                    return true;
                }
            }
        }
        
        return false;
    }
    
    calculateRelevanceScore(query, tool) {
        let score = 0;
        const queryLower = query.toLowerCase();
        
        // Title match (highest priority)
        if (tool.title.toLowerCase().includes(queryLower)) {
            score += 10;
            if (tool.title.toLowerCase().startsWith(queryLower)) {
                score += 5; // Bonus for starts with
            }
        }
        
        // Category match
        if (tool.category.toLowerCase().includes(queryLower)) {
            score += 5;
        }
        
        // Tagline match
        if (tool.tagline.toLowerCase().includes(queryLower)) {
            score += 3;
        }
        
        // Rating bonus
        score += (tool.rating || 4.0) * 0.5;
        
        return score;
    }
    
    applyFilters() {
        const category = this.categoryFilter.value;
        const price = this.priceFilter.value;
        const rating = this.ratingFilter.value;
        
        if (!category && !price && !rating) {
            // No filters applied, perform search with current query
            if (this.currentQuery) {
                this.performSearch(this.currentQuery);
            }
            return;
        }
        
        // Apply filters to current results or all tools
        let toolsToFilter = this.currentQuery ? this.filteredTools : this.tools;
        
        let filtered = toolsToFilter.filter(tool => {
            let matches = true;
            
            // Category filter
            if (category && !tool.category.includes(category.replace(/[🎯🤖🎨📢🛍️💻⏰📝]/g, '').trim())) {
                matches = false;
            }
            
            // Price filter
            if (price && matches) {
                const toolPrice = tool.price || 29;
                switch (price) {
                    case 'free':
                        matches = toolPrice === 0;
                        break;
                    case '0-29':
                        matches = toolPrice >= 0 && toolPrice <= 29;
                        break;
                    case '30-99':
                        matches = toolPrice >= 30 && toolPrice <= 99;
                        break;
                    case '100-299':
                        matches = toolPrice >= 100 && toolPrice <= 299;
                        break;
                    case '300+':
                        matches = toolPrice >= 300;
                        break;
                }
            }
            
            // Rating filter
            if (rating && matches) {
                const toolRating = tool.rating || 4.3;
                const minRating = parseFloat(rating.replace('+', ''));
                matches = toolRating >= minRating;
            }
            
            return matches;
        });
        
        this.filteredTools = filtered;
        this.displayResults();
        
        // Track filter usage
        this.trackEvent('filter_applied', {
            category: category || 'none',
            price: price || 'none',
            rating: rating || 'none',
            results: filtered.length
        });
    }
    
    displayResults() {
        if (this.filteredTools.length === 0) {
            this.showNoResults();
            return;
        }
        
        // Update results count
        document.querySelector('.results-count').textContent = `${this.filteredTools.length} tools found`;
        
        // Generate results HTML
        const resultsHTML = this.filteredTools.map((tool, index) => `
            <div class="search-result-item" data-index="${index}" onclick="window.location.href='${tool.url}'">
                <div class="search-result-info">
                    <div class="search-result-title">${tool.title}</div>
                    <div class="search-result-meta">
                        ${tool.tagline}
                        <span class="search-result-category">${tool.category}</span>
                    </div>
                </div>
            </div>
        `).join('');
        
        this.searchResultsList.innerHTML = resultsHTML;
        this.showResults();
    }
    
    showResults() {
        this.searchResults.style.display = 'block';
    }
    
    hideResults() {
        this.searchResults.style.display = 'none';
    }
    
    showLoadingState() {
        this.searchResultsList.innerHTML = '<div class="loading-state">🔍 Searching tools...</div>';
        this.showResults();
    }
    
    showNoResults() {
        const query = this.currentQuery;
        const filters = this.getActiveFilters();
        
        this.searchResultsList.innerHTML = `
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <p><strong>No tools found</strong></p>
                <p>Try adjusting your search or filters</p>
                ${query ? `<p><small>Searched for: "${query}"</small></p>` : ''}
                ${filters.length > 0 ? `<p><small>Active filters: ${filters.join(', ')}</small></p>` : ''}
            </div>
        `;
        
        document.querySelector('.results-count').textContent = '0 tools found';
        this.showResults();
    }
    
    getActiveFilters() {
        const filters = [];
        if (this.categoryFilter.value) filters.push(this.categoryFilter.value);
        if (this.priceFilter.value) filters.push(this.priceFilter.options[this.priceFilter.selectedIndex].text);
        if (this.ratingFilter.value) filters.push(this.ratingFilter.options[this.ratingFilter.selectedIndex].text);
        return filters;
    }
    
    clearSearch() {
        this.searchInput.value = '';
        this.currentQuery = '';
        this.hideResults();
        this.searchInput.focus();
    }
    
    resetAllFilters() {
        this.categoryFilter.value = '';
        this.priceFilter.value = '';
        this.ratingFilter.value = '';
        this.applyFilters();
        
        this.trackEvent('filters_reset', {
            had_query: !!this.currentQuery
        });
    }
    
    handleKeyNavigation(e) {
        const results = this.searchResultsList.querySelectorAll('.search-result-item');
        if (results.length === 0) return;
        
        const current = this.searchResultsList.querySelector('.search-result-item.active');
        let index = current ? parseInt(current.dataset.index) : -1;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                index = Math.min(index + 1, results.length - 1);
                this.highlightResult(index);
                break;
            case 'ArrowUp':
                e.preventDefault();
                index = Math.max(index - 1, 0);
                this.highlightResult(index);
                break;
            case 'Enter':
                e.preventDefault();
                if (current) {
                    current.click();
                } else if (results[0]) {
                    results[0].click();
                }
                break;
            case 'Escape':
                this.hideResults();
                break;
        }
    }
    
    highlightResult(index) {
        const results = this.searchResultsList.querySelectorAll('.search-result-item');
        results.forEach(r => r.classList.remove('active'));
        if (results[index]) {
            results[index].classList.add('active');
            results[index].scrollIntoView({ block: 'nearest' });
        }
    }
    
    trackSearchEvents() {
        // Track search usage for analytics
        this.searchInput.addEventListener('focus', () => {
            this.trackEvent('search_focused');
        });
        
        this.searchInput.addEventListener('input', () => {
            if (this.searchInput.value.length >= 2) {
                this.trackEvent('search_query', {
                    query_length: this.searchInput.value.length,
                    has_results: this.filteredTools.length > 0
                });
            }
        });
    }
    
    trackEvent(eventName, properties = {}) {
        // Integrate with existing affiliate tracking
        if (window.affiliateTracker && window.affiliateTracker.trackEvent) {
            window.affiliateTracker.trackEvent(eventName, {
                ...properties,
                timestamp: new Date().toISOString(),
                page: window.location.pathname
            });
        }
        
        console.log('Search Event:', eventName, properties);
    }
}

// Initialize search when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('searchContainer')) {
        window.toolSearch = new ToolSearch();
        console.log('🔍 Advanced search functionality initialized');
    }
});

// Add active result highlighting styles
const style = document.createElement('style');
style.textContent = `
    .search-result-item.active {
        background: #f0f4f8 !important;
        border-left: 3px solid #dc2626;
    }
`;
document.head.appendChild(style);