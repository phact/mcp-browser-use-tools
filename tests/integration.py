import asyncio
import pytest
import mcp_server.mcp_server as mcp_server

# Use a pytest fixture to initialize the real browser context once for all tests.
@pytest.fixture(scope="module", autouse=True)
def real_browser_context():
    # This will initialize the actual browser context used by your tools.
    asyncio.run(mcp_server.initialize_browser_context())
    # Optionally, yield and later add any cleanup if your Browser has a shutdown method.
    yield

# A simple helper to create a dummy action object with attributes.
def create_action(**kwargs):
    return type("Action", (), kwargs)()

def test_done_tool_real():
    action = create_action(text="Real Test", success=True)
    result = mcp_server.done_tool(action)
    assert "Task done: 'Real Test'" in result
    assert "success=True" in result

@pytest.mark.asyncio
async def test_search_google_tool_real():
    action = create_action(query="real query")
    result = await mcp_server.search_google_tool(action)
    # The actual page title returned by your browser may vary.
    assert "Searched Google for: 'real query'" in result
    assert "on page with title" in result

@pytest.mark.asyncio
async def test_go_to_url_tool_real():
    test_url = "http://example.com"
    action = create_action(url=test_url)
    result = await mcp_server.go_to_url_tool(action)
    assert f"Navigated to URL: {test_url}" in result

@pytest.mark.asyncio
async def test_go_back_tool_real():
    action = create_action()  # No parameters expected.
    result = await mcp_server.go_back_tool(action)
    assert "Navigated back" in result

@pytest.mark.asyncio
async def test_wait_tool_real():
    # Test the wait tool with a 1-second delay.
    result = await mcp_server.wait_tool(1)
    assert "Waited for 1 seconds" in result

@pytest.mark.asyncio
async def test_click_element_tool_real():
    action = create_action(index=0)
    result = await mcp_server.click_element_tool(action)
    # Since your real browser context is used, the actual response may vary.
    # For example, if the element is clickable and triggers a download, expect a download path.
    # Otherwise, it might return the element's text.
    assert "Clicked element 0" in result

@pytest.mark.asyncio
async def test_input_text_tool_real():
    action = create_action(index=0, text="hello world")
    result = await mcp_server.input_text_tool(action)
    assert "Input 'hello world' into element at index 0" in result

@pytest.mark.asyncio
async def test_switch_tab_tool_real():
    action = create_action(page_id="tab_real")
    result = await mcp_server.switch_tab_tool(action)
    assert "Switched to tab tab_real" in result

@pytest.mark.asyncio
async def test_open_tab_tool_real():
    test_url = "http://newtab-real.com"
    action = create_action(url=test_url)
    result = await mcp_server.open_tab_tool(action)
    assert f"Opened new tab with URL: {test_url}" in result

@pytest.mark.asyncio
async def test_extract_content_tool_real():
    action = create_action(value="sample")
    result = await mcp_server.extract_content_tool(action)
    # Check that the result begins with the expected text.
    assert result.startswith("Extracted content for 'sample':")
    # The real content will depend on the page loaded by your browser context.

@pytest.mark.asyncio
async def test_scroll_down_tool_real():
    action = create_action(amount=300)
    result = await mcp_server.scroll_down_tool(action)
    assert "Scrolled down by 300" in result

@pytest.mark.asyncio
async def test_scroll_up_tool_real():
    action = create_action(amount=150)
    result = await mcp_server.scroll_up_tool(action)
    assert "Scrolled up by 150" in result

@pytest.mark.asyncio
async def test_send_keys_tool_real():
    action = create_action(keys="Enter")
    result = await mcp_server.send_keys_tool(action)
    assert "Sent keys: Enter" in result

@pytest.mark.asyncio
async def test_scroll_to_text_tool_real():
    test_text = "Footer"
    result = await mcp_server.scroll_to_text_tool(test_text)
    assert f"Scrolled to text: {test_text}" in result

@pytest.mark.asyncio
async def test_get_dropdown_options_tool_real():
    result = await mcp_server.get_dropdown_options_tool(0)
    assert "Retrieved dropdown options for element at index 0" in result

@pytest.mark.asyncio
async def test_select_dropdown_option_tool_real():
    result = await mcp_server.select_dropdown_option_tool(0, "Option A")
    assert "Selected dropdown option 'Option A' for element at index 0" in result

