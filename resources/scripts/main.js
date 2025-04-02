// Smooth scroll functionality for navigation links
document.querySelectorAll('nav a').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const targetId = this.getAttribute('href').slice(1);
        const targetElement = document.getElementById(targetId);
        
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    });
});


// Check for saved theme preference or use system preference
function getInitialTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    return savedTheme;
  }
  
  // Check for system preference
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return 'dark';
  }
  
  return 'light';
}

// Apply theme to document
function applyTheme(theme) {
  let themeLink = document.getElementById('theme-colors');
  
  if (!themeLink) {
    themeLink = document.createElement('link');
    themeLink.id = 'theme-colors';
    themeLink.rel = 'stylesheet';
    document.head.appendChild(themeLink);
  }

   // Set the appropriate CSS file based on theme
  themeLink.href = theme === 'dark' ? 'styles/colors_dark.css' : 'styles/colors.css';
  
  // Save theme preference
  localStorage.setItem('theme', theme);
  
  // Update button icon
  updateButtonIcon(theme);
  
  // Add a data attribute to the body for any additional styling
  document.body.setAttribute('data-theme', theme);
  
  // Save theme preference
  localStorage.setItem('theme', theme);
  
  // Update button icon
  updateButtonIcon(theme);
}

// Update the button icon based on current theme
function updateButtonIcon(theme) {
  const icon = document.getElementById('theme-toggle-icon');
  if (icon) {
    icon.textContent = theme === 'dark' ? '☀️' : '🌙';
    icon.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  }
}

// Toggle between light and dark themes
function toggleTheme() {
  const currentTheme = localStorage.getItem('theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  applyTheme(newTheme);
}

// Create and add theme toggle button
function createToggleButton() {
  const button = document.createElement('button');
  button.id = 'theme-toggle-btn';
  button.className = 'theme-toggle';
  
  const icon = document.createElement('span');
  icon.id = 'theme-toggle-icon';
  button.appendChild(icon);
  
  // Style the button
  button.style.position = 'fixed';
  button.style.bottom = '20px';
  button.style.right = '20px';
  button.style.width = '50px';
  button.style.height = '50px';
  button.style.borderRadius = '50%';
  button.style.backgroundColor = '#ffffff';
  button.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.2)';
  button.style.border = 'none';
  button.style.cursor = 'pointer';
  button.style.display = 'flex';
  button.style.alignItems = 'center';
  button.style.justifyContent = 'center';
  button.style.fontSize = '24px';
  button.style.zIndex = '9999';
  button.style.transition = 'transform 0.3s ease';
  
  // Add hover effect
  button.onmouseenter = () => {
    button.style.transform = 'scale(1.1)';
  };
  button.onmouseleave = () => {
    button.style.transform = 'scale(1)';
  };
  
  // Add click event
  button.addEventListener('click', toggleTheme);
  
  document.body.appendChild(button);
}

// Add CSS for dark theme
function addThemeStyles() {
  const style = document.createElement('style');
  style.textContent = `
    .dark-theme {
      --bg-color: #121212;
      --text-color: #e0e0e0;
      --link-color: #90caf9;
      --border-color: #333;
      --card-bg: #1e1e1e;
    }
    
    .dark-theme body {
      background-color: var(--bg-color);
      color: var(--text-color);
    }
    
    .dark-theme a {
      color: var(--link-color);
    }
    
    .dark-theme input, 
    .dark-theme textarea, 
    .dark-theme select {
      background-color: #2d2d2d;
      color: var(--text-color);
      border-color: var(--border-color);
    }
    
    .dark-theme button {
      background-color: #333;
      color: var(--text-color);
    }
    
    .dark-theme .theme-toggle {
      background-color: #333;
    }
    
    /* Add transition for smooth theme switching */
    body, button, input, a, textarea, select {
      transition: background-color 0.3s ease, color 0.3s ease, border-color 0.3s ease;
    }
  `;
  
  document.head.appendChild(style);
}

// Initialize everything
function init() {
  addThemeStyles();
  createToggleButton();
  
  // Apply initial theme
  const initialTheme = getInitialTheme();
  applyTheme(initialTheme);
}

// Run when DOM is fully loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}