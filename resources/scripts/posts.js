function createNavMenuFromAnchors() {
  // Find all anchor links on the page
  const anchors = document.querySelectorAll('.anchor-link');
  
  // Skip if no anchor links found
  if (anchors.length === 0) {
    console.log('No anchor links found on this page');
    return;
  }
  
  // Create the navigation menu container
  const navMenu = document.getElementById('nb-nav-menu');
  
  // Create the list for navigation items
  const navList = document.createElement('ul');
  navList.className = 'nav-list';
  
  // Create element to display current section title
  const currentSectionDisplay = document.createElement('div');
  currentSectionDisplay.id = 'current-section';
  currentSectionDisplay.className = 'current-section-display';
  
  // Find the nav-button to place the current section display next to it
  const navButton = document.querySelector('.nav-button');
  if (navButton && navButton.parentNode) {
    navButton.parentNode.insertBefore(currentSectionDisplay, navButton.nextSibling);
  }
  
  // Store anchor elements and their corresponding sections for intersection observer
  const anchorElements = [];
  
  // Process each anchor link
  anchors.forEach((anchor, index) => {
    // Skip empty anchors or those without text content
    if (!anchor.textContent.trim()) return;
    
    const anchorRef = anchor.getAttribute('href');
    const anchorType = anchor.parentElement.nodeName;
    const navText = '  '.repeat(anchorType.replace(/[^0-9]/g, '') - 1);
    const navInner = document.createElement(anchorType);
    navInner.textContent = `${navText}${anchorRef.substring(1)}`;
    
    // Create the navigation link
    const navLink = document.createElement('a');
    navLink.href = anchor.getAttribute('href');
    navLink.className = 'nav-link';
    navLink.appendChild(navInner);
    
    // Create list item for this anchor
    const listItem = document.createElement('li');
    listItem.className = 'nav-item';
    listItem.dataset.sectionTitle = anchorRef.substring(1);
    
    // Add click event listener to smoothly scroll to the anchor
    navLink.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href').substring(1);
      const targetElement = document.getElementById(targetId);
      
      if (targetElement) {
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        
        // Update URL without page reload
        history.pushState(null, null, this.getAttribute('href'));
        
        // Update current section display
        updateCurrentSectionDisplay(targetId);
      }
    });
    
    // Add the link to the list item
    listItem.appendChild(navLink);
    
    // Add the list item to the navigation list
    navList.appendChild(listItem);
    
    // Store the target element for intersection observer
    const targetId = anchorRef.substring(1);
    const targetElement = document.getElementById(targetId);
    if (targetElement) {
      anchorElements.push({
        element: targetElement,
        id: targetId
      });
    }
  });
  
  // Add the list to the navigation menu
  navMenu.appendChild(navList);
  
  // Set up intersection observer to detect which section is currently in view
  setupIntersectionObserver(anchorElements);
}


// Function to update the current section display
function updateCurrentSectionDisplay(sectionId) {
  const currentSectionDisplay = document.getElementById('current-section');
  if (currentSectionDisplay) {
    currentSectionDisplay.textContent = sectionId;
    currentSectionDisplay.classList.add('visible');
  }
}

// Function to set up intersection observer
function setupIntersectionObserver(anchorElements) {
  // Options for the observer
  const options = {
    root: null, // viewport
    rootMargin: '0px',
    threshold: 0.1 // trigger when at least 10% of the target is visible
  };
  
  // Create the observer
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Found a section in view
        updateCurrentSectionDisplay(entry.target.id);
        
        // Highlight the corresponding nav item
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
          if (item.dataset.sectionTitle === entry.target.id) {
            item.classList.add('active');
          } else {
            item.classList.remove('active');
          }
        });
      }
    });
  }, options);
  
  // Observe all section elements
  anchorElements.forEach(({ element }) => {
    observer.observe(element);
  });
}

let handleScroll = (e) => {
  console.log(e);
  // This will be handled by the Intersection Observer
  // but we keep this for browsers that don't support it
  if (!("IntersectionObserver" in window)) {
    const scrollPosition = window.scrollY + 100; // offset for better UX

    // Find the section that is currently in view
    const anchorElements = document.querySelectorAll("[id]");
    let currentSection = null;

    anchorElements.forEach((element) => {
      const elementTop = element.offsetTop;
      const elementHeight = element.offsetHeight;

      if (scrollPosition >= elementTop && scrollPosition < elementTop + elementHeight) {
        currentSection = element.id;
      }
    });

    // Update the current section display
    if (currentSection) {
      updateCurrentSectionDisplay(currentSection);
    }
  }
};


document.addEventListener('DOMContentLoaded', () => {
  createNavMenuFromAnchors();
  
  handleScroll();
  window.addEventListener('scroll', handleScroll);
  
});