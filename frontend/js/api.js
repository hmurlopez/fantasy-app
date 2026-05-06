/**
 * API client — thin wrapper around fetch.
 * Reads BASE_URL from window.APP_CONFIG (set in index.html).
 */

const API_BASE = window.APP_CONFIG?.apiBase ?? "http://localhost:8000";

function getToken() {
  return localStorage.getItem("fantasy_token");
}

async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  const data = res.headers.get("content-type")?.includes("json")
    ? await res.json()
    : await res.text();

  if (!res.ok) {
    const msg = data?.detail ?? data ?? `HTTP ${res.status}`;
    throw new Error(Array.isArray(msg) ? msg.map(e => e.msg).join(", ") : msg);
  }
  return data;
}

// ── Auth ──────────────────────────────────────────────────────────────────
const Auth = {
  register: (username, email, password) =>
    apiFetch("/auth/register", { method: "POST", body: JSON.stringify({ username, email, password }) }),

  login: async (username, password) => {
    const data = await apiFetch("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    });
    localStorage.setItem("fantasy_token", data.access_token);
    return data;
  },

  logout: () => localStorage.removeItem("fantasy_token"),
};

// ── Players ───────────────────────────────────────────────────────────────
const Players = {
  list: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return apiFetch(`/players/${qs ? "?" + qs : ""}`);
  },
  get: (id) => apiFetch(`/players/${id}`),
  stats: (id) => apiFetch(`/players/${id}/stats`),
};

// ── Teams ─────────────────────────────────────────────────────────────────
const Teams = {
  create: (name) =>
    apiFetch("/teams/", { method: "POST", body: JSON.stringify({ name }) }),
  myTeam: () => apiFetch("/teams/me"),
  mySquad: () => apiFetch("/teams/me/squad"),
  transfer: (player_out_id, player_in_id) =>
    apiFetch("/teams/me/transfer", { method: "POST", body: JSON.stringify({ player_out_id, player_in_id }) }),
  setLineup: (starters, captain_id, vice_captain_id) =>
    apiFetch("/teams/me/lineup", { method: "POST", body: JSON.stringify({ starters, captain_id, vice_captain_id }) }),
};

// ── Leagues ───────────────────────────────────────────────────────────────
const Leagues = {
  create: (name, league_type = "classic") =>
    apiFetch("/leagues/", { method: "POST", body: JSON.stringify({ name, league_type }) }),
  join: (invite_code) =>
    apiFetch(`/leagues/join/${invite_code}`, { method: "POST" }),
  myLeagues: () => apiFetch("/leagues/"),
  standings: (id) => apiFetch(`/leagues/${id}/standings`),
};

// ── Gameweeks ─────────────────────────────────────────────────────────────
const Gameweeks = {
  list: () => apiFetch("/gameweeks/"),
  current: () => apiFetch("/gameweeks/current"),
  myPicks: (gwId) => apiFetch(`/gameweeks/${gwId}/my-picks`),
  points: (gwId) => apiFetch(`/gameweeks/${gwId}/points`),
};
