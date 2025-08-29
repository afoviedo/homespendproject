// Widget Configuration for HomeSpend
// This script provides additional configuration for better widget behavior

(function() {
    'use strict';
    
    // Configuration object
    const config = {
        // Z-index levels
        zIndex: {
            base: 1,
            dropdown: 10000,
            datePicker: 10000,
            sidebar: 1045,
            navbar: 1030,
            modal: 1050,
            tooltip: 1070,
            popover: 1060
        },
        
        // Timing delays
        delays: {
            sidebar: 150,
            theme: 200,
            navigation: 300,
            widget: 50,
            periodic: 2000
        },
        
        // Selectors
        selectors: {
            dropdown: '.Select-control',
            dropdownMenu: '.Select-menu-outer',
            datePicker: '.DateRangePickerInput',
            datePickerMenu: '.DateRangePicker_picker',
            sidebar: '#sidebar',
            sidebarToggle: '#sidebar-toggle',
            themeToggle: '#theme-toggle'
        }
    };
    
    // Function to apply configuration
    function applyConfiguration() {
        // Apply z-index configuration
        Object.keys(config.zIndex).forEach(function(key) {
            const value = config.zIndex[key];
            const elements = document.querySelectorAll(`[data-z-index="${key}"]`);
            elements.forEach(function(element) {
                element.style.zIndex = value;
            });
        });
        
        // Apply specific widget configurations
        applyDropdownConfiguration();
        applyDatePickerConfiguration();
    }
    
    // Configure dropdowns
    function applyDropdownConfiguration() {
        const dropdowns = document.querySelectorAll(config.selectors.dropdown);
        dropdowns.forEach(function(dropdown) {
            // Ensure proper positioning
            dropdown.style.position = 'relative';
            dropdown.style.zIndex = config.zIndex.base;
            
            // Add event listeners for better stability
            dropdown.addEventListener('focus', function() {
                this.style.zIndex = config.zIndex.dropdown;
            });
            
            dropdown.addEventListener('blur', function() {
                setTimeout(() => {
                    if (!this.classList.contains('is-open')) {
                        this.style.zIndex = config.zIndex.base;
                    }
                }, 100);
            });
        });
    }
    
    // Configure date pickers
    function applyDatePickerConfiguration() {
        const datePickers = document.querySelectorAll(config.selectors.datePicker);
        datePickers.forEach(function(picker) {
            // Ensure proper positioning
            picker.style.position = 'relative';
            picker.style.zIndex = config.zIndex.base;
            
            // Add event listeners for better stability
            picker.addEventListener('focus', function() {
                this.style.zIndex = config.zIndex.datePicker;
            });
            
            picker.addEventListener('blur', function() {
                setTimeout(() => {
                    const pickerMenu = document.querySelector(config.selectors.datePickerMenu);
                    if (!pickerMenu || pickerMenu.style.display === 'none') {
                        this.style.zIndex = config.zIndex.base;
                    }
                }, 100);
            });
        });
    }
    
    // Function to handle sidebar interactions
    function handleSidebarInteraction() {
        const sidebar = document.querySelector(config.selectors.sidebar);
        if (sidebar) {
            // When sidebar opens, ensure widgets are properly positioned
            const observer = new MutationObserver(function(mutations) {
                mutations.forEach(function(mutation) {
                    if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        const isOpen = sidebar.classList.contains('show');
                        if (isOpen) {
                            setTimeout(applyConfiguration, config.delays.sidebar);
                        }
                    }
                });
            });
            
            observer.observe(sidebar, {
                attributes: true,
                attributeFilter: ['class']
            });
        }
    }
    
    // Function to handle theme changes
    function handleThemeChanges() {
        const themeToggle = document.querySelector(config.selectors.themeToggle);
        if (themeToggle) {
            themeToggle.addEventListener('click', function() {
                setTimeout(applyConfiguration, config.delays.theme);
            });
        }
    }
    
    // Function to handle navigation
    function handleNavigation() {
        window.addEventListener('popstate', function() {
            setTimeout(applyConfiguration, config.delays.navigation);
        });
        
        // Listen for Dash navigation events
        if (window.dash_clientside) {
            const originalNoUpdate = window.dash_clientside.no_update;
            window.dash_clientside.no_update = function() {
                if (originalNoUpdate) {
                    originalNoUpdate();
                }
                setTimeout(applyConfiguration, config.delays.widget);
            };
        }
    }
    
    // Initialize configuration
    function initialize() {
        // Apply initial configuration
        applyConfiguration();
        
        // Set up event handlers
        handleSidebarInteraction();
        handleThemeChanges();
        handleNavigation();
        
        // Periodic configuration check
        setInterval(applyConfiguration, config.delays.periodic);
        
        // Configuration on window focus
        window.addEventListener('focus', function() {
            setTimeout(applyConfiguration, 100);
        });
        
        // Configuration on DOM changes
        const observer = new MutationObserver(function(mutations) {
            let shouldApply = false;
            
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) {
                            if (node.classList && (
                                node.classList.contains('Select-control') ||
                                node.classList.contains('DateRangePickerInput') ||
                                node.classList.contains('Select-menu-outer') ||
                                node.classList.contains('DateRangePicker_picker')
                            )) {
                                shouldApply = true;
                            }
                        }
                    });
                }
            });
            
            if (shouldApply) {
                setTimeout(applyConfiguration, config.delays.widget);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }
    
    // Export configuration for external use
    window.HomeSpendWidgetConfig = config;
    
})();
