// Affiliate Link Tracking System
// Tracks clicks, conversions, and revenue for ToolChest Pro

(function() {
    'use strict';

    // Configuration
    const config = {
        trackingEndpoint: '/api/track-affiliate', // Future endpoint for tracking
        debug: false,
        storage: 'localStorage'
    };

    // Utility functions
    function log(message, data = null) {
        if (config.debug) {
            console.log('[Affiliate Tracker]', message, data);
        }
    }

    function generateClickId() {
        return 'click_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    function getSessionData() {
        const sessionKey = 'toolchest_session';
        let session = JSON.parse(localStorage.getItem(sessionKey) || '{}');
        
        if (!session.id) {
            session = {
                id: 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9),
                startTime: Date.now(),
                pageViews: 0,
                affiliateClicks: 0
            };
            localStorage.setItem(sessionKey, JSON.stringify(session));
        }
        
        return session;
    }

    function updateSessionData(updates) {
        const sessionKey = 'toolchest_session';
        let session = getSessionData();
        Object.assign(session, updates);
        localStorage.setItem(sessionKey, JSON.stringify(session));
        return session;
    }

    // Main tracking function
    function trackAffiliateClick(toolName, category, affiliateUrl) {
        const clickId = generateClickId();
        const session = getSessionData();
        const timestamp = Date.now();
        
        const clickData = {
            clickId: clickId,
            sessionId: session.id,
            toolName: toolName,
            category: category,
            affiliateUrl: affiliateUrl,
            timestamp: timestamp,
            userAgent: navigator.userAgent,
            referrer: document.referrer,
            pageUrl: window.location.href,
            sessionPageViews: session.pageViews,
            sessionAffiliateClicks: session.affiliateClicks + 1
        };

        // Update session
        updateSessionData({
            affiliateClicks: session.affiliateClicks + 1,
            lastAffiliateClick: timestamp
        });

        // Store click data
        const clicksKey = 'toolchest_affiliate_clicks';
        let clicks = JSON.parse(localStorage.getItem(clicksKey) || '[]');
        clicks.push(clickData);
        
        // Keep only last 50 clicks to prevent storage bloat
        if (clicks.length > 50) {
            clicks = clicks.slice(-50);
        }
        
        localStorage.setItem(clicksKey, JSON.stringify(clicks));

        // Send to analytics (Google Analytics 4 if available)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'affiliate_click', {
                'tool_name': toolName,
                'category': category,
                'affiliate_url': affiliateUrl,
                'click_id': clickId,
                'session_id': session.id
            });
        }

        // Send to tracking endpoint (future implementation)
        if (config.trackingEndpoint) {
            fetch(config.trackingEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(clickData)
            }).catch(error => {
                log('Tracking endpoint error:', error);
            });
        }

        log('Affiliate click tracked:', clickData);
        
        // Visual feedback
        const clickedLink = event.target.closest('.affiliate-link');
        if (clickedLink) {
            clickedLink.setAttribute('data-tracked', 'true');
            clickedLink.style.opacity = '0.8';
            setTimeout(() => {
                clickedLink.style.opacity = '1';
            }, 300);
        }
    }

    // Page view tracking
    function trackPageView() {
        const session = updateSessionData({
            pageViews: getSessionData().pageViews + 1,
            lastPageView: Date.now()
        });

        // Track tool page views specifically
        const isToolPage = document.querySelector('[data-premium-zone="tool-page"]');
        if (isToolPage) {
            const toolTitle = document.querySelector('h1')?.textContent;
            const category = document.querySelector('.category-tag')?.textContent;
            
            log('Tool page view:', {
                tool: toolTitle,
                category: category,
                sessionId: session.id
            });

            // Send to GA4 if available
            if (typeof gtag !== 'undefined') {
                gtag('event', 'tool_page_view', {
                    'tool_name': toolTitle,
                    'category': category,
                    'session_id': session.id
                });
            }
        }
    }

    // Initialize tracking
    function init() {
        log('Affiliate tracking initialized');
        
        // Track page view
        trackPageView();

        // Add click tracking to all affiliate links
        document.addEventListener('click', function(event) {
            const affiliateLink = event.target.closest('.affiliate-link');
            if (affiliateLink) {
                const toolName = affiliateLink.getAttribute('data-tool');
                const category = affiliateLink.getAttribute('data-category');
                const url = affiliateLink.href;
                
                if (toolName && category) {
                    trackAffiliateClick(toolName, category, url);
                }
            }
        });

        // Track affiliate link impressions (when they come into view)
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const link = entry.target;
                        const toolName = link.getAttribute('data-tool');
                        const category = link.getAttribute('data-category');
                        
                        if (toolName && !link.hasAttribute('data-impression-tracked')) {
                            link.setAttribute('data-impression-tracked', 'true');
                            
                            log('Affiliate link impression:', {
                                tool: toolName,
                                category: category
                            });

                            // Send to GA4 if available
                            if (typeof gtag !== 'undefined') {
                                gtag('event', 'affiliate_impression', {
                                    'tool_name': toolName,
                                    'category': category
                                });
                            }
                        }
                    }
                });
            }, {
                threshold: 0.5,
                rootMargin: '0px 0px -50px 0px'
            });

            // Observe all affiliate links
            document.querySelectorAll('.affiliate-link').forEach(link => {
                observer.observe(link);
            });
        }
    }

    // Export tracking function globally
    window.trackAffiliateClick = trackAffiliateClick;

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Analytics helper functions
    window.ToolChestAnalytics = {
        getSessionData: getSessionData,
        getAffiliateClicks: function() {
            return JSON.parse(localStorage.getItem('toolchest_affiliate_clicks') || '[]');
        },
        clearData: function() {
            localStorage.removeItem('toolchest_session');
            localStorage.removeItem('toolchest_affiliate_clicks');
            log('Analytics data cleared');
        },
        exportData: function() {
            return {
                session: getSessionData(),
                clicks: JSON.parse(localStorage.getItem('toolchest_affiliate_clicks') || '[]')
            };
        }
    };

})();