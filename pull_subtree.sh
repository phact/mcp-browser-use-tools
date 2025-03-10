#!/bin/bash

GIT_LFS_SKIP_SMUDGE=1 git subtree pull --prefix=browser-use https://github.com/browser-use/browser-use main --squash
cp browser-use/browser_use/browser/*.py src/minimal_browser/
cp browser-use/browser_use/controller/views.py src/controller/views.py
