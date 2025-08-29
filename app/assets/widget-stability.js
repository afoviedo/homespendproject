// Widget Stability Enhancement for HomeSpend
// This script ensures proper z-index management and widget stability

(function() {
    'use strict';
    
    // Function to fix z-index issues
    function fixZIndexIssues() {
        // Fix dropdown menus
        const dropdowns = document.querySelectorAll('.Select-control');
        dropdowns.forEach(function(dropdown) {
            dropdown.style.position = 'relative';
            dropdown.style.zIndex = '1';
        });
        
        // Fix dropdown menus when open
        const openDropdowns = document.querySelectorAll('.Select-control.is-open');
        openDropdowns.forEach(function(dropdown) {
            const menu = dropdown.querySelector('.Select-menu-outer');
            if (menu) {
                menu.style.zIndex = '10002';
                menu.style.position = 'absolute';
            }
        });
        
        // Fix DatePicker
        const datePickers = document.querySelectorAll('.DateRangePickerInput');
        datePickers.forEach(function(picker) {
            picker.style.position = 'relative';
            picker.style.zIndex = '1';
        });
        
        // Fix DatePicker when open
        const openDatePickers = document.querySelectorAll('.DateRangePicker_picker');
        openDatePickers.forEach(function(picker) {
            picker.style.zIndex = '10002';
            picker.style.position = 'absolute';
        });
    }
    
    // Function to handle sidebar state changes
    function handleSidebarChange() {
        setTimeout(function() {
            fixZIndexIssues();
        }, 150);
    }
    
    // Function to handle theme changes
    function handleThemeChange() {
        setTimeout(function() {
            fixZIndexIssues();
        }, 200);
    }
    
    // Function to handle page navigation
    function handlePageNavigation() {
        setTimeout(function() {
            fixZIndexIssues();
        }, 300);
    }
    
    // Observer for DOM changes
    const observer = new MutationObserver(function(mutations) {
        let shouldFix = false;
        
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                // Check if dropdowns or date pickers were added
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && (
                            node.classList.contains('Select-menu-outer') ||
                            node.classList.contains('DateRangePicker_picker') ||
                            node.classList.contains('Select-control') ||
                            node.classList.contains('DateRangePickerInput')
                        )) {
                            shouldFix = true;
                        }
                    }
                });
            }
        });
        
        if (shouldFix) {
            setTimeout(function() {
                fixZIndexIssues();
            }, 50);
        }
    });
    
    // Start observing when DOM is ready
    function initialize() {
        // Initial fix
        fixZIndexIssues();
        
        // Start observing
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        // Listen for sidebar toggle events
        document.addEventListener('click', function(e) {
            if (e.target && e.target.id === 'sidebar-toggle') {
                handleSidebarChange();
            }
        });
        
        // Listen for theme toggle events
        document.addEventListener('click', function(e) {
            if (e.target && e.target.id === 'theme-toggle') {
                handleThemeChange();
            }
        });
        
        // Listen for navigation events
        window.addEventListener('popstate', handlePageNavigation);
        
        // Fix issues periodically (every 2 seconds)
        setInterval(fixZIndexIssues, 2000);
        
        // Fix issues when window gains focus
        window.addEventListener('focus', function() {
            setTimeout(fixZIndexIssues, 100);
        });
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Also initialize when Dash updates the page
    if (window.dash_clientside) {
        window.dash_clientside.no_update = function() {
            setTimeout(fixZIndexIssues, 100);
        };
    }
    
})();
