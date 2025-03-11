import argparse
import asyncio
import json
import logging
from typing import Optional

from fastmcp import FastMCP

from browser_use.browser.context import BrowserContext, BrowserContextConfig
from browser_use.controller.views import (
    ClickElementAction,
    DoneAction,
    GoToUrlAction,
    InputTextAction,
    NoParamsAction,
    OpenTabAction,
    ScrollAction,
    SearchGoogleAction,
    SendKeysAction,
    SwitchTabAction,
    ExtractPageContentAction,
)
from browser_use.browser.browser import Browser, BrowserConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global browser context
_browser_ctx: Optional[BrowserContext] = None

async def initialize_browser_context(headless: bool = False) -> None:
    global _browser_ctx
    if _browser_ctx is None:
        config = BrowserConfig(headless=headless)
        browser = Browser(config=config)
        # Set no_viewport=True if headless is True
        _browser_ctx = BrowserContext(browser, BrowserContextConfig())
        logger.info("Initialized browser context.")

def get_browser_context() -> BrowserContext:
    global _browser_ctx
    if _browser_ctx is None:
        # Synchronously initialize with default headless=False if needed.
        asyncio.run(initialize_browser_context())
    return _browser_ctx

mcp = FastMCP("Browser Use MCP Server")

@mcp.tool("done", description="Complete task with text and success flag")
def done_tool(params: DoneAction) -> str:
    msg = f"Task done: '{params.text}' with success={params.success}"
    logger.info(msg)
    return msg

@mcp.tool("search_google", description="Search Google using a query")
async def search_google_tool(params: SearchGoogleAction) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    url = f"https://www.google.com/search?q={params.query}&udm=14"
    await page.goto(url)
    await page.wait_for_load_state()
    title = await page.title()
    msg = f"🔍 Searched for '{params.query}' on page titled '{title}'"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("go_to_url", description="Navigate to a specified URL")
async def go_to_url_tool(params: GoToUrlAction) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    await page.goto(params.url)
    await page.wait_for_load_state()
    msg = f"🔗 Navigated to {params.url}"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("go_back", description="Navigate back in browser history")
async def go_back_tool(params: NoParamsAction) -> str:
    bc = get_browser_context()
    await bc.go_back()
    msg = "🔙 Navigated back"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("wait", description="Wait for a specified number of seconds (default 3)")
async def wait_tool(seconds: int = 3) -> str:
    msg = f"🕒 Waiting for {seconds} seconds"
    logger.info(msg)
    await asyncio.sleep(seconds)
    return msg

@mcp.tool("click_element", description="Click a DOM element by its index")
async def click_element_tool(params: ClickElementAction) -> str:
    bc = get_browser_context()
    session = await bc.get_session()
    selector_map = await bc.get_selector_map()
    if params.index not in selector_map:
        error_msg = f"Element with index {params.index} not found"
        logger.error(error_msg)
        return error_msg

    element_node = await bc.get_dom_element_by_index(params.index)
    initial_pages = len(session.context.pages)
    try:
        # If the element is a file uploader, advise to use the file upload function.
        if await bc.is_file_uploader(element_node):
            msg = f"Element at index {params.index} is a file uploader. Use file upload function."
            logger.info(msg)
            return msg

        download_path = await bc._click_element_node(element_node)
        if download_path:
            msg = f"💾 Clicked element {params.index} and downloaded file to: {download_path}"
        else:
            text = element_node.get_all_text_till_next_clickable_element(max_depth=2)
            msg = f"🖱️ Clicked element {params.index}: {text}"
        logger.info(msg)

        # If clicking the element opened a new tab, switch to it.
        if len(session.context.pages) > initial_pages:
            new_tab_msg = "New tab opened - switching to it"
            logger.info(new_tab_msg)
            await bc.switch_to_tab(-1)
            msg += f" - {new_tab_msg}"
        return msg + f"\nBrowser state: {bc.state}"
    except Exception as e:
        error_msg = f"Error clicking element {params.index}: {str(e)}"
        logger.warning(error_msg)
        return error_msg

@mcp.tool("input_text", description="Input text into an element by index")
async def input_text_tool(params: InputTextAction) -> str:
    bc = get_browser_context()
    selector_map = await bc.get_selector_map()
    if params.index not in selector_map:
        error_msg = f"Element at index {params.index} not found"
        logger.error(error_msg)
        return error_msg

    element_node = await bc.get_dom_element_by_index(params.index)
    await bc._input_text_element_node(element_node, params.text)
    msg = f"⌨️ Input '{params.text}' into element at index {params.index}"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("switch_tab", description="Switch to a different browser tab by page ID")
async def switch_tab_tool(params: SwitchTabAction) -> str:
    bc = get_browser_context()
    await bc.switch_to_tab(params.page_id)
    page = await bc.get_current_page()
    await page.wait_for_load_state()
    msg = f"🔄 Switched to tab {params.page_id}"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("open_tab", description="Open a URL in a new browser tab")
async def open_tab_tool(params: OpenTabAction) -> str:
    bc = get_browser_context()
    await bc.create_new_tab(params.url)
    msg = f"🔗 Opened new tab with URL: {params.url}"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("extract_content", description="Extract page content based on a goal")
async def extract_content_tool(params: ExtractPageContentAction) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    content = await page.content()
    snippet = content[:100] + "..." if len(content) > 100 else content
    msg = f"📄 Extracted content for '{params.value}': {snippet}"
    logger.info(msg)
    return msg + f"\nBrowser state: {bc.state}"

@mcp.tool("scroll_down", description="Scroll down the page by a pixel amount or one page if not specified")
async def scroll_down_tool(params: ScrollAction) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    if params.amount is not None:
        await page.evaluate(f"window.scrollBy(0, {params.amount});")
        amount_str = f"{params.amount} pixels"
    else:
        await page.evaluate("window.scrollBy(0, window.innerHeight);")
        amount_str = "one page"
    msg = f"🔍 Scrolled down by {amount_str}"
    logger.info(msg)
    return msg

@mcp.tool("scroll_up", description="Scroll up the page by a pixel amount or one page if not specified")
async def scroll_up_tool(params: ScrollAction) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    if params.amount is not None:
        await page.evaluate(f"window.scrollBy(0, -{params.amount});")
        amount_str = f"{params.amount} pixels"
    else:
        await page.evaluate("window.scrollBy(0, -window.innerHeight);")
        amount_str = "one page"
    msg = f"🔍 Scrolled up by {amount_str}"
    logger.info(msg)
    return msg

@mcp.tool("send_keys", description="Send keyboard keys (supports special keys)")
async def send_keys_tool(params: SendKeysAction) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    try:
        await page.keyboard.press(params.keys)
    except Exception as e:
        if "Unknown key" in str(e):
            for key in params.keys:
                try:
                    await page.keyboard.press(key)
                except Exception as inner_e:
                    logger.debug(f"Error sending key {key}: {str(inner_e)}")
                    raise inner_e
        else:
            raise e
    msg = f"⌨️ Sent keys: {params.keys}"
    logger.info(msg)
    return msg

@mcp.tool("scroll_to_text", description="Scroll the page to bring text into view")
async def scroll_to_text_tool(text: str) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    locators = [
        page.get_by_text(text, exact=False),
        page.locator(f"text={text}"),
        page.locator(f"//*[contains(text(), '{text}')]"),
    ]
    for locator in locators:
        try:
            if await locator.count() > 0 and await locator.first.is_visible():
                await locator.first.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)  # Allow scroll animation to complete.
                msg = f"🔍 Scrolled to text: {text}"
                logger.info(msg)
                return msg
        except Exception as e:
            logger.debug(f"Locator attempt failed: {str(e)}")
            continue
    msg = f"Text '{text}' not found or not visible on page"
    logger.info(msg)
    return msg

@mcp.tool("get_dropdown_options", description="Get options from a dropdown by element index")
async def get_dropdown_options_tool(index: int) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    selector_map = await bc.get_selector_map()
    if index not in selector_map:
        msg = f"Element with index {index} not found"
        logger.error(msg)
        return msg

    dom_element = selector_map[index]
    try:
        all_options = []
        frame_index = 0
        for frame in page.frames:
            try:
                options = await frame.evaluate(
                    """
                    (xpath) => {
                        const select = document.evaluate(xpath, document, null,
                            XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        if (!select) return null;
                        return {
                            options: Array.from(select.options).map(opt => ({
                                text: opt.text,
                                value: opt.value,
                                index: opt.index
                            })),
                            id: select.id,
                            name: select.name
                        };
                    }
                    """,
                    dom_element.xpath,
                )
                if options:
                    logger.debug(f"Found dropdown in frame {frame_index}")
                    for opt in options["options"]:
                        encoded_text = json.dumps(opt["text"])
                        all_options.append(f'{opt["index"]}: text={encoded_text}')
            except Exception as frame_e:
                logger.debug(f"Frame {frame_index} evaluation failed: {str(frame_e)}")
            frame_index += 1
        if all_options:
            msg = "\n".join(all_options) + "\nUse the exact text string in select_dropdown_option"
            logger.info(msg)
            return msg
        else:
            msg = "No options found in any frame for dropdown"
            logger.info(msg)
            return msg
    except Exception as e:
        error_msg = f"Error getting options: {str(e)}"
        logger.error(error_msg)
        return error_msg

@mcp.tool("select_dropdown_option", description="Select a dropdown option by element index and option text")
async def select_dropdown_option_tool(index: int, text: str) -> str:
    bc = get_browser_context()
    page = await bc.get_current_page()
    selector_map = await bc.get_selector_map()
    if index not in selector_map:
        msg = f"Element with index {index} not found"
        logger.error(msg)
        return msg

    dom_element = selector_map[index]
    if dom_element.tag_name.lower() != "select":
        msg = f"Cannot select option: Element with index {index} is a {dom_element.tag_name}, not a select"
        logger.error(msg)
        return msg

    xpath = '//' + dom_element.xpath
    try:
        frame_index = 0
        for frame in page.frames:
            try:
                find_dropdown_js = """
                    (xpath) => {
                        try {
                            const select = document.evaluate(xpath, document, null,
                                XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (!select) return null;
                            if (select.tagName.toLowerCase() !== 'select') {
                                return {error: `Found element but it's a ${select.tagName}, not SELECT`, found: false};
                            }
                            return {
                                id: select.id,
                                name: select.name,
                                found: true,
                                tagName: select.tagName,
                                optionCount: select.options.length,
                                currentValue: select.value,
                                availableOptions: Array.from(select.options).map(o => o.text.trim())
                            };
                        } catch (e) {
                            return {error: e.toString(), found: false};
                        }
                    }
                    """
                dropdown_info = await frame.evaluate(find_dropdown_js, dom_element.xpath)
                if dropdown_info and dropdown_info.get("found"):
                    selected_option = await frame.locator(xpath).nth(0).select_option(label=text, timeout=1000)
                    msg = f"Selected option '{text}' with value {selected_option} in frame {frame_index}"
                    logger.info(msg)
                    return msg
            except Exception as frame_e:
                logger.error(f"Frame {frame_index} attempt failed: {str(frame_e)}")
            frame_index += 1
        msg = f"Could not select option '{text}' in any frame"
        logger.info(msg)
        return msg
    except Exception as e:
        error_msg = f"Selection failed: {str(e)}"
        logger.error(error_msg)
        return error_msg

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode with no viewport")
    args = parser.parse_args()

    asyncio.run(initialize_browser_context(headless=args.headless))
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
