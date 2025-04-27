// PawPass - Main JavaScript File

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('PawPass initialized');
    
    // Initialize color-blind mode based on stored preference
    initColorBlindMode();
    
    // Add event listeners for flash message dismissal
    initFlashMessages();
    
    // Add form validation for update and checklist forms
    initFormValidation();
    
    // Initialize PWA install functionality
    initPwaInstall();
    
    // Initialize paw print background
    initPawBackground();
});

// Color-blind mode toggle
let colorBlind = localStorage.getItem('colorBlindMode') === 'true';

function initColorBlindMode() {
    // Set initial state based on localStorage
    updateColorBlindMode();
    
    // Add event listener to toggle button if it exists
    const toggleButton = document.getElementById('color-blind-toggle');
    if (toggleButton) {
        toggleButton.addEventListener('click', toggleColorBlindMode);
    }
}

function toggleColorBlindMode() {
    colorBlind = !colorBlind;
    localStorage.setItem('colorBlindMode', colorBlind);
    updateColorBlindMode();
}

function updateColorBlindMode() {
    // Apply colorblind mode class to body element
    if (colorBlind) {
        document.body.classList.add('colorblind-mode');
    } else {
        document.body.classList.remove('colorblind-mode');
    }
    
    // Update toggle button text if it exists
    const toggleButton = document.getElementById('color-blind-toggle');
    if (toggleButton) {
        toggleButton.innerHTML = colorBlind ? 
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg> Standard Mode' : 
            '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg> Color-Blind Mode';
    }
}

// Flash messages initialization
function initFlashMessages() {
    const flashMessages = document.querySelectorAll('.flash');
    flashMessages.forEach(message => {
        // Add close button to flash messages
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.className = 'flash-close';
        closeButton.style.float = 'right';
        closeButton.style.background = 'none';
        closeButton.style.border = 'none';
        closeButton.style.cursor = 'pointer';
        closeButton.style.fontSize = '1.2rem';
        closeButton.addEventListener('click', () => {
            message.style.display = 'none';
        });
        message.prepend(closeButton);
        
        // Auto-dismiss success messages after 5 seconds
        if (message.classList.contains('flash-success')) {
            setTimeout(() => {
                message.style.display = 'none';
            }, 5000);
        }
    });
}

// Form validation
function initFormValidation() {
    // Update form validation
    const updateForm = document.getElementById('update-form');
    if (updateForm) {
        updateForm.addEventListener('submit', function(event) {
            const updateText = document.getElementById('update-text');
            if (!updateText.value.trim()) {
                event.preventDefault();
                alert('Please enter an update note before submitting.');
                updateText.focus();
            }
        });
    }
    
    // Checklist form validation
    const checklistForm = document.getElementById('checklist-form');
    if (checklistForm) {
        checklistForm.addEventListener('submit', function(event) {
            const checkboxes = checklistForm.querySelectorAll('input[type="checkbox"]');
            let atLeastOneChecked = false;
            
            checkboxes.forEach(checkbox => {
                if (checkbox.checked) {
                    atLeastOneChecked = true;
                }
            });
            
            if (!atLeastOneChecked) {
                event.preventDefault();
                alert('Please check at least one task before submitting the checklist.');
            }
        });
    }
}

// Format date and time for display
function formatDateTime(date, time) {
    // Create a date object
    const dateObj = new Date(`${date}T${time}`);
    
    // Format options
    const options = {
        weekday: 'short',
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return dateObj.toLocaleDateString('en-US', options);
}

// Function to confirm before deleting (if needed later)
function confirmDelete(itemType) {
    return confirm(`Are you sure you want to delete this ${itemType}?`);
}

// PWA Installation
let deferredPrompt;

function initPwaInstall() {
    const installButton = document.getElementById('install-button');
    
    // Hide the install button by default
    if (installButton) {
        installButton.style.display = 'none';
    }
    
    // Save the event for later use
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        
        // Show the install button
        if (installButton) {
            installButton.style.display = 'inline-block';
            
            // Add click event listener to the install button
            installButton.addEventListener('click', installPwa);
        }
    });
    
    // Listen for appinstalled event to hide the button after installation
    window.addEventListener('appinstalled', () => {
        console.log('PawPass has been installed');
        // Hide the button
        if (installButton) {
            installButton.style.display = 'none';
        }
        deferredPrompt = null;
    });
}

// Function to trigger PWA installation
function installPwa() {
    if (!deferredPrompt) {
        return;
    }
    
    // Show the installation prompt
    deferredPrompt.prompt();
    
    // Wait for the user to respond to the prompt
    deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
            console.log('User accepted the PWA installation');
        } else {
            console.log('User dismissed the PWA installation');
        }
        
        // Clear the deferred prompt
        deferredPrompt = null;
        
        // Hide the button
        const installButton = document.getElementById('install-button');
        if (installButton) {
            installButton.style.display = 'none';
        }
    });
}

// Initialize paw prints background
function initPawBackground() {
    const container = document.querySelector('.paw-bg-container');
    if (!container) return;
    
    // Create multiple paw prints with different sizes, rotations, and positions
    const pawCount = 15; // Number of paw prints to create
    
    for (let i = 0; i < pawCount; i++) {
        createPawPrint(container);
    }
}

// Create a single paw print with random properties
function createPawPrint(container) {
    const pawPrint = document.createElement('div');
    pawPrint.className = 'paw-print';
    
    // Random size between 40px and 120px
    const size = Math.floor(Math.random() * 80) + 40;
    pawPrint.style.width = `${size}px`;
    pawPrint.style.height = `${size}px`;
    
    // Random position
    const xPos = Math.floor(Math.random() * 95); // 0-95% of the container width
    const yPos = Math.floor(Math.random() * 95); // 0-95% of the container height
    pawPrint.style.left = `${xPos}%`;
    pawPrint.style.top = `${yPos}%`;
    
    // Random rotation (0-360 degrees)
    const rotation = Math.floor(Math.random() * 360);
    pawPrint.style.transform = `rotate(${rotation}deg)`;
    
    // Add to container
    container.appendChild(pawPrint);
}

// Offline data handling
function saveOfflineData(url, method, data) {
    let offlineUpdates = JSON.parse(localStorage.getItem('offlineUpdates') || '[]');
    
    offlineUpdates.push({
        url, 
        method, 
        data,
        timestamp: new Date().getTime()
    });
    
    localStorage.setItem('offlineUpdates', JSON.stringify(offlineUpdates));
    
    // Try to register a sync
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
        navigator.serviceWorker.ready.then(registration => {
            registration.sync.register('sync-updates')
                .catch(err => console.error('Sync registration failed:', err));
        });
    }
}
