#!/bin/bash
# Deploy: start local server or push to GitHub Pages
python3 -m http.server 8080 --directory /home/a-steve/workspace > /dev/null 2>&1 &
echo "Local server at http://localhost:8080 (files in workspace)"
echo "For public URL: upload workspace to GitHub repo, enable GitHub Pages (branch main, folder /root)"
