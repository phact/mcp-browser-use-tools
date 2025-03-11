# mcp-browser-use-tools

This package vendors a subset of [browser-use](https://github.com/browser-use/browser-use) with minimal dependencies exposed as an mcp-server.

*Note* this does not wrap the full browser-use agent. There are other MCP's that do that. This one only exposes the internal tools for folks who want to roll their own agent loop.

Supports the following tools:

 - done
 - search_google
 - go_to_url
 - go_back
 - wait
 - click_element
 - input_text
 - switch_tab
 - open_tab
 - extract_content
 - scroll_down
 - scroll_up
 - send_keys
 - scroll_to_text
 - get_dropdown_options
 - select_dropdown_option
