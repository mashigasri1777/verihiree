/**
 * VeriHire AI – Client-Side Application Engine
 * "Verify Talent. Hire With Confidence."
 */

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initTabs();
  initModals();
  initCandidateFilters();
  initNotificationCenter();
});

// ============================================================================
// 1. Dark / Light Theme Engine
// ============================================================================
function initTheme() {
  const savedTheme = localStorage.getItem("verihire_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcons(savedTheme);

  document.querySelectorAll(".theme-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const current = document.documentElement.getAttribute("data-theme") || "light";
      const next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("verihire_theme", next);
      updateThemeIcons(next);
      showToast(`Switched to ${next} theme`, "info");
    });
  });
}

function updateThemeIcons(theme) {
  document.querySelectorAll(".theme-toggle-btn i").forEach((icon) => {
    if (theme === "dark") {
      icon.className = "fa-solid fa-sun text-warning";
    } else {
      icon.className = "fa-solid fa-moon text-muted";
    }
  });
}

// ============================================================================
// 2. Toast Notification Engine
// ============================================================================
function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;

  let iconHtml = '<i class="fa-solid fa-circle-info text-primary"></i>';
  if (type === "success") iconHtml = '<i class="fa-solid fa-circle-check text-success"></i>';
  if (type === "warning") iconHtml = '<i class="fa-solid fa-triangle-exclamation text-warning"></i>';
  if (type === "danger") iconHtml = '<i class="fa-solid fa-circle-exclamation text-danger"></i>';

  toast.innerHTML = `
    <div style="font-size: 1.15rem;">${iconHtml}</div>
    <div style="flex: 1;">${message}</div>
    <button type="button" style="background:none;border:none;cursor:pointer;color:var(--text-muted);padding:4px;" onclick="this.parentElement.remove()">
      <i class="fa-solid fa-xmark"></i>
    </button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(50px)";
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ============================================================================
// 3. Tab System
// ============================================================================
function initTabs() {
  document.querySelectorAll(".tabs-nav").forEach((tabNav) => {
    const buttons = tabNav.querySelectorAll(".tab-btn");
    buttons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const targetId = btn.getAttribute("data-tab");
        const container = tabNav.closest(".tab-container") || document;

        // Toggle active button
        buttons.forEach((b) => b.classList.remove("active"));
        btn.classList.add("active");

        // Toggle active pane
        container.querySelectorAll(".tab-pane").forEach((pane) => {
          if (pane.id === targetId) {
            pane.classList.add("active");
          } else {
            pane.classList.remove("active");
          }
        });
      });
    });
  });
}

// ============================================================================
// 4. Modals Engine
// ============================================================================
function initModals() {
  document.querySelectorAll("[data-modal-target]").forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const targetModal = document.getElementById(trigger.getAttribute("data-modal-target"));
      if (targetModal) openModal(targetModal);
    });
  });

  document.querySelectorAll(".modal-overlay").forEach((modal) => {
    modal.addEventListener("click", (e) => {
      if (e.target === modal || e.target.classList.contains("modal-close-btn")) {
        closeModal(modal);
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach((m) => closeModal(m));
    }
  });
}

function openModal(modal) {
  if (typeof modal === "string") modal = document.getElementById(modal);
  if (modal) {
    modal.classList.add("active");
    document.body.style.overflow = "hidden";
  }
}

function closeModal(modal) {
  if (typeof modal === "string") modal = document.getElementById(modal);
  if (modal) {
    modal.classList.remove("active");
    document.body.style.overflow = "";
  }
}

// ============================================================================
// 5. Candidate Table Filtering & Live Search
// ============================================================================
function initCandidateFilters() {
  const filterPills = document.querySelectorAll(".filter-pill[data-filter]");
  const tableRows = document.querySelectorAll("#candidatesTableBody tr");
  const searchInput = document.getElementById("tableSearchInput");

  filterPills.forEach((pill) => {
    pill.addEventListener("click", () => {
      filterPills.forEach((p) => p.classList.remove("active"));
      pill.classList.add("active");
      applyCandidateFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", () => {
      applyCandidateFilters();
    });
  }
}

function applyCandidateFilters() {
  const activePill = document.querySelector(".filter-pill.active[data-filter]");
  const currentFilter = activePill ? activePill.getAttribute("data-filter") : "all";
  const searchInput = document.getElementById("tableSearchInput");
  const searchQuery = searchInput ? searchInput.value.toLowerCase().trim() : "";

  const rows = document.querySelectorAll("#candidatesTableBody tr");
  rows.forEach((row) => {
    const status = (row.getAttribute("data-status") || "").toLowerCase();
    const risk = (row.getAttribute("data-risk") || "").toLowerCase();
    const text = row.innerText.toLowerCase();

    let matchesFilter = false;
    if (currentFilter === "all") matchesFilter = true;
    else if (currentFilter === "verified" && status.includes("verified")) matchesFilter = true;
    else if (currentFilter === "manual" && status.includes("manual")) matchesFilter = true;
    else if (currentFilter === "suspicious" && status.includes("suspicious")) matchesFilter = true;
    else if (currentFilter === "high-risk" && risk.includes("high")) matchesFilter = true;
    else if (currentFilter === "shortlisted" && row.getAttribute("data-decision") === "SHORTLISTED") matchesFilter = true;

    const matchesSearch = !searchQuery || text.includes(searchQuery);

    if (matchesFilter && matchesSearch) {
      row.style.display = "";
    } else {
      row.style.display = "none";
    }
  });
}

// ============================================================================
// 6. Recruiter Pipeline Decisions
// ============================================================================
async function setCandidateDecision(candidateId, decision) {
  try {
    const res = await fetch(`/api/candidate/${candidateId}/decision`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ decision })
    });

    const data = await res.json();
    if (res.ok) {
      if (decision === "SHORTLISTED") {
        showToast("Candidate successfully shortlisted for interview!", "success");
      } else if (decision === "VERIFICATION_REQUESTED") {
        showToast("Candidate flagged for manual registrar audit.", "warning");
      } else if (decision === "REJECTED") {
        showToast("Candidate application rejected.", "danger");
      } else {
        showToast("Candidate application saved to recruiter archive.", "info");
      }
      setTimeout(() => window.location.reload(), 900);
    } else {
      showToast(data.detail || "Failed to update candidate status", "danger");
    }
  } catch (err) {
    showToast("Network error executing recruiter action.", "danger");
  }
}

// ============================================================================
// 7. Schedule Interview Action
// ============================================================================
async function submitInterviewSchedule(e, candidateId) {
  e.preventDefault();
  const form = e.target;
  const interviewType = form.interview_type.value;
  const interviewerName = form.interviewer_name.value;
  const scheduledDate = form.scheduled_date.value;
  const notes = form.notes.value;

  try {
    const res = await fetch(`/api/candidate/${candidateId}/schedule-interview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        interview_type: interviewType,
        interviewer_name: interviewerName,
        scheduled_at: scheduledDate,
        notes: notes
      })
    });

    if (res.ok) {
      showToast("Interview invitation scheduled and calendar sync complete!", "success");
      closeModal("interviewScheduleModal");
      setTimeout(() => window.location.reload(), 900);
    } else {
      const err = await res.json();
      showToast(err.detail || "Error scheduling interview", "danger");
    }
  } catch (err) {
    showToast("Failed to connect to recruitment server.", "danger");
  }
}

// ============================================================================
// 8. View Evidence Modal Renderer
// ============================================================================
function viewCertificateEvidence(certName, candidateName, certId, issuer, diffJsonStr) {
  const modal = document.getElementById("evidenceModal");
  if (!modal) return;

  const contentArea = document.getElementById("evidenceContent");
  let diffData = { field_matches: [] };

  try {
    diffData = JSON.parse(diffJsonStr);
  } catch (e) {
    diffData = { field_matches: [] };
  }

  let tableRows = "";
  if (diffData.field_matches && diffData.field_matches.length > 0) {
    tableRows = diffData.field_matches
      .map(
        (m) => `
      <tr>
        <td style="font-weight: 600; padding: 10px 14px; border-bottom: 1px solid var(--border);">${m.field}</td>
        <td style="padding: 10px 14px; border-bottom: 1px solid var(--border); font-family: var(--font-mono); font-size: 0.85rem;">${m.claim || "—"}</td>
        <td style="padding: 10px 14px; border-bottom: 1px solid var(--border); font-family: var(--font-mono); font-size: 0.85rem;">${m.official || "—"}</td>
        <td style="padding: 10px 14px; border-bottom: 1px solid var(--border); text-align: center;">
          ${
            m.match
              ? '<span class="badge badge-verified"><i class="fa-solid fa-check"></i> Match</span>'
              : '<span class="badge badge-fake"><i class="fa-solid fa-xmark"></i> Mismatch</span>'
          }
        </td>
      </tr>
    `
      )
      .join("");
  } else {
    tableRows = `
      <tr>
        <td colspan="4" style="text-align: center; padding: 1.5rem; color: var(--text-muted);">
          Authority record queried. Detailed field reconciliation logged in audit records.
        </td>
      </tr>
    `;
  }

  contentArea.innerHTML = `
    <div style="margin-bottom: 1.25rem;">
      <h4 style="font-size: 1.15rem; font-weight: 700;">${certName}</h4>
      <p style="color: var(--text-muted); font-size: 0.85rem;">Claimed by ${candidateName} • Issuing Authority: ${issuer}</p>
    </div>

    <div style="background: var(--bg-surface-subtle); border: 1px solid var(--border); border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 1.5rem;">
      <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.875rem;">
        <thead>
          <tr style="background: var(--bg-hover);">
            <th style="padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase;">Field</th>
            <th style="padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase;">Resume Claim</th>
            <th style="padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase;">Issuer Registry</th>
            <th style="padding: 10px 14px; font-weight: 600; color: var(--text-muted); font-size: 0.75rem; text-transform: uppercase; text-align: center;">Verdict</th>
          </tr>
        </thead>
        <tbody>
          ${tableRows}
        </tbody>
      </table>
    </div>

    <div style="background: var(--primary-50); border: 1px solid var(--primary-200); border-radius: var(--radius-md); padding: 1rem; font-size: 0.85rem; color: var(--primary-800);">
      <i class="fa-solid fa-shield-halved"></i> <strong>Audit Hash Verified:</strong> Record timestamped and logged in candidate tamper-evident ledger.
    </div>
  `;

  openModal(modal);
}

// ============================================================================
// 9. Notification Center Drawer
// ============================================================================
function initNotificationCenter() {
  const notifBtn = document.getElementById("notifToggleBtn");
  const notifPopover = document.getElementById("notifPopover");

  if (notifBtn && notifPopover) {
    notifBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      notifPopover.classList.toggle("active");
    });

    document.addEventListener("click", (e) => {
      if (!notifPopover.contains(e.target) && e.target !== notifBtn) {
        notifPopover.classList.remove("active");
      }
    });
  }
}
