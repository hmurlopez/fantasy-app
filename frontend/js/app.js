/**
 * Fantasy Soccer — Main Application
 * Single-page app: views are div.view elements toggled with .active class.
 */

// ── Toast ─────────────────────────────────────────────────────────────────
function toast(msg, type = "") {
  const el = document.getElementById("toast");
  el.textContent = msg;
  el.className = `show ${type}`;
  setTimeout(() => (el.className = ""), 3000);
}

// ── View router ───────────────────────────────────────────────────────────
function showView(id) {
  document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
  const el = document.getElementById(id);
  if (el) el.classList.add("active");
}

// ── Auth state ────────────────────────────────────────────────────────────
function isLoggedIn() {
  return !!localStorage.getItem("fantasy_token");
}

function updateNavbar() {
  const badge = document.getElementById("user-badge");
  const logoutBtn = document.getElementById("btn-logout");
  const loginBtn = document.getElementById("btn-nav-login");
  if (isLoggedIn()) {
    badge.textContent = ""; // could decode JWT for username
    logoutBtn.style.display = "";
    loginBtn.style.display = "none";
  } else {
    badge.textContent = "";
    logoutBtn.style.display = "none";
    loginBtn.style.display = "";
  }
}

// ── Auth forms ────────────────────────────────────────────────────────────
async function handleLogin(e) {
  e.preventDefault();
  const username = document.getElementById("login-username").value;
  const password = document.getElementById("login-password").value;
  try {
    await Auth.login(username, password);
    toast("Welcome back!", "success");
    updateNavbar();
    loadDashboard();
    showView("view-dashboard");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const username = document.getElementById("reg-username").value;
  const email = document.getElementById("reg-email").value;
  const password = document.getElementById("reg-password").value;
  try {
    await Auth.register(username, email, password);
    await Auth.login(username, password);
    toast("Account created! Let's build your squad.", "success");
    updateNavbar();
    showView("view-create-team");
  } catch (err) {
    toast(err.message, "error");
  }
}

// ── Dashboard ─────────────────────────────────────────────────────────────
async function loadDashboard() {
  const wrap = document.getElementById("dashboard-content");
  wrap.innerHTML = "<p>Loading…</p>";
  try {
    const [team, gw] = await Promise.allSettled([Teams.myTeam(), Gameweeks.current()]);
    const teamData = team.status === "fulfilled" ? team.value : null;
    const gwData = gw.status === "fulfilled" ? gw.value : null;

    let html = "";

    if (teamData) {
      html += `
        <div class="card">
          <h2>My Team — ${esc(teamData.name)}</h2>
          <div class="stat-row">
            <div class="stat-pill"><strong>${teamData.total_points}</strong> Total pts</div>
            <div class="stat-pill"><strong>£${teamData.budget_remaining.toFixed(1)}m</strong> Budget</div>
            <div class="stat-pill"><strong>${teamData.free_transfers}</strong> Free transfer(s)</div>
          </div>
          <br>
          <button class="btn btn-green btn-sm" onclick="showView('view-squad')">Manage Squad</button>
          <button class="btn btn-outline btn-sm" onclick="navPlayers()">Transfer Market</button>
        </div>`;
    } else {
      html += `
        <div class="card">
          <h2>No team yet</h2>
          <p style="color:var(--gray-3);margin-bottom:.8rem">Create your squad to start playing.</p>
          <button class="btn btn-green" onclick="showView('view-create-team')">Create Team</button>
        </div>`;
    }

    if (gwData) {
      html += `
        <div class="card">
          <h2>Gameweek ${gwData.number}</h2>
          <div class="stat-row">
            <div class="stat-pill">Status: <strong>${gwData.status}</strong></div>
            <div class="stat-pill">Deadline: <strong>${new Date(gwData.deadline).toLocaleString()}</strong></div>
          </div>
        </div>`;
    }

    html += `
      <div class="card">
        <h2>Scoring Rules</h2>
        <div class="rules-grid">
          <div class="rule-pos" style="grid-column:1/-1">All players</div>
          <span class="rule-label">1–59 min played</span><span class="rule-val">+1 pt</span>
          <span class="rule-label">60+ min played</span><span class="rule-val">+2 pts</span>
          <span class="rule-label">Assist</span><span class="rule-val">+3 pts</span>
          <span class="rule-label">Yellow card</span><span class="rule-val">−1 pt</span>
          <span class="rule-label">Red card</span><span class="rule-val">−3 pts</span>
          <span class="rule-label">Own goal</span><span class="rule-val">−2 pts</span>
          <span class="rule-label">Penalty miss</span><span class="rule-val">−2 pts</span>
          <div class="rule-pos" style="grid-column:1/-1">Goalkeeper</div>
          <span class="rule-label">Goal scored</span><span class="rule-val">+10 pts</span>
          <span class="rule-label">Clean sheet</span><span class="rule-val">+6 pts</span>
          <span class="rule-label">Every 3 saves</span><span class="rule-val">+1 pt</span>
          <span class="rule-label">Penalty save</span><span class="rule-val">+5 pts</span>
          <span class="rule-label">Every 2 goals conceded</span><span class="rule-val">−1 pt</span>
          <div class="rule-pos" style="grid-column:1/-1">Defender</div>
          <span class="rule-label">Goal scored</span><span class="rule-val">+6 pts</span>
          <span class="rule-label">Clean sheet</span><span class="rule-val">+4 pts</span>
          <span class="rule-label">Every 2 goals conceded</span><span class="rule-val">−1 pt</span>
          <div class="rule-pos" style="grid-column:1/-1">Midfielder</div>
          <span class="rule-label">Goal scored</span><span class="rule-val">+5 pts</span>
          <span class="rule-label">Clean sheet</span><span class="rule-val">+1 pt</span>
          <div class="rule-pos" style="grid-column:1/-1">Forward</div>
          <span class="rule-label">Goal scored</span><span class="rule-val">+4 pts</span>
          <div class="rule-pos" style="grid-column:1/-1">Transfers</div>
          <span class="rule-label">Each extra transfer</span><span class="rule-val">−4 pts</span>
          <span class="rule-label">Captain</span><span class="rule-val">×2 points</span>
        </div>
      </div>`;

    wrap.innerHTML = html;
  } catch (err) {
    wrap.innerHTML = `<p style="color:var(--danger)">${err.message}</p>`;
  }
}

// ── Squad / Pitch view ────────────────────────────────────────────────────
let squadData = [];

async function loadSquad() {
  const wrap = document.getElementById("pitch-wrap");
  wrap.innerHTML = "<p>Loading squad…</p>";
  try {
    const res = await Teams.mySquad();
    squadData = res.squad;
    renderPitch(res.squad);
  } catch (err) {
    wrap.innerHTML = `<p style="color:var(--danger)">${err.message}</p>`;
  }
}

function renderPitch(squad) {
  const starters = squad.filter((p) => p.is_starter);
  const bench = squad.filter((p) => !p.is_starter);

  const byPos = (pos) => starters.filter((p) => p.position === pos);

  const slotHTML = (p) => `
    <div class="player-slot" data-id="${p.player_id}">
      <div class="slot-name">${esc(p.name.split(" ").pop())}</div>
      <div class="slot-club">${esc(p.club ?? "")}</div>
      <div class="slot-pts">${p.total_points} pts</div>
      <span class="pos-badge pos-${p.position}">${p.position}</span>
    </div>`;

  const rowHTML = (players) =>
    `<div class="pitch-row">${players.map(slotHTML).join("")}</div>`;

  document.getElementById("pitch-wrap").innerHTML = `
    <div class="pitch-wrapper">
      ${rowHTML(byPos("GK"))}
      ${rowHTML(byPos("DEF"))}
      ${rowHTML(byPos("MID"))}
      ${rowHTML(byPos("FWD"))}
      <hr style="border-color:var(--green-d);margin:.5rem 0">
      <p style="text-align:center;font-size:.75rem;color:var(--green-d)">Bench</p>
      ${rowHTML(bench)}
    </div>
    <p style="font-size:.8rem;color:var(--gray-3);margin-top:.5rem;text-align:center">
      Click a player to view stats. Use Transfer Market to swap players.
    </p>`;
}

// ── Player market ─────────────────────────────────────────────────────────
let allPlayers = [];

async function navPlayers() {
  showView("view-players");
  await loadPlayers();
}

async function loadPlayers() {
  const tbody = document.getElementById("players-tbody");
  tbody.innerHTML = "<tr><td colspan='6'>Loading…</td></tr>";
  const pos = document.getElementById("filter-pos").value;
  const search = document.getElementById("filter-search").value;
  const maxPrice = document.getElementById("filter-price").value;
  try {
    const params = {};
    if (pos) params.position = pos;
    if (search) params.search = search;
    if (maxPrice) params.max_price = maxPrice;
    allPlayers = await Players.list(params);
    tbody.innerHTML = allPlayers
      .map(
        (p) => `
        <tr>
          <td>${esc(p.name)}</td>
          <td><span class="pos-badge pos-${p.position}">${p.position}</span></td>
          <td>${esc(p.club ?? "—")}</td>
          <td>£${p.price.toFixed(1)}m</td>
          <td>${p.total_points}</td>
          <td>
            <button class="btn btn-green btn-sm" onclick="openTransferModal(${p.id})">
              + Add
            </button>
          </td>
        </tr>`
      )
      .join("") || "<tr><td colspan='6'>No players found</td></tr>";
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan='6' style='color:var(--danger)'>${err.message}</td></tr>`;
  }
}

function openTransferModal(incomingId) {
  const player = allPlayers.find((p) => p.id === incomingId);
  if (!player) return;
  document.getElementById("transfer-in-name").textContent = player.name;
  document.getElementById("transfer-in-price").textContent = `£${player.price.toFixed(1)}m`;
  const sel = document.getElementById("transfer-out-select");
  sel.innerHTML = squadData
    .map((s) => `<option value="${s.player_id}">${s.name} (${s.position}) — £${s.price.toFixed(1)}m</option>`)
    .join("");
  document.getElementById("confirm-transfer-btn").onclick = async () => {
    const outId = parseInt(sel.value);
    try {
      const res = await Teams.transfer(outId, incomingId);
      toast(res.message, "success");
      closeModal("transfer-modal");
      loadSquad();
    } catch (err) {
      toast(err.message, "error");
    }
  };
  openModal("transfer-modal");
}

// ── Leagues ───────────────────────────────────────────────────────────────
async function loadLeagues() {
  const wrap = document.getElementById("leagues-wrap");
  wrap.innerHTML = "<p>Loading…</p>";
  try {
    const leagues = await Leagues.myLeagues();
    if (!leagues.length) {
      wrap.innerHTML = `<p style="color:var(--gray-3)">You're not in any leagues yet. Create or join one below.</p>`;
      return;
    }
    wrap.innerHTML = leagues
      .map(
        (l) => `
      <div class="card" style="margin-bottom:.75rem">
        <h2>${esc(l.name)}</h2>
        <div class="stat-row">
          <div class="stat-pill">Type: <strong>${l.league_type}</strong></div>
          <div class="stat-pill">Season: <strong>${l.season}</strong></div>
        </div>
        <div class="invite-code" onclick="copyCode('${l.invite_code}')">${l.invite_code}</div>
        <button class="btn btn-outline btn-sm" onclick="viewStandings(${l.id}, '${esc(l.name)}')">
          View Standings
        </button>
      </div>`
      )
      .join("");
  } catch (err) {
    wrap.innerHTML = `<p style="color:var(--danger)">${err.message}</p>`;
  }
}

async function handleCreateLeague(e) {
  e.preventDefault();
  const name = document.getElementById("league-name").value;
  const type = document.getElementById("league-type").value;
  try {
    const league = await Leagues.create(name, type);
    toast(`League created! Invite code: ${league.invite_code}`, "success");
    loadLeagues();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleJoinLeague(e) {
  e.preventDefault();
  const code = document.getElementById("join-code").value.toUpperCase();
  try {
    const league = await Leagues.join(code);
    toast(`Joined "${league.name}"!`, "success");
    loadLeagues();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function viewStandings(id, name) {
  const modal = document.getElementById("standings-modal");
  document.getElementById("standings-title").textContent = name;
  document.getElementById("standings-body").innerHTML = "Loading…";
  openModal("standings-modal");
  try {
    const rows = await Leagues.standings(id);
    document.getElementById("standings-body").innerHTML = `
      <table class="standings-table">
        <thead><tr><th>#</th><th>Manager</th><th>Team</th><th>Points</th></tr></thead>
        <tbody>
          ${rows
            .map(
              (r) =>
                `<tr class="rank-${r.rank}">
                  <td>${r.rank}</td>
                  <td>${esc(r.username)}</td>
                  <td>${esc(r.team_name)}</td>
                  <td><strong>${r.total_points}</strong></td>
                </tr>`
            )
            .join("")}
        </tbody>
      </table>`;
  } catch (err) {
    document.getElementById("standings-body").innerHTML = `<p style="color:var(--danger)">${err.message}</p>`;
  }
}

// ── Create team ───────────────────────────────────────────────────────────
async function handleCreateTeam(e) {
  e.preventDefault();
  const name = document.getElementById("team-name-input").value;
  try {
    await Teams.create(name);
    toast("Team created! Now build your squad.", "success");
    showView("view-dashboard");
    loadDashboard();
  } catch (err) {
    toast(err.message, "error");
  }
}

// ── Modal helpers ─────────────────────────────────────────────────────────
function openModal(id) {
  document.getElementById(id).style.display = "flex";
}
function closeModal(id) {
  document.getElementById(id).style.display = "none";
}

// ── Utility ───────────────────────────────────────────────────────────────
function esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function copyCode(code) {
  navigator.clipboard.writeText(code).then(() => toast("Invite code copied!", "success"));
}

// ── Boot ──────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  updateNavbar();

  // Nav buttons
  document.getElementById("btn-nav-login").addEventListener("click", () => showView("view-auth"));
  document.getElementById("btn-logout").addEventListener("click", () => {
    Auth.logout();
    updateNavbar();
    showView("view-auth");
  });
  document.getElementById("btn-nav-dashboard").addEventListener("click", () => {
    if (!isLoggedIn()) { showView("view-auth"); return; }
    loadDashboard();
    showView("view-dashboard");
  });
  document.getElementById("btn-nav-squad").addEventListener("click", () => {
    if (!isLoggedIn()) { showView("view-auth"); return; }
    loadSquad();
    showView("view-squad");
  });
  document.getElementById("btn-nav-players").addEventListener("click", () => {
    if (!isLoggedIn()) { showView("view-auth"); return; }
    navPlayers();
  });
  document.getElementById("btn-nav-leagues").addEventListener("click", () => {
    if (!isLoggedIn()) { showView("view-auth"); return; }
    loadLeagues();
    showView("view-leagues");
  });

  // Auth tabs
  document.querySelectorAll(".auth-tab").forEach((tab) =>
    tab.addEventListener("click", () => {
      document.querySelectorAll(".auth-tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");
      document.querySelectorAll(".auth-panel").forEach((p) => (p.style.display = "none"));
      document.getElementById(tab.dataset.target).style.display = "block";
    })
  );

  // Forms
  document.getElementById("login-form").addEventListener("submit", handleLogin);
  document.getElementById("register-form").addEventListener("submit", handleRegister);
  document.getElementById("create-team-form").addEventListener("submit", handleCreateTeam);
  document.getElementById("create-league-form").addEventListener("submit", handleCreateLeague);
  document.getElementById("join-league-form").addEventListener("submit", handleJoinLeague);

  // Player filters
  ["filter-pos", "filter-search", "filter-price"].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", loadPlayers);
  });

  // Modal close buttons
  document.querySelectorAll("[data-close-modal]").forEach((btn) =>
    btn.addEventListener("click", () => closeModal(btn.dataset.closeModal))
  );

  // Initial view
  if (isLoggedIn()) {
    loadDashboard();
    showView("view-dashboard");
  } else {
    showView("view-auth");
  }
});
