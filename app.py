import os, json, time, re
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
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Agent", me.get("symbol"))
        c2.metric("Faction", me.get("startingFaction"))
        c3.metric("HQ", me.get("headquarters"))
        c4.metric("Credits", f"{me.get('credits',0):,}")
        c5.metric("Fleet Size", len(ships))
        st.caption("SpaceTraders is a programmable API game — automate everything you see here. (Docs home) ")
        st.caption("Quickstart: new game → first mission → purchase ship → mine → sell → deliver.")
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
        if not fleet:
            st.info("No ships found.")
        for ship in fleet:
            sym = ship.get("symbol")
            with st.expander(f"🚢 {sym} — {ship.get('registration',{}).get('role','?')}"):
                nav = ship.get("nav", {})
                fuel = ship.get("fuel", {})
                cargo = ship.get("cargo", {})
                c1, c2, c3, c4 = st.columns(4)
                c1.write(f"**Status**: {nav.get('status')}")
                c2.write(f"**At**: {nav.get('waypointSymbol')}")
                c3.write(f"**Fuel**: {fuel.get('current',0)}/{fuel.get('capacity',0)}")
                c4.write(f"**Engine**: {ship.get('engine',{}).get('name','?')}")

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
                c3.write(f"**Deadline**: {terms.get('deadline')}")
                deliver = terms.get("deliver", [])
                if deliver:
                    df = pd.DataFrame(deliver)
                    st.dataframe(df, hide_index=True, use_container_width=True)
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
            st.dataframe(pd.DataFrame(waypoints), use_container_width=True, hide_index=True)
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
                st.dataframe(pd.DataFrame(mk["tradeGoods"]), use_container_width=True, hide_index=True)
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
        st.caption("More mount/module swap endpoints can be wired similarly at shipyards (see outfitting docs).")
