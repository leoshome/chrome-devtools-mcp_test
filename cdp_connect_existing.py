# -*- coding: utf-8 -*-
"""
cdp_connect_existing.py
=======================
Connects to an already running Chrome instance without launching chrome.exe.

[Prerequisites (one-time setup)]
  Enter the following in Chrome's address bar:  chrome://inspect/#remote-debugging
  Turn on the Remote Debugging toggle.
  Chrome will display an Allow authorization dialog → click Allow.
  This will create the DevToolsActivePort file for us to connect to.

Dependencies:
  pip install websocket-client
"""

import os
import json
import time
import websocket

TARGET_URL = "https://www.youtube.com"

class CDPSession:
    """
    Synchronous CDP WebSocket Session.
    Supports root Browser Endpoint connections and Target Flattening (via sessionId routing).
    """

    def __init__(self, ws_url: str):
        # Create WebSocket connection, using suppress_origin=True to bypass Chrome 111+'s 403 blocking
        self._ws = websocket.create_connection(
            ws_url,
            timeout=10,
            suppress_origin=True
        )
        self._id = 0

    def send(self, method: str, params: dict | None = None, session_id: str | None = None) -> dict:
        """
        Sends a CDP command and waits for the corresponding response.
        If a session_id is specified, the command will be wrapped and routed to the specific target (Target Flattening).
        """
        self._id += 1
        cmd = {"id": self._id, "method": method, "params": params or {}}
        if session_id:
            cmd["sessionId"] = session_id
            
        self._ws.send(json.dumps(cmd))
        
        # Keep reading until we receive a response with the matching id
        while True:
            msg = json.loads(self._ws.recv())
            # Sometimes Chrome returns events; we only wait for the response matching our message id
            if msg.get("id") == self._id:
                return msg

    def close(self):
        self._ws.close()

def get_browser_ws_url() -> str:
    """
    Parses the Browser WebSocket URL from Chrome's DevToolsActivePort file.

    [Corresponds to chrome-devtools-mcp logic]
    MCP source: src/browser.ts → ensureBrowserConnected()
      const portPath = path.join(userDataDir, 'DevToolsActivePort');
      const fileContent = await fs.promises.readFile(portPath, 'utf8');
      const [rawPort, rawPath] = fileContent.split('\n').map(line => line.trim());
      const browserWSEndpoint = `ws://127.0.0.1:${port}${rawPath}`;

    [DevToolsActivePort file format] (automatically written by Chrome when --remote-debugging-port=0)
      Line 1: Dynamically assigned TCP port number (e.g. 49152)
      Line 2: WebSocket Path (e.g. /devtools/browser/abc123-...)

    Returns:
        str: Complete WebSocket URL (e.g. ws://127.0.0.1:49152/devtools/browser/abc123-...)
    Raises:
        Exception: LOCALAPPDATA not found, file does not exist, or incorrect format (less than two lines)
    """
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise Exception("LOCALAPPDATA environment variable not found, cannot locate Chrome profile")
        
    port_file = os.path.join(local_app_data, "Google", "Chrome", "User Data", "DevToolsActivePort")
    
    if not os.path.exists(port_file):
        print(f"[ERR] Cannot find {port_file}")
        print("      Please ensure Chrome is running and Remote Debugging is enabled at chrome://inspect.")
        raise SystemExit(1)
        
    with open(port_file, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        
    if len(lines) < 2:
        raise Exception("DevToolsActivePort format is incorrect")
        
    port = lines[0]
    browser_path = lines[1]
    return f"ws://127.0.0.1:{port}{browser_path}"

def main():
    print("=" * 60)
    print("  Pure CDP — Connecting to running Chrome (equivalent to MCP --autoConnect)")
    print("=" * 60)

    # A. Get WS URL and connect
    print("\n[A] Attempting to read DevToolsActivePort and establish Browser connection...")
    try:
        ws_url = get_browser_ws_url()
    except Exception as e:
        print(f"[ERR] {e}")
        raise SystemExit(1)
        
    print(f"    Browser WS URL: {ws_url}")
    cdp = CDPSession(ws_url)
    print("    WebSocket Browser connection successful!")

    # B. List existing tabs
    print("\n[B] Listing all tabs (equivalent to MCP list_pages tool)")
    res = cdp.send("Target.getTargets")
    targets = res.get("result", {}).get("targetInfos", [])
    pages = [t for t in targets if t.get("type") == "page"]
    
    if pages:
        for i, p in enumerate(pages):
            print(f"    [{i}] {p.get('title', '(blank)')[:50]}")
            print(f"         {p.get('url', '')[:60]}")
    else:
        print("    (No tabs currently open)")

    # C. Get or create target tab
    print("\n[C] Acquiring target tab and establishing Target Session...")
    if pages:
        target_id = pages[0]["targetId"]
        print(f"    [Tab] Using existing tab: '{pages[0].get('title', '(blank)')}'")
    else:
        res = cdp.send("Target.createTarget", {"url": "about:blank"})
        target_id = res.get("result", {}).get("targetId")
        print("    [Tab] New tab created")
        
    if not target_id:
        print("[ERR] Unable to get Target ID")
        raise SystemExit(1)

    # Attach to the specific tab to get a sessionId
    attach_res = cdp.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
    session_id = attach_res.get("result", {}).get("sessionId")
    if not session_id:
        # Sometimes the response is placed in params (depends on Chrome version)
        print("[WARN] Cannot find sessionId in result, please verify Chrome version behavior")
        raise SystemExit(1)
        
    print(f"    Session ID: {session_id}")

    # D. Enable Page domain
    print("\n[D] Enabling Page domain...")
    cdp.send("Page.enable", session_id=session_id)
    print("    OK")

    # E. Navigate to YouTube
    print(f"\n[E] Navigating to {TARGET_URL}  (equivalent to MCP navigate_page tool)")
    result = cdp.send("Page.navigate", {"url": TARGET_URL}, session_id=session_id)
    frame_id = result.get("result", {}).get("frameId", "N/A")
    print(f"    frameId: {frame_id}")

    # F. Wait for page load
    wait = 8
    print(f"\n[F] Waiting {wait} seconds for YouTube to load...")
    time.sleep(wait)

    # G. Get page title
    print("\n[G] Getting page title  (equivalent to MCP evaluate_script tool)")
    r = cdp.send("Runtime.evaluate", {"expression": "document.title"}, session_id=session_id)
    title = r.get("result", {}).get("result", {}).get("value", "(unable to get)")
    print(f"    Page title: {title}")

    # H. List tabs again
    print("\n[H] Listing tabs again  (equivalent to MCP list_pages tool)")
    res = cdp.send("Target.getTargets")
    pages_after = [t for t in res.get("result", {}).get("targetInfos", []) if t.get("type") == "page"]
    for i, p in enumerate(pages_after):
        print(f"    [{i}] {p.get('title', '')[:50]}")
        
    # I. Close test tab (completes the close logic from youtube_mcp_control.py)
    print("\n[I] Closing test tab  (equivalent to MCP close_page tool)")
    cdp.send("Target.closeTarget", {"targetId": target_id})
    print("    OK")

    cdp.close()
    print("\n[OK] Done! Browser connection closed.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!!] User interrupted")
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n[ERR] {type(e).__name__}: {e}")
