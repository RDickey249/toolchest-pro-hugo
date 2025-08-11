// Advanced Conversion Optimization System
// Maximizes affiliate revenue through behavioral analysis and A/B testing

(function() {
    'use strict';

    const ConversionOptimizer = {
        config: {
            heatmapEnabled: true,
            scrollTracking: true,
            timeOnPageTracking: true,
            exitIntentEnabled: true,
            debug: false
        },

        init() {
            console.log('🚀 Conversion Optimizer initialized');
            this.setupEventTracking();
            this.setupScrollTracking();
            this.setupTimeTracking();
            this.setupExitIntent();
            this.setupABTesting();
            this.setupHeatmapData();
        },

        // Track user engagement with affiliate buttons
        setupEventTracking() {
            document.addEventListener('mouseover', (e) => {
                const affiliateBtn = e.target.closest('.affiliate-link');
                if (affiliateBtn && !affiliateBtn.hasAttribute('data-hover-tracked')) {
                    affiliateBtn.setAttribute('data-hover-tracked', 'true');
                    
                    this.trackEvent('affiliate_hover', {
                        tool: affiliateBtn.getAttribute('data-tool'),
                        category: affiliateBtn.getAttribute('data-category'),
                        position: this.getElementPosition(affiliateBtn),
                        timeToHover: this.getTimeOnPage()
                    });
                }
            });

            // Enhanced click tracking with conversion funnel data
            document.addEventListener('click', (e) => {
                const affiliateBtn = e.target.closest('.affiliate-link');
                if (affiliateBtn) {
                    this.trackConversionFunnel(affiliateBtn);
                }
            });
        },

        // Advanced scroll tracking for engagement analysis  
        setupScrollTracking() {
            let maxScroll = 0;
            let scrollMilestones = [25, 50, 75, 90, 100];
            let trackedMilestones = new Set();

            window.addEventListener('scroll', () => {
                const scrollPercent = Math.round(
                    (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
                );
                
                maxScroll = Math.max(maxScroll, scrollPercent);
                
                scrollMilestones.forEach(milestone => {
                    if (scrollPercent >= milestone && !trackedMilestones.has(milestone)) {
                        trackedMilestones.add(milestone);
                        
                        this.trackEvent('scroll_depth', {
                            depth: milestone,
                            timeToReach: this.getTimeOnPage(),
                            toolPage: document.querySelector('[data-tool-page]') ? true : false
                        });

                        // Show sticky CTA after 75% scroll
                        if (milestone === 75 && document.querySelector('.affiliate-link')) {
                            this.showStickyCTA();
                        }
                    }
                });
            });
        },

        // Time-based engagement tracking
        setupTimeTracking() {
            const startTime = Date.now();
            const timeThresholds = [30, 60, 120, 300]; // seconds
            const trackedTimes = new Set();

            setInterval(() => {
                const timeOnPage = Math.floor((Date.now() - startTime) / 1000);
                
                timeThresholds.forEach(threshold => {
                    if (timeOnPage >= threshold && !trackedTimes.has(threshold)) {
                        trackedTimes.add(threshold);
                        
                        this.trackEvent('time_on_page', {
                            duration: threshold,
                            toolPage: document.querySelector('[data-tool-page]') ? true : false,
                            scrollDepth: this.getMaxScrollDepth()
                        });

                        // Show value proposition after 2 minutes
                        if (threshold === 120) {
                            this.showValueProposition();
                        }
                    }
                });
            }, 10000); // Check every 10 seconds
        },

        // Exit intent popup for conversion recovery
        setupExitIntent() {
            let exitIntentShown = false;
            
            document.addEventListener('mouseleave', (e) => {
                if (e.clientY <= 0 && !exitIntentShown && this.getTimeOnPage() > 30) {
                    exitIntentShown = true;
                    this.showExitIntentModal();
                }
            });
        },

        // A/B testing for button colors and text
        setupABTesting() {
            // Simple A/B test for button colors
            const userId = this.getUserId();
            const variant = userId % 2 === 0 ? 'green' : 'blue';
            
            document.querySelectorAll('.affiliate-link').forEach(btn => {
                btn.setAttribute('data-variant', variant);
                if (variant === 'green') {
                    btn.style.backgroundColor = '#39FF14'; // Neon green
                } else {
                    btn.style.backgroundColor = '#007bff'; // Blue
                }
            });

            this.trackEvent('ab_test_variant', {
                variant: variant,
                userId: userId
            });
        },

        // Heatmap data collection
        setupHeatmapData() {
            let clickData = JSON.parse(localStorage.getItem('toolchest_heatmap') || '[]');
            
            document.addEventListener('click', (e) => {
                const rect = e.target.getBoundingClientRect();
                clickData.push({
                    x: e.clientX,
                    y: e.clientY,
                    element: e.target.tagName,
                    className: e.target.className,
                    timestamp: Date.now(),
                    url: window.location.pathname
                });
                
                // Keep only last 100 clicks
                if (clickData.length > 100) {
                    clickData = clickData.slice(-100);
                }
                
                localStorage.setItem('toolchest_heatmap', JSON.stringify(clickData));
            });
        },

        // Show sticky CTA for high-engagement users
        showStickyCTA() {
            if (document.querySelector('.sticky-cta')) return;
            
            const affiliateLink = document.querySelector('.affiliate-link');
            if (!affiliateLink) return;
            
            const stickyCTA = document.createElement('div');
            stickyCTA.className = 'sticky-cta';
            stickyCTA.innerHTML = `
                <div class="sticky-cta-content">
                    <span>Ready to get started?</span>
                    <a href="${affiliateLink.href}" class="btn btn-primary">
                        ${affiliateLink.textContent}
                    </a>
                    <button class="close-sticky">×</button>
                </div>
            `;
            
            // Add CSS
            const style = document.createElement('style');
            style.textContent = `
                .sticky-cta {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: white;
                    border: 2px solid #39FF14;
                    border-radius: 8px;
                    padding: 15px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    z-index: 1000;
                    max-width: 300px;
                }
                .sticky-cta-content {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .close-sticky {
                    background: none;
                    border: none;
                    font-size: 20px;
                    cursor: pointer;
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(stickyCTA);
            
            // Close button
            stickyCTA.querySelector('.close-sticky').addEventListener('click', () => {
                stickyCTA.remove();
            });
            
            this.trackEvent('sticky_cta_shown', {
                tool: affiliateLink.getAttribute('data-tool'),
                timeOnPage: this.getTimeOnPage()
            });
        },

        // Exit intent modal
        showExitIntentModal() {
            const affiliateLink = document.querySelector('.affiliate-link');
            if (!affiliateLink) return;
            
            const modal = document.createElement('div');
            modal.className = 'exit-intent-modal';
            modal.innerHTML = `
                <div class="exit-modal-overlay">
                    <div class="exit-modal-content">
                        <h3>Wait! Don't miss out</h3>
                        <p>Get started with ${affiliateLink.getAttribute('data-tool')} now and transform your workflow today.</p>
                        <div class="exit-modal-buttons">
                            <a href="${affiliateLink.href}" class="btn btn-primary">
                                ${affiliateLink.textContent}
                            </a>
                            <button class="btn btn-secondary close-modal">Maybe Later</button>
                        </div>
                    </div>
                </div>
            `;
            
            // Add CSS
            const style = document.createElement('style');
            style.textContent = `
                .exit-intent-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 10000;
                }
                .exit-modal-overlay {
                    background: rgba(0,0,0,0.8);
                    width: 100%;
                    height: 100%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .exit-modal-content {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    max-width: 400px;
                    text-align: center;
                }
                .exit-modal-buttons {
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    margin-top: 20px;
                }
            `;
            document.head.appendChild(style);
            document.body.appendChild(modal);
            
            // Close modal
            modal.querySelector('.close-modal').addEventListener('click', () => {
                modal.remove();
            });
            
            this.trackEvent('exit_intent_shown', {
                tool: affiliateLink.getAttribute('data-tool'),
                timeOnPage: this.getTimeOnPage()
            });
        },

        // Show value proposition for engaged users
        showValueProposition() {
            const toolTitle = document.querySelector('h1')?.textContent;
            if (!toolTitle) return;
            
            console.log(`💡 User highly engaged with ${toolTitle} - prime for conversion`);
            
            this.trackEvent('high_engagement_detected', {
                tool: toolTitle,
                timeOnPage: this.getTimeOnPage(),
                scrollDepth: this.getMaxScrollDepth()
            });
        },

        // Track complete conversion funnel
        trackConversionFunnel(affiliateBtn) {
            const funnelData = {
                tool: affiliateBtn.getAttribute('data-tool'),
                category: affiliateBtn.getAttribute('data-category'),
                url: affiliateBtn.href,
                timeOnPage: this.getTimeOnPage(),
                scrollDepth: this.getMaxScrollDepth(),
                previousPages: this.getSessionPageViews(),
                referrer: document.referrer,
                utmSource: this.getURLParameter('utm_source'),
                conversionStage: 'affiliate_click'
            };
            
            this.trackEvent('conversion_funnel', funnelData);
            
            // Store for potential later conversion tracking
            localStorage.setItem('toolchest_pending_conversion', JSON.stringify({
                ...funnelData,
                clickTime: Date.now()
            }));
        },

        // Utility functions
        trackEvent(eventName, data) {
            if (typeof gtag !== 'undefined') {
                gtag('event', eventName, data);
            }
            
            if (this.config.debug) {
                console.log(`📊 Event: ${eventName}`, data);
            }
        },

        getUserId() {
            let userId = localStorage.getItem('toolchest_user_id');
            if (!userId) {
                userId = Date.now().toString(36) + Math.random().toString(36).substr(2);
                localStorage.setItem('toolchest_user_id', userId);
            }
            return userId;
        },

        getTimeOnPage() {
            const startTime = parseInt(sessionStorage.getItem('pageStartTime') || Date.now());
            return Math.floor((Date.now() - startTime) / 1000);
        },

        getMaxScrollDepth() {
            return Math.round(
                (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
            );
        },

        getElementPosition(element) {
            const rect = element.getBoundingClientRect();
            return {
                x: rect.left,
                y: rect.top,
                width: rect.width,
                height: rect.height
            };
        },

        getSessionPageViews() {
            return parseInt(sessionStorage.getItem('pageViews') || '1');
        },

        getURLParameter(param) {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get(param);
        }
    };

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => ConversionOptimizer.init());
    } else {
        ConversionOptimizer.init();
    }

    // Store page start time
    sessionStorage.setItem('pageStartTime', Date.now());
    
    // Increment page views
    const pageViews = parseInt(sessionStorage.getItem('pageViews') || '0') + 1;
    sessionStorage.setItem('pageViews', pageViews);

    // Export for external use
    window.ConversionOptimizer = ConversionOptimizer;

})();