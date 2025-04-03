
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

function toggleMenu() {
    const navButton = document.getElementById("navButton");
    navButton.classList.toggle("btn-toggle");


    const navMenu = document.getElementById("navMenu");
    navMenu.classList.toggle("open");
    navMenu.classList.toggle("hidden");
}


document.addEventListener('DOMContentLoaded', function () {
  const navLinks = document.querySelectorAll('.nb-nav-menu a');

  navLinks.forEach(link => {
    link.addEventListener('click', function (e) {
      e.preventDefault();

      const targetId = this.getAttribute('href');
      console.log(targetId)
      const targetElement = document.getElementById(targetId);
      console.log(targetElement)

      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop - 70,
          behavior: 'smooth'
        });
      }
    });
  });
});

// Apply theme to document
function applyTheme(theme) {
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
    icon.textContent = theme === 'dark' ? '⽇' : '⺝';
    icon.setAttribute('aria-label', theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  }
}

// Toggle between light and dark themes
function toggleTheme() {
  const currentTheme = localStorage.getItem('theme') || 'light';
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  applyTheme(newTheme);
}

function adjustControlsMenu() {
  const controlsMenu = document.querySelector(".controls");
  const footer = document.querySelector("footer");

  if (!controlsMenu || !footer) return;

  const footerRect = footer.getBoundingClientRect();
  const controlsRect = controlsMenu.getBoundingClientRect();
  const windowHeight = window.innerHeight;

  console.log("viewport:"+window.visualViewport);

  console.log("header" + controlsRect.bottom)
  console.log("footer" + footerRect.top)

  if (controlsRect.bottom > footerRect.top) {
    // Move the buttons above the footer
    controlsMenu.style.bottom = `${windowHeight - footerRect.top + 10}px`;
  } else {
    // Reset to default bottom positioning
    controlsMenu.style.bottom = "20px";
  }
}



// Initialize everything
function init() {
  const initialTheme = getInitialTheme();
  applyTheme(initialTheme);


  // adjustControlsMenu()

  // const content = document.querySelector(".content");
  // content.addEventListener("scroll", adjustControlsMenu);
  // window.addEventListener("resize", adjustControlsMenu);
}


// Run when DOM is fully loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}