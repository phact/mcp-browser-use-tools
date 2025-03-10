#!/bin/bash

GIT_LFS_SKIP_SMUDGE=1 git subtree pull --prefix=browser-use https://github.com/browser-use/browser-use main --squash
