#!/bin/bash
if test -f "deployment-package.zip"; then
    echo "Removing deployment-package.zip"
    rm deployment-package.zip
fi

if [ -d "package" ]; then
    echo "Removing /package"
    rm -rf package
fi

echo "Installing packages..."
pip3 install --target ./package slackclient
pip3 install --target ./package requests
echo "Installed packages"

echo "Zipping packages..."
cd package
zip -r ../deployment-package.zip .
echo "Zipped packages\n"

echo "Zipping the code..."
cd ..
zip -g deployment-package.zip duty_bot.py
zip -g deployment-package.zip config.py
zip -g deployment-package.zip ical.py
echo "Zipped the code"