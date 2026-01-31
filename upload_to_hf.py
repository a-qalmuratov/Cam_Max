"""Upload files to Hugging Face Spaces."""
import os
from huggingface_hub import HfApi, login

# Login with token - GET TOKEN FROM: https://huggingface.co/settings/tokens
print("🔑 Token olish uchun: https://huggingface.co/settings/tokens")
token = input("Token kiriting: ").strip()
login(token=token)

api = HfApi()
repo_id = "a-qalmuratov/cam-max-bot"
repo_type = "space"

# Files and folders to upload
base_path = r"G:\Coding\FULLL\Cam_Max"

files_to_upload = [
    "Dockerfile",
    "README.md", 
    "requirements.txt",
]

folders_to_upload = [
    "bot",
    "utils",
    "camera",
    "ai",
    "database",
]

print(f"\n📤 {repo_id} ga fayllar yuklanmoqda...\n")

# Upload individual files
for file in files_to_upload:
    file_path = os.path.join(base_path, file)
    if os.path.exists(file_path):
        print(f"  📄 {file} yuklanmoqda...")
        api.upload_file(
            path_or_fileobj=file_path,
            path_in_repo=file,
            repo_id=repo_id,
            repo_type=repo_type,
        )
        print(f"  ✅ {file} yuklandi!")

# Upload folders
for folder in folders_to_upload:
    folder_path = os.path.join(base_path, folder)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        print(f"  📁 {folder}/ yuklanmoqda...")
        api.upload_folder(
            folder_path=folder_path,
            path_in_repo=folder,
            repo_id=repo_id,
            repo_type=repo_type,
        )
        print(f"  ✅ {folder}/ yuklandi!")

print("\n🎉 Barcha fayllar muvaffaqiyatli yuklandi!")
print(f"🔗 Space: https://huggingface.co/spaces/{repo_id}")
