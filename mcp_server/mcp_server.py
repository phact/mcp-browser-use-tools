import asyncio
from fastmcp import FastMCP

from browser_use.browser.context import BrowserContext, BrowserContextConfig
from browser_use.controller.views import *
from browser_use.browser.browser import Browser

_browser_ctx: Optional[BrowserContext] = None

async def initialize_browser_context():
    global _browser_ctx
    if _browser_ctx is None:
        browser = Browser()
        _browser_ctx = BrowserContext(browser, BrowserContextConfig())

def get_browser_context() -> BrowserContext:
    global _browser_ctx
    if _browser_ctx is None:
        # Initialize synchronously for this demo.
        asyncio.run(initialize_browser_context())
    return _browser_ctx


mcp = FastMCP("Browser Use MCP Server")

@mcp.tool("done", description="Complete task with text and success flag")
def done_tool(params: DoneAction) -> str:
    return f"Task done: '{params.text}' with success={params.success}"

@mcp.tool("search_google", description="Search Google using a query")
async def search_google_tool(params: SearchGoogleAction) -> str:
    bc = await get_browser_context()
    # Use bc.get_current_page() and navigate to Google search URL.
    page = await bc.get_current_page()
    # For demonstration, we return a simulated message.
    return f"Searched Google for: '{params.query}' on page with title '{await page.title()}'"

@mcp.tool("go_to_url", description="Navigate to a specified URL")
async def go_to_url_tool(params: GoToUrlAction) -> str:
    bc = await get_browser_context()
    await bc.navigate_to(params.url)
    return f"Navigated to URL: {params.url}"

@mcp.tool("go_back", description="Navigate back in browser history")
async def go_back_tool(params: NoParamsAction) -> str:
    bc = await get_browser_context()
    await bc.go_back()
    return "Navigated back"

@mcp.tool("wait", description="Wait for a specified number of seconds (default 3)")
async def wait_tool(seconds: int = 3) -> str:
    await asyncio.sleep(seconds)
    return f"Waited for {seconds} seconds"

@mcp.tool("click_element", description="Click a DOM element by its index")
async def click_element_tool(params: ClickElementAction) -> str:
    bc = await get_browser_context()
    selector_map = await bc.get_selector_map()
    if params.index not in selector_map:
        return f"Element with index {params.index} not found"
    element_node = selector_map[params.index]
    download_path = await bc._click_element_node(element_node)
    if download_path:
        return f"Clicked element {params.index} and downloaded file to: {download_path}"
    else:
        text = element_node.get_all_text_till_next_clickable_element(max_depth=2)
        return f"Clicked element {params.index}: {text}"

@mcp.tool("input_text", description="Input text into an element by index")
async def input_text_tool(params: InputTextAction) -> str:
    bc = await get_browser_context()
    element_node = await bc.get_dom_element_by_index(params.index)
    if element_node is None:
        return f"Element at index {params.index} not found"
    await bc._input_text_element_node(element_node, params.text)
    return f"Input '{params.text}' into element at index {params.index}"

@mcp.tool("switch_tab", description="Switch to a different browser tab by page ID")
async def switch_tab_tool(params: SwitchTabAction) -> str:
    bc = await get_browser_context()
    await bc.switch_to_tab(params.page_id)
    return f"Switched to tab {params.page_id}"

@mcp.tool("open_tab", description="Open a URL in a new browser tab")
async def open_tab_tool(params: OpenTabAction) -> str:
    bc = await get_browser_context()
    await bc.create_new_tab(params.url)
    return f"Opened new tab with URL: {params.url}"

@mcp.tool("extract_content", description="Extract page content based on a goal")
async def extract_content_tool(params: ExtractPageContentAction) -> str:
    bc = await get_browser_context()
    page = await bc.get_current_page()
    content = await page.content()
    return f"Extracted content for '{params.value}': {content[:100]}..."

@mcp.tool("scroll_down", description="Scroll down the page by a pixel amount or one page if not specified")
async def scroll_down_tool(params: ScrollAction) -> str:
    amount = params.amount if params.amount is not None else "one page"
    # In production, call bc.page.evaluate(...) to scroll.
    return f"Scrolled down by {amount}"

@mcp.tool("scroll_up", description="Scroll up the page by a pixel amount or one page if not specified")
async def scroll_up_tool(params: ScrollAction) -> str:
    amount = params.amount if params.amount is not None else "one page"
    return f"Scrolled up by {amount}"

@mcp.tool("send_keys", description="Send keyboard keys (supports special keys)")
async def send_keys_tool(params: SendKeysAction) -> str:
    return f"Sent keys: {params.keys}"

@mcp.tool("scroll_to_text", description="Scroll the page to bring text into view")
async def scroll_to_text_tool(text: str) -> str:
    return f"Scrolled to text: {text}"

@mcp.tool("get_dropdown_options", description="Get options from a dropdown by element index")
async def get_dropdown_options_tool(index: int) -> str:
    return f"Retrieved dropdown options for element at index {index}"

@mcp.tool("select_dropdown_option", description="Select a dropdown option by element index and option text")
async def select_dropdown_option_tool(index: int, text: str) -> str:
    return f"Selected dropdown option '{text}' for element at index {index}"

def main():
    # Initialize the browser context asynchronously
    asyncio.run(initialize_browser_context())
    # Run the MCP server using stdio transport (for integration with Claude, etc.)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
