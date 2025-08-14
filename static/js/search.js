// Simple Working Search Implementation
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('headerSearchInput');
    const searchResults = document.getElementById('headerSearchResults');
    const searchResultsList = document.getElementById('headerSearchResultsList');
    
    if (!searchInput) return; // Exit if no search input found
    
    let tools = [];
    
    // Load tools data
    fetch('/index.json')
        .then(response => response.json())
        .then(data => {
            tools = data.tools || [];
            console.log('Search ready with ' + tools.length + ' tools');
        })
        .catch(error => {
            console.error('Search disabled - could not load data');
            tools = [];
        });
    
    // Simple search on input
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        
        if (query.length < 2) {
            searchResults.style.display = 'none';
            return;
        }
        
        // Basic search matching
        const results = tools.filter(tool => {
            const title = (tool.title || '').toLowerCase();
            const tagline = (tool.tagline || '').toLowerCase();
            const keywords = (tool.keywords || '').toLowerCase();
            
            return title.includes(query) || 
                   tagline.includes(query) || 
                   keywords.includes(query);
        }).slice(0, 10); // Limit to 10 results
        
        displayResults(results);
    });
    
    function displayResults(results) {
        if (results.length === 0) {
            searchResultsList.innerHTML = '<div style="padding: 1rem; color: #666;">No tools found</div>';
        } else {
            searchResultsList.innerHTML = results.map(tool => `
                <a href="${tool.url}" style="display: block; padding: 0.75rem; text-decoration: none; color: #333; border-bottom: 1px solid #eee;">
                    <strong>${tool.title}</strong><br>
                    <span style="color: #666; font-size: 0.9em;">${tool.tagline || ''}</span>
                </a>
            `).join('');
        }
        
        searchResults.style.display = 'block';
    }
    
    // Hide results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.style.display = 'none';
        }
    });
});