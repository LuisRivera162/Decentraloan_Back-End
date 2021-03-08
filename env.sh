#!/bin/zsh
# Script to set all environment variables needed to run the backend in Mac,by Hector.

export FLASK_APP=main.py
export FLASK_ENV=development
export WEB3_INFURA_PROJECT_ID=79018cb571954f159e09d92addd6803e
export WEB3_INFURA_API_SECRET=bbe128f3e602402d8149fe3ab4b6d3d2
export DEV_KETH_PRIVATE_KEY=820d856027a469d7002ec974853c0f4e17ae8314fc6a3a8e8b3841601245f1c1
echo "Local Environment Ready for Testing on Infura Kovan Network!"
