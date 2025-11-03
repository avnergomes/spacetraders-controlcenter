import os, json, time, re, math
from collections import Counter
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ================================
# App config
# ================================
st.set_page_config(page_title="SpaceTraders Control Center", page_icon="🚀", layout="wide")
st.title("🚀 SpaceTraders Control Center")

BASE_URL = "https://api.spacetraders.io/v2"

# ================================
# Helpers (retry, errors, cooldown)
# ================================
def backoff(attempt: int) -> float:
    return min(30, 2 ** attempt) + 0.05 * attempt

def parse_cooldown_seconds(err_text: str, fallback: int = 60) -> int:
    m = re.search(r"remainingSeconds['\"]?:\s*(\d+)", err_text)
    return int(m.group(1)) if m else fallback

def toast_ok(msg: str): st.toast(msg, icon="✅")
def toast_warn(msg: str): st.toast(msg, icon="⚠️")
def toast_err(msg: str): st.toast(msg, icon="❌")


def trigger_rerun() -> None:
    rerun_fn = getattr(st, "experimental_rerun", None)
    if rerun_fn is None:
        rerun_fn = getattr(st, "rerun")
    rerun_fn()


def parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def humanize_timedelta(delta_seconds: Optional[float]) -> str:
    if delta_seconds is None:
        return "—"
    seconds = int(delta_seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h"


def travel_progress(nav: Dict[str, Any]) -> Dict[str, Any]:
    route = nav.get("route", {}) if nav else {}
    dep = parse_ts(route.get("departureTime"))
    arr = parse_ts(route.get("arrival"))
    if not dep or not arr:
        return {"fraction": None, "eta": "—"}
    now = datetime.now(timezone.utc)
    total = (arr - dep).total_seconds()
    if total <= 0:
        return {"fraction": None, "eta": "—"}
    elapsed = (now - dep).total_seconds()
    fraction = min(1.0, max(0.0, elapsed / total))
    eta_seconds = (arr - now).total_seconds()
    return {
        "fraction": fraction,
        "eta": humanize_timedelta(eta_seconds if eta_seconds > 0 else 0),
        "arrival": arr,
    }


def normalize_symbol(symbol: Optional[str]) -> str:
    return symbol.strip().upper() if isinstance(symbol, str) else ""


def waypoint_distance(a: Optional[dict], b: Optional[dict]) -> Optional[float]:
    if not a or not b:
        return None
    try:
        ax, ay = float(a.get("x")), float(a.get("y"))
        bx, by = float(b.get("x")), float(b.get("y"))
        return math.hypot(ax - bx, ay - by)
    except Exception:
        return None


def parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def humanize_timedelta(delta_seconds: Optional[float]) -> str:
    if delta_seconds is None:
        return "—"
    seconds = int(delta_seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h"


def travel_progress(nav: Dict[str, Any]) -> Dict[str, Any]:
    route = nav.get("route", {}) if nav else {}
    dep = parse_ts(route.get("departureTime"))
    arr = parse_ts(route.get("arrival"))
    if not dep or not arr:
        return {"fraction": None, "eta": "—"}
    now = datetime.now(timezone.utc)
    total = (arr - dep).total_seconds()
    if total <= 0:
        return {"fraction": None, "eta": "—"}
    elapsed = (now - dep).total_seconds()
    fraction = min(1.0, max(0.0, elapsed / total))
    eta_seconds = (arr - now).total_seconds()
    return {
        "fraction": fraction,
        "eta": humanize_timedelta(eta_seconds if eta_seconds > 0 else 0),
        "arrival": arr,
    }


def normalize_symbol(symbol: Optional[str]) -> str:
    return symbol.strip().upper() if isinstance(symbol, str) else ""


def waypoint_distance(a: Optional[dict], b: Optional[dict]) -> Optional[float]:
    if not a or not b:
        return None
    try:
        ax, ay = float(a.get("x")), float(a.get("y"))
        bx, by = float(b.get("x")), float(b.get("y"))
        return math.hypot(ax - bx, ay - by)
    except Exception:
        return None


def parse_ts(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def humanize_timedelta(delta_seconds: Optional[float]) -> str:
    if delta_seconds is None:
        return "—"
    seconds = int(delta_seconds)
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    if hours < 24:
        return f"{hours}h {minutes}m"
    days, hours = divmod(hours, 24)
    return f"{days}d {hours}h"


def travel_progress(nav: Dict[str, Any]) -> Dict[str, Any]:
    route = nav.get("route", {}) if nav else {}
    dep = parse_ts(route.get("departureTime"))
    arr = parse_ts(route.get("arrival"))
    if not dep or not arr:
        return {"fraction": None, "eta": "—"}
    now = datetime.now(timezone.utc)
    total = (arr - dep).total_seconds()
    if total <= 0:
        return {"fraction": None, "eta": "—"}
    elapsed = (now - dep).total_seconds()
    fraction = min(1.0, max(0.0, elapsed / total))
    eta_seconds = (arr - now).total_seconds()
    return {
        "fraction": fraction,
        "eta": humanize_timedelta(eta_seconds if eta_seconds > 0 else 0),
        "arrival": arr,
    }


def normalize_symbol(symbol: Optional[str]) -> str:
    return symbol.strip().upper() if isinstance(symbol, str) else ""


def waypoint_distance(a: Optional[dict], b: Optional[dict]) -> Optional[float]:
    if not a or not b:
        return None
    try:
        ax, ay = float(a.get("x")), float(a.get("y"))
        bx, by = float(b.get("x")), float(b.get("y"))
        return math.hypot(ax - bx, ay - by)
    except Exception:
        return None

# ================================
# HTTP client (auto {} for POST)
# ================================
class STClient:
    def __init__(self, token: str, timeout: int = 30):
        self.s = requests.Session()
        self.s.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        })
        self.timeout = timeout

    def _respect_rate(self, r: requests.Response):
        try:
            remaining = int(r.headers.get("X-RateLimit-Remaining", "1"))
            reset = int(r.headers.get("X-RateLimit-Reset", "1"))
            if remaining <= 1:
                time.sleep(reset + 0.25)
        except Exception:
            pass

    def request(self, method: str, path: str, *, params=None, body: Optional[dict] = None, retries: int = 4):
        url = f"{BASE_URL}{path}"
        attempt = 0
        while True:
            try:
                # Always send a JSON body ({} if none) to satisfy strict Content-Type parsing
                payload = body if body is not None else {}
                r = self.s.request(method, url, params=params, json=payload, timeout=self.timeout)
                self._respect_rate(r)
                if r.status_code in (429, 500, 502, 503, 504):
                    attempt += 1
                    if attempt > retries:
                        r.raise_for_status()
                    time.sleep(backoff(attempt)); continue
                r.raise_for_status()
                return r.json()
            except requests.HTTPError as e:
                try:
                    detail = r.json()
                except Exception:
                    detail = {"error": str(e)}
                raise RuntimeError(f"HTTP {r.status_code} {method} {path}: {detail}")

    def get(self, path, **kw):  return self.request("GET", path, **kw)
    def post(self, path, **kw): return self.request("POST", path, **kw)
    def patch(self, path, **kw):return self.request("PATCH", path, **kw)

# ================================
# CACHED API wrappers (read-only)
# ================================
@st.cache_data(show_spinner=False)
def api_my_agent(token: str):  return STClient(token).get("/my/agent")  # Agents & /my explained in docs. :contentReference[oaicite:1]{index=1}

@st.cache_data(show_spinner=False)
def api_my_ships(token: str, page=1, limit=20):
    return STClient(token).get("/my/ships", params={"page": page, "limit": min(limit, 20)})

@st.cache_data(show_spinner=False)
def api_my_contracts(token: str, page=1, limit=20):
    return STClient(token).get("/my/contracts", params={"page": page, "limit": min(limit, 20)})

@st.cache_data(show_spinner=False)
def api_systems(token: str, page=1, limit=20):
    return STClient(token).get("/systems", params={"page": page, "limit": min(limit, 20)})

@st.cache_data(show_spinner=False)
def api_waypoints(token: str, system_symbol: str, page=1, limit=20, traits: Optional[str]=None):
    params = {"page": page, "limit": min(limit, 20)}
    if traits: params["traits"] = traits
    return STClient(token).get(f"/systems/{system_symbol}/waypoints", params=params)

@st.cache_data(show_spinner=False)
def api_market(token: str, waypoint_symbol: str):
    sys_sym = waypoint_symbol.split("-")[0]
    return STClient(token).get(f"/systems/{sys_sym}/waypoints/{waypoint_symbol}/market")  # Markets concept. :contentReference[oaicite:2]{index=2}

@st.cache_data(show_spinner=False)
def api_shipyard(token: str, waypoint_symbol: str):
    sys_sym = waypoint_symbol.split("-")[0]
    return STClient(token).get(f"/systems/{sys_sym}/waypoints/{waypoint_symbol}/shipyard")  # Shipyard quickstart. :contentReference[oaicite:3]{index=3}


@st.cache_data(show_spinner=False)
def fetch_system_waypoints(token: str, system_symbol: str, max_pages: int = 5) -> List[dict]:
    client = STClient(token)
    waypoints: List[dict] = []
    page = 1
    total_pages = 1
    while page <= max_pages and page <= total_pages:
        resp = client.get(
            f"/systems/{system_symbol}/waypoints",
            params={"page": page, "limit": 20},
        )
        data = resp.get("data", []) if isinstance(resp, dict) else []
        waypoints.extend(data)
        meta = resp.get("meta", {}) if isinstance(resp, dict) else {}
        total_pages = max(total_pages, meta.get("totalPages", total_pages))
        if not data:
            break
        page += 1
    return waypoints


def logistic_summary(waypoints: List[dict], current_symbol: Optional[str] = None) -> Dict[str, List[dict]]:
    symbol_map = {w.get("symbol"): w for w in waypoints if w.get("symbol")}
    current_wp = symbol_map.get(current_symbol) if current_symbol else None

    def traits_for(wp: dict) -> List[str]:
        traits = []
        for t in wp.get("traits", []) or []:
            if isinstance(t, dict):
                if t.get("symbol"): traits.append(t.get("symbol"))
            elif isinstance(t, str):
                traits.append(t)
        return traits

    def build_entry(wp: dict) -> dict:
        dist = waypoint_distance(current_wp, wp)
        return {
            "symbol": wp.get("symbol"),
            "type": wp.get("type"),
            "distance": round(dist, 1) if isinstance(dist, (float, int)) else None,
            "traits": ", ".join(sorted(traits_for(wp))) or "—",
        }

    mining_targets = []
    for wp in waypoints:
        t = (wp.get("type") or "").upper()
        wp_traits = {tr.upper() for tr in traits_for(wp)}
        if any(keyword in t for keyword in ("ASTEROID", "MINING")) or wp_traits.intersection({"COMMON_METAL_DEPOSITS", "RARE_METAL_DEPOSITS", "PRECIOUS_METAL_DEPOSITS", "MINERAL_DEPOSITS", "ASTEROID_FIELD"}):
            mining_targets.append(build_entry(wp))

    marketplace_targets = []
    warehouse_targets = []
    shipyard_targets = []
    for wp in waypoints:
        wp_traits = {tr.upper() for tr in traits_for(wp)}
        if "MARKETPLACE" in wp_traits:
            marketplace_targets.append(build_entry(wp))
        if "WAREHOUSE" in wp_traits:
            warehouse_targets.append(build_entry(wp))
        if "SHIPYARD" in wp_traits:
            shipyard_targets.append(build_entry(wp))

    summary: Dict[str, List[dict]] = {
        "Mining sites": mining_targets,
        "Markets & delivery": marketplace_targets,
        "Warehouses": warehouse_targets,
        "Shipyards": shipyard_targets,
    }
    return summary

# ================================
# Non-cached actions
# ================================
def api_orbit(token, ship):    return STClient(token).post(f"/my/ships/{ship}/orbit", body={})
def api_dock(token, ship):     return STClient(token).post(f"/my/ships/{ship}/dock", body={})
def api_refuel(token, ship):   return STClient(token).post(f"/my/ships/{ship}/refuel", body={})
def api_nav(token, ship, wp):
    try:
        return STClient(token).post(f"/my/ships/{ship}/navigate", body={"waypointSymbol": wp})
    except Exception:
        return STClient(token).post(f"/my/ships/{ship}/navigate", body={"course": {"destination": wp}})
def api_nav_status(token, ship): return STClient(token).get(f"/my/ships/{ship}/nav")  # Navigation concept. :contentReference[oaicite:4]{index=4}
def api_extract(token, ship, survey=None):
    body = {"survey": survey} if survey else {}
    return STClient(token).post(f"/my/ships/{ship}/extract", body=body)  # Extraction concept. :contentReference[oaicite:5]{index=5}
def api_survey(token, ship):
    return STClient(token).post(f"/my/ships/{ship}/survey", body={})
def api_jettison(token, ship, symbol, units):
    return STClient(token).post(f"/my/ships/{ship}/jettison", body={"symbol": symbol, "units": units})
def api_sell(token, ship, symbol, units):
    return STClient(token).post(f"/my/ships/{ship}/sell", body={"symbol": symbol, "units": units})
def api_buy(token, ship, symbol, units):
    return STClient(token).post(f"/my/ships/{ship}/purchase", body={"symbol": symbol, "units": units})
def api_deliver(token, contract_id, ship, trade_symbol, units):
    return STClient(token).post(f"/my/contracts/{contract_id}/deliver",
                                body={"shipSymbol": ship, "tradeSymbol": trade_symbol, "units": units})
def api_accept_contract(token, contract_id):
    return STClient(token).post(f"/my/contracts/{contract_id}/accept", body={})
def api_purchase_ship(token, ship_type, shipyard_waypoint):
    return STClient(token).post("/my/ships", body={"shipType": ship_type, "waypointSymbol": shipyard_waypoint})  # Purchase per quickstart. :contentReference[oaicite:6]{index=6}
def api_repair_ship(token, ship, parts=0):
    # Per maintenance guide: repair at shipyard. (Exact body may vary by version; keep minimal)
    sys_wp = api_nav_status(token, ship).get("data", {}).get("waypointSymbol")
    if not sys_wp: raise RuntimeError("Unknown ship location for repair.")
    sys_sym = sys_wp.split("-")[0]
    # Example repair endpoint from maintenance docs (high-level): use POST /my/ships/{ship}/repair
    return STClient(token).post(f"/my/ships/{ship}/repair", body={})  # Maintenance guide. :contentReference[oaicite:7]{index=7}
def api_scrap_ship(token, ship):
    return STClient(token).post(f"/my/ships/{ship}/scrap", body={})   # Added in v2.2 per changelog. :contentReference[oaicite:8]{index=8}

# ================================
# Auth / Token entry (SaaS-friendly)
# ================================
with st.sidebar:
    st.header("Authentication")
    st.caption("Paste your SpaceTraders bearer token (we do **not** store it).")
    token = st.text_input("Bearer Token", type="password", help="Generate via Quickstart → New game.")
    # Auth guidance. :contentReference[oaicite:9]{index=9}
    if token and st.button("Use Token", type="primary"):
        st.session_state["token"] = token
        st.cache_data.clear()
        toast_ok("Token active")

token = st.session_state.get("token")
if not token:
    st.warning("Paste your SpaceTraders token in the sidebar to begin.")
    st.stop()

if "mission_shortcuts" not in st.session_state:
    st.session_state["mission_shortcuts"] = {"mining": "", "delivery": "", "warehouse": ""}
for shortcut_key, state_key in (
    ("mining", "shortcut_mining"),
    ("delivery", "shortcut_delivery"),
    ("warehouse", "shortcut_warehouse"),
):
    desired_value = normalize_symbol(st.session_state["mission_shortcuts"].get(shortcut_key, ""))
    if st.session_state.get(state_key) != desired_value:
        st.session_state[state_key] = desired_value

# ================================
# Tabs
# ================================
tab_dash, tab_agent, tab_fleet, tab_contracts, tab_systems, tab_markets, tab_shipyards, tab_outfit = st.tabs(
    ["Dashboard", "Agent", "Fleet", "Contracts", "Systems & Waypoints", "Markets", "Shipyards", "Outfitting & Maintenance"]
)

# ================================
# Dashboard
# ================================
with tab_dash:
    st.subheader("Overview")
    try:
        me = api_my_agent(token).get("data", {})
        ships = api_my_ships(token).get("data", [])
        contracts = api_my_contracts(token).get("data", [])
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Agent", me.get("symbol"))
        c2.metric("Faction", me.get("startingFaction"))
        c3.metric("HQ", me.get("headquarters"))
        c4.metric("Credits", f"{me.get('credits',0):,}")
        c5.metric("Fleet Size", len(ships))

        c6, c7, c8 = st.columns(3)
        statuses = Counter([s.get("nav", {}).get("status", "UNKNOWN") for s in ships]) if ships else {}
        in_transit = statuses.get("IN_TRANSIT", 0)
        docked = statuses.get("DOCKED", 0)
        orbiting = statuses.get("IN_ORBIT", 0)
        c6.metric("Ships in transit", in_transit)
        c7.metric("Docked", docked)
        c8.metric("In orbit", orbiting)

        active_contracts = sum(1 for c in contracts if c.get("accepted") and not c.get("fulfilled"))
        pending_contracts = sum(1 for c in contracts if not c.get("accepted"))
        c9, c10 = st.columns(2)
        c9.metric("Active contracts", active_contracts)
        c10.metric("Pending offers", pending_contracts)

        st.caption("SpaceTraders is a programmable API game — automate everything you see here. (Docs home) ")
        st.caption("Quickstart: new game → first mission → purchase ship → mine → sell → deliver.")

        if ships:
            roles = Counter([s.get("registration", {}).get("role", "UNSPEC") for s in ships])
            role_df = pd.DataFrame(
                [{"Role": role, "Count": count} for role, count in roles.most_common()]
            )
            cchart, ctable = st.columns([2, 1])
            with cchart:
                fig = go.Figure()
                fig.add_trace(go.Pie(labels=role_df["Role"], values=role_df["Count"], hole=0.45))
                fig.update_layout(height=380, margin=dict(l=30, r=30, t=30, b=30), title="Fleet by role")
                st.plotly_chart(fig, use_container_width=True)
            with ctable:
                st.dataframe(role_df, hide_index=True, use_container_width=True)

            cargo_stats = []
            for ship in ships:
                cargo = ship.get("cargo", {})
                capacity = cargo.get("capacity", 0)
                used = cargo.get("units", 0)
                percent = round((used / capacity) * 100, 1) if capacity else 0
                cargo_stats.append({
                    "Ship": ship.get("symbol"),
                    "Role": ship.get("registration", {}).get("role"),
                    "Location": ship.get("nav", {}).get("waypointSymbol"),
                    "Status": ship.get("nav", {}).get("status"),
                    "Cargo": f"{used}/{capacity}",
                    "Fill %": percent,
                })
            st.dataframe(pd.DataFrame(cargo_stats), hide_index=True, use_container_width=True)
    except Exception as e:
        toast_err(str(e))

# ================================
# Agent
# ================================
with tab_agent:
    st.subheader("Agent Details")
    try:
        st.json(api_my_agent(token).get("data", {}))
    except Exception as e:
        toast_err(str(e))

# ================================
# Fleet
# ================================
with tab_fleet:
    st.subheader("Fleet")
    try:
        fleet = api_my_ships(token).get("data", [])
        shortcuts = st.session_state.get("mission_shortcuts", {})
        st.markdown("### Mission shortcuts & favorites")
        col_short1, col_short2, col_short3, col_short4 = st.columns([2, 2, 2, 1])
        col_short1.text_input("Primary mining waypoint", key="shortcut_mining")
        col_short2.text_input("Primary delivery waypoint", key="shortcut_delivery")
        col_short3.text_input("Preferred warehouse/shipyard", key="shortcut_warehouse")
        if col_short4.button("Save favorites"):
            shortcuts["mining"] = normalize_symbol(st.session_state.get("shortcut_mining"))
            shortcuts["delivery"] = normalize_symbol(st.session_state.get("shortcut_delivery"))
            shortcuts["warehouse"] = normalize_symbol(st.session_state.get("shortcut_warehouse"))
            st.toast("Mission shortcuts updated", icon="🧭")
        st.caption(
            "Set quick targets once, then use the buttons below each ship to jump between mining, delivery, and outfitting hubs."
        )

        if not fleet:
            st.info("No ships found.")
        else:
            colf1, colf2, colf3, colf4 = st.columns([2, 2, 2, 1])
            search_term = colf1.text_input("Search (symbol or location)")
            roles_available = sorted({ship.get("registration", {}).get("role", "UNSPEC") for ship in fleet})
            statuses_available = sorted({ship.get("nav", {}).get("status", "UNKNOWN") for ship in fleet})
            role_filter = colf2.multiselect("Roles", roles_available, default=roles_available)
            status_filter = colf3.multiselect("Statuses", statuses_available, default=statuses_available)
            if colf4.button("Refresh", help="Clear cache and reload from the API"):
                st.cache_data.clear()
                trigger_rerun()

            filtered = []
            for ship in fleet:
                role = ship.get("registration", {}).get("role", "UNSPEC")
                status = ship.get("nav", {}).get("status", "UNKNOWN")
                text_blob = f"{ship.get('symbol','')} {ship.get('nav',{}).get('waypointSymbol','')}".lower()
                if role_filter and role not in role_filter:
                    continue
                if status_filter and status not in status_filter:
                    continue
                if search_term and search_term.lower() not in text_blob:
                    continue
                filtered.append(ship)

            if filtered:
                utilization_rows = []
                for ship in filtered:
                    cargo = ship.get("cargo", {})
                    capacity = cargo.get("capacity", 0)
                    used = cargo.get("units", 0)
                    frac = (used / capacity) if capacity else 0
                    utilization_rows.append({
                        "Ship": ship.get("symbol"),
                        "Role": ship.get("registration", {}).get("role"),
                        "Status": ship.get("nav", {}).get("status"),
                        "Waypoint": ship.get("nav", {}).get("waypointSymbol"),
                        "Fuel": f"{ship.get('fuel',{}).get('current',0)}/{ship.get('fuel',{}).get('capacity',0)}",
                        "Cargo fill %": round(frac * 100, 1),
                    })
                if utilization_rows:
                    st.dataframe(pd.DataFrame(utilization_rows), hide_index=True, use_container_width=True)
                    st.download_button(
                        "Download filtered fleet manifest",
                        data=json.dumps(filtered, indent=2),
                        file_name="fleet_manifest.json",
                        mime="application/json",
                    )
            else:
                st.warning("No ships match the current filters.")

            for ship in filtered:
                sym = ship.get("symbol")
                with st.expander(f"🚢 {sym} — {ship.get('registration',{}).get('role','?')}"):
                    nav = ship.get("nav", {})
                    fuel = ship.get("fuel", {})
                    cargo = ship.get("cargo", {})
                    progress = travel_progress(nav)
                    c1, c2, c3, c4 = st.columns(4)
                    c1.write(f"**Status**: {nav.get('status')}")
                    c2.write(f"**At**: {nav.get('waypointSymbol')}")
                    c3.write(f"**Fuel**: {fuel.get('current',0)}/{fuel.get('capacity',0)}")
                    c4.write(f"**Engine**: {ship.get('engine',{}).get('name','?')}")

                    if progress.get("fraction") is not None:
                        st.progress(progress["fraction"], text=f"En route — ETA {progress['eta']}")
                    elif nav.get("status") == "IN_ORBIT":
                        st.info("Ship is in orbit and ready for commands.")
                    elif nav.get("status") == "DOCKED":
                        st.info("Ship is docked. Orbit before navigating or extracting.")

                    cap = cargo.get("capacity", 0); used = cargo.get("units", 0); left = max(0, cap - used)
                    st.progress(min(1.0, used / cap) if cap else 0.0, text=f"Cargo {used}/{cap} (free {left})")
                    inv = cargo.get("inventory", [])
                    if inv:
                        st.dataframe(pd.DataFrame(inv), use_container_width=True, hide_index=True)
                    else:
                        st.caption("Empty cargo")

                    # Controls
                    cc1, cc2, cc3, cc4, cc5, cc6 = st.columns(6)
                    if cc1.button("Orbit", key=f"o_{sym}"):
                        try: api_orbit(token, sym); toast_ok("In orbit"); st.cache_data.clear()
                        except Exception as e: toast_err(str(e))
                    if cc2.button("Dock", key=f"d_{sym}"):
                        try: api_dock(token, sym); toast_ok("Docked"); st.cache_data.clear()
                        except Exception as e: toast_err(str(e))
                    if cc3.button("Refuel", key=f"r_{sym}"):
                        try: api_refuel(token, sym); toast_ok("Refueled"); st.cache_data.clear()
                        except Exception as e: toast_err(str(e))

                    dest = cc4.text_input("Waypoint", value=nav.get("waypointSymbol",""), key=f"wp_{sym}")
                    if cc4.button("Navigate", key=f"n_{sym}"):
                        try:
                            api_nav(token, sym, dest); toast_ok(f"Navigating to {dest}")
                            st.cache_data.clear()
                        except Exception as e: toast_err(str(e))

                    if cc5.button("Extract", key=f"x_{sym}"):
                        try:
                            resp = api_extract(token, sym)
                            y = resp.get("data",{}).get("extraction",{}).get("yield",{})
                            toast_ok(f"Extracted {y.get('units',0)} of {y.get('symbol','?')}")
                            st.cache_data.clear()
                        except Exception as e:
                            toast_err(str(e)); st.info(f"⏳ Cooldown likely: wait ~{parse_cooldown_seconds(str(e))}s")

                    with cc6:
                        st.caption("Sell/Jettison")
                        s_sym = st.text_input("Symbol", key=f"sell_sym_{sym}")
                        s_units = st.number_input("Units", min_value=1, value=1, step=1, key=f"sell_qty_{sym}")
                        b1, b2 = st.columns(2)
                        if b1.button("Sell", key=f"sell_{sym}"):
                            try: api_sell(token, sym, s_sym, int(s_units)); toast_ok("Sold"); st.cache_data.clear()
                            except Exception as e: toast_err(str(e))
                        if b2.button("Jettison", key=f"jet_{sym}"):
                            try: api_jettison(token, sym, s_sym, int(s_units)); toast_ok("Jettisoned"); st.cache_data.clear()
                            except Exception as e: toast_err(str(e))

                    quick_mining = shortcuts.get("mining")
                    quick_delivery = shortcuts.get("delivery")
                    quick_warehouse = shortcuts.get("warehouse")
                    qc1, qc2, qc3, qc4 = st.columns(4)
                    if quick_delivery:
                        if qc1.button(f"Go deliver ({quick_delivery})", key=f"quick_delivery_{sym}"):
                            try:
                                api_nav(token, sym, normalize_symbol(quick_delivery))
                                toast_ok(f"Heading to {quick_delivery}")
                                st.cache_data.clear()
                            except Exception as e:
                                toast_err(str(e))
                    else:
                        qc1.caption("Set a delivery shortcut above to enable one-tap runs.")

                    if quick_mining:
                        if qc2.button(f"Return to mining ({quick_mining})", key=f"quick_mining_{sym}"):
                            try:
                                api_nav(token, sym, normalize_symbol(quick_mining))
                                toast_ok(f"Heading to {quick_mining}")
                                st.cache_data.clear()
                            except Exception as e:
                                toast_err(str(e))
                    else:
                        qc2.caption("Add a mining hotspot shortcut above.")

                    if quick_warehouse:
                        if qc3.button(f"To warehouse ({quick_warehouse})", key=f"quick_warehouse_{sym}"):
                            try:
                                api_nav(token, sym, normalize_symbol(quick_warehouse))
                                toast_ok(f"Heading to {quick_warehouse}")
                                st.cache_data.clear()
                            except Exception as e:
                                toast_err(str(e))
                    else:
                        qc3.caption("Set your outfitting hub to unlock this hop.")

                    qc4.caption("Route planner below lists logistics in-system.")

                    system_symbol = nav.get("systemSymbol")
                    if system_symbol:
                        try:
                            system_waypoints = fetch_system_waypoints(token, system_symbol)
                            logistics = logistic_summary(system_waypoints, nav.get("waypointSymbol"))
                        except Exception as e:
                            logistics = {}
                            toast_err(str(e))
                        if logistics and any(logistics_section for logistics_section in logistics.values() if logistics_section):
                            with st.expander("📍 Route planner & logistics", expanded=False):
                                st.caption("Choose a nearby waypoint to auto-navigate or store as a shortcut.")
                                for section_name, entries in logistics.items():
                                    if not entries:
                                        continue
                                    section_key = re.sub(r"[^A-Za-z0-9_]", "", section_name.replace(" ", "_"))
                                    st.markdown(f"**{section_name}**")
                                    df_entries = pd.DataFrame(entries)
                                    st.dataframe(df_entries, hide_index=True, use_container_width=True)
                                    options_map = {entry["symbol"]: entry for entry in entries if entry.get("symbol")}
                                    if not options_map:
                                        continue
                                    select_key = f"select_{section_key}_{sym}"
                                    selected_symbol = st.selectbox(
                                        "Select target",
                                        list(options_map.keys()),
                                        format_func=lambda s, m=options_map: f"{s} — {m[s].get('type','?')} ({m[s].get('distance','?')} su)",
                                        key=select_key,
                                    )
                                    action_cols = st.columns(3)
                                    if action_cols[0].button("Navigate", key=f"nav_{section_key}_{sym}"):
                                        try:
                                            api_nav(token, sym, normalize_symbol(selected_symbol))
                                            toast_ok(f"Heading to {selected_symbol}")
                                            st.cache_data.clear()
                                        except Exception as e:
                                            toast_err(str(e))
                                    if section_name == "Mining sites":
                                        if action_cols[1].button("Set mining shortcut", key=f"set_mining_{section_key}_{sym}"):
                                            shortcuts["mining"] = normalize_symbol(selected_symbol)
                                            toast_ok(f"Mining shortcut set to {selected_symbol}")
                                    elif section_name == "Markets & delivery":
                                        if action_cols[1].button("Set delivery shortcut", key=f"set_delivery_{section_key}_{sym}"):
                                            shortcuts["delivery"] = normalize_symbol(selected_symbol)
                                            toast_ok(f"Delivery shortcut set to {selected_symbol}")
                                    elif section_name == "Warehouses":
                                        if action_cols[1].button("Set warehouse shortcut", key=f"set_warehouse_{section_key}_{sym}"):
                                            shortcuts["warehouse"] = normalize_symbol(selected_symbol)
                                            toast_ok(f"Warehouse shortcut set to {selected_symbol}")
                                    elif section_name == "Shipyards":
                                        action_cols[1].caption("Shipyard services available here.")
                                    else:
                                        action_cols[1].write("")
                                    action_cols[2].caption(f"Traits: {options_map[selected_symbol].get('traits', '—')}")
                                
                    st.divider()
                    colops1, colops2, colops3 = st.columns(3)
                    if colops1.button("Sync Nav Status", key=f"sync_{sym}"):
                        try:
                            api_nav_status(token, sym)
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))

                    surveys_state = st.session_state.setdefault("surveys", {})
                    if colops2.button("Create Survey", key=f"survey_{sym}"):
                        try:
                            survey_resp = api_survey(token, sym)
                            survey_data = survey_resp.get("data", {}).get("surveys", [])
                            if survey_data:
                                ship_surveys = surveys_state.setdefault(sym, [])
                                ship_surveys.extend(survey_data)
                                toast_ok(f"Stored {len(survey_data)} surveys")
                            else:
                                toast_warn("No surveys returned")
                        except Exception as e:
                            toast_err(str(e))

                    available_surveys = surveys_state.get(sym, [])
                    if available_surveys:
                        with st.expander("Stored surveys"):
                            for idx, survey in enumerate(available_surveys):
                                expires = parse_ts(survey.get("expiration"))
                                expires_in = humanize_timedelta((expires - datetime.now(timezone.utc)).total_seconds() if expires else None)
                                st.write(f"Survey {idx + 1} — expires in {expires_in}")
                                st.json(survey)
                                if st.button("Use survey", key=f"use_survey_{sym}_{idx}"):
                                    try:
                                        api_extract(token, sym, survey)
                                        toast_ok("Extraction started with survey")
                                        st.cache_data.clear()
                                        surveys_state[sym].pop(idx)
                                        trigger_rerun()
                                    except Exception as e:
                                        toast_err(str(e))
    except Exception as e:
        toast_err(str(e))

# ================================
# Contracts
# ================================
with tab_contracts:
    st.subheader("Contracts")
    try:
        data = api_my_contracts(token).get("data", [])
        if not data:
            st.info("No contracts yet.")
        for c in data:
            cid = c.get("id"); acc = c.get("accepted"); terms = c.get("terms",{})
            with st.expander(f"📜 {cid} {'✅' if acc else '❗'}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"**Type**: {c.get('type')}")
                c2.write(f"**Accepted**: {acc}")
                deadline = terms.get("deadline")
                c3.write(f"**Deadline**: {deadline if deadline else '—'}")
                deliver = terms.get("deliver", [])
                if deliver:
                    df = pd.DataFrame(deliver)
                    st.dataframe(df, hide_index=True, use_container_width=True)
                    for deliver_idx, deliver_item in enumerate(deliver):
                        required = deliver_item.get("unitsRequired") or deliver_item.get("units", 0)
                        fulfilled = deliver_item.get("unitsFulfilled") or deliver_item.get("fulfilled", 0)
                        if required:
                            frac = min(1.0, fulfilled / required)
                        else:
                            frac = 0
                        destination = deliver_item.get("destinationSymbol", "?")
                        symbol = deliver_item.get("tradeSymbol", "?")
                        st.progress(frac, text=f"{symbol} to {destination} — {fulfilled}/{required} units")
                        col_d1, col_d2 = st.columns([3, 1])
                        if col_d1.button(
                            f"Set {destination} as delivery shortcut",
                            key=f"contract_delivery_{cid}_{deliver_idx}",
                        ):
                            st.session_state["mission_shortcuts"]["delivery"] = normalize_symbol(destination)
                            toast_ok(f"Delivery shortcut now set to {destination}")
                        col_d2.caption("Adds to fleet quick-nav buttons.")
                if not acc and st.button("Accept contract", key=f"ac_{cid}"):
                    try:
                        api_accept_contract(token, cid); toast_ok("Contract accepted"); st.cache_data.clear()
                    except Exception as e: toast_err(str(e))
                st.divider()
                # Quick delivery tool
                ships = api_my_ships(token).get("data", [])
                ship_opts = [s["symbol"] for s in ships] if ships else []
                colA, colB, colC, colD = st.columns(4)
                ship_sel = colA.selectbox("Ship", ship_opts, key=f"cd_ship_{cid}")
                trade = colB.text_input("Trade symbol", key=f"cd_trade_{cid}")
                qty = colC.number_input("Units", min_value=1, value=1, key=f"cd_qty_{cid}")
                if colD.button("Deliver", key=f"cd_btn_{cid}"):
                    try:
                        api_deliver(token, cid, ship_sel, trade, int(qty))
                        toast_ok("Delivered"); st.cache_data.clear()
                    except Exception as e:
                        toast_err(str(e))
        st.caption("Starter mission loop is: view → mine asteroid field → deliver → fulfill. ")  # First mission quickstart. :contentReference[oaicite:10]{index=10}
    except Exception as e:
        toast_err(str(e))

# ================================
# Systems & Waypoints (map)
# ================================
with tab_systems:
    st.subheader("Systems & Waypoints")
    try:
        ships = api_my_ships(token).get("data", [])
        default_system = ships[0]["nav"]["systemSymbol"] if ships else "X1-RV7"
        sys_sym = st.text_input("System symbol", value=default_system)
        traits = st.text_input("Filter by trait (comma or single, e.g. SHIPYARD, MARKETPLACE)")
        page = st.number_input("Page", min_value=1, value=1, step=1)
        if st.button("Load Waypoints"):
            trait_param = None
            if traits.strip():
                # Spaces/commas tolerated; docs support traits filter on waypoints. :contentReference[oaicite:11]{index=11}
                trait_param = ",".join([t.strip() for t in traits.split(",") if t.strip()])
            st.session_state["wps"] = api_waypoints(token, sys_sym, page=page, limit=20, traits=trait_param)
        wps_resp = st.session_state.get("wps", {})
        waypoints = wps_resp.get("data", []) if wps_resp else []
        if waypoints:
            waypoints_df = pd.DataFrame(waypoints)
            st.dataframe(waypoints_df, use_container_width=True, hide_index=True)
            type_counts = Counter()
            if "type" in waypoints_df:
                type_counts.update(waypoints_df["type"].fillna("UNKNOWN"))
            if not type_counts:
                type_counts = Counter([w.get("type", "UNKNOWN") for w in waypoints])
            trait_counts = Counter()
            for w in waypoints:
                for trait in w.get("traits", []):
                    name = trait.get("symbol") if isinstance(trait, dict) else trait
                    if name:
                        trait_counts[name] += 1
            ct1, ct2 = st.columns(2)
            if type_counts:
                type_df = pd.DataFrame({"Type": list(type_counts.keys()), "Count": list(type_counts.values())})
                type_df = type_df.sort_values("Count", ascending=False)
                with ct1:
                    fig_types = go.Figure()
                    fig_types.add_trace(go.Bar(x=type_df["Type"], y=type_df["Count"]))
                    fig_types.update_layout(height=320, margin=dict(l=10, r=10, t=30, b=80), title="Waypoint types")
                    st.plotly_chart(fig_types, use_container_width=True)
            if trait_counts:
                trait_df = pd.DataFrame({"Trait": list(trait_counts.keys()), "Count": list(trait_counts.values())})
                trait_df = trait_df.sort_values("Count", ascending=False)
                with ct2:
                    st.dataframe(trait_df, hide_index=True, use_container_width=True)
            st.download_button(
                "Download waypoints JSON",
                data=json.dumps(waypoints, indent=2),
                file_name=f"{sys_sym}_waypoints.json",
                mime="application/json",
            )
            # Simple XY scatter
            xs = [w.get("x", 0) for w in waypoints]; ys = [w.get("y", 0) for w in waypoints]
            labels = [w.get("symbol") for w in waypoints]; types = [w.get("type","?") for w in waypoints]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",
                                     text=[f"{l} ({t})" for l,t in zip(labels,types)],
                                     textposition="top center",
                                     marker=dict(size=11)))
            fig.update_layout(height=520, margin=dict(l=10,r=10,t=30,b=10), title=f"Waypoints in {sys_sym}")
            st.plotly_chart(fig, use_container_width=True)
        st.caption("Universe model: systems (stars) with XY; waypoints (planets, stations, asteroids) within each system.")  # Concept page. :contentReference[oaicite:12]{index=12}
    except Exception as e:
        toast_err(str(e))

# ================================
# Markets
# ================================
with tab_markets:
    st.subheader("Markets")
    wp = st.text_input("Waypoint symbol (e.g., X1-ABC-DEF)")
    if st.button("Load Market") and wp:
        try:
            mk = api_market(token, wp).get("data", {})
            st.json(mk)
            if mk.get("tradeGoods"):
                st.write("**Trade Goods**")
                goods_df = pd.DataFrame(mk["tradeGoods"])
                st.dataframe(goods_df, use_container_width=True, hide_index=True)
                exports = goods_df[goods_df.get("type") == "EXPORT"] if "type" in goods_df else pd.DataFrame()
                imports = goods_df[goods_df.get("type") == "IMPORT"] if "type" in goods_df else pd.DataFrame()
                exchanges = goods_df[goods_df.get("type") == "EXCHANGE"] if "type" in goods_df else pd.DataFrame()
                colm1, colm2, colm3 = st.columns(3)
                if not exports.empty:
                    best_sell = exports.sort_values("sellPrice", ascending=False).iloc[0]
                    colm1.metric("Best export sale", f"{best_sell['symbol']}", f"{int(best_sell['sellPrice']):,} credits")
                if not imports.empty:
                    best_buy = imports.sort_values("purchasePrice", ascending=True).iloc[0]
                    colm2.metric("Cheapest import", f"{best_buy['symbol']}", f"{int(best_buy['purchasePrice']):,} credits")
                if not exchanges.empty:
                    exchange = exchanges.iloc[0]
                    colm3.metric("Exchange good", exchange["symbol"], exchange.get("supply", "-"))
                st.download_button(
                    "Download market JSON",
                    data=json.dumps(mk, indent=2),
                    file_name=f"{wp}_market.json",
                    mime="application/json",
                )
            st.caption("Imports/Exports/Exchange reflect supply & demand — exports usually cheaper to buy.")  # Markets guide. :contentReference[oaicite:13]{index=13}
        except Exception as e:
            toast_err(str(e))

# ================================
# Shipyards
# ================================
with tab_shipyards:
    st.subheader("Shipyards")
    st.caption("Find waypoints with the SHIPYARD trait, view inventory, buy ships. Also swap/repair at shipyards.")
    sys_for_yards = st.text_input("System symbol to search", value="X1-RV7")
    if st.button("Find Shipyards"):
        try:
            yards = api_waypoints(token, sys_for_yards, page=1, limit=20, traits="SHIPYARD").get("data", [])
            st.dataframe(pd.DataFrame(yards), use_container_width=True, hide_index=True)
        except Exception as e:
            toast_err(str(e))
    yard_wp = st.text_input("Shipyard waypoint (orbital station with SHIPYARD)")
    coly1, coly2 = st.columns(2)
    if coly1.button("View Shipyard") and yard_wp:
        try:
            yd = api_shipyard(token, yard_wp).get("data", {})
            st.json(yd)
            if yd.get("ships"):
                st.write("**Available Ships**")
                st.dataframe(pd.DataFrame(yd["ships"]), use_container_width=True, hide_index=True)
            if yd.get("transactions"):
                st.write("**Recent Transactions**")
                st.dataframe(pd.DataFrame(yd["transactions"]), use_container_width=True, hide_index=True)
            st.caption("Price visibility may require a ship present at this waypoint (probe provided at start).")  # Quickstart note. :contentReference[oaicite:14]{index=14}
        except Exception as e:
            toast_err(str(e))
    # Purchase new ship
    ship_type = coly2.text_input("Ship type to purchase (e.g., SHIP_MINING_DRONE)")
    if coly2.button("Purchase Ship") and ship_type and yard_wp:
        try:
            api_purchase_ship(token, ship_type, yard_wp)
            toast_ok(f"Purchased {ship_type} at {yard_wp}")
            st.cache_data.clear()
        except Exception as e:
            toast_err(str(e))

# ================================
# Outfitting & Maintenance
# ================================
with tab_outfit:
    st.subheader("Outfitting & Maintenance")
    st.caption("Swap mounts/modules at shipyards; repair/scrap ships per v2.2 maintenance model.")
    ships = api_my_ships(token).get("data", [])
    ship_opts = [s["symbol"] for s in ships] if ships else []
    if not ship_opts:
        st.info("No ships.")
    else:
        ship_sel = st.selectbox("Ship", ship_opts)
        ship_data = next((s for s in ships if s.get("symbol") == ship_sel), {})
        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("Frame", ship_data.get("frame", {}).get("name", "?"))
        info_col2.metric("Reactor", ship_data.get("reactor", {}).get("name", "?"))
        info_col3.metric("Crew", ship_data.get("crew", {}).get("current", 0))
        shortcuts = st.session_state.get("mission_shortcuts", {})
        quick_section = st.columns(3)
        quick_mining = shortcuts.get("mining")
        quick_delivery = shortcuts.get("delivery")
        quick_warehouse = shortcuts.get("warehouse")
        if quick_delivery:
            if quick_section[0].button(f"Navigate to delivery hub ({quick_delivery})", key=f"outfit_delivery_{ship_sel}"):
                try:
                    api_nav(token, ship_sel, normalize_symbol(quick_delivery))
                    toast_ok(f"Heading to {quick_delivery}")
                    st.cache_data.clear()
                except Exception as e:
                    toast_err(str(e))
        else:
            quick_section[0].caption("Set a delivery shortcut in the Fleet tab.")
        if quick_mining:
            if quick_section[1].button(f"Back to mining ({quick_mining})", key=f"outfit_mining_{ship_sel}"):
                try:
                    api_nav(token, ship_sel, normalize_symbol(quick_mining))
                    toast_ok(f"Heading to {quick_mining}")
                    st.cache_data.clear()
                except Exception as e:
                    toast_err(str(e))
        else:
            quick_section[1].caption("Add a mining shortcut for fast redeployments.")
        if quick_warehouse:
            if quick_section[2].button(f"Head to warehouse ({quick_warehouse})", key=f"outfit_warehouse_{ship_sel}"):
                try:
                    api_nav(token, ship_sel, normalize_symbol(quick_warehouse))
                    toast_ok(f"Heading to {quick_warehouse}")
                    st.cache_data.clear()
                except Exception as e:
                    toast_err(str(e))
        else:
            quick_section[2].caption("Choose a warehouse shortcut to unlock outfitting jumps.")
        colm1, colm2, colm3 = st.columns(3)
        if colm1.button("Repair Ship"):
            try:
                api_repair_ship(token, ship_sel)
                toast_ok("Repair requested")
                st.cache_data.clear()
            except Exception as e:
                toast_err(str(e))
        if colm2.button("Scrap Ship"):
            try:
                api_scrap_ship(token, ship_sel)
                toast_ok("Scrap requested")
                st.cache_data.clear()
            except Exception as e:
                toast_err(str(e))
        with st.expander("Modules"):
            modules = ship_data.get("modules", [])
            if modules:
                st.dataframe(pd.DataFrame(modules), hide_index=True, use_container_width=True)
            else:
                st.caption("No modules equipped.")
        with st.expander("Mounts"):
            mounts = ship_data.get("mounts", [])
            if mounts:
                st.dataframe(pd.DataFrame(mounts), hide_index=True, use_container_width=True)
            else:
                st.caption("No mounts equipped.")
        st.caption("More mount/module swap endpoints can be wired similarly at shipyards (see outfitting docs).")
        warehouse_symbol = shortcuts.get("warehouse")
        with st.expander("Warehouse & add-on planner", expanded=False):
            st.caption("Preview the warehouse/shipyard data before flying in.")
            default_lookup = warehouse_symbol or ship_data.get("nav", {}).get("waypointSymbol", "")
            lookup_key = f"warehouse_lookup_{ship_sel}"
            if lookup_key not in st.session_state:
                st.session_state[lookup_key] = default_lookup
            lookup_value = st.text_input("Waypoint symbol", key=lookup_key)
            lookup_value_norm = normalize_symbol(lookup_value)
            col_lookup1, col_lookup2 = st.columns([1, 1])
            if col_lookup1.button("Load waypoint traits", key=f"load_traits_{ship_sel}") and lookup_value_norm:
                try:
                    system = lookup_value_norm.split("-")[0]
                    wps = fetch_system_waypoints(token, system)
                    wp_match = next((w for w in wps if normalize_symbol(w.get("symbol")) == lookup_value_norm), None)
                    if wp_match:
                        st.json(wp_match)
                    else:
                        st.warning("Waypoint not found in cached pages — adjust page limit or check symbol.")
                except Exception as e:
                    toast_err(str(e))
            if col_lookup2.button("Preview shipyard", key=f"preview_shipyard_{ship_sel}") and lookup_value_norm:
                try:
                    yard = api_shipyard(token, lookup_value_norm).get("data", {})
                    st.json(yard)
                except Exception as e:
                    toast_err(str(e))
