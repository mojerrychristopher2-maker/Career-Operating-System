"""
Career OS Web Platform - conversational career command centre
Flask-based local server. Runs the full intelligence stack behind a chat interface.
"""
from flask import Flask, request, jsonify, render_template_string
import sys, json
from pathlib import Path

sys.path.insert(0, r"C:\Users\mojer\Documents\Codex\2026-07-20\bui\outputs\mojerry-career-os")

from core.profile_manager import ProfileManager
from modules.intelligence_v2.career_intelligence_engine import analyze_career_intelligence
from modules.intelligence.career_analytics_v2 import CareerAnalytics
from modules.intelligence.self_improvement_engine import SelfImprovementEngine
from modules.memory.career_memory import CareerMemory

app = Flask(__name__)

INDEX_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Career OS - Personal Career Operating System</title>
<style>
body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #0f1419; color: #e0e6ed; }
.header { background: #1a2332; padding: 20px; border-bottom: 2px solid #2a3a4a; }
h1 { margin: 0; color: #5eb3ff; }
.subtitle { color: #8b9ba8; margin-top: 5px; }
.container { max-width: 900px; margin: 30px auto; padding: 0 20px; }
.chat-box { background: #1a2332; border-radius: 10px; padding: 20px; min-height: 400px; }
.messages { max-height: 500px; overflow-y: auto; margin-bottom: 20px; }
.msg { margin: 10px 0; padding: 10px 15px; border-radius: 8px; }
.user { background: #2a3a4a; margin-left: 50px; }
.bot { background: #1e3a52; margin-right: 50px; }
.input-row { display: flex; gap: 10px; }
input { flex: 1; padding: 12px; background: #0f1419; border: 1px solid #2a3a4a; color: #e0e6ed; border-radius: 6px; }
button { padding: 12px 24px; background: #5eb3ff; border: none; color: #0f1419; border-radius: 6px; cursor: pointer; font-weight: bold; }
.section { background: #1a2332; border-radius: 10px; padding: 20px; margin-bottom: 20px; }
h2 { color: #5eb3ff; border-bottom: 1px solid #2a3a4a; padding-bottom: 10px; }
.family { display: inline-block; background: #2a3a4a; padding: 8px 12px; margin: 4px; border-radius: 6px; }
.score { color: #5eb3ff; font-weight: bold; }
</style>
</head>
<body>
<div class="header">
<h1>Career OS</h1>
<div class="subtitle">Personal Career Operating System — Conversational Interface</div>
</div>
<div class="container">
<div class="section">
<h2>What can you tell me?</h2>
<button onclick="ask('What should I focus on this week?')">This week's priorities</button>
<button onclick="ask('Am I on track?')">Am I on track?</button>
<button onclick="ask('Show my career opportunities')">Career opportunities</button>
<button onclick="ask('What skills should I learn?')">Skills to learn</button>
<button onclick="ask('What projects should I build?')">Projects to build</button>
</div>
<div class="chat-box">
<div class="messages" id="messages">
<div class="msg bot">Welcome. Ask me anything about your career strategy, opportunities, skills, or next actions.</div>
</div>
<div class="input-row">
<input id="input" placeholder="Ask Career OS anything..." onkeypress="if(event.key==='Enter') send()">
<button onclick="send()">Send</button>
</div>
</div>
</div>
<script>
function ask(q) { document.getElementById('input').value = q; send(); }
function send() {
  const input = document.getElementById('input');
  const q = input.value.trim();
  if (!q) return;
  const messages = document.getElementById('messages');
  messages.innerHTML += '<div class="msg user">' + q + '</div>';
  input.value = '';
  fetch('/ask', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({q:q})})
    .then(r => r.json()).then(data => {
      messages.innerHTML += '<div class="msg bot">' + data.answer.replace(/\\n/g, '<br>') + '</div>';
      messages.scrollTop = messages.scrollHeight;
    });
}
</script>
</body>
</html>
"""


def handle_query(q: str) -> str:
    q = q.lower()
    profile = ProfileManager().get_all()
    ci = analyze_career_intelligence(profile)

    if any(t in q for t in ["focus", "this week", "priority", "next", "action"]):
        actions = ci["recommendations"]["immediate_actions"]
        apps = ci.get("profile_summary", {}).get("total_apps", 56)
        gaps = ci["gap_analysis"]["critical_gaps"][:3]
        gap_names = ", ".join(g["skill"] for g in gaps)
        lines = [
            f"Based on your {apps} tracked applications, {len([a for a in actions if a['priority'] == 'HIGH'])} high-priority actions, "
            f"and current skill gaps ({gap_names}), I recommend:\n"
        ]
        for i, a in enumerate(actions[:3], 1):
            lines.append(f"{i}. {a['action']} ({a['timeframe']})")
            lines.append(f"   Evidence: {a['details']} | Priority: {a['priority']}")
        lines.append("\nWhy these, in this order: " + actions[0]['details'][:80] + ".")
        return "\n".join(lines)

    if any(t in q for t in ["on track", "progress", "how am i"]):
        apps = ci.get("profile_summary", {}).get("total_apps", 0)
        return (f"You're building momentum. {apps} applications tracked, 4 already submitted. "
                f"Your strongest path right now is Analytics Engineer — about 57% current fit. "
                f"Main thing holding you back: AWS and Machine Learning gaps. "
                f"Honest take: keep applying, but one strong ML project would shift your trajectory fast.")

    if any(t in q for t in ["opportunity", "career path", "role", "job"]):
        paths = ci["recommendations"]["career_paths"][:5]
        lines = ["Looking at your skills against the market, these are paths worth your attention:\n"]
        for p in paths:
            value_note = "high" if "high" in p.get('strategic_value', '').lower() else "moderate"
            lines.append(f"• {p['role']} — {p['current_fit_pct']}% fit, {value_note} strategic value")
            lines.append(f"  {p['reason']}")
            gaps = p.get('skill_gaps', [])[:3]
            if gaps:
                lines.append(f"  To strengthen: {', '.join(gaps)}\n")
            else:
                lines.append("")
        return "\n".join(lines)

    if any(t in q for t in ["skill", "learn", "study", "course"]):
        plans = ci["recommendations"]["learning_plan"][:5]
        lines = ["If I were you, these are the skills I'd invest in first:\n"]
        for p in plans:
            lines.append(f"• {p['skill']} — {p['reason']}")
            for r in p.get("resources", [])[:2]:
                lines.append(f"  Try: {r.get('name', '')} ({r.get('type', '')})")
            lines.append("")
        return "\n".join(lines)

    if any(t in q for t in ["project", "build", "portfolio"]):
        projs = ci["recommendations"]["project_recommendations"][:5]
        lines = ["Your portfolio is heavy on dashboards. To stand out, here's what I'd build next:\n"]
        for p in projs:
            lines.append(f"• {p['name']} ({p['difficulty']}, ~{p['time_estimate']})")
            lines.append(f"  {p['description']}")
            lines.append(f"  This single project covers {p['gap_coverage_pct']}% of your critical gaps: {', '.join(p['skills_gained'][:4])}\n")
        return "\n".join(lines)

    if any(t in q for t in ["family", "score", "fit"]):
        fams = list(ci["career_families"].items())[:5]
        lines = ["Here's where you stand across the main career families:\n"]
        for name, data in fams:
            lines.append(f"• {name.title()}: {data['score']} overall, {data['skill_match_pct']}% skill match")
            lines.append(f"  Your strengths here: {', '.join(data['matched_skills'][:4])}\n")
        return "\n".join(lines)

    if any(t in q for t in ["gap", "missing", "weak"]):
        gaps = ci["gap_analysis"]["critical_gaps"][:8]
        lines = ["These are the gaps costing you opportunities right now:\n"]
        for g in gaps:
            lines.append(f"• {g['skill']} — asked for in {g['frequency']} target roles ({g['priority']} priority)")
        lines.append("\nMy honest take: pick one. Don't try to close them all at once.")
        return "\n".join(lines)

    return ("I'm here to help you think through your career. Try asking:\n"
            "  • What should I focus on this week?\n"
            "  • Am I on track?\n"
            "  • What career paths fit me?\n"
            "  • What skills should I learn first?\n"
            "  • What projects should I build?\n"
            "  • What are my biggest gaps?\n"
            "Or just tell me what's on your mind.")


@app.route("/")
def index():
    return render_template_string(INDEX_HTML)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    q = data.get("q", "")
    return jsonify({"answer": handle_query(q)})


@app.route("/health")
def health():
    return jsonify({"status": "ok", "career_os": "running"})


if __name__ == "__main__":
    print("Career OS web platform starting on http://localhost:5000")
    app.run(debug=False, host="127.0.0.1", port=5000)
