def UnzipFile(zip_file_path, extract_to_dir):
    import zipfile
    import os

    # 确保解压目录存在
    if not os.path.exists(extract_to_dir):
        os.makedirs(extract_to_dir)
    
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_dir)
        # print(f"Extracted all files to {extract_to_dir