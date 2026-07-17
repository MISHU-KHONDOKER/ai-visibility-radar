# 🔬 HEIDSTAR Dashboard — How to Access

## Start it

Run from the project root (PowerShell). Activate the venv, then launch:
```powershell
.\venv\Scripts\Activate.ps1
streamlit run dashboard.py
```

Or as a one-liner without activating the venv:
```powershell
.\venv\Scripts\streamlit.exe run dashboard.py
```

Your browser opens at http://localhost:8501. Press **Ctrl+C** in the terminal to stop.
(Watch the terminal — it prints the Local + Network URLs and the actual port.)

### For the "Live Engine Runs" buttons (Measurement / Customer Search / Procurement)
These call DeepSeek/Qwen. If your network needs an outbound proxy to reach them,
launch with the proxy set so those subprocesses can connect:
```powershell
$env:HTTPS_PROXY="http://PROXY_HOST:PROXY_PORT"; $env:HTTP_PROXY="http://PROXY_HOST:PROXY_PORT"
.\venv\Scripts\streamlit.exe run dashboard.py
```
(The read-only views — scorecard, competitors, cost charts — work fine without the proxy.)

## Open it

| From | URL |
|---|---|
| **This computer** | http://localhost:8501 |
| **Other devices on the same Wi-Fi/LAN** | http://YOUR-LAN-IP:8501 |

- Port is **8501** by default. If it's busy, Streamlit uses 8502/8503… (check the terminal).
- Force a port: `streamlit run dashboard.py --server.port 8501`

## Login
Password-gated — enter the password from `config/config.ini` → `[dashboard] password`.

## If other devices can't connect
It's almost always **Windows Firewall** → allow inbound TCP port **8501** (or allow Python/Streamlit through the firewall).

---
*`YOUR-LAN-IP` is this PC's private LAN address (only reachable inside your local network, not the public internet). Find it with `ipconfig` (Windows) or `ifconfig`/`ip addr` (macOS/Linux).*
