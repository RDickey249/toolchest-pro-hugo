// Enhanced Search with Autocomplete and Instant Results
class ToolSearch {
    constructor() {
        // Page search elements
        this.searchInput = document.getElementById('searchInput');
        this.searchResults = document.getElementById('searchResults');
        this.searchResultsList = document.getElementById('searchResultsList');
        this.clearSearch = document.getElementById('clearSearch');
        
        // Header search elements
        this.headerSearchInput = document.getElementById('headerSearchInput');
        this.headerSearchResults = document.getElementById('headerSearchResults');
        this.headerSearchResultsList = document.getElementById('headerSearchResultsList');
        this.headerClearSearch = document.getElementById('headerClearSearch');
        
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
            const data = await response.json();
            this.tools = data.tools || [];
            console.log(`Loaded ${this.tools.length} tools for search`);
        } catch (error) {
            console.error('Failed to load tools data:', error);
            this.tools = [];
        }
    }
    
    bindEvents() {
        // Debounce function
        this.debounce = (func, wait) => {
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
        
        // Page search events
        if (this.searchInput) {
            this.searchInput.addEventListener('input', this.debounce(() => {
                this.handleSearch('page');
            }, 200));
            
            this.searchInput.addEventListener('focus', () => {
                if (this.searchInput.value.length >= 2) {
                    this.handleSearch('page');
                }
            });
        }
        
        // Header search events
        if (this.headerSearchInput) {
            this.headerSearchInput.addEventListener('input', this.debounce(() => {
                this.handleSearch('header');
            }, 200));
            
            this.headerSearchInput.addEventListener('focus', () => {
                if (this.headerSearchInput.value.length >= 2) {
                    this.handleSearch('header');
                }
            });
        }
        
        // Clear events
        if (this.clearSearch) {
            this.clearSearch.addEventListener('click', () => this.clearSearchQuery('page'));
        }
        if (this.headerClearSearch) {
            this.headerClearSearch.addEventListener('click', () => this.clearSearchQuery('header'));
        }
        
        // Outside click detection
        document.addEventListener('click', (e) => {
            // Close page search if clicking outside
            if (this.searchResults && !this.searchResults.contains(e.target) && 
                !this.searchInput?.contains(e.target)) {
                this.hideResults('page');
            }
            
            // Close header search if clicking outside
            if (this.headerSearchResults && !this.headerSearchResults.contains(e.target) && 
                !this.headerSearchInput?.contains(e.target)) {
                this.hideResults('header');
            }
        });
        
        // Handle Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideResults('page');
                this.hideResults('header');
            }
        });
    }
    
    handleSearch(context = 'page') {
        const input = context === 'header' ? this.headerSearchInput : this.searchInput;
        const query = input.value.trim();
        
        if (query.length < 2) {
            this.hideResults(context);
            return;
        }
        
        this.performSearch(query, context);
    }
    
    performSearch(query, context = 'page') {
        const normalizedQuery = query.toLowerCase();
        
        // Score and rank results
        const results = this.tools
            .map(tool => {
                let score = 0;
                const normalizedTitle = tool.title.toLowerCase();
                const normalizedTagline = tool.tagline ? tool.tagline.toLowerCase() : '';
                const normalizedCategory = tool.category ? tool.category.toLowerCase() : '';
                const normalizedSubcategory = tool.subcategory ? tool.subcategory.toLowerCase() : '';
                const normalizedKeywords = tool.keywords ? tool.keywords.toLowerCase() : '';
                
                // Exact title match
                if (normalizedTitle === normalizedQuery) score += 100;
                // Title starts with query
                else if (normalizedTitle.startsWith(normalizedQuery)) score += 50;
                // Title contains query
                else if (normalizedTitle.includes(normalizedQuery)) score += 30;
                
                // Tagline matches
                if (normalizedTagline.includes(normalizedQuery)) score += 20;
                
                // Category/subcategory matches
                if (normalizedCategory.includes(normalizedQuery)) score += 25;
                if (normalizedSubcategory.includes(normalizedQuery)) score += 15;
                
                // Keywords matches (HIGH PRIORITY for feature search)
                if (normalizedKeywords.includes(normalizedQuery)) score += 35;
                
                // Boost affiliate tools for revenue optimization
                if (tool.url && (tool.url.includes('shopify.pxf.io') || tool.url.includes('plrfunnels.com') || 
                                tool.url.includes('activecampaign') || tool.url.includes('systeme.io') ||
                                tool.url.includes('saleshandy') || tool.url.includes('customers-ai'))) {
                    score += 5;
                }
                
                return { ...tool, score };
            })
            .filter(tool => tool.score > 0)
            .sort((a, b) => b.score - a.score)
            .slice(0, 20); // Limit to top 20 results
        
        this.displayResults(results, query, context);
        
        // Track search
        this.trackEvent('search_performed', {
            query: query,
            results_count: results.length,
            context: context
        });
    }
    
    displayResults(results, query, context = 'page') {
        const resultsList = context === 'header' ? this.headerSearchResultsList : this.searchResultsList;
        const resultsContainer = context === 'header' ? this.headerSearchResults : this.searchResults;
        const resultsCount = resultsContainer.querySelector('.results-count');
        
        if (results.length === 0) {
            resultsList.innerHTML = `
                <div class="no-results">
                    <div class="no-results-icon">🔍</div>
                    <p><strong>No tools found for "${query}"</strong></p>
                    <p>Try different keywords or browse categories</p>
                </div>
            `;
            resultsCount.textContent = '0 tools found';
        } else {
            const resultsHTML = results.map((tool, index) => `
                <div class="search-result-item" data-index="${index}" onclick="window.location.href='${tool.url}'">
                    <div class="search-result-info">
                        <div class="search-result-title">
                            ${tool.title}
                            ${tool.affiliate_link ? '<span class="affiliate-indicator">💰</span>' : ''}
                        </div>
                        <div class="search-result-meta">
                            ${tool.tagline || 'Professional tool solution'}
                            <span class="search-result-category">${tool.category}</span>
                        </div>
                    </div>
                </div>
            `).join('');
            
            resultsList.innerHTML = resultsHTML;
            resultsCount.textContent = `${results.length} tool${results.length !== 1 ? 's' : ''} found`;
        }
        
        this.showResults(context);
    }
    
    showResults(context = 'page') {
        const resultsContainer = context === 'header' ? this.headerSearchResults : this.searchResults;
        if (resultsContainer) {
            resultsContainer.style.display = 'block';
        }
    }
    
    hideResults(context = 'page') {
        const resultsContainer = context === 'header' ? this.headerSearchResults : this.searchResults;
        if (resultsContainer) {
            resultsContainer.style.display = 'none';
        }
    }
    
    clearSearchQuery(context = 'page') {
        const input = context === 'header' ? this.headerSearchInput : this.searchInput;
        if (input) {
            input.value = '';
            input.focus();
        }
        this.hideResults(context);
        
        this.trackEvent('search_cleared', { context: context });
    }
    
    trackSearchEvents() {
        // Track when search is focused
        if (this.searchInput) {
            this.searchInput.addEventListener('focus', () => {
                this.trackEvent('search_focused', { context: 'page' });
            });
        }
        
        if (this.headerSearchInput) {
            this.headerSearchInput.addEventListener('focus', () => {
                this.trackEvent('search_focused', { context: 'header' });
            });
        }
    }
    
    trackEvent(eventName, data = {}) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', eventName, {
                event_category: 'Search',
                ...data
            });
        }
        
        // Console logging for debugging
        console.log(`Search Event: ${eventName}`, data);
    }
}

// Initialize search when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new ToolSearch();
    });
} else {
    new ToolSearch();
}