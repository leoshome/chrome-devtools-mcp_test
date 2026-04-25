# Chrome DevTools MCP Test Project

A test project for automating Chrome browser using the **Chrome DevTools MCP (Model Context Protocol)** server. This repository includes examples for controlling Chrome and automating tasks like analyzing YouTube content.

---

### 專案簡介
本專案演示如何透過 MCP 協議與 Chrome DevTools 進行互動，實現瀏覽器的自動化控制。包含以下腳本：
- **`youtube_mcp_control.py`**：使用 MCP 協議導航至 YouTube 並分析影片標題
- **`cdp_connect_existing.py`**：純 CDP WebSocket 連線，不依賴 MCP 伺服器

> [!NOTE]
> 本專案為純腳本自動化示範，**不需要 AI 模型或 AI 代理程式**即可獨立運行。

**`youtube_mcp_control.py` 示範流程：**
1. **自動連接**：使用 `chrome-devtools-mcp` 自動連線至執行中的 Chrome。
2. **網頁導覽**：自動跳轉至 YouTube 頁面。
3. **等待載入**：暫停 5 秒以確保內容載入完成。
4. **HTML 擷取**：透過 MCP 指令獲取目前頁面的完整 HTML 原始碼。
5. **資料解析**：使用 `BeautifulSoup` 分析網頁結構。
6. **標題提取**：精準定位並提取首頁影片清單中的影片標題。
7. **結果輸出**：將分析出的標題條列印在終端機視窗中。

**`cdp_connect_existing.py` 示範流程：**
1. **讀取連線資訊**：從 Chrome 的 `DevToolsActivePort` 檔案解析 WebSocket URL。
2. **建立連線**：使用原生 WebSocket 連接至 Chrome 的 CDP endpoint。
3. **列出分頁**：取得所有開啟的分頁資訊。
4. **附加目標**：附加到指定分頁並建立 session。
5. **頁面導覽**：導航至目標網站（預設為 YouTube）。
6. **執行指令**：使用 CDP 指令獲取頁面標題。
7. **關閉連線**：關閉分頁並斷開 WebSocket 連線。

### 前置需求
- **Chrome 瀏覽器**: 需為 **Version 146 或更高版本**。
- **Python 3.10+**: 用於執行控制腳本。

### Chrome 設定方法
依照 [Chrome 開發者部落格](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session?hl=zh-tw) 的說明，請進行以下設定以允許 MCP 連線：

1. 開啟 Chrome 並在網址列輸入：`chrome://inspect/#remote-debugging`
2. **啟用遠端偵錯 (Enable remote debugging)**。
3. 當執行腳本時，Chrome 會彈出對話框詢問是否允許連線，請點擊 **「允許 (Allow)」**。
4. 偵錯啟動後，Chrome 頂部會顯示「Chrome 目前受到自動測試軟體控制」的橫幅。

### 如何執行
1. 安裝必要套件：
   ```bash
   pip install -r requirements.txt
   ```
2. 執行腳本：
   ```bash
   # 使用 MCP 協議
   python youtube_mcp_control.py
   
   # 使用純 CDP WebSocket
   python cdp_connect_existing.py
   ```

---

### Overview
This project demonstrates how to interact with Chrome DevTools via the MCP protocol for browser automation. It includes the following scripts:
- **`youtube_mcp_control.py`**: Uses the MCP protocol to navigate to YouTube and analyze video titles
- **`cdp_connect_existing.py`**: Pure CDP WebSocket connection without relying on MCP server

> [!NOTE]
> This is a pure script-based automation demo and **does not require an AI model or AI agent** to function.

**`youtube_mcp_control.py` Demonstration Workflow:**
1. **Auto-Connect**: Connects to the running Chrome instance via `chrome-devtools-mcp`.
2. **Navigation**: Navigates the browser to the YouTube homepage.
3. **Wait**: Pauses for 5 seconds to ensure page content is fully loaded.
4. **HTML Extraction**: Retrieves the full HTML source code of the current page via MCP.
5. **Parsing**: Uses `BeautifulSoup` to parse the retrieved HTML.
6. **Title Extraction**: Selects and extracts video titles from the homepage video list.
7. **Console Output**: Lists the extracted titles in the console for verification.

**`cdp_connect_existing.py` Demonstration Workflow:**
1. **Read Connection Info**: Parses WebSocket URL from Chrome's `DevToolsActivePort` file.
2. **Establish Connection**: Uses native WebSocket to connect to Chrome's CDP endpoint.
3. **List Tabs**: Retrieves information about all open tabs.
4. **Attach Target**: Attaches to a specific tab and creates a session.
5. **Page Navigation**: Navigates to the target website (default: YouTube).
6. **Execute Commands**: Uses CDP commands to retrieve page titles.
7. **Close Connection**: Closes the tab and disconnects the WebSocket connection.

### Prerequisites
- **Chrome Browser**: **Version 146 or higher** is required.
- **Python 3.10+**: Required to run the control scripts.

### Chrome Configuration
Based on the [Chrome Developer Blog](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session), follow these steps to enable MCP connections:

1. Open Chrome and navigate to: `chrome://inspect/#remote-debugging`
2. **Enable remote debugging**.
3. When running the script, Chrome will display a dialog asking for permission to connect. Click **"Allow"**.
4. Once active, a banner stating "Chrome is being controlled by automated test software" will appear at the top of the browser.

### How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script:
   ```bash
   # Using MCP protocol
   python youtube_mcp_control.py
   
   # Using pure CDP WebSocket
   python cdp_connect_existing.py
   ```

---

## References / 參考資料
- [Debug your browser session with the Chrome DevTools MCP server](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session?hl=zh-tw)
