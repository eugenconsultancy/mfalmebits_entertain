/* ═══════════════════════════════════════════════════════════════════
   MfalmeBits Admin — Custom JavaScript
   File: static/admin/js/mfalmebits_admin.js
   Loaded via: JAZZMIN_SETTINGS["custom_js"]
   ═══════════════════════════════════════════════════════════════════ */

(function () {
  'use strict';

  /* ─── Utility helpers ─────────────────────────────────────────── */
  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  /* ─── 1. Animate page entry ───────────────────────────────────── */
  function animateEntry() {
    const contentWrapper = $('.content-wrapper');
    if (!contentWrapper) return;
    contentWrapper.style.opacity = '0';
    contentWrapper.style.transform = 'translateY(8px)';
    contentWrapper.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        contentWrapper.style.opacity = '1';
        contentWrapper.style.transform = 'translateY(0)';
      });
    });
  }

  /* ─── 2. Add row-count badge to changelist ────────────────────── */
  function addRowCount() {
    const resultCount = $('.paginator');
    const table = $('#result_list');
    if (!resultCount || !table) return;

    const rows = $$('tbody tr', table).length;
    const badge = document.createElement('span');
    badge.style.cssText = `
      display: inline-flex; align-items: center;
      background: rgba(193,58,16,0.2); color: #ffb8a0;
      border: 1px solid rgba(193,58,16,0.3); border-radius: 99px;
      font-size: 0.72rem; font-weight: 700; padding: 2px 10px;
      margin-left: 10px; font-family: 'Outfit', sans-serif;
      letter-spacing: 0.04em;
    `;
    badge.textContent = `${rows} shown`;
    resultCount.appendChild(badge);
  }

  /* ─── 3. Sticky table header on scroll ───────────────────────── */
  function stickyTableHeader() {
    const table = $('#result_list');
    if (!table) return;
    const thead = $('thead', table);
    if (!thead) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        thead.style.position = entry.isIntersecting ? '' : 'sticky';
        thead.style.top = entry.isIntersecting ? '' : '56px'; // navbar height
        thead.style.zIndex = entry.isIntersecting ? '' : '10';
      },
      { threshold: 0, rootMargin: '-56px 0px 0px 0px' }
    );
    observer.observe(table);
  }

  /* ─── 4. Confirm dangerous actions ───────────────────────────── */
  function confirmDangerousActions() {
    const deleteLinks = $$('a.deletelink, .submit-row a.deletelink');
    deleteLinks.forEach(link => {
      link.addEventListener('click', e => {
        if (!confirm('⚠️  Are you sure you want to delete this item? This cannot be undone.')) {
          e.preventDefault();
        }
      });
    });

    // Warn on bulk delete action
    const actionForm = $('#changelist-form');
    if (actionForm) {
      actionForm.addEventListener('submit', e => {
        const action = $('select[name=action]', actionForm);
        if (!action) return;
        if (action.value.includes('delete')) {
          const checked = $$('input[name=_selected_action]:checked', actionForm).length;
          if (!confirm(`⚠️  Delete ${checked} selected item(s)? This cannot be undone.`)) {
            e.preventDefault();
          }
        }
      });
    }
  }

  /* ─── 5. Auto-slug from title field ──────────────────────────── */
  function setupSlugPreview() {
    const titleInput = $('input#id_title, input#id_name');
    const slugInput  = $('input#id_slug');
    if (!titleInput || !slugInput || slugInput.value) return; // only on new records

    let userEdited = false;
    slugInput.addEventListener('input', () => { userEdited = true; });

    titleInput.addEventListener('input', () => {
      if (userEdited) return;
      const slug = titleInput.value
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .trim()
        .replace(/\s+/g, '-');
      slugInput.value = slug;
      // pulse animation
      slugInput.style.transition = 'border-color 0.3s';
      slugInput.style.borderColor = '#c13a10';
      setTimeout(() => { slugInput.style.borderColor = ''; }, 400);
    });
  }

  /* ─── 6. Image previews on file input change ─────────────────── */
  function liveImagePreview() {
    $$('input[type=file]').forEach(input => {
      if (!input.accept || !input.accept.includes('image')) return;

      const wrapper = input.closest('.field-box, .form-row, td') || input.parentElement;
      let previewEl = $('img.mb-live-preview', wrapper);

      if (!previewEl) {
        previewEl = document.createElement('img');
        previewEl.className = 'mb-live-preview';
        previewEl.style.cssText = `
          display: none; max-width: 200px; max-height: 140px;
          border-radius: 8px; margin-top: 8px;
          border: 2px solid rgba(193,58,16,0.3);
          box-shadow: 0 4px 16px rgba(0,0,0,0.4);
          object-fit: cover; transition: opacity 0.3s;
        `;
        input.insertAdjacentElement('afterend', previewEl);
      }

      input.addEventListener('change', () => {
        const file = input.files[0];
        if (!file || !file.type.startsWith('image/')) return;
        const url = URL.createObjectURL(file);
        previewEl.style.opacity = '0';
        previewEl.style.display = 'block';
        previewEl.onload = () => {
          previewEl.style.opacity = '1';
          URL.revokeObjectURL(url);
        };
        previewEl.src = url;
      });
    });
  }

  /* ─── 7. Character counters on textareas ─────────────────────── */
  function charCounters() {
    $$('textarea').forEach(ta => {
      const max = ta.maxLength > 0 ? ta.maxLength : null;
      if (!max) return;
      const counter = document.createElement('small');
      counter.style.cssText = `
        display: block; text-align: right; margin-top: 3px;
        font-size: 0.72rem; font-family: 'Outfit', sans-serif;
        color: #8888aa; transition: color 0.2s;
      `;
      ta.insertAdjacentElement('afterend', counter);

      const update = () => {
        const remaining = max - ta.value.length;
        counter.textContent = `${ta.value.length} / ${max}`;
        counter.style.color = remaining < 20 ? '#c13a10' : remaining < 50 ? '#d4922a' : '#8888aa';
      };
      ta.addEventListener('input', update);
      update();
    });
  }

  /* ─── 8. Collapsible fieldsets toggle ────────────────────────── */
  function collapsibleFieldsets() {
    $$('fieldset.module.collapse').forEach(fs => {
      const h2 = $('h2', fs);
      if (!h2) return;

      // Start collapsed
      const content = $$(':scope > .form-row, :scope > .field-box', fs);
      let open = false;

      const toggle = () => {
        open = !open;
        content.forEach(el => {
          el.style.display = open ? '' : 'none';
        });
        h2.style.borderRadius = open ? '0' : 'var(--mb-radius)';
        const icon = $('i.collapse-icon', h2) || (() => {
          const i = document.createElement('i');
          i.className = 'fas fa-chevron-right collapse-icon';
          i.style.cssText = `
            float: right; margin-top: 1px;
            transition: transform 0.25s ease; font-size: 0.75rem;
          `;
          h2.appendChild(i);
          return i;
        })();
        icon.style.transform = open ? 'rotate(90deg)' : 'rotate(0deg)';
      };

      // Initialise closed
      content.forEach(el => { el.style.display = 'none'; });
      h2.addEventListener('click', toggle);
    });
  }

  /* ─── 9. Keyboard shortcuts ───────────────────────────────────── */
  function keyboardShortcuts() {
    document.addEventListener('keydown', e => {
      // Ctrl/Cmd + S → submit the form
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        const saveBtn = $('input[name=_save], .submit-row input[type=submit]');
        if (saveBtn) {
          e.preventDefault();
          saveBtn.click();
          showToast('💾 Saving…', 'info');
        }
      }
      // Escape → go back (if inside a change form)
      if (e.key === 'Escape' && window.location.pathname.includes('/change/')) {
        e.preventDefault();
        history.back();
      }
    });
  }

  /* ─── 10. Toast notification ──────────────────────────────────── */
  function showToast(message, type = 'success', duration = 3000) {
    const colours = {
      success: ['rgba(74,124,107,0.2)', '#a0dfce', 'var(--mb-sage)'],
      error:   ['rgba(193,58,16,0.2)', '#ffb8a0', 'var(--mb-terra)'],
      info:    ['rgba(14,158,154,0.2)', '#a0f0ee', 'var(--mb-teal)'],
      warning: ['rgba(212,146,42,0.2)', '#ffe0a0', 'var(--mb-ochre)'],
    };
    const [bg, fg, border] = colours[type] || colours.info;

    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed; top: 70px; right: 20px; z-index: 99999;
      background: ${bg}; color: ${fg};
      border-left: 3px solid ${border};
      border-radius: 8px; padding: 12px 20px;
      font-family: 'Outfit', sans-serif; font-size: 0.84rem; font-weight: 600;
      box-shadow: 0 8px 32px rgba(0,0,0,0.5);
      backdrop-filter: blur(8px);
      transform: translateX(120%); transition: transform 0.3s ease;
      max-width: 320px;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    requestAnimationFrame(() => {
      requestAnimationFrame(() => { toast.style.transform = 'translateX(0)'; });
    });
    setTimeout(() => {
      toast.style.transform = 'translateX(120%)';
      setTimeout(() => toast.remove(), 350);
    }, duration);
  }
  // Expose globally so inline templates can call it
  window.mbShowToast = showToast;

  /* ─── 11. Highlight selected sidebar item ────────────────────── */
  function highlightActiveSidebarItem() {
    const path = window.location.pathname;
    $$('.nav-sidebar .nav-link').forEach(link => {
      if (link.getAttribute('href') === path) {
        link.classList.add('active');
        // Expand parent tree if collapsed
        const parent = link.closest('.nav-treeview');
        if (parent) {
          parent.style.display = 'block';
          const parentLi = parent.closest('.nav-item.has-treeview');
          if (parentLi) parentLi.classList.add('menu-open');
        }
      }
    });
  }

  /* ─── 12. Table row click-to-select ──────────────────────────── */
  function rowClickSelect() {
    $$('#result_list tbody tr').forEach(row => {
      const checkbox = $('input[type=checkbox]', row);
      if (!checkbox) return;
      row.style.cursor = 'pointer';
      row.addEventListener('click', e => {
        if (e.target.tagName === 'A' || e.target.tagName === 'INPUT') return;
        checkbox.checked = !checkbox.checked;
        row.style.background = checkbox.checked
          ? 'rgba(193,58,16,0.12)'
          : '';
      });
      // Pre-highlight if already checked
      if (checkbox.checked) {
        row.style.background = 'rgba(193,58,16,0.12)';
      }
    });
  }

  /* ─── 13. Show save success toast from Django message ────────── */
  function djangoMessagesToToast() {
    $$('.messagelist li').forEach(li => {
      const text = li.textContent.trim();
      const type = li.classList.contains('error')   ? 'error'
                 : li.classList.contains('warning') ? 'warning'
                 : li.classList.contains('info')    ? 'info'
                 : 'success';
      showToast(text, type, 4500);
      // Fade out the original message box gracefully
      li.style.transition = 'opacity 0.5s ease 4s';
      li.style.opacity = '0';
      setTimeout(() => li.closest('.messagelist')?.remove(), 5000);
    });
  }

  /* ─── 14. Filter pill summary ─────────────────────────────────── */
  function showActiveFilters() {
    const params = new URLSearchParams(window.location.search);
    const excluded = ['q', 'p', 'o', 'all'];
    const filters = [...params.entries()].filter(([k]) => !excluded.includes(k));
    if (!filters.length) return;

    const container = $('#changelist-search') || $('.actions');
    if (!container) return;

    const pill = document.createElement('div');
    pill.style.cssText = `
      display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
      margin-bottom: 8px; font-family: 'Outfit', sans-serif;
    `;
    const label = document.createElement('span');
    label.style.cssText = `color: #8888aa; font-size: 0.75rem; font-weight: 600;
      letter-spacing: 0.06em; text-transform: uppercase;`;
    label.textContent = 'Filters:';
    pill.appendChild(label);

    filters.forEach(([key, val]) => {
      const tag = document.createElement('span');
      tag.style.cssText = `
        display: inline-flex; align-items: center; gap: 5px;
        background: rgba(193,58,16,0.15); color: #ffb8a0;
        border: 1px solid rgba(193,58,16,0.3); border-radius: 99px;
        font-size: 0.72rem; font-weight: 600; padding: 2px 10px;
      `;
      tag.textContent = `${key.replace(/_/g,' ')}: ${val}`;

      // Click to remove this filter
      tag.style.cursor = 'pointer';
      tag.title = 'Remove filter';
      tag.addEventListener('click', () => {
        params.delete(key);
        window.location.search = params.toString();
      });
      pill.appendChild(tag);
    });

    const clearAll = document.createElement('a');
    clearAll.href = window.location.pathname;
    clearAll.textContent = '✕ Clear all';
    clearAll.style.cssText = `color: var(--mb-terra); font-size: 0.72rem;
      font-weight: 700; text-decoration: none; margin-left: 4px;`;
    pill.appendChild(clearAll);

    container.insertAdjacentElement('beforebegin', pill);
  }

  /* ─── 15. Inline admin image preview on existing entries ──────── */
  function inlineImagePreviews() {
    $$('.inline-group img').forEach(img => {
      if (img.width > 120 || img.naturalWidth > 120) return;
      img.style.cssText += `
        cursor: zoom-in; transition: transform 0.25s ease;
      `;
      img.addEventListener('click', () => {
        const modal = document.createElement('div');
        modal.style.cssText = `
          position: fixed; inset: 0; z-index: 99999;
          background: rgba(0,0,0,0.85); display: flex;
          align-items: center; justify-content: center;
          backdrop-filter: blur(6px);
          animation: mb-fade-in 0.2s ease;
        `;
        modal.innerHTML = `
          <img src="${img.src}"
            style="max-width:90vw;max-height:85vh;border-radius:12px;
              box-shadow:0 24px 80px rgba(0,0,0,0.8);" />
        `;
        modal.addEventListener('click', () => modal.remove());
        document.body.appendChild(modal);
      });
    });
  }

  /* ─── Init ─────────────────────────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', () => {
    animateEntry();
    addRowCount();
    stickyTableHeader();
    confirmDangerousActions();
    setupSlugPreview();
    liveImagePreview();
    charCounters();
    collapsibleFieldsets();
    keyboardShortcuts();
    highlightActiveSidebarItem();
    rowClickSelect();
    djangoMessagesToToast();
    showActiveFilters();
    inlineImagePreviews();

    console.log('%c MfalmeBits Admin ✦ ', [
      'background: linear-gradient(135deg, #c13a10, #d4922a)',
      'color: white', 'font-family: Outfit, sans-serif',
      'font-size: 13px', 'font-weight: 700',
      'padding: 6px 14px', 'border-radius: 4px',
    ].join(';'));
  });
})();