"""
SpaceTraders Control Center - Streamlit Application
A comprehensive interface for managing SpaceTraders fleet operations
"""
import os
import json
import time
import re
import math
from collections import Counter
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple

import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ================================
# App Configuration
# ================================
st.set_page_config(
    page_title="SpaceTraders Control Center",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = "https://api.spacetraders.io/v2"

# ================================
# Utility Functions
# ================================
def backoff(attempt: int) -> float:
    """Calculate exponential backoff time"""
    return min(30, 2 ** attempt) + 0.05 * attempt


def parse_cooldown_seconds(err_text: str, fallback: int = 60) -> int:
    """Extract cooldown seconds from error message"""
    m = re.search(r"remainingSeconds['\"]?:\s*(\d+)", err_text)
    return int(m.group(1)) if m else fallback


def toast_ok(msg: str):
    st.toast(msg, icon="✅")


def toast_warn(msg: str):
    st.toast(msg, icon="⚠️")


def toast_err(msg: str):
    st.toast(msg, icon="❌")


def trigger_rerun() -> None:
    """Trigger Streamlit rerun"""
    rerun_fn = getattr(st, "rerun", None) or getattr(st, "experimental_rerun", None)
    if rerun_fn:
        rerun_fn()


def parse_ts(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamp string to datetime"""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def humanize_timedelta(delta_seconds: Optional[float]) -> str:
    """Convert seconds to human readable format"""
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
    """Calculate travel progress and ETA"""
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
    """Normalize waypoint/system symbol"""
    return symbol.strip().upper() if isinstance(symbol, str) else ""


def system_symbol_from_waypoint(symbol: Optional[str]) -> str:
    """Extract system symbol from waypoint symbol"""
    parts = normalize_symbol(symbol).split("-")
    if len(parts) >= 2:
        return "-".join(parts[:2])
    return ""


def waypoint_distance(a: Optional[dict], b: Optional[dict]) -> Optional[float]:
    """Calculate Euclidean distance between two waypoints"""
    if not a or not b:
        return None
    try:
        ax, ay = float(a.get("x", 0)), float(a.get("y", 0))
        bx, by = float(b.get("x", 0)), float(b.get("y", 0))
        return math.hypot(ax - bx, ay - by)
    except Exception:
        return None


def format_credits(amount: int) -> str:
    """Format credits with thousands separator"""
    return f"{amount:,}"


def calculate_cargo_value(inventory: List[Dict]) -> int:
    """Calculate total value of cargo"""
    total = 0
    for item in inventory:
        units = item.get("units", 0)
        # Estimate value if available in item data
        value = item.get("purchasePrice", 0) or item.get("sellPrice", 0)
        total += units * value
    return total


# ================================
# HTTP Client
# ================================
class STClient:
    """SpaceTraders API Client with retry logic and rate limiting"""
    
    def __init__(self, token: str, timeout: int = 30):
        self.s = requests.Session()
        self.s.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        })
        self.timeout = timeout

    def _respect_rate(self, r: requests.Response):
        """Handle rate limiting"""
        try:
            remaining = int(r.headers.get("X-RateLimit-Remaining", "1"))
            reset = int(r.headers.get("X-RateLimit-Reset", "1"))
            if remaining <= 1:
                time.sleep(reset + 0.25)
        except Exception:
            pass

    def request(
        self,
        method: str,
        path: str,
        *,
        params=None,
        body: Optional[dict] = None,
        retries: int = 4
    ):
        """Make HTTP request with retry logic"""
        url = f"{BASE_URL}{path}"
        attempt = 0
        
        while True:
            try:
                payload = body if body is not None else {}
                r = self.s.request(
                    method,
                    url,
                    params=params,
                    json=payload,
                    timeout=self.timeout
                )
                self._respect_rate(r)
                
                if r.status_code in (429, 500, 502, 503, 504):
                    attempt += 1
                    if attempt > retries:
                        r.raise_for_status()
                    time.sleep(backoff(attempt))
                    continue
                    
                r.raise_for_status()
                return r.json()
                
            except requests.HTTPError as e:
                try:
                    detail = r.json()
                except Exception:
                    detail = {"error": str(e)}
                raise RuntimeError(f"HTTP {r.status_code} {method} {path}: {detail}")

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def patch(self, path, **kw):
        return self.request("PATCH", path, **kw)


# ================================
# Cached API Functions
# ================================
@st.cache_data(show_spinner=False, ttl=60)
def api_my_agent(token: str):
    """Get agent information"""
    return STClient(token).get("/my/agent")


@st.cache_data(show_spinner=False, ttl=30)
def api_my_ships(token: str, page=1, limit=20):
    """Get list of ships"""
    return STClient(token).get("/my/ships", params={"page": page, "limit": min(limit, 20)})


@st.cache_data(show_spinner=False, ttl=60)
def api_my_contracts(token: str, page=1, limit=20):
    """Get list of contracts"""
    return STClient(token).get("/my/contracts", params={"page": page, "limit": min(limit, 20)})


@st.cache_data(show_spinner=False, ttl=300)
def api_systems(token: str, page=1, limit=20):
    """Get list of systems"""
    return STClient(token).get("/systems", params={"page": page, "limit": min(limit, 20)})


@st.cache_data(show_spinner=False, ttl=300)
def api_waypoints(token: str, system_symbol: str, page=1, limit=20, traits: Optional[str] = None):
    """Get waypoints in a system"""
    params = {"page": page, "limit": min(limit, 20)}
    if traits:
        params["traits"] = traits
    return STClient(token).get(f"/systems/{system_symbol}/waypoints", params=params)


@st.cache_data(show_spinner=False, ttl=120)
def api_market(token: str, waypoint_symbol: str):
    """Get market data for a waypoint"""
    sys_sym = system_symbol_from_waypoint(waypoint_symbol)
    if not sys_sym:
        raise RuntimeError(f"Unable to determine system for waypoint {waypoint_symbol}")
    return STClient(token).get(f"/systems/{sys_sym}/waypoints/{waypoint_symbol}/market")


@st.cache_data(show_spinner=False, ttl=300)
def api_shipyard(token: str, waypoint_symbol: str):
    """Get shipyard data for a waypoint"""
    sys_sym = system_symbol_from_waypoint(waypoint_symbol)
    if not sys_sym:
        raise RuntimeError(f"Unable to determine system for waypoint {waypoint_symbol}")
    return STClient(token).get(f"/systems/{sys_sym}/waypoints/{waypoint_symbol}/shipyard")


@st.cache_data(show_spinner=False, ttl=300)
def fetch_system_waypoints(token: str, system_symbol: str, max_pages: int = 5) -> List[dict]:
    """Fetch all waypoints in a system"""
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


def logistic_summary(
    waypoints: List[dict],
    current_symbol: Optional[str] = None
) -> Dict[str, List[dict]]:
    """Generate logistics summary for waypoints"""
    symbol_map = {w.get("symbol"): w for w in waypoints if w.get("symbol")}
    current_wp = symbol_map.get(current_symbol) if current_symbol else None

    def traits_for(wp: dict) -> List[str]:
        traits = []
        for t in wp.get("traits", []) or []:
            if isinstance(t, dict):
                if t.get("symbol"):
                    traits.append(t.get("symbol"))
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
        if any(keyword in t for keyword in ("ASTEROID", "MINING")) or wp_traits.intersection({
            "COMMON_METAL_DEPOSITS", "RARE_METAL_DEPOSITS",
            "PRECIOUS_METAL_DEPOSITS", "MINERAL_DEPOSITS", "ASTEROID_FIELD"
        }):
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
# Action API Functions (Not Cached)
# ================================
def api_orbit(token, ship):
    """Put ship in orbit"""
    return STClient(token).post(f"/my/ships/{ship}/orbit", body={})


def api_dock(token, ship):
    """Dock ship at waypoint"""
    return STClient(token).post(f"/my/ships/{ship}/dock", body={})


def api_refuel(token, ship):
    """Refuel ship"""
    return STClient(token).post(f"/my/ships/{ship}/refuel", body={})


def api_nav(token, ship, wp):
    """Navigate ship to waypoint"""
    waypoint = normalize_symbol(wp)
    if not waypoint:
        raise ValueError("Waypoint symbol is required for navigation.")
    try:
        return STClient(token).post(
            f"/my/ships/{ship}/navigate",
            body={"waypointSymbol": waypoint}
        )
    except RuntimeError as err:
        message = str(err)
        if any(hint in message for hint in ("'course'", '"course"', "course.destination")):
            return STClient(token).post(
                f"/my/ships/{ship}/navigate",
                body={"course": {"destination": waypoint}}
            )
        raise


def api_nav_status(token, ship):
    """Get ship navigation status"""
    return STClient(token).get(f"/my/ships/{ship}/nav")


def api_extract(token, ship, survey=None):
    """Extract resources"""
    body = {"survey": survey} if survey else {}
    return STClient(token).post(f"/my/ships/{ship}/extract", body=body)


def api_survey(token, ship):
    """Create survey"""
    return STClient(token).post(f"/my/ships/{ship}/survey", body={})


def api_jettison(token, ship, symbol, units):
    """Jettison cargo"""
    return STClient(token).post(
        f"/my/ships/{ship}/jettison",
        body={"symbol": symbol, "units": units}
    )


def api_sell(token, ship, symbol, units):
    """Sell cargo"""
    return STClient(token).post(
        f"/my/ships/{ship}/sell",
        body={"symbol": symbol, "units": units}
    )


def api_buy(token, ship, symbol, units):
    """Buy goods"""
    return STClient(token).post(
        f"/my/ships/{ship}/purchase",
        body={"symbol": symbol, "units": units}
    )


def api_deliver(token, contract_id, ship, trade_symbol, units):
    """Deliver goods for contract"""
    return STClient(token).post(
        f"/my/contracts/{contract_id}/deliver",
        body={"shipSymbol": ship, "tradeSymbol": trade_symbol, "units": units}
    )


def api_accept_contract(token, contract_id):
    """Accept contract"""
    return STClient(token).post(f"/my/contracts/{contract_id}/accept", body={})


def api_purchase_ship(token, ship_type, shipyard_waypoint):
    """Purchase new ship"""
    return STClient(token).post(
        "/my/ships",
        body={"shipType": ship_type, "waypointSymbol": shipyard_waypoint}
    )


def api_repair_ship(token, ship):
    """Repair ship"""
    return STClient(token).post(f"/my/ships/{ship}/repair", body={})


def api_scrap_ship(token, ship):
    """Scrap ship"""
    return STClient(token).post(f"/my/ships/{ship}/scrap", body={})


def api_transfer_cargo(token, from_ship, to_ship, trade_symbol, units):
    """Transfer cargo between ships"""
    return STClient(token).post(
        f"/my/ships/{from_ship}/transfer",
        body={"tradeSymbol": trade_symbol, "units": units, "shipSymbol": to_ship}
    )


# ================================
# Session State Initialization
# ================================
if "token" not in st.session_state:
    st.session_state["token"] = None

if "mission_shortcuts" not in st.session_state:
    st.session_state["mission_shortcuts"] = {
        "mining": "",
        "delivery": "",
        "warehouse": ""
    }

if "surveys" not in st.session_state:
    st.session_state["surveys"] = {}

# ================================
# Sidebar - Authentication
# ================================
with st.sidebar:
    st.header("🔐 Authentication")
    st.caption("Paste your SpaceTraders bearer token")
    
    token_input = st.text_input(
        "Bearer Token",
        type="password",
        help="Generate via SpaceTraders website → New game"
    )
    
    col1, col2 = st.columns(2)
    
    if col1.button("Use Token", type="primary", use_container_width=True):
        if token_input:
            st.session_state["token"] = token_input
            st.cache_data.clear()
            toast_ok("Token activated")
            trigger_rerun()
        else:
            toast_warn("Please enter a token")
    
    if col2.button("Clear Token", use_container_width=True):
        st.session_state["token"] = None
        st.cache_data.clear()
        toast_ok("Token cleared")
        trigger_rerun()
    
    st.divider()
    
    if st.session_state.get("token"):
        st.success("✅ Authenticated")
        try:
            agent = api_my_agent(st.session_state["token"]).get("data", {})
            st.metric("Agent", agent.get("symbol", "Unknown"))
            st.metric("Credits", format_credits(agent.get("credits", 0)))
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠️ Not authenticated")
    
    st.divider()
    st.caption("📚 [API Docs](https://docs.spacetraders.io)")
    st.caption("💬 [Discord](https://discord.gg/spacetraders)")

token = st.session_state.get("token")

if not token:
    st.title("🚀 SpaceTraders Control Center")
    st.warning("⚠️ Please enter your SpaceTraders token in the sidebar to begin.")
    st.info("""
    ### Getting Started
    1. Visit [spacetraders.io](https://spacetraders.io)
    2. Create a new agent or get your token
    3. Paste it in the sidebar
    4. Start managing your fleet!
    """)
    st.stop()

# ================================
# Main App
# ================================
st.title("🚀 SpaceTraders Control Center")

# Initialize shortcuts in session state
for shortcut_key in ["mining", "delivery", "warehouse"]:
    state_key = f"shortcut_{shortcut_key}"
    desired_value = normalize_symbol(
        st.session_state["mission_shortcuts"].get(shortcut_key, "")
    )
    if st.session_state.get(state_key) != desired_value:
        st.session_state[state_key] = desired_value

# ================================
# Tabs
# ================================
tab_dash, tab_fleet, tab_contracts, tab_explorer, tab_markets, tab_shipyards, tab_maintenance = st.tabs([
    "📊 Dashboard",
    "🚢 Fleet",
    "📜 Contracts",
    "🗺️ Explorer",
    "💰 Markets",
    "🏗️ Shipyards",
    "🔧 Maintenance"
])

# ================================
# Dashboard Tab
# ================================
with tab_dash:
    try:
        me = api_my_agent(token).get("data", {})
        ships = api_my_ships(token).get("data", [])
        contracts = api_my_contracts(token).get("data", [])
        
        # Key Metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Agent", me.get("symbol", "Unknown"))
        col2.metric("Faction", me.get("startingFaction", "Unknown"))
        col3.metric("HQ", me.get("headquarters", "Unknown"))
        col4.metric("Credits", format_credits(me.get("credits", 0)))
        col5.metric("Fleet Size", len(ships))
        
        # Fleet Status
        st.subheader("Fleet Status")
        statuses = Counter([s.get("nav", {}).get("status", "UNKNOWN") for s in ships])
        
        col6, col7, col8, col9 = st.columns(4)
        col6.metric("In Transit", statuses.get("IN_TRANSIT", 0))
        col7.metric("Docked", statuses.get("DOCKED", 0))
        col8.metric("In Orbit", statuses.get("IN_ORBIT", 0))
        col9.metric("Other", sum(statuses.values()) - statuses.get("IN_TRANSIT", 0) - 
                   statuses.get("DOCKED", 0) - statuses.get("IN_ORBIT", 0))
        
        # Contract Status
        st.subheader("Contract Status")
        active_contracts = sum(1 for c in contracts if c.get("accepted") and not c.get("fulfilled"))
        pending_contracts = sum(1 for c in contracts if not c.get("accepted"))
        fulfilled_contracts = sum(1 for c in contracts if c.get("fulfilled"))
        
        col10, col11, col12 = st.columns(3)
        col10.metric("Active", active_contracts)
        col11.metric("Pending", pending_contracts)
        col12.metric("Fulfilled", fulfilled_contracts)
        
        # Fleet Composition
        if ships:
            st.subheader("Fleet Composition")
            roles = Counter([s.get("registration", {}).get("role", "UNSPEC") for s in ships])
            
            col_chart, col_table = st.columns([2, 1])
            
            with col_chart:
                fig = go.Figure()
                fig.add_trace(go.Pie(
                    labels=list(roles.keys()),
                    values=list(roles.values()),
                    hole=0.4
                ))
                fig.update_layout(
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                    title="Ships by Role"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col_table:
                role_df = pd.DataFrame([
                    {"Role": role, "Count": count}
                    for role, count in roles.most_common()
                ])
                st.dataframe(role_df, hide_index=True, use_container_width=True)
            
            # Cargo Utilization
            st.subheader("Cargo Utilization")
            cargo_data = []
            for ship in ships:
                cargo = ship.get("cargo", {})
                capacity = cargo.get("capacity", 0)
                used = cargo.get("units", 0)
                percent = round((used / capacity) * 100, 1) if capacity else 0
                
                cargo_data.append({
                    "Ship": ship.get("symbol"),
                    "Role": ship.get("registration", {}).get("role"),
                    "Location": ship.get("nav", {}).get("waypointSymbol"),
                    "Status": ship.get("nav", {}).get("status"),
                    "Used": used,
                    "Capacity": capacity,
                    "Fill %": percent,
                })
            
            st.dataframe(
                pd.DataFrame(cargo_data),
                hide_index=True,
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        toast_err(str(e))

# ================================
# Fleet Tab
# ================================
with tab_fleet:
    st.subheader("Fleet Management")
    
    try:
        fleet = api_my_ships(token).get("data", [])
        shortcuts = st.session_state.get("mission_shortcuts", {})
        
        # Mission Shortcuts
        st.markdown("### 🎯 Mission Shortcuts")
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        col1.text_input("Mining Waypoint", key="shortcut_mining")
        col2.text_input("Delivery Waypoint", key="shortcut_delivery")
        col3.text_input("Warehouse/Shipyard", key="shortcut_warehouse")
        
        if col4.button("💾 Save", use_container_width=True):
            shortcuts["mining"] = normalize_symbol(st.session_state.get("shortcut_mining", ""))
            shortcuts["delivery"] = normalize_symbol(st.session_state.get("shortcut_delivery", ""))
            shortcuts["warehouse"] = normalize_symbol(st.session_state.get("shortcut_warehouse", ""))
            toast_ok("Mission shortcuts updated")
        
        st.caption("Set quick navigation targets for common operations")
        
        st.divider()
        
        if not fleet:
            st.info("No ships found in your fleet.")
        else:
            # Filters
            st.markdown("### 🔍 Filters")
            col_f1, col_f2, col_f3, col_f4 = st.columns([2, 2, 2, 1])
            
            search_term = col_f1.text_input("Search", placeholder="Ship symbol or location")
            
            roles_available = sorted({
                ship.get("registration", {}).get("role", "UNSPEC")
                for ship in fleet
            })
            role_filter = col_f2.multiselect("Roles", roles_available, default=roles_available)
            
            statuses_available = sorted({
                ship.get("nav", {}).get("status", "UNKNOWN")
                for ship in fleet
            })
            status_filter = col_f3.multiselect("Status", statuses_available, default=statuses_available)
            
            if col_f4.button("🔄 Refresh", use_container_width=True):
                st.cache_data.clear()
                trigger_rerun()
            
            # Filter ships
            filtered = []
            for ship in fleet:
                role = ship.get("registration", {}).get("role", "UNSPEC")
                status = ship.get("nav", {}).get("status", "UNKNOWN")
                text_blob = f"{ship.get('symbol', '')} {ship.get('nav', {}).get('waypointSymbol', '')}".lower()
                
                if role_filter and role not in role_filter:
                    continue
                if status_filter and status not in status_filter:
                    continue
                if search_term and search_term.lower() not in text_blob:
                    continue
                    
                filtered.append(ship)
            
            st.caption(f"Showing {len(filtered)} of {len(fleet)} ships")
            
            # Ship Cards
            for ship in filtered:
                sym = ship.get("symbol")
                
                with st.expander(f"🚢 {sym} — {ship.get('registration', {}).get('role', '?')}"):
                    nav = ship.get("nav", {})
                    fuel = ship.get("fuel", {})
                    cargo = ship.get("cargo", {})
                    
                    # Ship Info
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Status", nav.get("status", "UNKNOWN"))
                    col2.metric("Location", nav.get("waypointSymbol", "UNKNOWN"))
                    col3.metric("Fuel", f"{fuel.get('current', 0)}/{fuel.get('capacity', 0)}")
                    col4.metric("Speed", ship.get("engine", {}).get("speed", "?"))
                    
                    # Travel Progress
                    progress = travel_progress(nav)
                    if progress.get("fraction") is not None:
                        st.progress(
                            progress["fraction"],
                            text=f"En route — ETA {progress['eta']}"
                        )
                    elif nav.get("status") == "IN_ORBIT":
                        st.info("Ship is in orbit and ready for operations")
                    elif nav.get("status") == "DOCKED":
                        st.info("Ship is docked. Orbit before navigating or extracting")
                    
                    # Cargo
                    cap = cargo.get("capacity", 0)
                    used = cargo.get("units", 0)
                    st.progress(
                        min(1.0, used / cap) if cap else 0.0,
                        text=f"Cargo: {used}/{cap} units ({max(0, cap - used)} free)"
                    )
                    
                    inv = cargo.get("inventory", [])
                    if inv:
                        st.dataframe(
                            pd.DataFrame(inv),
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.caption("Empty cargo hold")
                    
                    st.divider()
                    
                    # Ship Controls
                    st.markdown("#### Controls")
                    
                    col_c1, col_c2, col_c3, col_c4, col_c5, col_c6 = st.columns(6)
                    
                    if col_c1.button("🛸 Orbit", key=f"o_{sym}", use_container_width=True):
                        try:
                            api_orbit(token, sym)
                            toast_ok("Ship in orbit")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    if col_c2.button("🏠 Dock", key=f"d_{sym}", use_container_width=True):
                        try:
                            api_dock(token, sym)
                            toast_ok("Ship docked")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    if col_c3.button("⛽ Refuel", key=f"r_{sym}", use_container_width=True):
                        try:
                            api_refuel(token, sym)
                            toast_ok("Ship refueled")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    if col_c4.button("⛏️ Extract", key=f"x_{sym}", use_container_width=True):
                        try:
                            resp = api_extract(token, sym)
                            extracted = resp.get("data", {}).get("extraction", {}).get("yield", {})
                            toast_ok(
                                f"Extracted {extracted.get('units', 0)} " +
                                f"{extracted.get('symbol', '?')}"
                            )
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                            cooldown = parse_cooldown_seconds(str(e))
                            st.info(f"⏳ Cooldown: wait ~{cooldown}s")
                    
                    if col_c5.button("📊 Survey", key=f"survey_{sym}", use_container_width=True):
                        try:
                            survey_resp = api_survey(token, sym)
                            surveys = survey_resp.get("data", {}).get("surveys", [])
                            if surveys:
                                if sym not in st.session_state["surveys"]:
                                    st.session_state["surveys"][sym] = []
                                st.session_state["surveys"][sym].extend(surveys)
                                toast_ok(f"Created {len(surveys)} surveys")
                            else:
                                toast_warn("No surveys returned")
                        except Exception as e:
                            toast_err(str(e))
                    
                    if col_c6.button("🔄 Sync", key=f"sync_{sym}", use_container_width=True):
                        try:
                            api_nav_status(token, sym)
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    # Navigation
                    st.markdown("#### Navigation")
                    col_n1, col_n2 = st.columns([3, 1])
                    
                    dest_input = col_n1.text_input(
                        "Destination Waypoint",
                        value=nav.get("waypointSymbol", ""),
                        key=f"wp_{sym}"
                    )
                    
                    if col_n2.button("🗺️ Navigate", key=f"n_{sym}", use_container_width=True):
                        dest_normalized = normalize_symbol(dest_input)
                        if not dest_normalized:
                            toast_warn("Enter a waypoint symbol")
                        else:
                            try:
                                api_nav(token, sym, dest_normalized)
                                toast_ok(f"Navigating to {dest_normalized}")
                                st.cache_data.clear()
                                trigger_rerun()
                            except Exception as e:
                                toast_err(str(e))
                    
                    # Quick Navigation
                    if any([shortcuts.get("mining"), shortcuts.get("delivery"), shortcuts.get("warehouse")]):
                        st.markdown("#### Quick Navigation")
                        qc1, qc2, qc3 = st.columns(3)
                        
                        if shortcuts.get("mining"):
                            if qc1.button(
                                f"⛏️ Mine ({shortcuts['mining']})",
                                key=f"quick_mine_{sym}",
                                use_container_width=True
                            ):
                                try:
                                    api_nav(token, sym, shortcuts["mining"])
                                    toast_ok(f"Heading to {shortcuts['mining']}")
                                    st.cache_data.clear()
                                    trigger_rerun()
                                except Exception as e:
                                    toast_err(str(e))
                        
                        if shortcuts.get("delivery"):
                            if qc2.button(
                                f"📦 Deliver ({shortcuts['delivery']})",
                                key=f"quick_deliver_{sym}",
                                use_container_width=True
                            ):
                                try:
                                    api_nav(token, sym, shortcuts["delivery"])
                                    toast_ok(f"Heading to {shortcuts['delivery']}")
                                    st.cache_data.clear()
                                    trigger_rerun()
                                except Exception as e:
                                    toast_err(str(e))
                        
                        if shortcuts.get("warehouse"):
                            if qc3.button(
                                f"🏭 Warehouse ({shortcuts['warehouse']})",
                                key=f"quick_warehouse_{sym}",
                                use_container_width=True
                            ):
                                try:
                                    api_nav(token, sym, shortcuts["warehouse"])
                                    toast_ok(f"Heading to {shortcuts['warehouse']}")
                                    st.cache_data.clear()
                                    trigger_rerun()
                                except Exception as e:
                                    toast_err(str(e))
                    
                    # Cargo Operations
                    st.markdown("#### Cargo Operations")
                    col_co1, col_co2, col_co3 = st.columns(3)
                    
                    item_symbol = col_co1.text_input("Item Symbol", key=f"item_{sym}")
                    item_units = col_co2.number_input(
                        "Units",
                        min_value=1,
                        value=1,
                        step=1,
                        key=f"units_{sym}"
                    )
                    
                    col_btn1, col_btn2, col_btn3 = col_co3.columns(3)
                    
                    if col_btn1.button("💰 Sell", key=f"sell_{sym}"):
                        try:
                            api_sell(token, sym, item_symbol, int(item_units))
                            toast_ok("Sold")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    if col_btn2.button("🛒 Buy", key=f"buy_{sym}"):
                        try:
                            api_buy(token, sym, item_symbol, int(item_units))
                            toast_ok("Purchased")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    if col_btn3.button("🗑️ Jettison", key=f"jet_{sym}"):
                        try:
                            api_jettison(token, sym, item_symbol, int(item_units))
                            toast_ok("Jettisoned")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                    
                    # Surveys
                    available_surveys = st.session_state["surveys"].get(sym, [])
                    if available_surveys:
                        with st.expander("📊 Stored Surveys"):
                            for idx, survey in enumerate(available_surveys):
                                expires = parse_ts(survey.get("expiration"))
                                if expires:
                                    expires_in = humanize_timedelta(
                                        (expires - datetime.now(timezone.utc)).total_seconds()
                                    )
                                else:
                                    expires_in = "Unknown"
                                
                                st.write(f"Survey {idx + 1} — expires in {expires_in}")
                                st.json(survey)
                                
                                if st.button("Use Survey", key=f"use_survey_{sym}_{idx}"):
                                    try:
                                        api_extract(token, sym, survey)
                                        toast_ok("Extraction started with survey")
                                        st.cache_data.clear()
                                        st.session_state["surveys"][sym].pop(idx)
                                        trigger_rerun()
                                    except Exception as e:
                                        toast_err(str(e))
                    
                    # Route Planner
                    system_symbol = nav.get("systemSymbol")
                    if system_symbol:
                        with st.expander("📍 Route Planner"):
                            try:
                                system_waypoints = fetch_system_waypoints(token, system_symbol)
                                logistics = logistic_summary(
                                    system_waypoints,
                                    nav.get("waypointSymbol")
                                )
                                
                                for section_name, entries in logistics.items():
                                    if not entries:
                                        continue
                                    
                                    st.markdown(f"**{section_name}**")
                                    df = pd.DataFrame(entries)
                                    st.dataframe(df, hide_index=True, use_container_width=True)
                                    
                            except Exception as e:
                                st.error(f"Error loading route planner: {str(e)}")
                    
    except Exception as e:
        st.error(f"Error loading fleet: {str(e)}")
        toast_err(str(e))

# ================================
# Contracts Tab
# ================================
with tab_contracts:
    st.subheader("Contract Management")
    
    try:
        contracts = api_my_contracts(token).get("data", [])
        
        if not contracts:
            st.info("No contracts available")
        else:
            for contract in contracts:
                cid = contract.get("id")
                accepted = contract.get("accepted")
                fulfilled = contract.get("fulfilled")
                terms = contract.get("terms", {})
                
                status_icon = "✅" if fulfilled else ("🔄" if accepted else "❗")
                
                with st.expander(f"{status_icon} {cid}"):
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Type", contract.get("type", "Unknown"))
                    col2.metric("Accepted", "Yes" if accepted else "No")
                    col3.metric("Fulfilled", "Yes" if fulfilled else "No")
                    
                    deadline = parse_ts(terms.get("deadline"))
                    if deadline:
                        time_left = humanize_timedelta(
                            (deadline - datetime.now(timezone.utc)).total_seconds()
                        )
                        st.info(f"⏰ Time remaining: {time_left}")
                    
                    # Payment info
                    payment = terms.get("payment", {})
                    st.write(f"**Payment on Accept**: {format_credits(payment.get('onAccepted', 0))} credits")
                    st.write(f"**Payment on Fulfill**: {format_credits(payment.get('onFulfilled', 0))} credits")
                    
                    # Deliverables
                    deliver = terms.get("deliver", [])
                    if deliver:
                        st.markdown("#### Deliverables")
                        
                        for deliver_item in deliver:
                            required = deliver_item.get("unitsRequired", 0)
                            fulfilled_units = deliver_item.get("unitsFulfilled", 0)
                            destination = deliver_item.get("destinationSymbol", "?")
                            symbol = deliver_item.get("tradeSymbol", "?")
                            
                            progress_frac = (fulfilled_units / required) if required else 0
                            
                            st.progress(
                                progress_frac,
                                text=f"{symbol} to {destination} — {fulfilled_units}/{required} units"
                            )
                        
                        # Delivery table
                        df = pd.DataFrame(deliver)
                        st.dataframe(df, hide_index=True, use_container_width=True)
                    
                    # Actions
                    st.divider()
                    
                    if not accepted:
                        if st.button(f"✅ Accept Contract", key=f"accept_{cid}"):
                            try:
                                api_accept_contract(token, cid)
                                toast_ok("Contract accepted")
                                st.cache_data.clear()
                                trigger_rerun()
                            except Exception as e:
                                toast_err(str(e))
                    
                    if accepted and not fulfilled:
                        st.markdown("#### Quick Delivery")
                        
                        ships = api_my_ships(token).get("data", [])
                        ship_opts = [s["symbol"] for s in ships]
                        
                        col_d1, col_d2, col_d3, col_d4 = st.columns(4)
                        
                        ship_sel = col_d1.selectbox("Ship", ship_opts, key=f"del_ship_{cid}")
                        trade_sym = col_d2.text_input("Trade Symbol", key=f"del_trade_{cid}")
                        qty = col_d3.number_input("Units", min_value=1, value=1, key=f"del_qty_{cid}")
                        
                        if col_d4.button("📦 Deliver", key=f"del_btn_{cid}", use_container_width=True):
                            try:
                                api_deliver(token, cid, ship_sel, trade_sym, int(qty))
                                toast_ok("Delivered successfully")
                                st.cache_data.clear()
                                trigger_rerun()
                            except Exception as e:
                                toast_err(str(e))
                    
    except Exception as e:
        st.error(f"Error loading contracts: {str(e)}")
        toast_err(str(e))

# ================================
# Explorer Tab
# ================================
with tab_explorer:
    st.subheader("System Explorer")
    
    try:
        ships = api_my_ships(token).get("data", [])
        default_system = ships[0]["nav"]["systemSymbol"] if ships else "X1-RV7"
        
        col1, col2, col3, col4 = st.columns(4)
        
        sys_sym = col1.text_input("System Symbol", value=default_system)
        traits_filter = col2.text_input("Traits Filter (comma-separated)", placeholder="MARKETPLACE,SHIPYARD")
        page = col3.number_input("Page", min_value=1, value=1, step=1)
        
        if col4.button("🔍 Load Waypoints", use_container_width=True):
            trait_param = None
            if traits_filter.strip():
                trait_param = ",".join([t.strip() for t in traits_filter.split(",") if t.strip()])
            
            st.session_state["wps"] = api_waypoints(
                token,
                sys_sym,
                page=page,
                limit=20,
                traits=trait_param
            )
        
        wps_resp = st.session_state.get("wps", {})
        waypoints = wps_resp.get("data", [])
        
        if waypoints:
            st.success(f"Found {len(waypoints)} waypoints")
            
            # Display table
            df = pd.DataFrame(waypoints)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Statistics
            col_stat1, col_stat2 = st.columns(2)
            
            with col_stat1:
                st.markdown("#### Waypoint Types")
                type_counts = Counter(df.get("type", []))
                type_df = pd.DataFrame([
                    {"Type": t, "Count": c}
                    for t, c in type_counts.most_common()
                ])
                
                fig = px.bar(type_df, x="Type", y="Count", title="Waypoint Types")
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col_stat2:
                st.markdown("#### Traits")
                trait_counts = Counter()
                for wp in waypoints:
                    for trait in wp.get("traits", []):
                        name = trait.get("symbol") if isinstance(trait, dict) else trait
                        if name:
                            trait_counts[name] += 1
                
                trait_df = pd.DataFrame([
                    {"Trait": t, "Count": c}
                    for t, c in trait_counts.most_common(10)
                ])
                st.dataframe(trait_df, hide_index=True, use_container_width=True)
            
            # Map visualization
            st.markdown("#### System Map")
            
            xs = [w.get("x", 0) for w in waypoints]
            ys = [w.get("y", 0) for w in waypoints]
            labels = [w.get("symbol", "?") for w in waypoints]
            types = [w.get("type", "?") for w in waypoints]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                text=[f"{l}\n({t})" for l, t in zip(labels, types)],
                textposition="top center",
                marker=dict(size=10, opacity=0.7),
                hovertext=[f"{l} - {t}" for l, t in zip(labels, types)]
            ))
            
            fig.update_layout(
                height=500,
                title=f"Waypoints in {sys_sym}",
                xaxis_title="X",
                yaxis_title="Y",
                hovermode="closest"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Download
            st.download_button(
                "📥 Download Waypoints JSON",
                data=json.dumps(waypoints, indent=2),
                file_name=f"{sys_sym}_waypoints.json",
                mime="application/json"
            )
            
    except Exception as e:
        st.error(f"Error loading waypoints: {str(e)}")
        toast_err(str(e))

# ================================
# Markets Tab
# ================================
with tab_markets:
    st.subheader("Market Data")
    
    col1, col2 = st.columns([3, 1])
    
    wp = col1.text_input("Market Waypoint Symbol", placeholder="X1-ABC-DEF")
    
    if col2.button("📊 Load Market", use_container_width=True) and wp:
        try:
            market_data = api_market(token, wp).get("data", {})
            st.session_state["market_data"] = market_data
        except Exception as e:
            st.error(f"Error loading market: {str(e)}")
            toast_err(str(e))
    
    market_data = st.session_state.get("market_data")
    
    if market_data:
        st.success(f"Market at {market_data.get('symbol', '?')}")
        
        # Trade goods
        trade_goods = market_data.get("tradeGoods", [])
        
        if trade_goods:
            st.markdown("### Trade Goods")
            
            df = pd.DataFrame(trade_goods)
            
            # Add profit potential column
            if "purchasePrice" in df.columns and "sellPrice" in df.columns:
                df["Profit Margin"] = df["sellPrice"] - df["purchasePrice"]
                df["Profit %"] = ((df["sellPrice"] - df["purchasePrice"]) / df["purchasePrice"] * 100).round(2)
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Market analysis
            col_m1, col_m2, col_m3 = st.columns(3)
            
            exports = df[df.get("type") == "EXPORT"] if "type" in df.columns else pd.DataFrame()
            imports = df[df.get("type") == "IMPORT"] if "type" in df.columns else pd.DataFrame()
            exchanges = df[df.get("type") == "EXCHANGE"] if "type" in df.columns else pd.DataFrame()
            
            if not exports.empty and "sellPrice" in exports.columns:
                best_export = exports.nlargest(1, "sellPrice").iloc[0]
                col_m1.metric(
                    "Best Export Sale",
                    best_export["symbol"],
                    f"{format_credits(int(best_export['sellPrice']))} credits"
                )
            
            if not imports.empty and "purchasePrice" in imports.columns:
                best_import = imports.nsmallest(1, "purchasePrice").iloc[0]
                col_m2.metric(
                    "Cheapest Import",
                    best_import["symbol"],
                    f"{format_credits(int(best_import['purchasePrice']))} credits"
                )
            
            if not exchanges.empty:
                col_m3.metric(
                    "Exchange Goods",
                    len(exchanges),
                    f"{exchanges.iloc[0]['symbol'] if len(exchanges) > 0 else '?'}"
                )
            
            # Price charts
            if not df.empty and "sellPrice" in df.columns and "purchasePrice" in df.columns:
                st.markdown("### Price Comparison")
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    name="Sell Price",
                    x=df["symbol"],
                    y=df["sellPrice"]
                ))
                fig.add_trace(go.Bar(
                    name="Purchase Price",
                    x=df["symbol"],
                    y=df["purchasePrice"]
                ))
                
                fig.update_layout(
                    barmode="group",
                    height=400,
                    title="Market Prices",
                    xaxis_title="Good",
                    yaxis_title="Price (credits)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Download
            st.download_button(
                "📥 Download Market Data",
                data=json.dumps(market_data, indent=2),
                file_name=f"{wp}_market.json",
                mime="application/json"
            )
        else:
            st.info("No trade goods available at this market")
        
        # Transactions
        transactions = market_data.get("transactions", [])
        if transactions:
            with st.expander("Recent Transactions"):
                st.dataframe(
                    pd.DataFrame(transactions),
                    use_container_width=True,
                    hide_index=True
                )

# ================================
# Shipyards Tab
# ================================
with tab_shipyards:
    st.subheader("Shipyard Browser")
    
    # Find shipyards
    col1, col2 = st.columns([3, 1])
    
    sys_search = col1.text_input("System to Search", value="X1-RV7")
    
    if col2.button("🔍 Find Shipyards", use_container_width=True):
        try:
            yards = api_waypoints(
                token,
                sys_search,
                page=1,
                limit=20,
                traits="SHIPYARD"
            ).get("data", [])
            st.session_state["shipyards"] = yards
        except Exception as e:
            st.error(f"Error finding shipyards: {str(e)}")
            toast_err(str(e))
    
    shipyards = st.session_state.get("shipyards", [])
    
    if shipyards:
        st.success(f"Found {len(shipyards)} shipyards")
        st.dataframe(
            pd.DataFrame(shipyards),
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    # View specific shipyard
    col_y1, col_y2 = st.columns([3, 1])
    
    yard_wp = col_y1.text_input("Shipyard Waypoint")
    
    if col_y2.button("📋 View Shipyard", use_container_width=True) and yard_wp:
        try:
            yard_data = api_shipyard(token, yard_wp).get("data", {})
            st.session_state["yard_data"] = yard_data
        except Exception as e:
            st.error(f"Error loading shipyard: {str(e)}")
            toast_err(str(e))
    
    yard_data = st.session_state.get("yard_data")
    
    if yard_data:
        st.success(f"Shipyard at {yard_data.get('symbol', '?')}")
        
        # Available ships
        ships_available = yard_data.get("ships", [])
        
        if ships_available:
            st.markdown("### Available Ships")
            
            df = pd.DataFrame(ships_available)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Purchase interface
            st.markdown("### Purchase Ship")
            
            col_p1, col_p2 = st.columns([3, 1])
            
            ship_type = col_p1.selectbox(
                "Ship Type",
                [s.get("type") for s in ships_available]
            )
            
            if col_p2.button("🛒 Purchase", use_container_width=True):
                try:
                    result = api_purchase_ship(token, ship_type, yard_wp)
                    toast_ok(f"Purchased {ship_type}")
                    st.cache_data.clear()
                    trigger_rerun()
                except Exception as e:
                    st.error(f"Error purchasing ship: {str(e)}")
                    toast_err(str(e))
        else:
            st.info("No ships currently available")
        
        # Transactions
        transactions = yard_data.get("transactions", [])
        if transactions:
            with st.expander("Recent Transactions"):
                st.dataframe(
                    pd.DataFrame(transactions),
                    use_container_width=True,
                    hide_index=True
                )

# ================================
# Maintenance Tab
# ================================
with tab_maintenance:
    st.subheader("Ship Maintenance & Outfitting")
    
    try:
        ships = api_my_ships(token).get("data", [])
        
        if not ships:
            st.info("No ships available")
        else:
            ship_opts = [s["symbol"] for s in ships]
            ship_sel = st.selectbox("Select Ship", ship_opts)
            
            ship_data = next((s for s in ships if s.get("symbol") == ship_sel), {})
            
            if ship_data:
                # Ship Info
                col1, col2, col3, col4 = st.columns(4)
                
                col1.metric("Frame", ship_data.get("frame", {}).get("name", "?"))
                col2.metric("Reactor", ship_data.get("reactor", {}).get("name", "?"))
                col3.metric("Engine", ship_data.get("engine", {}).get("name", "?"))
                col4.metric("Crew", f"{ship_data.get('crew', {}).get('current', 0)}/{ship_data.get('crew', {}).get('capacity', 0)}")
                
                st.divider()
                
                # Maintenance Actions
                st.markdown("### Maintenance")
                
                col_m1, col_m2, col_m3 = st.columns(3)
                
                if col_m1.button("🔧 Repair Ship", use_container_width=True):
                    try:
                        api_repair_ship(token, ship_sel)
                        toast_ok("Ship repaired")
                        st.cache_data.clear()
                        trigger_rerun()
                    except Exception as e:
                        toast_err(str(e))
                
                if col_m2.button("♻️ Scrap Ship", type="secondary", use_container_width=True):
                    if st.checkbox("Confirm scrap", key=f"confirm_scrap_{ship_sel}"):
                        try:
                            api_scrap_ship(token, ship_sel)
                            toast_ok("Ship scrapped")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                
                st.divider()
                
                # Modules
                st.markdown("### Modules")
                modules = ship_data.get("modules", [])
                
                if modules:
                    st.dataframe(
                        pd.DataFrame(modules),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.caption("No modules equipped")
                
                # Mounts
                st.markdown("### Mounts")
                mounts = ship_data.get("mounts", [])
                
                if mounts:
                    st.dataframe(
                        pd.DataFrame(mounts),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.caption("No mounts equipped")
                
                # Cargo Transfer
                st.markdown("### Cargo Transfer")
                
                other_ships = [s for s in ship_opts if s != ship_sel]
                
                if other_ships:
                    col_t1, col_t2, col_t3, col_t4 = st.columns(4)
                    
                    target_ship = col_t1.selectbox("Target Ship", other_ships)
                    transfer_symbol = col_t2.text_input("Good Symbol")
                    transfer_units = col_t3.number_input("Units", min_value=1, value=1)
                    
                    if col_t4.button("📦 Transfer", use_container_width=True):
                        try:
                            api_transfer_cargo(
                                token,
                                ship_sel,
                                target_ship,
                                transfer_symbol,
                                int(transfer_units)
                            )
                            toast_ok("Cargo transferred")
                            st.cache_data.clear()
                            trigger_rerun()
                        except Exception as e:
                            toast_err(str(e))
                else:
                    st.info("Need at least 2 ships for cargo transfer")
                
    except Exception as e:
        st.error(f"Error loading maintenance: {str(e)}")
        toast_err(str(e))

# ================================
# Footer
# ================================
st.divider()
st.caption("🚀 SpaceTraders Control Center | [Documentation](https://docs.spacetraders.io) | [Discord](https://discord.gg/spacetraders)")
