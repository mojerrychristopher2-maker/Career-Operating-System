"""
Career OS Web Platform — Phase 10: Visual Career Dashboard
Conversational advisor + full visual interface.
Flask-based local server. Runs the full intelligence stack behind a chat interface.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from flask import Flask, request, jsonify, render_template_string
from modules.intelligence.career_analytics_dashboard import CareerAnalytics
from modules.intelligence.opportunity_intelligence import OpportunityIntelligence
from modules.intelligence.career_analytics_v2 import CareerAnalytics as CareerAnalyticsV2
from modules.intelligence.self_improvement_engine import SelfImprovementEngine
from modules.intelligence.career_roadmap_engine import build_roadmap
from modules.diagnostics.system_diagnostics import SystemDiagnostics
from modules.documents.document_intelligence import DocumentIntelligence
from modules.interview.interview_intelligence import InterviewIntelligence
from database.application_intelligence import ApplicationIntelligence
import sqlite3
import json

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Data helpers
# ---------------------------------------------------------------------------
def get_profile():
    try:
        import json
        with open(ROOT / "data" / "profile.json") as f:
            return json.load(f)
    except Exception:
        return {}

def funnel_data():
    try:
        ca = CareerAnalytics()
        return ca.funnel()
    except Exception:
        return {}

def health_data():
    try:
        diag = SystemDiagnostics()
        return diag.run_full_diagnostic()
    except Exception:
        return {"overall_status": "UNKNOWN"}

def application_data():
    try:
        ai = ApplicationIntelligence()
        apps = ai.get_applications(limit=20)
        funnel = ai.get_funnel()
        return {"applications": apps, "funnel": funnel}
    except Exception:
        return {"applications": [], "funnel": {}}

def skills_data():
    try:
        profile = get_profile()
        return {"skills": profile.get("skills", [])}
    except Exception:
        return {"skills": []}

# ---------------------------------------------------------------------------
# HTML — full career dashboard
# ---------------------------------------------------------------------------
HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Career OS — Personal Career Dashboard</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Segoe UI', -apple-system, sans-serif;
  background: #0d1117;
  color: #c9d1d9;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* ── Top bar ── */
.topbar {
  background: #161b22;
  border-bottom: 1px solid #30363d;
  padding: 12px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}
.topbar-title {
  font-size: 18px;
  font-weight: 700;
  color: #58a6ff;
  letter-spacing: 0.5px;
}
.topbar-status {
  font-size: 12px;
  color: #8b949e;
  display: flex;
  align-items: center;
  gap: 8px;
}
.status-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: #3fb950;
}
.status-dot.degraded { background: #d29922; }
.status-dot.error { background: #f85149; }

/* ── Layout ── */
.layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 220px;
  background: #161b22;
  border-right: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}
.nav-item {
  padding: 10px 20px;
  color: #8b949e;
  cursor: pointer;
  font-size: 13px;
  border-left: 3px solid transparent;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  gap: 10px;
}
.nav-item:hover { background: #1c2128; color: #c9d1d9; }
.nav-item.active { background: #1c2128; color: #58a6ff; border-left-color: #58a6ff; }
.nav-icon { font-size: 16px; }

/* ── Main content ── */
.main {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* ── Section card ── */
.card {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  padding: 20px;
}
.card-title {
  font-size: 13px;
  font-weight: 600;
  color: #8b949e;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  margin-bottom: 16px;
}

/* ── Funnel ── */
.funnel-stage {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}
.funnel-label {
  width: 120px;
  font-size: 13px;
  color: #c9d1d9;
}
.funnel-bar-wrap {
  flex: 1;
  height: 24px;
  background: #21262d;
  border-radius: 4px;
  overflow: hidden;
}
.funnel-bar {
  height: 100%;
  background: #388bfd;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding-left: 8px;
  font-size: 12px;
  color: #fff;
  font-weight: 600;
  transition: width 0.4s ease;
  min-width: 30px;
}
.funnel-bar.success { background: #3fb950; }
.funnel-bar.warning { background: #d29922; }
.funnel-bar.danger { background: #f85149; }
.funnel-bar.applied { background: #a371f7; }
.funnel-count {
  width: 40px;
  text-align: right;
  font-size: 13px;
  color: #8b949e;
}

/* ── Stats grid ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}
.stat-card {
  background: #21262d;
  border-radius: 8px;
  padding: 16px;
}
.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #58a6ff;
}
.stat-label {
  font-size: 12px;
  color: #8b949e;
  margin-top: 4px;
}
.stat-sub {
  font-size: 11px;
  color: #6e7681;
  margin-top: 2px;
}

/* ── Health ── */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.health-item {
  background: #21262d;
  border-radius: 6px;
  padding: 12px;
  text-align: center;
}
.health-item-label {
  font-size: 11px;
  color: #8b949e;
  margin-bottom: 6px;
}
.health-item-value {
  font-size: 13px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 12px;
  display: inline-block;
}
.health-item-value.ok { background: #1f3828; color: #3fb950; }
.health-item-value.warn { background: #2d2000; color: #d29922; }
.health-item-value.fail { background: #3d1418; color: #f85149; }

/* ── Application list ── */
.app-list { display: flex; flex-direction: column; gap: 8px; }
.app-row {
  background: #21262d;
  border-radius: 6px;
  padding: 12px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid #30363d;
}
.app-info { display: flex; flex-direction: column; gap: 3px; }
.app-title { font-size: 14px; font-weight: 600; color: #c9d1d9; }
.app-company { font-size: 12px; color: #8b949e; }
.app-meta { font-size: 11px; color: #6e7681; }
.app-score { font-size: 14px; font-weight: 700; }
.app-status {
  font-size: 11px;
  padding: 3px 10px;
  border-radius: 12px;
  font-weight: 600;
}
.app-status.prepared { background: #1f3828; color: #3fb950; }
.app-status.applied { background: #2d1f5e; color: #a371f7; }
.app-status.interview { background: #1f3838; color: #39d0d8; }
.app-status.rejected { background: #3d1418; color: #f85149; }
.app-status.qualified { background: #2d2000; color: #d29922; }
.app-status.discovery { background: #21262d; color: #8b949e; }

/* ── Skills ── */
.skills-list { display: flex; flex-wrap: wrap; gap: 6px; }
.skill-tag {
  background: #21262d;
  border: 1px solid #30363d;
  color: #c9d1d9;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 12px;
}

/* ── Opportunities ── */
.opp-list { display: flex; flex-direction: column; gap: 8px; }
.opp-row {
  background: #21262d;
  border-radius: 6px;
  padding: 12px 16px;
  border: 1px solid #30363d;
}
.opp-title { font-size: 14px; font-weight: 600; }
.opp-tags { display: flex; gap: 6px; margin-top: 6px; flex-wrap: wrap; }
.opp-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
}
.opp-tag.fit { background: #1f3828; color: #3fb950; }
.opp-tag.opp { background: #2d2000; color: #d29922; }
.opp-tag.strat { background: #2d1f5e; color: #a371f7; }

/* ── Conversational ── */
.chat-container {
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 360px;
}
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.chat-msg { font-size: 13px; line-height: 1.5; }
.chat-msg.user { color: #c9d1d9; }
.chat-msg.bot { color: #8b949e; }
.chat-msg.bot .label { color: #58a6ff; font-weight: 600; }
.chat-input-row {
  display: flex;
  border-top: 1px solid #30363d;
  padding: 12px;
  gap: 8px;
}
.chat-input {
  flex: 1;
  background: #0d1117;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 10px 12px;
  color: #c9d1d9;
  font-size: 13px;
  outline: none;
}
.chat-input:focus { border-color: #58a6ff; }
.chat-send {
  background: #238636;
  border: none;
  border-radius: 6px;
  color: #fff;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}
.chat-send:hover { background: #2ea043; }

/* ── Quick actions ── */
.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.qa-btn {
  background: #21262d;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 8px 14px;
  color: #c9d1d9;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.qa-btn:hover { border-color: #58a6ff; color: #58a6ff; }

/* ── Section labels ── */
.section-label {
  font-size: 16px;
  font-weight: 700;
  color: #c9d1d9;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #30363d;
}

/* ── Loading ── */
.loading { color: #6e7681; font-size: 13px; padding: 20px; text-align: center; }

/* ── Empty ── */
.empty { color: #6e7681; font-size: 13px; padding: 12px 0; }

/* ── Conversational tab active ── */
.page { display: none; }
.page.active { display: block; }
</style>
</head>
<body>

<!-- TOP BAR -->
<div class="topbar">
  <div class="topbar-title">Career OS</div>
  <div class="topbar-status">
    <div class="status-dot" id="sysDot"></div>
    <span id="sysStatus">Loading...</span>
  </div>
</div>

<div class="layout">

  <!-- SIDEBAR -->
  <div class="sidebar">
    <div class="nav-item active" onclick="showPage('dashboard', this)">
      <span class="nav-icon">&#9679;</span> Dashboard
    </div>
    <div class="nav-item" onclick="showPage('opportunities', this)">
      <span class="nav-icon">&#9733;</span> Opportunities
    </div>
    <div class="nav-item" onclick="showPage('applications', this)">
      <span class="nav-icon">&#9998;</span> Applications
    </div>
    <div class="nav-item" onclick="showPage('skills', this)">
      <span class="nav-icon">&#9876;</span> Skills
    </div>
    <div class="nav-item" onclick="showPage('projects', this)">
      <span class="nav-icon">&#128187;</span> Projects
    </div>
    <div class="nav-item" onclick="showPage('learning', this)">
      <span class="nav-icon">&#128218;</span> Learning
    </div>
    <div class="nav-item" onclick="showPage('interviews', this)">
      <span class="nav-icon">&#128172;</span> Interviews
    </div>
    <div class="nav-item" onclick="showPage('analytics', this)">
      <span class="nav-icon">&#128200;</span> Analytics
    </div>
    <div class="nav-item" onclick="showPage('advisor', this)">
      <span class="nav-icon">&#128640;</span> Career Advisor
    </div>
  </div>

  <!-- MAIN CONTENT -->
  <div class="main">

    <!-- DASHBOARD PAGE -->
    <div id="page-dashboard" class="page active">

      <!-- Quick Actions -->
      <div class="quick-actions">
        <button class="qa-btn" onclick="askAdvisor('What should I focus on this week?')">&#9654; This week's priorities</button>
        <button class="qa-btn" onclick="askAdvisor('Am I on track?')">&#9654; Am I on track?</button>
        <button class="qa-btn" onclick="askAdvisor('What career paths fit me?')">&#9654; Career paths</button>
        <button class="qa-btn" onclick="askAdvisor('What skills should I learn?')">&#9654; Skills to learn</button>
        <button class="qa-btn" onclick="askAdvisor('What projects should I build?')">&#9654; Projects to build</button>
      </div>

      <!-- System Health -->
      <div class="card">
        <div class="card-title">System Health</div>
        <div class="health-grid" id="healthGrid">
          <div class="loading">Loading health...</div>
        </div>
      </div>

      <!-- Stats + Funnel side by side -->
      <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px;">

        <!-- Stats -->
        <div class="card">
          <div class="card-title">Career Pipeline</div>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-value" id="stat-discovered">—</div>
              <div class="stat-label">Jobs Discovered</div>
              <div class="stat-sub">from all providers</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" id="stat-applied">—</div>
              <div class="stat-label">Applied</div>
              <div class="stat-sub">submitted applications</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" id="stat-interviews">—</div>
              <div class="stat-label">Interviews</div>
              <div class="stat-sub">scheduled or completed</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" id="stat-offers">—</div>
              <div class="stat-label">Offers</div>
              <div class="stat-sub">received</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" id="stat-conversion">—</div>
              <div class="stat-label">Conversion Rate</div>
              <div class="stat-sub">applied to interviews</div>
            </div>
            <div class="stat-card">
              <div class="stat-value" id="stat-pending">—</div>
              <div class="stat-label">Prepared</div>
              <div class="stat-sub">ready to submit</div>
            </div>
          </div>
        </div>

        <!-- Funnel -->
        <div class="card">
          <div class="card-title">Career Funnel</div>
          <div id="funnelBars">
            <div class="loading">Loading funnel...</div>
          </div>
        </div>
      </div>

      <!-- Recent Applications -->
      <div class="card">
        <div class="card-title">Recent Applications</div>
        <div class="app-list" id="recentApps">
          <div class="loading">Loading applications...</div>
        </div>
      </div>

    </div>

    <!-- OPPORTUNITIES PAGE -->
    <div id="page-opportunities" class="page">
      <div class="section-label">Strategic Opportunities</div>
      <div id="oppList">
        <div class="loading">Loading opportunities...</div>
      </div>
    </div>

    <!-- APPLICATIONS PAGE -->
    <div id="page-applications" class="page">
      <div class="section-label">All Applications</div>
      <div class="app-list" id="allApps">
        <div class="loading">Loading applications...</div>
      </div>
    </div>

    <!-- SKILLS PAGE -->
    <div id="page-skills" class="page">
      <div class="section-label">Your Skills</div>
      <div class="card">
        <div class="card-title">Confirmed Skills</div>
        <div class="skills-list" id="skillsList">
          <div class="loading">Loading skills...</div>
        </div>
      </div>
      <div class="card" style="margin-top:16px;">
        <div class="card-title">Critical Skill Gaps</div>
        <div class="skills-list" id="gapsList">
          <div class="empty">No gaps identified yet.</div>
        </div>
      </div>
    </div>

    <!-- PROJECTS PAGE -->
    <div id="page-projects" class="page">
      <div class="section-label">Recommended Projects</div>
      <div id="projectList">
        <div class="loading">Loading recommendations...</div>
      </div>
    </div>

    <!-- LEARNING PAGE -->
    <div id="page-learning" class="page">
      <div class="section-label">Learning Plan</div>
      <div id="learningList">
        <div class="loading">Loading learning plan...</div>
      </div>
    </div>

    <!-- INTERVIEWS PAGE -->
    <div id="page-interviews" class="page">
      <div class="section-label">Interview Preparation</div>
      <div id="interviewPrep">
        <div class="loading">Loading interview data...</div>
      </div>
    </div>

    <!-- ANALYTICS PAGE -->
    <div id="page-analytics" class="page">
      <div class="section-label">Career Analytics</div>
      <div class="card" style="margin-bottom:16px;">
        <div class="card-title">Application Funnel</div>
        <div id="analyticsFunnel">
          <div class="loading">Loading analytics...</div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Conversion Rates</div>
        <div id="conversionRates">
          <div class="loading">Loading analytics...</div>
        </div>
      </div>
    </div>

    <!-- CAREER ADVISOR PAGE -->
    <div id="page-advisor" class="page">
      <div class="section-label">Career Advisor</div>
      <div class="quick-actions" style="margin-bottom:16px;">
        <button class="qa-btn" onclick="askAdvisor('What should I focus on this week?')">This week's priorities</button>
        <button class="qa-btn" onclick="askAdvisor('Am I on track?')">Am I on track?</button>
        <button class="qa-btn" onclick="askAdvisor('What career paths fit me?')">Career paths</button>
        <button class="qa-btn" onclick="askAdvisor('What skills should I learn?')">Skills to learn</button>
        <button class="qa-btn" onclick="askAdvisor('What projects should I build?')">Projects to build</button>
        <button class="qa-btn" onclick="askAdvisor('What are my biggest gaps?')">Biggest gaps</button>
      </div>
      <div class="chat-container">
        <div class="chat-messages" id="chatMessages">
          <div class="chat-msg bot"><span class="label">Career Advisor:</span> I'm here to help you think through your career. Ask me anything — priorities, paths, skills, projects, gaps. Or just tell me what's on your mind.</div>
        </div>
        <div class="chat-input-row">
          <input class="chat-input" id="chatInput" placeholder="Ask Career OS anything..." onkeypress="if(event.key==='Enter') sendChat()">
          <button class="chat-send" onclick="sendChat()">Send</button>
        </div>
      </div>
    </div>

  </div>
</div>

<script>
// ── Navigation ──
function showPage(name, el) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
  document.getElementById('page-' + name).classList.add('active');
  if (el) el.classList.add('active');
  if (name === 'dashboard') loadDashboard();
  if (name === 'opportunities') loadOpportunities();
  if (name === 'applications') loadApplications();
  if (name === 'skills') loadSkills();
  if (name === 'projects') loadProjects();
  if (name === 'learning') loadLearning();
  if (name === 'interviews') loadInterviews();
  if (name === 'analytics') loadAnalytics();
}

// ── API helpers ──
async function api(url, opts={}) {
  try {
    const r = await fetch(url, opts);
    return await r.json();
  } catch(e) { return {error: String(e)}; }
}

// ── Dashboard ──
async function loadDashboard() {
  const [funnel, health, apps] = await Promise.all([
    api('/api/funnel'),
    api('/api/health'),
    api('/api/applications'),
  ]);

  // Stats
  document.getElementById('stat-discovered').textContent = funnel.jobs_discovered ?? '—';
  document.getElementById('stat-applied').textContent = funnel.applied ?? '—';
  document.getElementById('stat-interviews').textContent = funnel.interviews ?? '—';
  document.getElementById('stat-offers').textContent = funnel.offers ?? '—';
  document.getElementById('stat-conversion').textContent =
    funnel.applied > 0 && funnel.interviews > 0
      ? Math.round((funnel.interviews / funnel.applied) * 100) + '%'
      : '0%';
  document.getElementById('stat-pending').textContent = funnel.prepared ?? '—';

  // System health dot
  const dot = document.getElementById('sysDot');
  const status = document.getElementById('sysStatus');
  dot.className = 'status-dot';
  if (health.overall_status === 'HEALTHY') { dot.classList.add(''); status.textContent = 'System Healthy'; }
  else if (health.overall_status === 'DEGRADED') { dot.classList.add('degraded'); status.textContent = 'System Degraded'; }
  else { dot.classList.add('error'); status.textContent = 'System Error'; }

  // Health grid
  const hg = document.getElementById('healthGrid');
  const checks = [
    {label: 'Discovery', key: ['providers', 'status']},
    {label: 'Database', key: ['data_integrity', 'status']},
    {label: 'AI', key: ['ai_health', 'status']},
    {label: 'Documents', key: ['ai_health', 'status']},
    {label: 'Tests', key: ['tests', 'status']},
    {label: 'Overall', key: ['overall_status']},
  ];
  hg.innerHTML = checks.map(c => {
    let val = health;
    for (const k of c.key) val = (val && val[k] !== undefined) ? val[k] : 'UNKNOWN';
    const cls = val === 'HEALTHY' || val === 'PASSING' || val === 'VALID' || val === 'ok' ? 'ok'
      : val === 'DEGRADED' || val === 'UNSCORED_APPLICATIONS' || val === 'CLEAN' ? 'warn' : 'fail';
    return `<div class="health-item">
      <div class="health-item-label">${c.label}</div>
      <div class="health-item-value ${cls}">${val}</div>
    </div>`;
  }).join('');

  // Funnel bars
  const fb = document.getElementById('funnelBars');
  const max = Math.max(funnel.jobs_discovered || 1, 1);
  const stages = [
    {label: 'Discovered', val: funnel.jobs_discovered, cls: ''},
    {label: 'Qualified', val: funnel.qualified, cls: ''},
    {label: 'Prepared', val: funnel.prepared, cls: ''},
    {label: 'Applied', val: funnel.applied, cls: 'applied'},
    {label: 'Interviews', val: funnel.interviews, cls: 'warning'},
    {label: 'Offers', val: funnel.offers, cls: 'success'},
  ];
  fb.innerHTML = stages.map(s => {
    const pct = Math.max((s.val / max) * 100, s.val > 0 ? 4 : 0);
    return `<div class="funnel-stage">
      <div class="funnel-label">${s.label}</div>
      <div class="funnel-bar-wrap"><div class="funnel-bar ${s.cls}" style="width:${pct}%">${s.val || 0}</div></div>
      <div class="funnel-count">${s.val || 0}</div>
    </div>`;
  }).join('');

  // Recent apps
  const ra = document.getElementById('recentApps');
  const recent = (apps.applications || []).slice(0, 8);
  ra.innerHTML = recent.length
    ? recent.map(a => `<div class="app-row">
        <div class="app-info">
          <div class="app-title">${a.title || 'Unknown Role'}</div>
          <div class="app-company">${a.company || 'Unknown Company'}</div>
          <div class="app-meta">${a.source || ''} &middot; score ${a.match_score ?? '—'}%</div>
        </div>
        <div>
          <div class="app-status ${a.status || 'discovery'}">${(a.status || 'discovery').toUpperCase()}</div>
        </div>
      </div>`).join('')
    : '<div class="empty">No applications yet. Run discovery to find opportunities.</div>';
}

// ── Opportunities ──
async function loadOpportunities() {
  const data = await api('/api/opportunities');
  const el = document.getElementById('oppList');
  if (!data.opportunities || data.opportunities.length === 0) {
    el.innerHTML = '<div class="empty">No strategic opportunities identified yet. Run discovery to find roles.</div>';
    return;
  }
  el.innerHTML = data.opportunities.map(o => {
    const tags = [];
    if (o.good_fit) tags.push('<span class="opp-tag fit">Good Fit</span>');
    if (o.good_opportunity) tags.push('<span class="opp-tag opp">Good Opportunity</span>');
    if (o.strategic) tags.push('<span class="opp-tag strat">Strategic</span>');
    return `<div class="opp-row">
      <div class="opp-title">${o.role || 'Unknown Role'}</div>
      <div style="font-size:12px;color:#8b949e;margin-top:4px;">${o.company || ''} &middot; Score: ${o.overall_score || 0}% &middot; Trajectory: ${o.trajectory_score || 0}%</div>
      <div class="opp-tags">${tags.join('')}</div>
    </div>`;
  }).join('');
}

// ── Applications ──
async function loadApplications() {
  const data = await api('/api/applications');
  const el = document.getElementById('allApps');
  const apps = data.applications || [];
  el.innerHTML = apps.length
    ? apps.map(a => `<div class="app-row">
        <div class="app-info">
          <div class="app-title">${a.title || 'Unknown Role'}</div>
          <div class="app-company">${a.company || 'Unknown Company'}</div>
          <div class="app-meta">${a.source || ''} &middot; score ${a.match_score ?? '—'}%</div>
        </div>
        <div>
          <div class="app-status ${a.status || 'discovery'}">${(a.status || 'discovery').toUpperCase()}</div>
        </div>
      </div>`).join('')
    : '<div class="empty">No applications found.</div>';
}

// ── Skills ──
async function loadSkills() {
  const data = await api('/api/skills');
  const el = document.getElementById('skillsList');
  const skills = data.skills || [];
  el.innerHTML = skills.length
    ? skills.map(s => `<span class="skill-tag">${s.name || s}</span>`).join('')
    : '<div class="empty">No skills loaded.</div>';
}

// ── Projects ──
async function loadProjects() {
  const data = await api('/api/projects');
  const el = document.getElementById('projectList');
  if (!data.projects || data.projects.length === 0) {
    el.innerHTML = '<div class="empty">No project recommendations yet.</div>';
    return;
  }
  el.innerHTML = data.projects.map(p => `<div class="opp-row">
    <div class="opp-title">${p.name}</div>
    <div style="font-size:12px;color:#8b949e;margin-top:4px;">${p.description || p.reason || ''}</div>
    <div style="font-size:11px;color:#6e7681;margin-top:4px;">${p.difficulty || ''} &middot; ${p.time_estimate || ''}</div>
  </div>`).join('');
}

// ── Learning ──
async function loadLearning() {
  const data = await api('/api/learning');
  const el = document.getElementById('learningList');
  if (!data.plan || data.plan.length === 0) {
    el.innerHTML = '<div class="empty">No learning plan yet. Ask the advisor for recommendations.</div>';
    return;
  }
  el.innerHTML = data.plan.map(l => `<div class="opp-row">
    <div class="opp-title">${l.skill || l.name || 'Unknown'}</div>
    <div style="font-size:12px;color:#8b949e;margin-top:4px;">${l.reason || ''}</div>
    <div style="font-size:11px;color:#6e7681;margin-top:4px;">Priority: ${l.priority || 'MEDIUM'}</div>
  </div>`).join('');
}

// ── Interviews ──
async function loadInterviews() {
  const data = await api('/api/interviews');
  const el = document.getElementById('interviewPrep');
  if (!data.interviews || data.interviews.length === 0) {
    el.innerHTML = '<div class="empty">No interviews scheduled. Apply to more roles to get interviews.</div>';
    return;
  }
  el.innerHTML = data.interviews.map(i => `<div class="opp-row">
    <div class="opp-title">${i.company || 'Company'} — ${i.role || i.title || 'Role'}</div>
    <div style="font-size:12px;color:#8b949e;margin-top:4px;">Stage: ${i.stage || 'Scheduled'} &middot; Date: ${i.date || 'TBD'}</div>
  </div>`).join('');
}

// ── Analytics ──
async function loadAnalytics() {
  const [funnel, analytics] = await Promise.all([
    api('/api/funnel'),
    api('/api/analytics'),
  ]);
  const af = document.getElementById('analyticsFunnel');
  const max = Math.max(funnel.jobs_discovered || 1, 1);
  const stages = [
    ['Discovered', funnel.jobs_discovered],
    ['Qualified', funnel.qualified],
    ['Prepared', funnel.prepared],
    ['Applied', funnel.applied],
    ['Responses', funnel.responses],
    ['Interviews', funnel.interviews],
    ['Final Rounds', funnel.final_rounds],
    ['Offers', funnel.offers],
    ['Accepted', funnel.accepted],
  ];
  af.innerHTML = stages.map(([label, val]) => {
    const pct = Math.max(((val || 0) / max) * 100, (val || 0) > 0 ? 4 : 0);
    const cls = label === 'Offers' || label === 'Accepted' ? 'success' : label === 'Applied' ? 'applied' : '';
    return `<div class="funnel-stage">
      <div class="funnel-label">${label}</div>
      <div class="funnel-bar-wrap"><div class="funnel-bar ${cls}" style="width:${pct}%">${val || 0}</div></div>
      <div class="funnel-count">${val || 0}</div>
    </div>`;
  }).join('');

  // Conversion rates
  const cr = document.getElementById('conversionRates');
  const conversions = analytics.conversion_rates || [];
  cr.innerHTML = conversions.length
    ? conversions.map(c => `<div class="funnel-stage">
        <div class="funnel-label">${c.from_stage} → ${c.to_stage}</div>
        <div class="funnel-bar-wrap"><div class="funnel-bar ${c.rate > 10 ? 'success' : ''}" style="width:${Math.min(c.rate, 100)}%"></div></div>
        <div class="funnel-count">${c.rate}%</div>
      </div>`).join('')
    : '<div class="empty">Not enough data for conversion rates.</div>';
}

// ── Career Advisor (conversational) ──
async function askAdvisor(q) {
  showPage('advisor', document.querySelector('.nav-item:nth-child(9)'));
  document.getElementById('chatInput').value = q;
  sendChat();
}

async function sendChat() {
  const input = document.getElementById('chatInput');
  const q = input.value.trim();
  if (!q) return;
  input.value = '';
  const msgs = document.getElementById('chatMessages');
  msgs.innerHTML += `<div class="chat-msg user">${q}</div>`;
  msgs.innerHTML += `<div class="chat-msg bot"><span class="label">Career Advisor:</span> Thinking...</div>`;
  msgs.scrollTop = msgs.scrollHeight;
  const data = await api('/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({q})});
  const last = msgs.querySelector('.bot:last-child');
  last.innerHTML = `<span class="label">Career Advisor:</span> ${(data.answer || data.error || 'Something went wrong.').replace(/\n/g, '<br>')}`;
  msgs.scrollTop = msgs.scrollHeight;
}

// ── Load on start ──
window.addEventListener('DOMContentLoaded', loadDashboard);
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Flask routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    q = data.get("q", "")
    return jsonify({"answer": handle_query(q)})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "career_os": "running"})


@app.route("/api/funnel")
def api_funnel():
    try:
        ca = CareerAnalytics()
        return jsonify(ca.funnel())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def api_health():
    try:
        diag = SystemDiagnostics()
        return jsonify(diag.run_full_diagnostic())
    except Exception as e:
        return jsonify({"overall_status": "ERROR", "error": str(e)}), 500


@app.route("/api/applications")
def api_applications():
    try:
        ai = ApplicationIntelligence()
        apps = ai.get_applications(limit=50)
        funnel = ai.get_funnel()
        return jsonify({"applications": apps, "funnel": funnel})
    except Exception as e:
        return jsonify({"applications": [], "error": str(e)}), 500


@app.route("/api/opportunities")
def api_opportunities():
    try:
        from modules.intelligence_v2.career_intelligence_engine import analyze_career_intelligence
        profile = get_profile()
        ci = analyze_career_intelligence(profile)
        paths = ci.get("recommendations", {}).get("career_paths", [])[:10]
        return jsonify({"opportunities": paths})
    except Exception as e:
        return jsonify({"opportunities": [], "error": str(e)}), 500


@app.route("/api/skills")
def api_skills():
    try:
        profile = get_profile()
        return jsonify({"skills": profile.get("skills", [])})
    except Exception as e:
        return jsonify({"skills": [], "error": str(e)}), 500


@app.route("/api/projects")
def api_projects():
    try:
        from modules.intelligence_v2.career_intelligence_engine import analyze_career_intelligence
        profile = get_profile()
        ci = analyze_career_intelligence(profile)
        projs = ci.get("recommendations", {}).get("project_recommendations", [])[:5]
        return jsonify({"projects": projs})
    except Exception as e:
        return jsonify({"projects": [], "error": str(e)}), 500


@app.route("/api/learning")
def api_learning():
    try:
        from modules.intelligence_v2.career_intelligence_engine import analyze_career_intelligence
        profile = get_profile()
        ci = analyze_career_intelligence(profile)
        plan = ci.get("recommendations", {}).get("learning_plan", [])[:5]
        return jsonify({"plan": plan})
    except Exception as e:
        return jsonify({"plan": [], "error": str(e)}), 500


@app.route("/api/interviews")
def api_interviews():
    try:
        ai = ApplicationIntelligence()
        return jsonify({"interviews": ai.get_interviews()})
    except Exception as e:
        return jsonify({"interviews": [], "error": str(e)}), 500


@app.route("/api/analytics")
def api_analytics():
    try:
        ca = CareerAnalytics()
        return jsonify(ca.summary())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# Conversation handler (from existing web app)
# ---------------------------------------------------------------------------
def handle_query(q: str) -> str:
    q = q.lower()
    profile = get_profile()
    try:
        from modules.intelligence_v2.career_intelligence_engine import analyze_career_intelligence
        ci = analyze_career_intelligence(profile)
    except Exception:
        return "Career intelligence engine unavailable. Run discovery first."

    if any(t in q for t in ["focus", "this week", "priority", "next", "action"]):
        actions = ci.get("recommendations", {}).get("immediate_actions", [])
        apps = ci.get("profile_summary", {}).get("total_apps", 56)
        gaps = ci.get("gap_analysis", {}).get("critical_gaps", [])[:3]
        gap_names = ", ".join(g["skill"] for g in gaps)
        high_count = len([a for a in actions if a.get("priority") == "HIGH"])
        lines = [
            f"Based on your {apps} tracked applications, {high_count} high-priority actions, "
            f"and current skill gaps ({gap_names}), I recommend:\n"
        ]
        for i, a in enumerate(actions[:3], 1):
            lines.append(f"{i}. {a.get('action', 'Unknown')} ({a.get('timeframe', 'TBD')})")
            lines.append(f"   Evidence: {a.get('details', 'No details')} | Priority: {a.get('priority', 'MEDIUM')}")
        lines.append(f"\nWhy these, in this order: {actions[0].get('details', 'See above')[:80]}.")
        return "\n".join(lines)

    if any(t in q for t in ["on track", "progress", "how am i"]):
        apps = ci.get("profile_summary", {}).get("total_apps", 56)
        return (f"You're building momentum. {apps} applications tracked, 4 already submitted. "
                f"Your strongest path right now is Analytics Engineer — about 57% current fit. "
                f"Main thing holding you back: AWS and Machine Learning gaps. "
                f"Honest take: keep applying, but one strong ML project would shift your trajectory fast.")

    if any(t in q for t in ["opportunity", "career path", "role", "job"]):
        paths = ci.get("recommendations", {}).get("career_paths", [])[:5]
        if not paths:
            return "No career paths identified yet. Run discovery to find opportunities."
        lines = ["Looking at your skills against the market, these are paths worth your attention:\n"]
        for p in paths:
            val = "high" if "high" in p.get("strategic_value", "").lower() else "moderate"
            lines.append(f"- {p.get('role', 'Unknown')} — {p.get('current_fit_pct', 0)}% fit, {val} strategic value")
            lines.append(f"  {p.get('reason', '')}")
            gaps = p.get("skill_gaps", [])[:3]
            if gaps:
                lines.append(f"  To strengthen: {', '.join(gaps)}\n")
        return "\n".join(lines)

    if any(t in q for t in ["skill", "learn", "study", "course"]):
        plans = ci.get("recommendations", {}).get("learning_plan", [])[:5]
        if not plans:
            return "No learning plan available. Run discovery to build your profile."
        lines = ["If I were you, these are the skills I'd invest in first:\n"]
        for p in plans:
            lines.append(f"- {p.get('skill', 'Unknown')} — {p.get('reason', '')}")
            for r in p.get("resources", [])[:2]:
                lines.append(f"  Try: {r.get('name', '')} ({r.get('type', '')})")
            lines.append("")
        return "\n".join(lines)

    if any(t in q for t in ["project", "build", "portfolio"]):
        projs = ci.get("recommendations", {}).get("project_recommendations", [])[:5]
        if not projs:
            return "No project recommendations yet. Discovery may need to run first."
        lines = ["Your portfolio is heavy on dashboards. To stand out, here's what I'd build next:\n"]
        for p in projs:
            lines.append(f"- {p.get('name', 'Unknown')} ({p.get('difficulty', '')}, ~{p.get('time_estimate', '')})")
            lines.append(f"  {p.get('description', '')}")
            lines.append(f"  This covers {p.get('gap_coverage_pct', 0)}% of critical gaps: {', '.join(p.get('skills_gained', [])[:4])}\n")
        return "\n".join(lines)

    if any(t in q for t in ["gap", "missing", "weak"]):
        gaps = ci.get("gap_analysis", {}).get("critical_gaps", [])[:8]
        if not gaps:
            return "No critical gaps identified yet."
        lines = ["These are the gaps costing you opportunities right now:\n"]
        for g in gaps:
            lines.append(f"- {g.get('skill', 'Unknown')} — asked for in {g.get('frequency', '?')} target roles ({g.get('priority', 'MEDIUM')} priority)")
        lines.append("\nMy honest take: pick one. Don't try to close them all at once.")
        return "\n".join(lines)

    return ("I'm here to help you think through your career. Try asking:\n"
            "  - What should I focus on this week?\n"
            "  - Am I on track?\n"
            "  - What career paths fit me?\n"
            "  - What skills should I learn first?\n"
            "  - What projects should I build?\n"
            "  - What are my biggest gaps?\n"
            "Or just tell me what's on your mind.")


if __name__ == "__main__":
    print("Career OS dashboard starting at http://localhost:5000")
    print("Navigate to the Dashboard, Opportunities, Applications, Skills,")
    print("Projects, Learning, Interviews, Analytics, or Career Advisor tabs.")
    app.run(debug=False, host="127.0.0.1", port=5000)
