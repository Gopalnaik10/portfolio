// Gopal Naik - Portfolio Client Logic
document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // State
  let portfolioData = null;
  let allProjects = [];
  let currentCategory = 'all';
  let searchQuery = '';

  // DOM Elements
  const header = document.getElementById('site-header');
  const menuToggle = document.getElementById('menu-toggle');
  const mobileDrawer = document.getElementById('mobile-drawer');
  const mobileBackdrop = document.getElementById('mobile-backdrop');
  const themeToggle = document.getElementById('theme-toggle');

  const projectSearchInput = document.getElementById('project-search');
  const categoryChipsContainer = document.getElementById('category-chips-container');
  const projectsContainer = document.getElementById('projects-container');
  const skillsContainer = document.getElementById('skills-container');
  const educationContainer = document.getElementById('education-container');

  const projectModal = document.getElementById('project-modal');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const contactForm = document.getElementById('contact-form');
  const formFeedback = document.getElementById('form-feedback');

  // 1. Dark / Light Theme Manager
  const initTheme = () => {
    const savedTheme = localStorage.getItem('portfolio_theme');
    if (savedTheme === 'light') {
      document.documentElement.classList.add('light-theme');
    } else {
      document.documentElement.classList.remove('light-theme');
    }
  };

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      const isLight = document.documentElement.classList.toggle('light-theme');
      localStorage.setItem('portfolio_theme', isLight ? 'light' : 'dark');
    });
  }
  initTheme();

  // 2. Sticky Header Translucent Blur
  const handleHeaderScroll = () => {
    if (window.scrollY > 20) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };
  window.addEventListener('scroll', handleHeaderScroll, { passive: true });
  handleHeaderScroll();

  // 3. Mobile Drawer Controls
  const toggleMobileMenu = (open) => {
    const isOpen = open !== undefined ? open : !mobileDrawer.classList.contains('is-open');
    menuToggle.classList.toggle('is-open', isOpen);
    menuToggle.setAttribute('aria-expanded', String(isOpen));
    mobileDrawer.classList.toggle('is-open', isOpen);
    mobileBackdrop.classList.toggle('is-open', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  };

  if (menuToggle) menuToggle.addEventListener('click', () => toggleMobileMenu());
  if (mobileBackdrop) mobileBackdrop.addEventListener('click', () => toggleMobileMenu(false));
  document.querySelectorAll('.mobile-nav-link').forEach(link => {
    link.addEventListener('click', () => toggleMobileMenu(false));
  });

  // 4. Fetch & Hydrate Dynamic Portfolio Data
  const fetchPortfolioData = async () => {
    try {
      const response = await fetch('/api/public/portfolio');
      const result = await response.json();

      if (!result.success) return;

      // Handle Maintenance Mode
      if (result.maintenance_mode) {
        const overlay = document.getElementById('maintenance-overlay');
        const msg = document.getElementById('maintenance-msg');
        if (overlay) {
          if (msg && result.maintenance_message) msg.textContent = result.maintenance_message;
          overlay.style.display = 'flex';
        }
        return;
      }

      portfolioData = result.data;
      hydrateProfile(portfolioData.profile, portfolioData.settings);
      hydrateSkills(portfolioData.skill_categories);
      hydrateProjects(portfolioData.projects, portfolioData.project_categories);
      hydrateEducation(portfolioData.education);
      hydrateSocials(portfolioData.social_links, portfolioData.profile);
      hydrateResume(portfolioData.resume);

      initScrollObservers();
    } catch (err) {
      console.warn("Using current DOM state:", err);
      initScrollObservers();
    }
  };

  // Hydrate Profile, Hero, and SEO/OpenGraph
  const hydrateProfile = (profile, settings) => {
    if (!profile) return;

    if (settings) {
      if (settings.site_title) {
        document.title = settings.site_title;
        const metaTitle = document.getElementById('meta-title');
        if (metaTitle) metaTitle.textContent = settings.site_title;
        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (ogTitle) ogTitle.setAttribute('content', settings.site_title);
      }
      if (settings.meta_description) {
        const metaDesc = document.getElementById('meta-desc');
        if (metaDesc) metaDesc.setAttribute('content', settings.meta_description);
        const ogDesc = document.querySelector('meta[property="og:description"]');
        if (ogDesc) ogDesc.setAttribute('content', settings.meta_description);
      }
      if (settings.keywords) {
        const metaKey = document.querySelector('meta[name="keywords"]');
        if (metaKey) metaKey.setAttribute('content', settings.keywords);
      }
      if (profile.profile_image) {
        const ogImg = document.querySelector('meta[property="og:image"]');
        if (ogImg) ogImg.setAttribute('content', profile.profile_image);
      }
    }

    const setText = (id, text) => {
      const el = document.getElementById(id);
      if (el && text) el.textContent = text;
    };

    setText('hero-greeting', profile.greeting || "Hello, I'm");
    setText('hero-name', profile.name || "Gopal Naik");
    setText('hero-title', profile.title || "Computer Science & Engineering Student | Data Science");
    setText('hero-tagline', profile.tagline || "I build data-driven applications and modern web solutions.");
    
    // Dynamic About Me Section
    setText('about-heading', profile.about_heading || "Turning Ideas Into\nImpactful Solutions");
    setText('about-narrative', profile.about_narrative);

    // 4 Customizable Factual Statistics
    setText('about-stat-1-val', profile.stat_1_val || "4+");
    setText('about-stat-1-label', profile.stat_1_label || "Projects Built");
    setText('about-stat-2-val', profile.stat_2_val || "15+");
    setText('about-stat-2-label', profile.stat_2_label || "Technologies & Tools");
    setText('about-stat-3-val', profile.stat_3_val || "2026");
    setText('about-stat-3-label', profile.stat_3_label || "Expected Graduation");
    setText('about-stat-4-val', profile.stat_4_val || "Data Science");
    setText('about-stat-4-label', profile.stat_4_label || "Specialization");

    if (profile.primary_cta_url) {
      const pCta = document.getElementById('hero-primary-cta');
      if (pCta) {
        pCta.setAttribute('href', profile.primary_cta_url);
        pCta.innerHTML = `<span>${escapeHtml(profile.primary_cta_text || 'View My Work →')}</span>`;
      }
    }

    if (profile.secondary_cta_url) {
      const sCta = document.getElementById('hero-secondary-cta');
      if (sCta) {
        sCta.setAttribute('href', profile.secondary_cta_url);
        sCta.innerHTML = `
          <span>${escapeHtml(profile.secondary_cta_text || 'Contact Me')}</span>
          <svg viewBox="0 0 24 24" width="17" height="17" stroke="currentColor" stroke-width="2" fill="none"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
        `;
      }
    }

    if (profile.profile_image) {
      const avatarImg = document.getElementById('hero-avatar');
      if (avatarImg) avatarImg.src = profile.profile_image;
    }
  };

  // Hydrate Skills (5 Organized Categories)
  const hydrateSkills = (categoriesDict) => {
    if (!skillsContainer || !categoriesDict) return;
    skillsContainer.innerHTML = '';

    const catIcons = {
      "Programming": `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>`,
      "Data Science & AI": `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path><polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline><line x1="12" y1="22.08" x2="12" y2="12"></line></svg>`,
      "Backend": `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect><rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect><line x1="6" y1="6" x2="6.01" y2="6"></line><line x1="6" y1="18" x2="6.01" y2="18"></line></svg>`,
      "Database": `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>`,
      "Frontend": `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>`
    };

    const catKeys = Object.keys(categoriesDict);
    catKeys.forEach((catName, idx) => {
      const skillsList = categoriesDict[catName];
      const iconSvg = catIcons[catName] || `<svg viewBox="0 0 24 24" width="20" height="20" stroke="currentColor" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>`;

      const box = document.createElement('div');
      box.className = `skill-category-box reveal-on-scroll delay-${(idx % 4) + 1}`;
      box.innerHTML = `
        <div class="skill-cat-header">
          <div class="skill-cat-icon">${iconSvg}</div>
          <h3 class="skill-cat-title">${escapeHtml(catName)}</h3>
        </div>
        <div class="skills-pills-wrap">
          ${skillsList.map(s => `<span class="skill-pill">${escapeHtml(s.name)}</span>`).join('')}
        </div>
      `;
      skillsContainer.appendChild(box);
    });
  };

  // Hydrate Projects & Setup Live Filtering
  const hydrateProjects = (projects, categories) => {
    allProjects = projects || [];
    if (!projectsContainer) return;

    if (categoryChipsContainer && categories) {
      categoryChipsContainer.innerHTML = `
        <button class="category-chip ${currentCategory === 'all' ? 'active' : ''}" data-category="all">All Projects</button>
        <button class="category-chip ${currentCategory === 'featured' ? 'active' : ''}" data-category="featured">★ Featured</button>
        ${categories.map(c => `<button class="category-chip ${currentCategory === c ? 'active' : ''}" data-category="${escapeHtml(c)}">${escapeHtml(c)}</button>`).join('')}
      `;

      categoryChipsContainer.querySelectorAll('.category-chip').forEach(btn => {
        btn.addEventListener('click', () => {
          categoryChipsContainer.querySelectorAll('.category-chip').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          currentCategory = btn.getAttribute('data-category');
          renderFilteredProjects();
        });
      });
    }

    if (projectSearchInput) {
      projectSearchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
        renderFilteredProjects();
      });
    }

    renderFilteredProjects();
  };

  // Render Filtered Projects List (Professional Developer Cards)
  const renderFilteredProjects = () => {
    if (!projectsContainer) return;
    projectsContainer.innerHTML = '';

    const filtered = allProjects.filter(p => {
      let matchCat = true;
      if (currentCategory === 'featured') matchCat = p.featured;
      else if (currentCategory !== 'all') matchCat = p.category === currentCategory;

      let matchSearch = true;
      if (searchQuery) {
        const titleMatch = (p.title || '').toLowerCase().includes(searchQuery);
        const descMatch = (p.short_description || '').toLowerCase().includes(searchQuery);
        const techMatch = (p.technologies || []).some(t => t.toLowerCase().includes(searchQuery));
        matchSearch = titleMatch || descMatch || techMatch;
      }

      return matchCat && matchSearch;
    });

    if (filtered.length === 0) {
      projectsContainer.innerHTML = `
        <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
          <p class="section-subtitle">No matching projects found for "${escapeHtml(searchQuery)}".</p>
        </div>
      `;
      return;
    }

    filtered.forEach((p, idx) => {
      const card = document.createElement('article');
      card.className = `project-card reveal-on-scroll delay-${(idx % 3) + 1}`;
      card.setAttribute('data-id', p.id);

      const techTags = (p.technologies || []).slice(0, 5).map(t => `<span class="project-tag">${escapeHtml(t)}</span>`).join('');

      card.innerHTML = `
        <div class="project-media">
          <img src="${escapeHtml(p.image || '/assets/project-placeholder.svg')}" alt="${escapeHtml(p.title)} preview" class="project-img" loading="lazy" />
          <div class="project-card-badges">
            <span class="project-category-badge">${escapeHtml(p.category || 'General')}</span>
            ${p.featured ? '<span class="project-featured-badge">★ Featured</span>' : '<span></span>'}
          </div>
        </div>
        <div class="project-body">
          <h3 class="project-title">${escapeHtml(p.title)}</h3>
          <p class="project-desc">${escapeHtml(p.short_description)}</p>
          <div class="project-tags">${techTags}</div>
          <div class="project-actions">
            <button type="button" class="btn-view-project" aria-label="View details for ${escapeHtml(p.title)}">
              <span>View Project</span>
              <svg viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" stroke-width="2.2" fill="none"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
            </button>
            <div class="project-links-group">
              ${p.github_url ? `
                <a href="${escapeHtml(p.github_url)}" target="_blank" rel="noopener noreferrer" class="project-link-icon" title="View Source Code" onclick="event.stopPropagation()">
                  <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                </a>
              ` : ''}
              ${p.live_url ? `
                <a href="${escapeHtml(p.live_url)}" target="_blank" rel="noopener noreferrer" class="project-link-icon" title="Live Demo" onclick="event.stopPropagation()">
                  <svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                </a>
              ` : ''}
            </div>
          </div>
        </div>
      `;

      card.addEventListener('click', () => openProjectModal(p));
      projectsContainer.appendChild(card);
    });

    initScrollObservers();
  };

  // 5. Project Details Modal
  const openProjectModal = (project) => {
    if (!projectModal) return;

    // Image & Meta
    document.getElementById('modal-project-img').src = project.image || '/assets/project-placeholder.svg';
    document.getElementById('modal-project-category').textContent = project.category || 'General';
    
    const featBadge = document.getElementById('modal-project-featured');
    if (featBadge) featBadge.style.display = project.featured ? 'inline-block' : 'none';

    // Title & Description
    document.getElementById('modal-project-title').textContent = project.title;
    document.getElementById('modal-project-desc').textContent = project.description || project.short_description;

    // Problem / Purpose Box
    const probWrapper = document.getElementById('modal-problem-wrapper');
    const probText = document.getElementById('modal-project-problem');
    if (probWrapper && probText) {
      if (project.problem_statement && project.problem_statement.trim()) {
        probText.textContent = project.problem_statement.trim();
        probWrapper.style.display = 'block';
      } else {
        probWrapper.style.display = 'none';
      }
    }

    // Key Features List
    const featWrapper = document.getElementById('modal-features-wrapper');
    const featList = document.getElementById('modal-project-features');
    if (featWrapper && featList) {
      const features = project.key_features || [];
      if (Array.isArray(features) && features.length > 0) {
        featList.innerHTML = features.map(f => `<li>${escapeHtml(f)}</li>`).join('');
        featWrapper.style.display = 'block';
      } else {
        featWrapper.style.display = 'none';
      }
    }

    // Technologies
    const tagsContainer = document.getElementById('modal-project-tags');
    tagsContainer.innerHTML = (project.technologies || []).map(t => `<span class="project-tag">${escapeHtml(t)}</span>`).join('');

    // Actions
    const githubLink = document.getElementById('modal-github-link');
    if (project.github_url) {
      githubLink.style.display = 'inline-flex';
      githubLink.href = project.github_url;
    } else {
      githubLink.style.display = 'none';
    }

    const liveLink = document.getElementById('modal-live-link');
    if (project.live_url) {
      liveLink.style.display = 'inline-flex';
      liveLink.href = project.live_url;
    } else {
      liveLink.style.display = 'none';
    }

    projectModal.classList.add('is-open');
    projectModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Track project view
    fetch(`/api/public/view-project/${project.id}`, { method: 'POST' }).catch(() => {});
  };


  const closeProjectModal = () => {
    if (!projectModal) return;
    projectModal.classList.remove('is-open');
    projectModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeProjectModal);
  if (projectModal) {
    projectModal.addEventListener('click', (e) => {
      if (e.target === projectModal) closeProjectModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (projectModal && projectModal.classList.contains('is-open')) closeProjectModal();
      if (mobileDrawer && mobileDrawer.classList.contains('is-open')) toggleMobileMenu(false);
    }
  });

  // Hydrate Education / Journey
  const hydrateEducation = (educationList) => {
    if (!educationContainer || !educationList) return;
    educationContainer.innerHTML = '';

    educationList.forEach((e, idx) => {
      const item = document.createElement('div');
      item.className = `timeline-item reveal-on-scroll delay-${(idx % 2) + 1}`;
      
      const courseworkTags = (e.coursework || []).map(c => `<span class="course-tag">${escapeHtml(c)}</span>`).join('');
      const dateRange = `${e.start_year || ''} — ${e.end_year || ''} ${e.expected_graduation ? '(Expected)' : ''}`.trim();

      item.innerHTML = `
        <div class="timeline-dot"></div>
        <div class="timeline-card">
          <div class="timeline-header">
            <h3 class="timeline-degree">${escapeHtml(e.degree)}</h3>
            <span class="timeline-date">${escapeHtml(dateRange)}</span>
          </div>
          <p class="timeline-institution">${escapeHtml(e.institution)} &bull; ${escapeHtml(e.specialization || '')}</p>
          ${e.description ? `<p class="timeline-desc">${escapeHtml(e.description)}</p>` : ''}
          ${courseworkTags ? `<div class="coursework-list">${courseworkTags}</div>` : ''}
        </div>
      `;
      educationContainer.appendChild(item);
    });
  };

  // Hydrate Socials in Hero, Contact & Footer
  const hydrateSocials = (socials, profile) => {
    const heroSocialsContainer = document.getElementById('hero-socials-container');
    const contactChannelsContainer = document.getElementById('contact-channels-container');
    const footerSocialsContainer = document.getElementById('footer-socials-container');

    if (!socials || socials.length === 0) return;

    let heroHtml = '';
    let footerHtml = '';
    let contactHtml = '';

    // Direct Email
    // Build contact channels from social links ONLY (no duplicate email entry)
    // The socials list already includes the Email entry.
    socials.forEach(s => {
      let iconSvg = `<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>`;
      const iconName = (s.icon || s.name || '').toLowerCase();

      if (iconName.includes('github')) {
        iconSvg = `<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>`;
      } else if (iconName.includes('linkedin')) {
        iconSvg = `<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>`;
      } else if (iconName.includes('mail') || iconName.includes('email')) {
        iconSvg = `<svg viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" fill="none"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>`;
      }

      heroHtml += `
        <a href="${escapeHtml(s.url)}" ${s.url.startsWith('mailto') ? '' : 'target="_blank" rel="noopener noreferrer"'} class="social-icon-btn" aria-label="${escapeHtml(s.name)}">
          ${iconSvg}
        </a>
      `;

      footerHtml += `
        <a href="${escapeHtml(s.url)}" ${s.url.startsWith('mailto') ? '' : 'target="_blank" rel="noopener noreferrer"'} class="social-icon-btn" aria-label="${escapeHtml(s.name)}">
          ${iconSvg}
        </a>
      `;

      const displayUrl = s.url.startsWith('mailto:')
        ? s.url.replace('mailto:', '')
        : s.url.replace(/^https?:\/\//, '');

      contactHtml += `
        <a href="${escapeHtml(s.url)}" ${s.url.startsWith('mailto') ? '' : 'target="_blank" rel="noopener noreferrer"'} class="channel-card" aria-label="${escapeHtml(s.name)}">
          <div class="channel-icon-box">${iconSvg}</div>
          <div>
            <div class="channel-label">${escapeHtml(s.name)}</div>
            <div class="channel-value">${escapeHtml(displayUrl)}</div>
          </div>
        </a>
      `;
    });

    if (heroSocialsContainer) heroSocialsContainer.innerHTML = heroHtml;
    if (footerSocialsContainer) footerSocialsContainer.innerHTML = footerHtml;
    if (contactChannelsContainer) contactChannelsContainer.innerHTML = contactHtml;
  };

  // Hydrate Resume Button
  const hydrateResume = (resume) => {
    const cvBtn = document.getElementById('header-cv-btn');
    const mobileCvBtn = document.getElementById('mobile-cv-btn');
    const mobileCvWrapper = document.getElementById('mobile-cv-wrapper');

    if (resume && resume.is_active) {
      const downloadUrl = `/api/public/resume/download?t=${Date.now()}`;
      if (cvBtn) {
        cvBtn.href = downloadUrl;
        cvBtn.style.display = 'inline-flex';
      }
      if (mobileCvBtn) {
        mobileCvBtn.href = downloadUrl;
        mobileCvBtn.style.display = 'inline-flex';
      }
      if (mobileCvWrapper) {
        mobileCvWrapper.style.display = 'block';
      }
    } else {
      if (cvBtn) {
        cvBtn.style.display = 'none';
        cvBtn.removeAttribute('href');
      }
      if (mobileCvBtn) {
        mobileCvBtn.style.display = 'none';
        mobileCvBtn.removeAttribute('href');
      }
      if (mobileCvWrapper) {
        mobileCvWrapper.style.display = 'none';
      }
    }
  };

  // 6. Contact Form Submission
  if (contactForm) {
    const nameInput = document.getElementById('contact-name');
    const emailInput = document.getElementById('contact-email');
    const subjectInput = document.getElementById('contact-subject');
    const messageInput = document.getElementById('contact-message');
    const submitBtn = document.getElementById('submit-btn');
    const submitBtnText = document.getElementById('submit-btn-text');

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const setFieldError = (input, errorId, isErr) => {
      const errEl = document.getElementById(errorId);
      input.classList.toggle('error', isErr);
      if (errEl) errEl.classList.toggle('visible', isErr);
    };

    [nameInput, emailInput, subjectInput, messageInput].forEach(inp => {
      if (inp) {
        inp.addEventListener('input', () => setFieldError(inp, `${inp.name}-error`, false));
      }
    });

    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      let isValid = true;

      if (!nameInput.value.trim()) { setFieldError(nameInput, 'name-error', true); isValid = false; }
      if (!emailInput.value.trim() || !emailRegex.test(emailInput.value.trim())) { setFieldError(emailInput, 'email-error', true); isValid = false; }
      if (!subjectInput.value.trim()) { setFieldError(subjectInput, 'subject-error', true); isValid = false; }
      if (!messageInput.value.trim() || messageInput.value.trim().length < 5) { setFieldError(messageInput, 'message-error', true); isValid = false; }

      if (!isValid) return;

      submitBtn.disabled = true;
      if (submitBtnText) submitBtnText.textContent = 'Sending Message...';

      try {
        const res = await fetch('/api/public/contact', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: nameInput.value.trim(),
            email: emailInput.value.trim(),
            subject: subjectInput.value.trim(),
            message: messageInput.value.trim()
          })
        });

        const data = await res.json();
        if (res.ok && data.success) {
          formFeedback.className = 'form-feedback-modal visible';
          formFeedback.style.color = '#34d399';
          formFeedback.innerHTML = `<strong>Message Sent Successfully!</strong> Thank you, Gopal will get back to you shortly.`;
          contactForm.reset();
        } else {
          formFeedback.className = 'form-feedback-modal visible';
          formFeedback.style.color = '#f87171';
          formFeedback.innerHTML = `<strong>Submission Failed:</strong> ${escapeHtml(data.error || 'Please try again.')}`;
        }
      } catch {
        formFeedback.className = 'form-feedback-modal visible';
        formFeedback.style.color = '#f87171';
        formFeedback.innerHTML = `<strong>Network Error:</strong> Could not connect to server.`;
      } finally {
        submitBtn.disabled = false;
        if (submitBtnText) submitBtnText.textContent = 'Send Message';
      }
    });
  }

  // 7. Scroll Observers (Active Nav & Scroll Reveal)
  const initScrollObservers = () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');

    const navObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const id = entry.target.getAttribute('id');
          navLinks.forEach(link => {
            const href = link.getAttribute('href').replace('#', '');
            // 'journey' section is shown under Education nav link
            link.classList.toggle('active', href === id);
          });
        }
      });
    }, { rootMargin: '-15% 0px -55% 0px' });

    sections.forEach(s => navObserver.observe(s));

    // Reveal on scroll
    const revealElements = document.querySelectorAll('.reveal-on-scroll:not(.is-visible)');
    const revealObserver = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    revealElements.forEach(el => revealObserver.observe(el));
  };

  const escapeHtml = (str) => {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  // Initial fetch
  fetchPortfolioData();
});
