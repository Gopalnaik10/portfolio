// Admin CMS Dashboard Client JavaScript
document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // Global Section State Cache
  let currentTab = 'dashboard';
  let profileState = {};
  let skillsData = [];
  let projectsData = [];
  let educationData = [];
  let socialsData = [];
  let messagesData = [];

  // DOM Elements
  const sidebar = document.getElementById('admin-sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const navItems = document.querySelectorAll('.nav-item[data-tab]');
  const tabPanes = document.querySelectorAll('.tab-pane');
  const tabTitle = document.getElementById('current-tab-title');
  const sidebarLogoutBtn = document.getElementById('sidebar-logout-btn');
  const toastContainer = document.getElementById('toast-container');
  const modal = document.getElementById('admin-modal');
  const modalContent = document.getElementById('admin-modal-content');

  // 1. Toast Notification Helper
  const showToast = (message, type = 'success') => {
    if (!toastContainer) return;
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;

    let iconSvg = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="#34d399" stroke-width="2" fill="none"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    if (type === 'error') {
      iconSvg = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="#fca5a5" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else if (type === 'info') {
      iconSvg = `<svg viewBox="0 0 24 24" width="18" height="18" stroke="var(--accent-secondary)" stroke-width="2" fill="none"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.innerHTML = `${iconSvg}<span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(30px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  };

  // 2. Navigation & Tab Switching
  const tabTitlesMap = {
    'dashboard': 'Dashboard Overview',
    'hero': 'Hero Section & Identity',
    'about': 'About Me Editor',
    'projects': 'Projects Management',
    'skills': 'Skills & Toolkit',
    'education': 'Academic Background',
    'contact': 'Contact & Socials',
    'messages': 'Messages Inbox',
    'settings': 'Settings & SEO'
  };

  const switchTab = (tabName) => {
    // Always cleanly close any active modal before switching tabs
    closeModal();

    currentTab = tabName;
    navItems.forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-tab') === tabName);
    });

    tabPanes.forEach(pane => {
      pane.classList.toggle('active', pane.id === `tab-${tabName}`);
    });

    if (tabTitle) tabTitle.textContent = tabTitlesMap[tabName] || 'Dashboard';

    // Safely load data for selected tab without halting on individual errors
    try {
      if (tabName === 'dashboard') loadDashboardStats();
      else if (tabName === 'hero') loadHeroData();
      else if (tabName === 'about') loadAboutData();
      else if (tabName === 'projects') loadProjectsData();
      else if (tabName === 'skills') loadSkillsData();
      else if (tabName === 'education') loadEducationData();
      else if (tabName === 'contact') loadContactData();
      else if (tabName === 'messages') loadMessagesData();
      else if (tabName === 'settings') loadSettingsData();
    } catch (err) {
      console.error(`Error loading tab ${tabName}:`, err);
    }

    if (window.innerWidth <= 900 && sidebar) {
      sidebar.classList.remove('is-open');
    }
  };

  navItems.forEach(btn => {
    btn.addEventListener('click', () => switchTab(btn.getAttribute('data-tab')));
  });

  if (sidebarToggle) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('is-open');
    });
  }

  // Logout Handler
  if (sidebarLogoutBtn) {
    sidebarLogoutBtn.addEventListener('click', async () => {
      try {
        await fetch('/api/auth/logout', { method: 'POST' });
      } finally {
        window.location.href = '/admin/login';
      }
    });
  }

  // 3. Tab: Dashboard Statistics
  const loadDashboardStats = async () => {
    try {
      const res = await fetch('/api/admin/dashboard-stats');
      const json = await res.json();
      if (!json.success) return;

      const data = json.data;
      const setElText = (id, text) => {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
      };

      setElText('stat-published-projects', data.published_projects);
      setElText('stat-total-projects', `${data.total_projects} total created`);
      setElText('stat-total-skills', data.total_skills);
      setElText('stat-unread-messages', data.unread_messages);
      setElText('stat-total-messages', `${data.total_messages} total inquiries`);

      // Analytics
      const analytics = data.analytics || {};
      const totalViews = analytics.total_page_views || 0;
      const uniqueVisitors = analytics.estimated_unique_visitors || 0;
      setElText('stat-total-visits', totalViews);
      setElText('stat-unique-visitors', uniqueVisitors > 0 ? `~${uniqueVisitors} unique visitors` : '0 unique visitors');

      // Update sidebar badge
      const msgBadge = document.getElementById('sidebar-msg-badge');
      if (msgBadge) {
        if (data.unread_messages > 0) {
          msgBadge.textContent = data.unread_messages;
          msgBadge.style.display = 'inline-block';
        } else {
          msgBadge.style.display = 'none';
        }
      }

      // Populate Activity Logs
      const activityContainer = document.getElementById('activity-log-list');
      if (activityContainer) {
        if (data.recent_activities && data.recent_activities.length > 0) {
          activityContainer.innerHTML = data.recent_activities.map(act => `
            <div style="padding: 0.75rem 1rem; background: var(--bg-surface-elevated); border-radius: var(--radius-sm); border-left: 3px solid var(--accent-primary);">
              <div style="font-size: 0.88rem; font-weight: 600;">${escapeHtml(act.description)}</div>
              <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 0.2rem;">${escapeHtml(act.formatted_time)}</div>
            </div>
          `).join('');
        } else {
          activityContainer.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 1.5rem 0;">No activity yet.</p>`;
        }
      }

      // Populate Popular Projects
      const popularContainer = document.getElementById('popular-projects-list');
      if (popularContainer) {
        if (data.popular_projects && data.popular_projects.length > 0) {
          popularContainer.innerHTML = data.popular_projects.map(p => `
            <div style="display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: var(--bg-surface-elevated); border-radius: var(--radius-sm);">
              <div>
                <div style="font-weight: 600; font-size: 0.9rem;">${escapeHtml(p.title)}</div>
                <div style="font-size: 0.78rem; color: var(--accent-secondary);">${escapeHtml(p.category)}</div>
              </div>
              <span class="status-tag active">${p.view_count} views</span>
            </div>
          `).join('');
        } else {
          popularContainer.innerHTML = `<p style="color: var(--text-muted); text-align: center; padding: 1.5rem 0;">No project view data yet.</p>`;
        }
      }
    } catch (err) {
      console.warn("Dashboard stats load error:", err);
    }
  };

  // Helper: Fetch Latest Profile State
  const fetchProfileState = async () => {
    try {
      const res = await fetch('/api/admin/profile');
      const json = await res.json();
      if (json.success) {
        profileState = json.data;
        return profileState;
      }
    } catch {
      showToast("Failed to load profile data", "error");
    }
    return null;
  };

  // 4. Tab: Hero Section & Identity
  const loadHeroData = async () => {
    const p = await fetchProfileState();
    if (!p) return;

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val !== undefined && val !== null ? val : '';
    };

    setVal('hero-greeting-input', p.greeting);
    setVal('hero-name-input', p.name);
    setVal('hero-title-input', p.title);
    setVal('hero-tagline-input', p.tagline);
    setVal('hero-availability-input', p.availability_status);
    setVal('hero-location-input', p.location);
    setVal('hero-p-cta-text', p.primary_cta_text);
    setVal('hero-p-cta-url', p.primary_cta_url);
    setVal('hero-s-cta-text', p.secondary_cta_text);
    setVal('hero-s-cta-url', p.secondary_cta_url);
  };

  const heroForm = document.getElementById('hero-form');
  if (heroForm) {
    heroForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = heroForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const payload = {
        greeting: document.getElementById('hero-greeting-input').value.trim(),
        name: document.getElementById('hero-name-input').value.trim(),
        title: document.getElementById('hero-title-input').value.trim(),
        tagline: document.getElementById('hero-tagline-input').value.trim(),
        availability_status: document.getElementById('hero-availability-input').value.trim(),
        location: document.getElementById('hero-location-input').value.trim(),
        primary_cta_text: document.getElementById('hero-p-cta-text').value.trim(),
        primary_cta_url: document.getElementById('hero-p-cta-url').value.trim(),
        secondary_cta_text: document.getElementById('hero-s-cta-text').value.trim(),
        secondary_cta_url: document.getElementById('hero-s-cta-url').value.trim()
      };

      try {
        const res = await fetch('/api/admin/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
          showToast("Hero section updated successfully!");
          profileState = json.data;
        } else {
          showToast(json.error || "Update failed", "error");
        }
      } catch {
        showToast("Error saving hero section", "error");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // 5. Tab: Dedicated About Me Editor (Image Upload, Heading, Narrative, 4 Stats)
  const loadAboutData = async () => {
    const p = await fetchProfileState();
    if (!p) return;

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val !== undefined && val !== null ? val : '';
    };

    setVal('about-heading-input', p.about_heading || 'Turning Ideas Into Impactful Solutions');
    setVal('about-narrative-input', p.about_narrative);
    setVal('about-focus-input', p.about_focus);

    // 4 Stats
    setVal('stat1-val', p.stat_1_val || '4+');
    setVal('stat1-label', p.stat_1_label || 'Projects Built');
    setVal('stat2-val', p.stat_2_val || '15+');
    setVal('stat2-label', p.stat_2_label || 'Technologies & Tools');
    setVal('stat3-val', p.stat_3_val || '2026');
    setVal('stat3-label', p.stat_3_label || 'Expected Graduation');
    setVal('stat4-val', p.stat_4_val || 'Data Science');
    setVal('stat4-label', p.stat_4_label || 'Specialization');

    // Profile photo preview
    const preview = document.getElementById('about-image-preview');
    if (preview && p.profile_image) {
      preview.src = p.profile_image;
    }
  };

  // Profile / Headshot Image Upload in About Me Tab
  const aboutImageInput = document.getElementById('about-image-input');
  if (aboutImageInput) {
    aboutImageInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      // Validate file type
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
      if (!validTypes.includes(file.type)) {
        showToast("Invalid file type. Please upload JPG, PNG, or WebP.", "error");
        return;
      }

      // Validate size (20MB)
      if (file.size > 20 * 1024 * 1024) {
        showToast("File size exceeds 20MB limit.", "error");
        return;
      }

      // Instant client-side preview
      const preview = document.getElementById('about-image-preview');
      if (preview) {
        preview.src = URL.createObjectURL(file);
      }

      // Upload to server
      const formData = new FormData();
      formData.append('image', file);

      try {
        const res = await fetch('/api/admin/profile/upload-image', {
          method: 'POST',
          body: formData
        });
        const json = await res.json();
        if (json.success) {
          if (preview) preview.src = json.image_url;
          showToast("Profile image uploaded and updated successfully!");
          await fetchProfileState();
        } else {
          showToast(json.error || "Upload failed", "error");
        }
      } catch (err) {
        showToast("Error uploading profile image", "error");
      }
    });
  }

  // About Me Form Submit
  const aboutForm = document.getElementById('about-form');
  if (aboutForm) {
    aboutForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = aboutForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const payload = {
        about_heading: document.getElementById('about-heading-input').value.trim(),
        about_narrative: document.getElementById('about-narrative-input').value.trim(),
        about_focus: document.getElementById('about-focus-input').value.trim(),
        stat_1_val: document.getElementById('stat1-val').value.trim(),
        stat_1_label: document.getElementById('stat1-label').value.trim(),
        stat_2_val: document.getElementById('stat2-val').value.trim(),
        stat_2_label: document.getElementById('stat2-label').value.trim(),
        stat_3_val: document.getElementById('stat3-val').value.trim(),
        stat_3_label: document.getElementById('stat3-label').value.trim(),
        stat_4_val: document.getElementById('stat4-val').value.trim(),
        stat_4_label: document.getElementById('stat4-label').value.trim()
      };

      try {
        const res = await fetch('/api/admin/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
          showToast("About Me details & statistics updated successfully!");
          profileState = json.data;
        } else {
          showToast(json.error || "Update failed", "error");
        }
      } catch {
        showToast("Error saving About Me details", "error");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // 6. Tab: Projects Management
  const loadProjectsData = async () => {
    try {
      const res = await fetch('/api/admin/projects');
      const json = await res.json();
      if (!json.success) return;

      projectsData = json.data || [];
      renderProjectsTable();
    } catch {
      showToast("Error loading projects list", "error");
    }
  };

  const renderProjectsTable = () => {
    const tbody = document.getElementById('projects-table-body');
    if (!tbody) return;

    if (projectsData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2rem;">No projects found. Click "+ Add New Project" to add one.</td></tr>`;
      return;
    }

    tbody.innerHTML = projectsData.map((p, idx) => `
      <tr class="draggable-row" draggable="true" data-id="${p.id}">
        <td><span class="drag-handle">&#9776;</span> ${idx + 1}</td>
        <td>
          <img src="${escapeHtml(p.image || '/assets/project-placeholder.svg')}" style="width: 48px; height: 32px; border-radius: 4px; object-fit: cover;" alt="preview" />
        </td>
        <td><strong>${escapeHtml(p.title)}</strong></td>
        <td><span class="status-tag" style="background: rgba(56,189,248,0.1); color: var(--accent-secondary);">${escapeHtml(p.category)}</span></td>
        <td>${p.featured ? '<span class="status-tag active">★ Featured</span>' : '<span style="color: var(--text-muted); font-size: 0.8rem;">Standard</span>'}</td>
        <td><span class="status-tag ${p.published ? 'published' : 'draft'}">${p.published ? 'Published' : 'Draft'}</span></td>
        <td style="text-align: right;">
          <div class="table-actions" style="justify-content: flex-end;">
            <button class="btn btn-secondary btn-sm edit-proj-btn" data-id="${p.id}">Edit</button>
            <button class="btn btn-danger btn-sm delete-proj-btn" data-id="${p.id}">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll('.edit-proj-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = projectsData.find(p => p.id === parseInt(btn.dataset.id));
        if (item) openProjectModal(item);
      });
    });

    tbody.querySelectorAll('.delete-proj-btn').forEach(btn => {
      btn.addEventListener('click', () => confirmDelete('Project', async () => {
        try {
          const res = await fetch(`/api/admin/projects/${btn.dataset.id}`, { method: 'DELETE' });
          if (res.ok) {
            showToast("Project deleted successfully");
            loadProjectsData();
          } else {
            showToast("Failed to delete project", "error");
          }
        } catch {
          showToast("Network error deleting project", "error");
        }
      }));
    });

    initDragAndDrop(tbody, '/api/admin/projects/reorder', () => loadProjectsData());
  };

  const openProjectModal = (project = null) => {
    const isEdit = Boolean(project);
    const techStr = project ? (project.technologies_raw || (project.technologies || []).join(', ')) : '';

    // Format key features as clean newlines
    let featuresStr = '';
    if (project && project.key_features) {
      if (Array.isArray(project.key_features)) {
        featuresStr = project.key_features.join('\n');
      } else {
        featuresStr = project.key_features_raw || project.key_features;
      }
    }

    modalContent.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">${isEdit ? 'Edit Project' : 'Add New Project'}</h3>
      </div>
      <form id="project-modal-form">
        <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label" for="m-proj-title">Project Title</label>
            <input type="text" id="m-proj-title" class="form-input" value="${isEdit ? escapeHtml(project.title) : ''}" placeholder="e.g. AI Gym Trainer" required />
          </div>
          <div class="form-group">
            <label class="form-label" for="m-proj-cat">Category</label>
            <input type="text" id="m-proj-cat" class="form-input" value="${isEdit ? escapeHtml(project.category) : 'Machine Learning'}" placeholder="e.g. Machine Learning, Computer Vision, NLP" required />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="m-proj-short">Short Description (Card Summary)</label>
          <textarea id="m-proj-short" class="form-textarea" placeholder="2-3 sentence overview shown on project card..." required>${isEdit ? escapeHtml(project.short_description) : ''}</textarea>
        </div>

        <div class="form-group">
          <label class="form-label" for="m-proj-problem">Problem Statement &amp; Purpose</label>
          <textarea id="m-proj-problem" class="form-textarea" placeholder="What specific problem does this project solve? Who is it for?">${isEdit ? escapeHtml(project.problem_statement || '') : ''}</textarea>
        </div>

        <div class="form-group">
          <label class="form-label" for="m-proj-features">Key Features &amp; Capabilities (One per line)</label>
          <textarea id="m-proj-features" class="form-textarea" style="min-height: 100px;" placeholder="• Real-time skeletal landmark tracking&#10;• Posture deviation alert algorithm&#10;• Interactive workout progress dashboard">${escapeHtml(featuresStr)}</textarea>
        </div>

        <div class="form-group">
          <label class="form-label" for="m-proj-desc">Detailed Description &amp; Methodology</label>
          <textarea id="m-proj-desc" class="form-textarea" style="min-height: 110px;" placeholder="Detailed technical architecture, models, datasets, benchmarks, and implementation details...">${isEdit ? escapeHtml(project.description || '') : ''}</textarea>
        </div>

        <div class="form-group">
          <label class="form-label" for="m-proj-tech">Technologies (Comma-separated)</label>
          <input type="text" id="m-proj-tech" class="form-input" value="${escapeHtml(techStr)}" placeholder="e.g. Python, OpenCV, MediaPipe, Streamlit, NumPy" />
        </div>

        <div class="form-group">
          <label class="form-label">Project Preview Image</label>
          <div style="display: flex; gap: 1rem; align-items: center;">
            <img src="${isEdit ? escapeHtml(project.image) : '/assets/project-placeholder.svg'}" id="m-proj-img-preview" style="width: 80px; height: 50px; border-radius: 4px; object-fit: cover;" alt="Preview" />
            <div>
              <input type="file" id="m-proj-img-file" accept="image/png, image/jpeg, image/webp" style="display: none;" />
              <button type="button" class="btn btn-secondary btn-sm" onclick="document.getElementById('m-proj-img-file').click()">Select Screenshot Image</button>
              <input type="hidden" id="m-proj-img-url" value="${isEdit ? escapeHtml(project.image) : '/assets/project-placeholder.svg'}" />
            </div>
          </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label" for="m-proj-github">GitHub Repository URL</label>
            <input type="url" id="m-proj-github" class="form-input" value="${isEdit ? escapeHtml(project.github_url || '') : ''}" placeholder="https://github.com/gopalnaik/repo" />
          </div>
          <div class="form-group">
            <label class="form-label" for="m-proj-live">Live Demo URL (Optional)</label>
            <input type="url" id="m-proj-live" class="form-input" value="${isEdit ? escapeHtml(project.live_url || '') : ''}" placeholder="https://..." />
          </div>
        </div>

        <div style="display: flex; gap: 1.5rem; margin-top: 0.5rem;">
          <label class="form-checkbox-label">
            <input type="checkbox" id="m-proj-featured" ${isEdit && project.featured ? 'checked' : ''} />
            <span>Mark as Featured Project</span>
          </label>
          <label class="form-checkbox-label">
            <input type="checkbox" id="m-proj-published" ${!isEdit || project.published ? 'checked' : ''} />
            <span>Publish publicly</span>
          </label>
        </div>

        <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary" id="m-proj-submit-btn">${isEdit ? 'Save Project' : 'Create Project'}</button>
        </div>
      </form>
    `;

    // Handle project image upload
    const fileInput = document.getElementById('m-proj-img-file');
    if (fileInput) {
      fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const formData = new FormData();
        formData.append('image', file);
        try {
          const res = await fetch('/api/admin/projects/upload-image', { method: 'POST', body: formData });
          const json = await res.json();
          if (json.success) {
            document.getElementById('m-proj-img-preview').src = json.image_url;
            document.getElementById('m-proj-img-url').value = json.image_url;
            showToast("Project image uploaded");
          } else {
            showToast(json.error || "Image upload failed", "error");
          }
        } catch {
          showToast("Error uploading project image", "error");
        }
      });
    }

    const pForm = document.getElementById('project-modal-form');
    if (pForm) {
      pForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('m-proj-submit-btn');
        if (submitBtn) submitBtn.disabled = true;

        // Parse key features into clean array
        const rawFeatures = document.getElementById('m-proj-features').value.trim();
        const featuresArray = rawFeatures.split('\n').map(l => l.trim().replace(/^[•\-\*]\s*/, '')).filter(Boolean);

        const payload = {
          title: document.getElementById('m-proj-title').value.trim(),
          category: document.getElementById('m-proj-cat').value.trim(),
          short_description: document.getElementById('m-proj-short').value.trim(),
          problem_statement: document.getElementById('m-proj-problem').value.trim(),
          key_features: featuresArray,
          description: document.getElementById('m-proj-desc').value.trim(),
          technologies: document.getElementById('m-proj-tech').value.trim(),
          image: document.getElementById('m-proj-img-url').value.trim(),
          github_url: document.getElementById('m-proj-github').value.trim(),
          live_url: document.getElementById('m-proj-live').value.trim(),
          featured: document.getElementById('m-proj-featured').checked,
          published: document.getElementById('m-proj-published').checked
        };

        const url = isEdit ? `/api/admin/projects/${project.id}` : '/api/admin/projects';
        const method = isEdit ? 'PUT' : 'POST';

        try {
          const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const json = await res.json();
          if (json.success || res.ok) {
            closeModal();
            showToast(isEdit ? "Project updated successfully!" : "Project created successfully!");
            loadProjectsData();
          } else {
            showToast(json.error || "Failed to save project", "error");
          }
        } catch {
          showToast("Network error saving project", "error");
        } finally {
          if (submitBtn) submitBtn.disabled = false;
        }
      });
    }

    openModal();
  };

  const addProjBtn = document.getElementById('btn-add-project');
  if (addProjBtn) addProjBtn.addEventListener('click', () => openProjectModal());

  // 7. Tab: Skills Management

  const loadSkillsData = async () => {
    try {
      const res = await fetch('/api/admin/skills');
      const json = await res.json();
      if (!json.success) return;

      skillsData = json.data || [];
      renderSkillsTable();
    } catch {
      showToast("Error loading skills", "error");
    }
  };

  const renderSkillsTable = () => {
    const tbody = document.getElementById('skills-table-body');
    if (!tbody) return;

    if (skillsData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">No skills found. Click "+ Add New Skill" to add one.</td></tr>`;
      return;
    }

    tbody.innerHTML = skillsData.map((s, idx) => `
      <tr class="draggable-row" draggable="true" data-id="${s.id}">
        <td><span class="drag-handle">&#9776;</span> ${idx + 1}</td>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td><span class="status-tag" style="background: rgba(99, 102, 241, 0.1); color: var(--accent-primary);">${escapeHtml(s.category)}</span></td>
        <td><span class="status-tag ${s.enabled ? 'active' : 'inactive'}">${s.enabled ? 'Enabled' : 'Disabled'}</span></td>
        <td style="text-align: right;">
          <div class="table-actions" style="justify-content: flex-end;">
            <button class="btn btn-secondary btn-sm edit-skill-btn" data-id="${s.id}">Edit</button>
            <button class="btn btn-danger btn-sm delete-skill-btn" data-id="${s.id}">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll('.edit-skill-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = skillsData.find(s => s.id === parseInt(btn.dataset.id));
        if (item) openSkillModal(item);
      });
    });

    tbody.querySelectorAll('.delete-skill-btn').forEach(btn => {
      btn.addEventListener('click', () => confirmDelete('Skill', async () => {
        try {
          const res = await fetch(`/api/admin/skills/${btn.dataset.id}`, { method: 'DELETE' });
          if (res.ok) {
            showToast("Skill deleted successfully");
            loadSkillsData();
          } else {
            showToast("Failed to delete skill", "error");
          }
        } catch {
          showToast("Network error deleting skill", "error");
        }
      }));
    });

    initDragAndDrop(tbody, '/api/admin/skills/reorder', () => loadSkillsData());
  };

  const openSkillModal = (skill = null) => {
    const isEdit = Boolean(skill);
    modalContent.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">${isEdit ? 'Edit Skill' : 'Add New Skill'}</h3>
      </div>
      <form id="skill-modal-form">
        <div class="form-group">
          <label class="form-label" for="m-skill-name">Skill Name</label>
          <input type="text" id="m-skill-name" class="form-input" value="${isEdit ? escapeHtml(skill.name) : ''}" placeholder="e.g. Python, TensorFlow, React" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="m-skill-cat">Category</label>
          <input type="text" id="m-skill-cat" class="form-input" value="${isEdit ? escapeHtml(skill.category) : 'Programming'}" placeholder="e.g. Programming, Data Science & AI, Backend, Frontend, Database" required />
        </div>
        <div class="form-group">
          <label class="form-checkbox-label">
            <input type="checkbox" id="m-skill-enabled" ${!isEdit || skill.enabled ? 'checked' : ''} />
            <span>Enable skill on public portfolio</span>
          </label>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary" id="m-skill-submit-btn">${isEdit ? 'Save Changes' : 'Create Skill'}</button>
        </div>
      </form>
    `;

    const sForm = document.getElementById('skill-modal-form');
    if (sForm) {
      sForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('m-skill-submit-btn');
        if (submitBtn) submitBtn.disabled = true;

        const payload = {
          name: document.getElementById('m-skill-name').value.trim(),
          category: document.getElementById('m-skill-cat').value.trim(),
          enabled: document.getElementById('m-skill-enabled').checked
        };

        const url = isEdit ? `/api/admin/skills/${skill.id}` : '/api/admin/skills';
        const method = isEdit ? 'PUT' : 'POST';

        try {
          const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const json = await res.json();
          if (json.success || res.ok) {
            closeModal();
            showToast(isEdit ? "Skill updated!" : "Skill created!");
            loadSkillsData();
          } else {
            showToast(json.error || "Operation failed", "error");
          }
        } catch {
          showToast("Network error saving skill", "error");
        } finally {
          if (submitBtn) submitBtn.disabled = false;
        }
      });
    }

    openModal();
  };

  const addSkillBtn = document.getElementById('btn-add-skill');
  if (addSkillBtn) addSkillBtn.addEventListener('click', () => openSkillModal());

  // 8. Tab: Education Management (Dedicated Editor & All Records List)

  const loadEducationData = async () => {
    try {
      const res = await fetch('/api/admin/education');
      const json = await res.json();
      if (!json.success) return;

      educationData = json.data || [];
      renderEducationTable();

      // Populate dedicated primary Education Editor form
      if (educationData.length > 0) {
        const primary = educationData[0];
        populateEducationForm(primary);
      } else {
        resetEducationForm();
      }
    } catch {
      showToast("Error loading education data", "error");
    }
  };

  const populateEducationForm = (edu) => {
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val !== undefined && val !== null ? val : '';
    };

    setVal('edu-form-id', edu.id || '');
    setVal('edu-form-degree', edu.degree || '');
    setVal('edu-form-specialization', edu.specialization || '');
    setVal('edu-form-institution', edu.institution || '');
    setVal('edu-form-start-year', edu.start_year || '');
    setVal('edu-form-end-year', edu.end_year || '');

    const cwStr = edu.coursework_raw || (Array.isArray(edu.coursework) ? edu.coursework.join(', ') : edu.coursework) || '';
    setVal('edu-form-coursework', cwStr);
    setVal('edu-form-description', edu.description || '');

    const expCb = document.getElementById('edu-form-expected');
    if (expCb) expCb.checked = Boolean(edu.expected_graduation);

    const pubCb = document.getElementById('edu-form-published');
    if (pubCb) pubCb.checked = edu.published !== undefined ? Boolean(edu.published) : true;
  };

  const resetEducationForm = () => {
    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.value = val;
    };
    setVal('edu-form-id', '');
    setVal('edu-form-degree', '');
    setVal('edu-form-specialization', '');
    setVal('edu-form-institution', '');
    setVal('edu-form-start-year', '');
    setVal('edu-form-end-year', '');
    setVal('edu-form-coursework', '');
    setVal('edu-form-description', '');

    const expCb = document.getElementById('edu-form-expected');
    if (expCb) expCb.checked = false;

    const pubCb = document.getElementById('edu-form-published');
    if (pubCb) pubCb.checked = true;
  };

  // Dedicated Education Form Submit Handler
  const educationForm = document.getElementById('education-form');
  if (educationForm) {
    educationForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('edu-form-save-btn');
      if (submitBtn) submitBtn.disabled = true;

      const eduId = document.getElementById('edu-form-id').value.trim();
      const degree = document.getElementById('edu-form-degree').value.trim();
      const institution = document.getElementById('edu-form-institution').value.trim();

      if (!degree || !institution) {
        showToast("Degree and institution name are required.", "error");
        if (submitBtn) submitBtn.disabled = false;
        return;
      }

      const payload = {
        degree,
        specialization: document.getElementById('edu-form-specialization').value.trim(),
        institution,
        start_year: document.getElementById('edu-form-start-year').value.trim(),
        end_year: document.getElementById('edu-form-end-year').value.trim(),
        coursework: document.getElementById('edu-form-coursework').value.trim(),
        description: document.getElementById('edu-form-description').value.trim(),
        expected_graduation: document.getElementById('edu-form-expected').checked,
        published: document.getElementById('edu-form-published').checked
      };

      try {
        const url = eduId ? `/api/admin/education/${eduId}` : '/api/admin/education';
        const method = eduId ? 'PUT' : 'POST';

        const res = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const json = await res.json();
        if (json.success) {
          showToast("Education background saved successfully!");
          loadEducationData();
        } else {
          showToast(json.error || "Failed to save education", "error");
        }
      } catch {
        showToast("Network error saving education background", "error");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  const renderEducationTable = () => {
    const tbody = document.getElementById('education-table-body');
    if (!tbody) return;

    if (educationData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No education entries added yet. Use the form above to add one.</td></tr>`;
      return;
    }

    tbody.innerHTML = educationData.map((e, idx) => `
      <tr class="draggable-row" draggable="true" data-id="${e.id}">
        <td><span class="drag-handle">&#9776;</span> ${idx + 1}</td>
        <td>
          <strong>${escapeHtml(e.degree)}</strong>
          ${e.specialization ? `<div style="font-size: 0.8rem; color: var(--accent-secondary);">${escapeHtml(e.specialization)}</div>` : ''}
        </td>
        <td>${escapeHtml(e.institution)}</td>
        <td>${escapeHtml(e.start_year)} – ${escapeHtml(e.end_year || 'Present')}</td>
        <td><span class="status-tag ${e.published ? 'published' : 'draft'}">${e.published ? 'Published' : 'Draft'}</span></td>
        <td style="text-align: right;">
          <div class="table-actions" style="justify-content: flex-end;">
            <button class="btn btn-secondary btn-sm edit-edu-btn" data-id="${e.id}">Edit</button>
            <button class="btn btn-danger btn-sm delete-edu-btn" data-id="${e.id}">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll('.edit-edu-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = educationData.find(e => e.id === parseInt(btn.dataset.id));
        if (item) {
          populateEducationForm(item);
          openEducationModal(item);
        }
      });
    });

    tbody.querySelectorAll('.delete-edu-btn').forEach(btn => {
      btn.addEventListener('click', () => confirmDelete('Education record', async () => {
        try {
          const res = await fetch(`/api/admin/education/${btn.dataset.id}`, { method: 'DELETE' });
          if (res.ok) {
            showToast("Education record deleted");
            loadEducationData();
          } else {
            showToast("Failed to delete education record", "error");
          }
        } catch {
          showToast("Network error deleting education record", "error");
        }
      }));
    });

    initDragAndDrop(tbody, '/api/admin/education/reorder', () => loadEducationData());
  };

  const openEducationModal = (edu = null) => {
    const isEdit = Boolean(edu);
    const cwStr = edu ? (edu.coursework_raw || (Array.isArray(edu.coursework) ? edu.coursework.join(', ') : edu.coursework) || '') : '';

    modalContent.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">${isEdit ? 'Edit Education Record' : 'Add New Academic Record'}</h3>
      </div>
      <form id="edu-modal-form">
        <div class="form-group">
          <label class="form-label" for="m-edu-degree">Degree / Program</label>
          <input type="text" id="m-edu-degree" class="form-input" value="${isEdit ? escapeHtml(edu.degree) : ''}" placeholder="e.g. Computer Science & Engineering" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="m-edu-spec">Specialization (Optional)</label>
          <input type="text" id="m-edu-spec" class="form-input" value="${isEdit ? escapeHtml(edu.specialization || '') : ''}" placeholder="e.g. Specialization in Data Science" />
        </div>
        <div class="form-group">
          <label class="form-label" for="m-edu-inst">Institution Name</label>
          <input type="text" id="m-edu-inst" class="form-input" value="${isEdit ? escapeHtml(edu.institution) : ''}" placeholder="e.g. University / College Name" required />
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
          <div class="form-group">
            <label class="form-label" for="m-edu-start">Start Year</label>
            <input type="text" id="m-edu-start" class="form-input" value="${isEdit ? escapeHtml(edu.start_year) : '2022'}" required />
          </div>
          <div class="form-group">
            <label class="form-label" for="m-edu-end">End Year / Expected</label>
            <input type="text" id="m-edu-end" class="form-input" value="${isEdit ? escapeHtml(edu.end_year || '') : '2026'}" placeholder="2026" />
          </div>
        </div>
        <div class="form-group">
          <label class="form-label" for="m-edu-desc">Summary &amp; Focus</label>
          <textarea id="m-edu-desc" class="form-textarea" placeholder="Core focus of studies, honors, or research...">${isEdit ? escapeHtml(edu.description || '') : ''}</textarea>
        </div>
        <div class="form-group">
          <label class="form-label" for="m-edu-courses">Relevant Coursework (Comma-separated)</label>
          <input type="text" id="m-edu-courses" class="form-input" value="${escapeHtml(cwStr)}" placeholder="e.g. Data Structures, Machine Learning, DBMS, Computer Networks" />
        </div>
        <div style="display: flex; gap: 1.5rem; margin-top: 0.5rem;">
          <label class="form-checkbox-label">
            <input type="checkbox" id="m-edu-expected" ${isEdit && edu.expected_graduation ? 'checked' : ''} />
            <span>Mark as in-progress / Expected graduation</span>
          </label>
          <label class="form-checkbox-label">
            <input type="checkbox" id="m-edu-published" ${!isEdit || edu.published ? 'checked' : ''} />
            <span>Publish publicly</span>
          </label>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary" id="m-edu-submit-btn">${isEdit ? 'Save Changes' : 'Create Record'}</button>
        </div>
      </form>
    `;

    const eForm = document.getElementById('edu-modal-form');
    if (eForm) {
      eForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('m-edu-submit-btn');
        if (submitBtn) submitBtn.disabled = true;

        const payload = {
          degree: document.getElementById('m-edu-degree').value.trim(),
          specialization: document.getElementById('m-edu-spec').value.trim(),
          institution: document.getElementById('m-edu-inst').value.trim(),
          start_year: document.getElementById('m-edu-start').value.trim(),
          end_year: document.getElementById('m-edu-end').value.trim(),
          description: document.getElementById('m-edu-desc').value.trim(),
          coursework: document.getElementById('m-edu-courses').value.trim(),
          expected_graduation: document.getElementById('m-edu-expected').checked,
          published: document.getElementById('m-edu-published').checked
        };

        const url = isEdit ? `/api/admin/education/${edu.id}` : '/api/admin/education';
        const method = isEdit ? 'PUT' : 'POST';

        try {
          const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const json = await res.json();
          if (json.success || res.ok) {
            closeModal();
            showToast(isEdit ? "Education record updated successfully!" : "Education record created!");
            loadEducationData();
          } else {
            showToast(json.error || "Failed to save education record", "error");
          }
        } catch {
          showToast("Network error saving education record", "error");
        } finally {
          if (submitBtn) submitBtn.disabled = false;
        }
      });
    }

    openModal();
  };

  const addEduBtn = document.getElementById('btn-add-education');
  if (addEduBtn) addEduBtn.addEventListener('click', () => openEducationModal());


  // 9. Tab: Contact Channels, Resume & Social Links

  const loadContactData = async () => {
    const p = await fetchProfileState();
    if (p) {
      const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.value = val !== undefined && val !== null ? val : '';
      };
      setVal('contact-email-input', p.email);
      setVal('contact-phone-input', p.phone);
      setVal('contact-location-input', p.location);
    }
    loadResumeData();
    loadSocialsData();
  };

  const contactInfoForm = document.getElementById('contact-info-form');
  if (contactInfoForm) {
    contactInfoForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = contactInfoForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const payload = {
        email: document.getElementById('contact-email-input').value.trim(),
        phone: document.getElementById('contact-phone-input').value.trim(),
        location: document.getElementById('contact-location-input').value.trim()
      };

      try {
        const res = await fetch('/api/admin/profile', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
          showToast("Contact details saved successfully!");
          profileState = json.data;
        } else {
          showToast(json.error || "Failed to save contact details", "error");
        }
      } catch {
        showToast("Error saving contact details", "error");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // Resume Management
  const loadResumeData = async () => {
    try {
      const res = await fetch('/api/admin/resume?t=' + Date.now());
      const json = await res.json();
      const view = document.getElementById('resume-current-view');
      if (!view) return;

      if (json.success && json.data) {
        const r = json.data;
        const sizeKb = (r.file_size / 1024).toFixed(1);
        view.innerHTML = `
          <div style="display: flex; align-items: center; justify-content: space-between; padding: 1rem; background: var(--bg-surface-elevated); border-radius: var(--radius-sm); border: 1px solid var(--border-subtle);">
            <div>
              <div style="font-weight: 600;">📄 ${escapeHtml(r.original_filename)}</div>
              <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.2rem;">${sizeKb} KB &bull; Uploaded on ${escapeHtml(r.formatted_date || r.uploaded_at || '')}</div>
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <a href="${escapeHtml(r.download_url)}" target="_blank" class="btn btn-secondary btn-sm">Download</a>
              <button type="button" class="btn btn-danger btn-sm" id="btn-delete-resume">Delete</button>
            </div>
          </div>
        `;

        const delResumeBtn = document.getElementById('btn-delete-resume');
        if (delResumeBtn) {
          delResumeBtn.addEventListener('click', async () => {
            if (confirm("Are you sure you want to permanently delete this resume from storage and public access?")) {
              delResumeBtn.disabled = true;
              delResumeBtn.textContent = 'Deleting...';
              try {
                const delRes = await fetch(`/api/admin/resume/${r.id}`, { method: 'DELETE' });
                const delJson = await delRes.json();
                if (delJson.success) {
                  showToast("Resume deleted successfully from storage!");
                  await loadResumeData();
                } else {
                  showToast(delJson.error || "Failed to delete resume", "error");
                  delResumeBtn.disabled = false;
                  delResumeBtn.textContent = 'Delete';
                }
              } catch {
                showToast("Network error deleting resume", "error");
                delResumeBtn.disabled = false;
                delResumeBtn.textContent = 'Delete';
              }
            }
          });
        }
      } else {
        view.innerHTML = `<p style="color: var(--text-muted);">No active resume uploaded yet.</p>`;
      }
    } catch {
      showToast("Error loading resume details", "error");
    }
  };

  const resumeFileInput = document.getElementById('resume-file-input');
  if (resumeFileInput) {
    resumeFileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
        showToast("Only PDF documents are permitted", "error");
        return;
      }

      const formData = new FormData();
      formData.append('resume', file);

      try {
        const res = await fetch('/api/admin/resume/upload', { method: 'POST', body: formData });
        const json = await res.json();
        if (json.success) {
          showToast("Resume PDF uploaded successfully!");
          loadResumeData();
        } else {
          showToast(json.error || "Upload failed", "error");
        }
      } catch {
        showToast("Error uploading resume", "error");
      }
    });
  }

  // Social Links Management
  const loadSocialsData = async () => {
    try {
      const res = await fetch('/api/admin/socials');
      const json = await res.json();
      if (!json.success) return;

      socialsData = json.data || [];
      renderSocialsTable();
    } catch {
      showToast("Error loading social links", "error");
    }
  };

  const renderSocialsTable = () => {
    const tbody = document.getElementById('socials-table-body');
    if (!tbody) return;

    if (socialsData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 2rem;">No social links added yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = socialsData.map(s => `
      <tr>
        <td><strong>${escapeHtml(s.name)}</strong></td>
        <td><a href="${escapeHtml(s.url)}" target="_blank" style="color: var(--accent-secondary);">${escapeHtml(s.url)}</a></td>
        <td><span class="status-tag ${s.enabled ? 'active' : 'inactive'}">${s.enabled ? 'Active' : 'Hidden'}</span></td>
        <td style="text-align: right;">
          <div class="table-actions" style="justify-content: flex-end;">
            <button class="btn btn-secondary btn-sm edit-soc-btn" data-id="${s.id}">Edit</button>
            <button class="btn btn-danger btn-sm delete-soc-btn" data-id="${s.id}">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll('.edit-soc-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const item = socialsData.find(s => s.id === parseInt(btn.dataset.id));
        if (item) openSocialModal(item);
      });
    });

    tbody.querySelectorAll('.delete-soc-btn').forEach(btn => {
      btn.addEventListener('click', () => confirmDelete('Social link', async () => {
        try {
          const res = await fetch(`/api/admin/socials/${btn.dataset.id}`, { method: 'DELETE' });
          if (res.ok) {
            showToast("Social link deleted");
            loadSocialsData();
          } else {
            showToast("Failed to delete social link", "error");
          }
        } catch {
          showToast("Network error deleting social link", "error");
        }
      }));
    });
  };

  const openSocialModal = (soc = null) => {
    const isEdit = Boolean(soc);
    modalContent.innerHTML = `
      <div class="card-header">
        <h3 class="card-title">${isEdit ? 'Edit Social Link' : 'Add Social Link'}</h3>
      </div>
      <form id="soc-modal-form">
        <div class="form-group">
          <label class="form-label" for="m-soc-name">Platform Name</label>
          <input type="text" id="m-soc-name" class="form-input" value="${isEdit ? escapeHtml(soc.name) : ''}" placeholder="e.g. GitHub, LinkedIn, Kaggle, Twitter" required />
        </div>
        <div class="form-group">
          <label class="form-label" for="m-soc-url">Profile URL</label>
          <input type="url" id="m-soc-url" class="form-input" value="${isEdit ? escapeHtml(soc.url) : ''}" placeholder="https://..." required />
        </div>
        <div class="form-group">
          <label class="form-checkbox-label">
            <input type="checkbox" id="m-soc-enabled" ${!isEdit || soc.enabled ? 'checked' : ''} />
            <span>Enable link publicly</span>
          </label>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 0.75rem; margin-top: 1.5rem;">
          <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
          <button type="submit" class="btn btn-primary" id="m-soc-submit-btn">${isEdit ? 'Save Changes' : 'Create Link'}</button>
        </div>
      </form>
    `;

    const socForm = document.getElementById('soc-modal-form');
    if (socForm) {
      socForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const submitBtn = document.getElementById('m-soc-submit-btn');
        if (submitBtn) submitBtn.disabled = true;

        const payload = {
          name: document.getElementById('m-soc-name').value.trim(),
          url: document.getElementById('m-soc-url').value.trim(),
          enabled: document.getElementById('m-soc-enabled').checked
        };

        const url = isEdit ? `/api/admin/socials/${soc.id}` : '/api/admin/socials';
        const method = isEdit ? 'PUT' : 'POST';

        try {
          const res = await fetch(url, {
            method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
          });
          const json = await res.json();
          if (json.success || res.ok) {
            closeModal();
            showToast("Social link saved");
            loadSocialsData();
          } else {
            showToast(json.error || "Failed to save social link", "error");
          }
        } catch {
          showToast("Network error saving social link", "error");
        } finally {
          if (submitBtn) submitBtn.disabled = false;
        }
      });
    }

    openModal();
  };

  const addSocBtn = document.getElementById('btn-add-social');
  if (addSocBtn) addSocBtn.addEventListener('click', () => openSocialModal());

  // 10. Tab: Messages Inbox

  const loadMessagesData = async () => {
    try {
      const res = await fetch('/api/admin/messages');
      const json = await res.json();
      if (!json.success) return;

      messagesData = json.data || [];
      renderMessagesTable();
    } catch {
      showToast("Error loading messages inbox", "error");
    }
  };

  const renderMessagesTable = () => {
    const tbody = document.getElementById('messages-table-body');
    if (!tbody) return;

    if (messagesData.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-muted); padding: 2rem;">No messages yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = messagesData.map(m => `
      <tr style="${!m.is_read ? 'background: rgba(99, 102, 241, 0.05);' : ''}">
        <td><span style="font-size: 0.8rem; color: var(--text-muted);">${escapeHtml(m.formatted_date)}</span></td>
        <td><strong>${escapeHtml(m.name)}</strong></td>
        <td><a href="mailto:${escapeHtml(m.email)}" style="color: var(--accent-secondary);">${escapeHtml(m.email)}</a></td>
        <td>${escapeHtml(m.subject)}</td>
        <td><span class="status-tag ${m.is_read ? 'draft' : 'active'}">${m.is_read ? 'Read' : 'New'}</span></td>
        <td style="text-align: right;">
          <div class="table-actions" style="justify-content: flex-end;">
            <button class="btn btn-secondary btn-sm view-msg-btn" data-id="${m.id}">Read</button>
            <button class="btn btn-danger btn-sm delete-msg-btn" data-id="${m.id}">Delete</button>
          </div>
        </td>
      </tr>
    `).join('');

    tbody.querySelectorAll('.view-msg-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const msg = messagesData.find(m => m.id === parseInt(btn.dataset.id));
        if (msg) openMessageModal(msg);
      });
    });

    tbody.querySelectorAll('.delete-msg-btn').forEach(btn => {
      btn.addEventListener('click', () => confirmDelete('Message', async () => {
        try {
          const res = await fetch(`/api/admin/messages/${btn.dataset.id}`, { method: 'DELETE' });
          if (res.ok) {
            showToast("Message deleted");
            loadMessagesData();
          } else {
            showToast("Failed to delete message", "error");
          }
        } catch {
          showToast("Network error deleting message", "error");
        }
      }));
    });
  };

  const openMessageModal = (msg) => {
    if (!msg) return;

    // Mark as read in background without blocking modal
    if (!msg.is_read) {
      msg.is_read = true;
      fetch(`/api/admin/messages/${msg.id}/read`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_read: true })
      }).then(() => {
        loadMessagesData();
        loadDashboardStats();
      }).catch(() => { });
    }

    modalContent.innerHTML = `
      <div class="card-header">
        <div>
          <h3 class="card-title">${escapeHtml(msg.subject)}</h3>
          <p class="card-desc">From: <strong>${escapeHtml(msg.name)}</strong> &lt;${escapeHtml(msg.email)}&gt; &bull; ${escapeHtml(msg.formatted_date)}</p>
        </div>
      </div>
      <div style="background: var(--bg-surface-elevated); padding: 1.5rem; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); line-height: 1.7; white-space: pre-wrap; font-size: 0.95rem; margin-bottom: 1.5rem;">${escapeHtml(msg.message)}</div>
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <a href="mailto:${escapeHtml(msg.email)}?subject=Re: ${encodeURIComponent(msg.subject)}" class="btn btn-primary btn-sm">
          <span>Reply via Email</span>
        </a>
        <button type="button" class="btn btn-secondary btn-sm" onclick="closeModal()">Close</button>
      </div>
    `;

    openModal();
  };


  // 11. Tab: Settings, SEO, Security & Backup

  const loadSettingsData = async () => {
    try {
      const res = await fetch('/api/admin/settings');
      const json = await res.json();
      if (!json.success) return;

      const s = json.data;
      const setVal = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.value = val !== undefined && val !== null ? val : '';
      };

      setVal('set-site-title', s.site_title);
      setVal('set-meta-desc', s.meta_description);
      setVal('set-keywords', s.keywords);

      const mmCb = document.getElementById('set-maintenance-mode');
      if (mmCb) mmCb.checked = Boolean(s.maintenance_mode);

      setVal('set-maintenance-msg', s.maintenance_message);
    } catch {
      showToast("Error loading site settings", "error");
    }
  };

  const settingsForm = document.getElementById('settings-form');
  if (settingsForm) {
    settingsForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = settingsForm.querySelector('button[type="submit"]');
      if (submitBtn) submitBtn.disabled = true;

      const payload = {
        site_title: document.getElementById('set-site-title').value.trim(),
        meta_description: document.getElementById('set-meta-desc').value.trim(),
        keywords: document.getElementById('set-keywords').value.trim(),
        maintenance_mode: document.getElementById('set-maintenance-mode').checked,
        maintenance_message: document.getElementById('set-maintenance-msg').value.trim()
      };

      try {
        const res = await fetch('/api/admin/settings', {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const json = await res.json();
        if (json.success) {
          showToast("SEO & maintenance settings saved successfully!");
        } else {
          showToast(json.error || "Save failed", "error");
        }
      } catch {
        showToast("Error saving site settings", "error");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // Password Change Form
  const passwordForm = document.getElementById('password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = passwordForm.querySelector('button[type="submit"]');

      const newPass = document.getElementById('admin-new-password').value;
      const confPass = document.getElementById('admin-confirm-password').value;

      if (newPass !== confPass) {
        showToast("New passwords do not match", "error");
        return;
      }

      if (newPass.length < 8) {
        showToast("Password must be at least 8 characters long", "error");
        return;
      }

      if (submitBtn) submitBtn.disabled = true;

      try {
        const res = await fetch('/api/auth/change-password', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ new_password: newPass })
        });
        const json = await res.json();
        if (json.success) {
          showToast("Password updated successfully!");
          document.getElementById('admin-new-password').value = '';
          document.getElementById('admin-confirm-password').value = '';
        } else {
          showToast(json.error || "Password change failed", "error");
        }
      } catch {
        showToast("Error changing password", "error");
      } finally {
        if (submitBtn) submitBtn.disabled = false;
      }
    });
  }

  // Backup Import Uploader
  const backupImportInput = document.getElementById('backup-import-file');
  if (backupImportInput) {
    backupImportInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      if (!confirm("Warning: Restoring will overwrite current portfolio data with backup contents. Continue?")) {
        backupImportInput.value = '';
        return;
      }

      const formData = new FormData();
      formData.append('backup_file', file);

      try {
        const res = await fetch('/api/admin/backup/import', { method: 'POST', body: formData });
        const json = await res.json();
        if (json.success) {
          showToast("Database successfully restored from JSON backup!");
          setTimeout(() => window.location.reload(), 1200);
        } else {
          showToast(json.error || "Restore failed", "error");
        }
      } catch {
        showToast("Error restoring backup", "error");
      }
    });
  }


  // Universal Modal Controls (Rock-Solid State Lifecycle)

  window.openModal = () => {
    if (modal) {
      modal.style.display = 'flex';
      modal.classList.add('is-open');
      modal.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    }
  };

  window.closeModal = () => {
    if (modal) {
      modal.classList.remove('is-open');
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';
      document.body.style.overflow = '';
      if (modalContent) modalContent.innerHTML = '';
    }
  };

  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal && modal.classList.contains('is-open')) {
      closeModal();
    }
  });

  const confirmDelete = (itemType, callback) => {
    if (confirm(`Are you sure you want to permanently delete this ${itemType.toLowerCase()}?`)) {
      callback();
    }
  };


  // Drag & Drop Reordering Utility

  function initDragAndDrop(tbodyElement, reorderApiUrl, onComplete) {
    let draggedRow = null;

    const rows = tbodyElement.querySelectorAll('.draggable-row');
    rows.forEach(row => {
      row.addEventListener('dragstart', (e) => {
        draggedRow = row;
        row.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
      });

      row.addEventListener('dragend', () => {
        row.classList.remove('dragging');
        draggedRow = null;
      });

      row.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        const currentHoverRow = e.target.closest('.draggable-row');
        if (!currentHoverRow || currentHoverRow === draggedRow) return;

        const rect = currentHoverRow.getBoundingClientRect();
        const next = (e.clientY - rect.top) / (rect.bottom - rect.top) > 0.5;
        tbodyElement.insertBefore(draggedRow, next ? currentHoverRow.nextSibling : currentHoverRow);
      });

      row.addEventListener('drop', async (e) => {
        e.preventDefault();
        const reorderedIds = Array.from(tbodyElement.querySelectorAll('.draggable-row')).map(r => parseInt(r.dataset.id));
        try {
          const res = await fetch(reorderApiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ordered_ids: reorderedIds })
          });
          if (res.ok) {
            showToast("Order updated");
            if (onComplete) onComplete();
          }
        } catch {
          showToast("Failed to save reordering", "error");
        }
      });
    });
  }

  // Utility: Escape HTML
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Initial Load
  loadDashboardStats();
});
