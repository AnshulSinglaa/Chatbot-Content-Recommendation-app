"""
Setup verification script.
Checks if all dependencies are installed and configured correctly.
"""
import sys
import os
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'pandas',
        'numpy',
        'sentence_transformers',
        'faiss',
        'langchain',
        'langchain_groq',
        'dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'dotenv':
                __import__('dotenv')
            elif package == 'faiss':
                import faiss
            elif package == 'sentence_transformers':
                import sentence_transformers
            elif package == 'langchain_groq':
                import langchain_groq
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"❌ {package} not installed")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages: pip install {' '.join(missing)}")
        return False
    return True


def check_dataset():
    """Check if dataset exists."""
    data_path = Path("data/tmdb_top_movies_cleaned.csv")
    if data_path.exists():
        print(f"✓ Dataset found: {data_path}")
        return True
    print(f"❌ Dataset not found: {data_path}")
    return False


def check_api_key():
    """Check if Groq API key is set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        # Mask the key for security
        masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
        print(f"✓ Groq API key found: {masked_key}")
        return True
    print("❌ GROQ_API_KEY not found")
    print("   Set it using: export GROQ_API_KEY='your-key'")
    print("   Or create a .env file with: GROQ_API_KEY=your-key")
    return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Movie Recommendation Chatbot - Setup Verification")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Dataset", check_dataset),
        ("Groq API Key", check_api_key),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        results.append(check_func())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✓ All checks passed! You're ready to run the chatbot.")
        print("\nRun: python app.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
