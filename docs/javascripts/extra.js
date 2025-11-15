// Extra JavaScript for PrompTrek Documentation

document.addEventListener('DOMContentLoaded', function() {
  // Add copy button feedback
  const clipboardButtons = document.querySelectorAll('.md-clipboard');
  clipboardButtons.forEach(button => {
    button.addEventListener('click', function() {
      const originalTitle = this.getAttribute('title');
      this.setAttribute('title', 'Copied!');
      setTimeout(() => {
        this.setAttribute('title', originalTitle);
      }, 2000);
    });
  });

  // External link handling
  const links = document.querySelectorAll('a[href^="http"]');
  links.forEach(link => {
    if (!link.hostname.includes('flamingquaks.github.io')) {
      link.setAttribute('target', '_blank');
      link.setAttribute('rel', 'noopener noreferrer');
    }
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });

  // Add version info to footer
  const footer = document.querySelector('.md-footer-meta');
  if (footer) {
    const versionInfo = document.createElement('div');
    versionInfo.className = 'md-footer-meta__version';
    versionInfo.innerHTML = '<small>Documentation built with MkDocs Material</small>';
    footer.appendChild(versionInfo);
  }

  // Highlight current navigation item
  const currentPath = window.location.pathname;
  document.querySelectorAll('.md-nav__link').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('md-nav__link--active');
    }
  });

  // Add table of contents scroll spy
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      const id = entry.target.getAttribute('id');
      if (entry.intersectionRatio > 0) {
        document.querySelector(`.md-nav__link[href="#${id}"]`)?.classList.add('md-nav__link--active');
      } else {
        document.querySelector(`.md-nav__link[href="#${id}"]`)?.classList.remove('md-nav__link--active');
      }
    });
  }, {
    rootMargin: '-20% 0px -35% 0px'
  });

  // Track all headings with IDs
  document.querySelectorAll('h2[id], h3[id], h4[id]').forEach((heading) => {
    observer.observe(heading);
  });

  // Schema version switcher functionality
  const schemaSwitchers = document.querySelectorAll('.schema-version-switcher');
  schemaSwitchers.forEach(switcher => {
    switcher.addEventListener('change', function() {
      const version = this.value;
      document.querySelectorAll('.schema-example').forEach(example => {
        if (example.dataset.version === version) {
          example.style.display = 'block';
        } else {
          example.style.display = 'none';
        }
      });
    });
  });

  // Add copy code block functionality with line numbers
  document.querySelectorAll('pre code').forEach(block => {
    const button = document.createElement('button');
    button.className = 'copy-code-button';
    button.textContent = 'Copy';
    button.addEventListener('click', () => {
      const code = block.textContent;
      navigator.clipboard.writeText(code).then(() => {
        button.textContent = 'Copied!';
        setTimeout(() => {
          button.textContent = 'Copy';
        }, 2000);
      });
    });
    block.parentElement.style.position = 'relative';
    block.parentElement.appendChild(button);
  });
});

// Search enhancement
document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.querySelector('.md-search__input');
  if (searchInput) {
    searchInput.setAttribute('placeholder', 'Search PrompTrek docs...');
  }
});
