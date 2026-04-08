import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from bs4 import BeautifulSoup


async def automate_youtube():
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "chrome-devtools-mcp@latest", "--autoConnect"],
        env=None
    )

    print("Connecting to Chrome DevTools MCP server...")

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # List all available tools
                tools = await session.list_tools()
                tool_names = [tool.name for tool in tools.tools]
                print(f"Available tools: {tool_names}")

                # -- Step 1: Navigate to target page ------------------------------
                print("\nStep 1: Navigating to YouTube...")
                await session.call_tool(
                    "navigate_page",
                    arguments={"url": "https://www.youtube.com"}
                )

                # -- Step 2: List pages (Confirm current page) --------------------
                if "list_pages" in tool_names:
                    pages_info = await session.call_tool("list_pages", arguments={})
                    print(f"Page info: {pages_info.content[0].text}")

                # -- Step 3: Wait for page load ----------------------------------
                print("\nWaiting for page to load (5s)...")
                await asyncio.sleep(5)

                # -- Step 4: Get current page HTML -------------------------------
                if "evaluate_script" in tool_names:
                    print("\nStep 4: Getting current page HTML...")
                    html_result = await session.call_tool(
                        "evaluate_script",
                        arguments={"function": "() => document.documentElement.outerHTML"}
                    )
                    raw_text = html_result.content[0].text if html_result.content else ""
                    
                    # Try parsing JSON content to restore \n
                    html_content = raw_text
                    is_valid_html = False
                    try:
                        if "```json" in raw_text:
                            json_str = raw_text.split("```json")[-1].split("```")[0].strip()
                            html_content = json.loads(json_str)
                            is_valid_html = True
                        elif raw_text.startswith('"') or raw_text.startswith('{'):
                            html_content = json.loads(raw_text)
                            is_valid_html = True
                        elif "<html" in raw_text.lower():
                            is_valid_html = True
                    except Exception as e:
                        if "<html" in raw_text.lower():
                            is_valid_html = True
                        else:
                            print(f"JSON parsing failed: {e}")

                    if not is_valid_html:
                        print(f"Warning: Content does not appear to be valid HTML (Length: {len(raw_text)})")
                        print(f"Content preview: {raw_text[:200]}...")
                        return

                    # Save to file (Backup)
                    with open("page.html", "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print(f"HTML saved (Length: {len(html_content)})")

                    # -- Step 5: Analysis phase --------------------------------------
                    print("\nStep 5: Analyzing video titles...")
                    soup = BeautifulSoup(html_content, 'html.parser')
                    
                    # Extract titles based on the specific path provided by the user
                    # selector: #content > yt-lockup-view-model > div > div > yt-lockup-metadata-view-model > div.ytLockupMetadataViewModelTextContainer > h3 > a > span
                    video_elements = soup.select('#content > yt-lockup-view-model > div > div > yt-lockup-metadata-view-model > div.ytLockupMetadataViewModelTextContainer > h3 > a > span')
                    
                    if not video_elements:
                        print("No video titles found. Structure might have changed or page not fully loaded.")
                    else:
                        print(f"Successfully found {len(video_elements)} video titles:")
                        print("-" * 50)
                        for i, el in enumerate(video_elements, 1):
                            title = el.get_text().strip()
                            # Some elements might be empty, filter them out
                            if title:
                                print(f"{i:2d}. {title}")
                        print("-" * 50)

                # -- Step 6: Close page (if tool exists) -------------------------
                if "close_page" in tool_names:
                    # Demonstrate closing page; actual ID might need extraction from list_pages
                    print("\nStep 6: Attempting to close page...")
                    # Since we don't know the exact ID, this is for demonstration
                    # await session.call_tool("close_page", arguments={"pageId": ...})
                    print("Command sent.")

    except Exception as e:
        print(f"Error occurred: {type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(automate_youtube())
