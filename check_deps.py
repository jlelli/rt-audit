#!/usr/bin/env python3

import subprocess
import sys
import importlib
import os
import shutil

def check_command(command, description, install_guide=""):
    """Check if a command is available in PATH."""
    if shutil.which(command):
        print(f"✅ {description}: {command}")
        return True
    else:
        print(f"❌ {description}: {command} - NOT FOUND")
        if install_guide:
            print(f"   Install: {install_guide}")
        return False

def check_python_package(package, description, install_guide=""):
    """Check if a Python package is available."""
    try:
        importlib.import_module(package)
        print(f"✅ {description}: {package}")
        return True
    except ImportError:
        print(f"❌ {description}: {package} - NOT FOUND")
        if install_guide:
            print(f"   Install: {install_guide}")
        return False

def check_rt_app():
    """Check for rt-app availability and version."""
    if check_command("rt-app", "rt-app framework"):
        try:
            result = subprocess.run(["rt-app", "--help"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("   ✅ rt-app is working correctly")
                return True
            else:
                print("   ❌ rt-app has issues (non-zero exit code)")
                return False
        except subprocess.TimeoutExpired:
            print("   ❌ rt-app timed out")
            return False
        except Exception as e:
            print(f"   ❌ rt-app error: {e}")
            return False
    return False



def check_system_requirements():
    """Check system-level requirements."""
    print("\n🔍 Checking System Requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 6:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version: {python_version.major}.{python_version.minor}.{python_version.micro} - Need Python 3.6+")
        return False
    
    # Check if running as root (for real-time testing)
    if os.geteuid() == 0:
        print("✅ Running as root (good for real-time testing)")
    else:
        print("⚠️  Not running as root (may limit real-time capabilities)")
    
    return True

def check_python_dependencies():
    """Check Python package dependencies."""
    print("\n🐍 Checking Python Dependencies...")
    
    dependencies = [
        ("pandas", "Data analysis library", "pip install pandas"),
        ("json", "JSON processing (built-in)", ""),
        ("argparse", "Command-line parsing (built-in)", ""),
        ("glob", "File pattern matching (built-in)", ""),
        ("re", "Regular expressions (built-in)", ""),
        ("os", "Operating system interface (built-in)", ""),
        ("subprocess", "Subprocess management (built-in)", ""),
        ("shutil", "File operations (built-in)", ""),
    ]
    
    all_available = True
    for package, description, install_guide in dependencies:
        if not check_python_package(package, description, install_guide):
            all_available = False
    
    return all_available

def check_external_tools():
    """Check external tool dependencies."""
    print("\n🛠️  Checking External Tools...")
    
    tools = [
        ("rt-app", "Real-time application framework", "Install from rt-app source or package manager"),
        ("git", "Version control system", "apt install git / yum install git"),
        ("python3", "Python interpreter", "apt install python3 / yum install python3"),
    ]
    
    all_available = True
    for tool, description, install_guide in tools:
        if tool == "rt-app":
            if not check_rt_app():
                all_available = False
        else:
            if not check_command(tool, description, install_guide):
                all_available = False
    
    return all_available

def check_kernel_support():
    """Check kernel support for SCHED_DEADLINE."""
    print("\n🐧 Checking Kernel Support...")
    
    # Check kernel version (SCHED_DEADLINE requires kernel >= 3.14)
    try:
        with open("/proc/version", "r") as f:
            version_line = f.read()
            # Extract kernel version using regex
            import re
            match = re.search(r'Linux version (\d+)\.(\d+)', version_line)
            if match:
                major = int(match.group(1))
                minor = int(match.group(2))
                kernel_version = f"{major}.{minor}"
                
                if major > 3 or (major == 3 and minor >= 14):
                    print(f"✅ Kernel version: {major}.{minor} (supports SCHED_DEADLINE)")
                    return True
                else:
                    print(f"❌ Kernel version: {major}.{minor} (SCHED_DEADLINE requires >= 3.14)")
                    return False
            else:
                print("⚠️  Could not determine kernel version from /proc/version")
                return False
    except Exception as e:
        print(f"❌ Error reading kernel version: {e}")
        return False

def provide_installation_guide():
    """Provide comprehensive installation guide."""
    print("\n📚 Installation Guide")
    print("=" * 50)
    
    print("\n1. System Dependencies:")
    print("   Ubuntu/Debian:")
    print("     sudo apt update")
    print("     sudo apt install python3 python3-pip git build-essential")
    print("     sudo apt install linux-tools-common linux-tools-generic")
    
    print("\n   RHEL/CentOS/Fedora:")
    print("     sudo yum install python3 python3-pip git gcc make")
    print("     sudo yum install kernel-tools kernel-devel")
    
    print("\n2. Python Dependencies:")
    print("     pip3 install pandas")
    
    print("\n3. Kernel Requirements:")
    print("     SCHED_DEADLINE requires Linux kernel >= 3.14")
    print("     Check current version: cat /proc/version")
    print("     Upgrade kernel if necessary")
    
    print("\n4. rt-app Installation:")
    print("     git clone https://github.com/scheduler-tools/rt-app.git")
    print("     cd rt-app")
    print("     make")
    print("     sudo make install")
    
    print("\n5. Real-time Setup:")
    print("     Set CPU governor to performance mode")
    print("     Configure real-time priorities")
    print("     Disable CPU frequency scaling for testing")

def main():
    """Main dependency checker."""
    print("🔍 SCHED_DEADLINE Testing Toolkit - Dependency Checker")
    print("=" * 60)
    
    all_good = True
    
    # Check system requirements
    if not check_system_requirements():
        all_good = False
    
    # Check Python dependencies
    if not check_python_dependencies():
        all_good = False
    
    # Check external tools
    if not check_external_tools():
        all_good = False
    
    # Check kernel support
    if not check_kernel_support():
        all_good = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Dependency Check Summary")
    print("=" * 60)
    
    if all_good:
        print("✅ All dependencies are satisfied!")
        print("   You can now use the SCHED_DEADLINE testing toolkit.")
    else:
        print("❌ Some dependencies are missing.")
        print("   Please install the missing components before proceeding.")
        provide_installation_guide()
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
