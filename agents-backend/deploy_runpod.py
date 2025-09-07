#!/usr/bin/env python3
"""
Deploy script for RunPod
This script helps you deploy your Intelligent Ambience system to RunPod
"""

import os
import subprocess
import json
import time

def check_runpod_cli():
    """Check if RunPod CLI is installed"""
    try:
        result = subprocess.run(["runpod", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ RunPod CLI found: {result.stdout.strip()}")
            return True
        else:
            print("❌ RunPod CLI not found")
            return False
    except FileNotFoundError:
        print("❌ RunPod CLI not installed")
        return False

def install_runpod_cli():
    """Install RunPod CLI"""
    print("📦 Installing RunPod CLI...")
    try:
        subprocess.run(["pip", "install", "runpod"], check=True)
        print("✅ RunPod CLI installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install RunPod CLI: {e}")
        return False

def build_and_deploy():
    """Build and deploy to RunPod"""
    print("🚀 Building and deploying to RunPod...")
    
    # Check if we're logged in
    try:
        result = subprocess.run(["runpod", "whoami"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not logged in to RunPod. Please run: runpod login")
            return False
    except:
        print("❌ RunPod CLI not working. Please check installation.")
        return False
    
    # Build the pod
    print("🔨 Building pod...")
    try:
        subprocess.run([
            "runpod", "build", 
            "--name", "intelligent-ambience",
            "--config", "runpod_config.json"
        ], check=True)
        print("✅ Pod built successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build pod: {e}")
        return False
    
    # Deploy the pod
    print("🚀 Deploying pod...")
    try:
        result = subprocess.run([
            "runpod", "deploy",
            "--name", "intelligent-ambience"
        ], capture_output=True, text=True, check=True)
        print("✅ Pod deployed successfully")
        print(f"Deployment result: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to deploy pod: {e}")
        return False

def test_deployment():
    """Test the deployed system"""
    print("🧪 Testing deployment...")
    
    test_payload = {
        "input": {
            "query": "Sarajevo, Bosnia and Herzegovina",
            "img_url": "https://farm5.staticflickr.com/4888/45890544791_0a419c887b_c.jpg",
            "user_feedback": ""
        }
    }
    
    try:
        # This would require the pod ID from deployment
        print("📝 To test your deployment, use the RunPod web interface or API")
        print(f"Test payload: {json.dumps(test_payload, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main deployment process"""
    print("🎵 Intelligent Ambience - RunPod Deployment")
    print("=" * 50)
    
    # Check RunPod CLI
    if not check_runpod_cli():
        if not install_runpod_cli():
            print("❌ Cannot proceed without RunPod CLI")
            return
    
    # Build and deploy
    if build_and_deploy():
        print("🎉 Deployment successful!")
        print("\nNext steps:")
        print("1. Check your RunPod dashboard for the pod status")
        print("2. Test the deployment using the web interface")
        print("3. Monitor logs for any issues")
    else:
        print("❌ Deployment failed")

if __name__ == "__main__":
    main()
