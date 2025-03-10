#!/bin/bash

GIT_LFS_SKIP_SMUDGE=1 git subtree pull --prefix=browser-use https://github.com/browser-use/browser-use main --squash
cp -R browser-use/browser_use/browser/ src/browser/
cp browser-use/browser_use/controller/views.py src/controller/views.py
cp -R browser-use/browser_use/dom/ src/dom
