const progressBar = document.getElementById('reading-progress');
const backToTop = document.getElementById('back-to-top');
const contentsButton = document.getElementById('contents-btn');
const drawerToggle = document.getElementById('drawer-toggle');
const drawerClose = document.getElementById('drawer-close');
const mobileDrawer = document.getElementById('mobile-drawer');
const drawerOverlay = document.getElementById('drawer-overlay');
const tocToggle = document.getElementById('toc-toggle');
const tocDrawer = document.getElementById('mobile-toc-drawer');
const tocOverlay = document.getElementById('toc-overlay');

const toggleDrawer = (drawer, overlay, open) => {
  if (!drawer || !overlay) return;
  drawer.classList.toggle('open', open);
  overlay.style.display = open ? 'block' : 'none';
  document.body.style.overflow = open ? 'hidden' : '';
};

const closeAllDrawers = () => {
  toggleDrawer(mobileDrawer, drawerOverlay, false);
  toggleDrawer(tocDrawer, tocOverlay, false);
};

if (drawerToggle && mobileDrawer && drawerOverlay) {
  drawerToggle.addEventListener('click', () => toggleDrawer(mobileDrawer, drawerOverlay, true));
  drawerOverlay.addEventListener('click', closeAllDrawers);
}

const drawerCloseButtons = document.querySelectorAll('.drawer-close');
drawerCloseButtons.forEach((button) => {
  button.addEventListener('click', closeAllDrawers);
});

if (tocToggle && tocDrawer && tocOverlay) {
  tocToggle.addEventListener('click', () => toggleDrawer(tocDrawer, tocOverlay, true));
  tocOverlay.addEventListener('click', closeAllDrawers);
}

if (contentsButton && tocDrawer && tocOverlay) {
  contentsButton.addEventListener('click', () => toggleDrawer(tocDrawer, tocOverlay, true));
}

const codeBlocks = document.querySelectorAll('.code-block');
codeBlocks.forEach((block) => {
  const copyBtn = block.querySelector('.copy-btn');
  const codeElement = block.querySelector('pre');

  if (!copyBtn || !codeElement) return;

  copyBtn.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(codeElement.innerText.trim());
      copyBtn.classList.add('copied');
      copyBtn.innerText = '✓';
      setTimeout(() => {
        copyBtn.classList.remove('copied');
        copyBtn.innerHTML = '&#128203;';
      }, 2000);
    } catch (error) {
      console.warn('Copy failed', error);
    }
  });
});

const anchorLinks = document.querySelectorAll('a[href^="#"]');
anchorLinks.forEach((link) => {
  link.addEventListener('click', (event) => {
    const targetId = link.getAttribute('href').slice(1);
    const target = document.getElementById(targetId);

    if (!target) return;
    event.preventDefault();
    closeAllDrawers();
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    history.replaceState(null, '', `#${targetId}`);
  });
});

window.addEventListener('scroll', () => {
  const scrollTop = window.scrollY;
  const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
  const progress = scrollHeight > 0 ? (scrollTop / scrollHeight) * 100 : 0;
  if (progressBar) progressBar.style.width = `${Math.min(Math.max(progress, 0), 100)}%`;
  if (backToTop) {
    backToTop.classList.toggle('visible', scrollTop > 400);
  }
  if (contentsButton) {
    contentsButton.classList.toggle('visible', scrollTop > 180);
  }
});

if (backToTop) {
  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

const tocLinks = document.querySelectorAll('.toc a[href^="#"]');
const sections = Array.from(document.querySelectorAll('main h2[id], main h3[id]'));
let sectionStatus = new Map();

const updateActiveToc = () => {
  if (!tocLinks.length || !sections.length) return;
  const visibleSections = sections
    .map((section) => ({
      id: section.id,
      top: section.getBoundingClientRect().top,
      visible: section.getBoundingClientRect().top >= 0,
    }))
    .filter((entry) => entry.top <= window.innerHeight * 0.5);

  const activeId = visibleSections.length ? visibleSections[visibleSections.length - 1].id : sections[0].id;
  tocLinks.forEach((link) => {
    const isActive = link.getAttribute('href') === `#${activeId}`;
    link.classList.toggle('active', isActive);
  });
};

if ('IntersectionObserver' in window && sections.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      sectionStatus.set(entry.target.id, entry.isIntersecting);
    });
  }, { rootMargin: '-40% 0px -55% 0px', threshold: [0.1, 0.4, 0.7] });

  sections.forEach((section) => observer.observe(section));
  setInterval(updateActiveToc, 100);
}

window.addEventListener('DOMContentLoaded', () => {
  updateActiveToc();
});