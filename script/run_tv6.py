import sys
import os
import pandas as pd
from pathlib import Path

# Thêm src vào sys.path để import
sys.path.append(os.path.abspath('src'))

from core.config import load_settings
from ingestion.corruption import corrupt_clean_dataframe
from observability.quality import run_data_quality_checks, build_freshness_report
from core.utils import write_csv, write_json

def main():
    print("Bat dau chay kich ban TV6 (Corruption & Observability)...")
    settings = load_settings(Path(os.getcwd()))
    
    clean_csv_path = settings.paths.clean_csv
    if not clean_csv_path.exists():
        print(f"Loi: Khong tim thay file du lieu sach tai {clean_csv_path}")
        return
        
    # 1. Load clean data
    print("1. Dang tai du lieu sach...")
    df = pd.read_csv(clean_csv_path)
    
    # 2. Chạy hàm tạo dữ liệu lỗi
    print("2. Dang tao du lieu loi (Corruption)...")
    log_path = settings.paths.corruption_log
    corrupted_df = corrupt_clean_dataframe(df, log_path)
    
    # 3. Lưu Corrupted Dataset ra file để TV4 dùng
    print("3. Dang luu Corrupted Dataset (CSV & JSON) de ban giao cho TV4...")
    write_csv(corrupted_df, settings.paths.corrupted_clean_csv)
    # Convert to list of dicts for JSON
    write_json(settings.paths.corrupted_clean_json, corrupted_df.to_dict(orient="records"))
    
    # 4. Chạy lại bài test Observability trên dữ liệu lỗi
    print("4. Chay kiem tra Quality & Freshness tren du lieu loi...")
    quality = run_data_quality_checks(corrupted_df, settings, "corrupted_quality")
    freshness = build_freshness_report(corrupted_df, settings, settings.paths.quality_dir / "corrupted_freshness.json")
    
    print(f"   => Quality: Pass {quality['passed_checks']}/{quality['total_checks']} checks.")
    print(f"   => Freshness: {freshness['stale_rows']} stale rows detected.")
    
    print("\nHoan tat! Cac file da duoc tao:")
    print(f"- {settings.paths.corrupted_clean_csv}")
    print(f"- {settings.paths.corrupted_clean_json}")
    print(f"- {settings.paths.corruption_log}")
    print(f"- {settings.paths.quality_dir / 'corrupted_quality.json'}")
    print(f"- {settings.paths.quality_dir / 'corrupted_freshness.json'}")

if __name__ == "__main__":
    main()
