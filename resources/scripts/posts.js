// Function to create a navigation menu with all anchor links
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
  
  // Process each anchor link
  anchors.forEach((anchor, index) => {
    // Skip empty anchors or those without text content
    if (!anchor.textContent.trim()) return;
    

    anchorRef= anchor.getAttribute('href');
    anchorType = anchor.parentElement.nodeName;
    navText = '  '.repeat(anchorType.replace(/[^0-9]/g, '') - 1);
    navInner = document.createElement(anchorType);
    navInner.textContent = `${navText}${anchorRef.substring(1)}`;
    

    // Create the navigation link
    const navLink = document.createElement('a');
    navLink.href = anchor.getAttribute('href');
    navLink.className = 'nav-link';
    navLink.appendChild(navInner);

    // Create list item for this anchor
    const listItem = document.createElement('li');
    listItem.className = 'nav-item';
    
    
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
      }
    });
    
    // Add the link to the list item
    listItem.appendChild(navLink);
    
    // Add the list item to the navigation list
    navList.appendChild(listItem);
  });
  
  // Add the list to the navigation menu
  navMenu.appendChild(navList);
}

// Run the function when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', createNavMenuFromAnchors);