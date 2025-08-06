#!/usr/bin/env bash

# translate from https://colab.research.google.com/drive/13AE8RvjnCfuBJGaACEqxeBIMo33_l-Sc
# by gemini-2.5-flash

# --- 2. Build the APK. This can take up to 15 minutes. ---

# Check if the Infinity-For-Reddit directory exists, implying previous setup was done.
if [ ! -d "Infinity-For-Reddit" ]; then
  echo ""
  echo -e "\033[31m[IMPORTANT]\033[0m"
  echo "The 'Infinity-For-Reddit' directory was not found."
  echo "Please ensure the setup steps (e.g., running build.py) have been completed successfully."
  exit 1
fi

# Navigate into the Infinity-For-Reddit directory
echo "Navigating to Infinity-For-Reddit directory..."
cd Infinity-For-Reddit || { echo -e "\033[31mError: Could not change directory to Infinity-For-Reddit.\033[0m"; exit 1; }
echo "Current directory: $(pwd)"

echo ""
echo "--- Starting APK Build Process (This can take up to 15 minutes) ---"

# Run Gradle commands
# updateLintBaseline is often run before assembleRelease to ensure lint checks are up-to-date
echo "Running ./gradlew updateLintBaseline..."
./gradlew updateLintBaseline

# Check if the previous command was successful
if [ $? -ne 0 ]; then
    echo -e "\033[31mError: gradlew updateLintBaseline failed.\033[0m"
    exit 1
fi

echo ""
echo "Running ./gradlew assembleRelease..."
./gradlew assembleRelease

# Check if the APK build was successful
if [ $? -ne 0 ]; then
    echo -e "\033[31mError: gradlew assembleRelease failed. APK build failed.\033[0m"
    exit 1
fi

echo ""
echo "--- APK Build Process Completed! ---"
echo "Your APK should now be available in 'app/build/outputs/apk/release/' within the Infinity-For-Reddit directory."
