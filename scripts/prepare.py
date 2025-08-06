# translate from https://colab.research.google.com/drive/13AE8RvjnCfuBJGaACEqxeBIMo33_l-Sc
# by gemini 2.5 flash

import os
import sys
import re
import subprocess
import threading # 导入 threading 模块

# --- 1. Setup the environment ---
# IMPORTANT: Replace with your actual API token and Reddit username
api_token = '' # Your Reddit API token
your_reddit_username = '' # Your Reddit username

# --- Configuration (do not change unless you know what you're doing) ---
user_agent = f"android:personal-app:0.0.1 (by /u/{your_reddit_username})"
redirect_uri = 'http://127.0.0.1'

# Choose where to download the source code from
# Options: "[GitHub Repository]", "[GitHub Archive]"
# If GitHub Repository fails, try "[GitHub Archive]"
version = '[GitHub Repository]' # You can change this to '[GitHub Archive]' if needed

# --- Input Validation ---
if not api_token or not your_reddit_username:
    print("\x1b[31m[IMPORTANT]")
    print("No settings have been set. Please input your API token and username in the script.\x1b[0m")
    sys.exit()
else:
    print("Following settings have been set:")
    print(f"- User-Agent: {user_agent}")
    print(f"- API token: {api_token}")
    print(f"- Source location: {version}")
    print("\nStarting environment setup. This may take a few minutes...")

# --- Helper function to read from a stream and print ---
def _read_stream(stream, output_func):
    """Reads lines from a given stream and prints them using the provided output function."""
    for line in iter(stream.readline, ''):
        output_func(line)
        sys.stdout.flush() # 确保立即刷新缓冲区，实现实时打印

# --- Helper function to run shell commands with real-time streaming ---
def run_command(command, cwd=None, check_output=False):
    """
    Executes a shell command and streams its stdout and stderr to the console in real-time.
    Note: check_output=True is not fully supported for real-time streaming as it implies capturing output.
    For this function, output is always streamed.
    """
    print(f"\nExecuting: {command}")
    try:
        # 使用 Popen 来获取对子进程的控制，并捕获 stdout 和 stderr
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True, # 解码为文本
            bufsize=1, # 行缓冲
            universal_newlines=True, # 处理不同操作系统的换行符
            cwd=cwd
        )

        # 创建两个线程，一个用于读取 stdout，一个用于读取 stderr
        stdout_thread = threading.Thread(target=_read_stream, args=(process.stdout, sys.stdout.write))
        stderr_thread = threading.Thread(target=_read_stream, args=(process.stderr, sys.stderr.write))

        # 启动线程
        stdout_thread.start()
        stderr_thread.start()

        # 等待所有线程完成读取
        stdout_thread.join()
        stderr_thread.join()

        # 等待子进程结束
        process.wait()

        if process.returncode != 0:
            print(f"\x1b[31mError executing command: {command}\x1b[0m")
            print(f"\x1b[31mReturn Code: {process.returncode}\x1b[0m")
            sys.exit(1)

    except FileNotFoundError:
        print(f"\x1b[31mCommand not found: {command.split(' ')[0]}. Make sure it's installed and in your PATH.\x1b[0m")
        sys.exit(1)
    except Exception as e:
        print(f"\x1b[31mAn unexpected error occurred: {e}\x1b[0m")
        sys.exit(1)


# --- 2. Update the VM, install JDK 17, Android SDK and setup sdkmanager ---
print("\n--- Installing dependencies and Android SDK ---")
run_command("apt-get --quiet update")
run_command("apt-get --quiet install -y openjdk-17-jdk") # -y to automatically answer yes

# Download and unzip Android command-line tools
run_command("wget --quiet --output-document=android-sdk.zip https://dl.google.com/android/repository/commandlinetools-linux-7583922_latest.zip")
run_command("unzip -q android-sdk.zip -d android-sdk")

# Set environment variables for Android SDK and Java
os.environ["ANDROID_SDK_ROOT"] = "/content/android-sdk"
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"
# Add SDK tools to PATH
os.environ["PATH"] += ":/content/android-sdk/cmdline-tools/latest/bin:/content/android-sdk/platform-tools"

# Setup sdkmanager: accept licenses and install platforms/build-tools
# Using 'yes |' to automatically accept licenses
print("\n--- Setting up Android SDK Manager (this may take a while) ---")
run_command(f"yes | {os.environ['ANDROID_SDK_ROOT']}/cmdline-tools/latest/bin/sdkmanager --sdk_root={os.environ['ANDROID_SDK_ROOT']} \"platforms;android-30\" \"build-tools;30.0.3\"")

# --- 3. Download the source code ---
print("\n--- Downloading Infinity for Reddit source code ---")
if version == "[GitHub Repository]":
    run_command("git clone \"https://github.com/Docile-Alligator/Infinity-For-Reddit\"")
else:
    run_command("wget \"https://github.com/Docile-Alligator/Infinity-For-Reddit/archive/a46e96f3e48a89f7b683fa7308c39f01c5b5ac21.zip\"")
    run_command("unzip \"a46e96f3e48a89f7b683fa7308c39f01c5b5ac21.zip\"")
    # Move the unzipped directory to a consistent name
    run_command("mv -T Infinity-For-Reddit-* Infinity-For-Reddit")

# Change current directory to the source code root
os.chdir("Infinity-For-Reddit")
print(f"Changed current directory to: {os.getcwd()}")

# --- 4. Change the API token, user agent, Redirect URI and add keystore ---
print("\n--- Modifying source code with your settings and adding keystore ---")

# Define file paths relative to the current working directory (Infinity-For-Reddit)
apiutils_file = "app/src/main/java/ml/docilealligator/infinityforreddit/utils/APIUtils.java"
build_gradle_file = "app/build.gradle"

# --- Modify APIUtils.java ---
try:
    with open(apiutils_file, "r", encoding="utf-8-sig") as f:
        apiutils_code = f.read()

    # Replace API token, redirect URI, and user agent
    apiutils_code = apiutils_code.replace("NOe2iKrPPzwscA", api_token)
    apiutils_code = apiutils_code.replace("infinity://localhost", redirect_uri)
    apiutils_code = re.sub(r'public static final String USER_AGENT = ".*?";', f'public static final String USER_AGENT = "{user_agent}";', apiutils_code)

    with open(apiutils_file, "w", encoding="utf-8") as f:
        f.write(apiutils_code)
    print(f"Successfully updated {apiutils_file}")

except FileNotFoundError:
    print(f"\x1b[31mError: {apiutils_file} not found. Ensure the source code was downloaded correctly.\x1b[0m")
    sys.exit(1)
except Exception as e:
    print(f"\x1b[31mError modifying {apiutils_file}: {e}\x1b[0m")
    sys.exit(1)

# --- Add Keystore ---
# Download the keystore file to /content/ (parent of Infinity-For-Reddit)
run_command("wget -P /content/ \"https://github.com/TanukiAI/Infinity-keystore/raw/main/Infinity.jks\"")

# --- Modify build.gradle ---
try:
    with open(build_gradle_file, "r", encoding="utf-8-sig") as f:
        build_gradle_code = f.read()

    # Add signing configuration
    build_gradle_code = build_gradle_code.replace(r"""    buildTypes {""", r"""    signingConfigs {
        release {
            storeFile file("/content/Infinity.jks")
            storePassword "Infinity"
            keyAlias "Infinity"
            keyPassword "Infinity"
        }
    }
    buildTypes {""")

    # Apply signing configuration to release build type
    build_gradle_code = build_gradle_code.replace(r"""    buildTypes {
        release {""", r"""    buildTypes {
        release {
            signingConfig signingConfigs.release""")

    # Modify lint configuration
    build_gradle_code = build_gradle_code.replace(r"""    lint {
        disable 'MissingTranslation'
    }""", r"""    lint {
        disable 'MissingTranslation'
        baseline = file("lint-baseline.xml")
    }""")

    with open(build_gradle_file, "w", encoding="utf-8") as f:
        f.write(build_gradle_code)
    print(f"Successfully updated {build_gradle_file}")

except FileNotFoundError:
    print(f"\x1b[31mError: {build_gradle_file} not found. Ensure the source code was downloaded correctly.\x1b[0m")
    sys.exit(1)
except Exception as e:
    print(f"\x1b[31mError modifying {build_gradle_file}: {e}\x1b[0m")
    sys.exit(1)

print("\nAll setup and configuration steps completed successfully!")
print("You are now ready to compile the APK.")
