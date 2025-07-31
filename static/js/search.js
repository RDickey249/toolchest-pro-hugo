/**
 * ToolChest Pro - Client-side Search Functionality
 * Searches across all 1,296 tools using pre-built index
 */

class ToolSearch {
    constructor() {
        this.searchIndex = null;
        this.currentResults = [];
        this.isIndexLoaded = false;
        this.initializeSearch();
    }

    async initializeSearch() {
        try {
            // Load the search index
            const response = await fetch('/search-index.json');
            this.searchIndex = await response.json();
            this.isIndexLoaded = true;
            // Search index loaded successfully
        } catch (error) {
            console.error('Failed to load search index:', error);
        }
    }

    search(query) {
        if (!this.isIndexLoaded || !query.trim()) {
            return [];
        }

        const searchTerm = query.toLowerCase().trim();
        const results = [];

        this.searchIndex.forEach(tool => {
            let score = 0;
            
            // Title match (highest priority)
            if (tool.title.toLowerCase().includes(searchTerm)) {
                score += 10;
            }
            
            // Category match
            if (tool.category.toLowerCase().includes(searchTerm)) {
                score += 5;
            }
            
            // Tagline match
            if (tool.tagline && tool.tagline.toLowerCase().includes(searchTerm)) {
                score += 3;
            }
            
            // Description match (if available)
            if (tool.description && tool.description.toLowerCase().includes(searchTerm)) {
                score += 2;
            }

            // Tags match
            if (tool.tags && tool.tags.some(tag => tag.toLowerCase().includes(searchTerm))) {
                score += 4;
            }

            if (score > 0) {
                results.push({
                    ...tool,
                    score: score
                });
            }
        });

        // Sort by relevance score
        results.sort((a, b) => b.score - a.score);
        
        // Limit to top 20 results
        return results.slice(0, 20);
    }

    displayResults(results, container) {
        if (!container) return;

        if (results.length === 0) {
            container.innerHTML = '<div class="search-no-results">No tools found matching your search.</div>';
            return;
        }

        const resultsHTML = results.map(tool => `
            <div class="search-result-item">
                <div class="search-result-header">
                    <h3 class="search-result-title">
                        <a href="${tool.url}" class="search-result-link">${tool.title}</a>
                    </h3>
                    <span class="search-result-category">${tool.category}</span>
                </div>
                <p class="search-result-tagline">${tool.tagline || 'Professional tool for enhanced productivity'}</p>
                <div class="search-result-meta">
                    <span class="search-result-subcategory">${tool.subcategory}</span>
                    ${tool.tags ? `<div class="search-result-tags">${tool.tags.slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}</div>` : ''}
                </div>
            </div>
        `).join('');

        container.innerHTML = `
            <div class="search-results-header">
                <h2>Search Results (${results.length})</h2>
            </div>
            <div class="search-results-list">
                ${resultsHTML}
            </div>
        `;
    }

    setupSearchInterface() {
        // Create search box if it doesn't exist
        const existingSearch = document.querySelector('.toolchest-search');
        if (existingSearch) return;

        const searchHTML = `
            <div class="toolchest-search">
                <div class="search-container">
                    <input type="text" 
                           id="toolchest-search-input" 
                           class="search-input" 
                           placeholder="Search 1,296 tools..." 
                           autocomplete="off">
                    <div id="search-results-container" class="search-results-container" style="display: none;"></div>
                </div>
            </div>
        `;

        // Insert search box at the top of main content
        const mainContent = document.querySelector('main') || document.querySelector('.app-main');
        if (mainContent) {
            mainContent.insertAdjacentHTML('afterbegin', searchHTML);
            this.bindSearchEvents();
        }
    }

    bindSearchEvents() {
        const searchInput = document.getElementById('toolchest-search-input');
        const resultsContainer = document.getElementById('search-results-container');
        
        if (!searchInput || !resultsContainer) return;

        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            const query = e.target.value;

            if (query.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }

            // Debounce search for performance
            searchTimeout = setTimeout(() => {
                const results = this.search(query);
                this.displayResults(results, resultsContainer);
                resultsContainer.style.display = 'block';
            }, 300);
        });

        // Hide results when clicking outside
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
                resultsContainer.style.display = 'none';
            }
        });

        // Show results when focusing on search input
        searchInput.addEventListener('focus', () => {
            if (searchInput.value.length >= 2 && this.currentResults.length > 0) {
                resultsContainer.style.display = 'block';
            }
        });
    }
}

// Initialize search when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const toolSearch = new ToolSearch();
    
    // Setup search interface after a brief delay to ensure page is ready
    setTimeout(() => {
        toolSearch.setupSearchInterface();
    }, 500);
});