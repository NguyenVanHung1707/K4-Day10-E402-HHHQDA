import sys
import os
import pandas as pd
from pathlib import Path

# Thêm src vào sys.path để import
sys.path.append(os.path.abspath('src'))

from core.config import load_settings
from core.utils import read_json
from observability.quality import run_data_quality_checks, build_freshness_report
from observability.reporting import generate_corruption_report

def main():
    print("Bat dau chay buoc 5 cua TV6 (Bao cao So sanh)...")
    settings = load_settings(Path(os.getcwd()))
    
    # Đọc các chỉ số từ TV5
    print("1. Dang tai cac metrics tu TV5...")
    try:
        baseline_metrics = read_json(settings.paths.baseline_metrics)
        corrupted_metrics = read_json(settings.paths.corrupted_metrics)
        repaired_metrics = read_json(settings.paths.repaired_metrics)
    except FileNotFoundError as e:
        print(f"Loi: Thieu file metrics tu TV5 - {e}")
        return

    # Đọc quality & freshness của Corrupted
    corrupted_quality = read_json(settings.paths.quality_dir / "corrupted_quality.json")
    corrupted_freshness = read_json(settings.paths.quality_dir / "corrupted_freshness.json")
    
    # 2. Đánh giá chất lượng của tập dữ liệu Repaired (từ TV3)
    print("2. Dang chay Quality & Freshness checks tren tap Repaired...")
    repaired_csv_path = settings.paths.repaired_clean_csv
    if not repaired_csv_path.exists():
        print(f"Loi: Khong tim thay tap du lieu repaired tu TV3 tai {repaired_csv_path}")
        return
        
    repaired_df = pd.read_csv(repaired_csv_path)
    repaired_quality = run_data_quality_checks(repaired_df, settings, "repaired_quality")
    repaired_freshness = build_freshness_report(repaired_df, settings, settings.paths.quality_dir / "repaired_freshness.json")
    
    print(f"   => Repaired Quality: Pass {repaired_quality['passed_checks']}/{repaired_quality['total_checks']} checks.")
    print(f"   => Repaired Freshness: {repaired_freshness['stale_rows']} stale rows detected.")

    # 3. Tổng hợp Báo cáo So sánh
    print("3. Dang tu dong tong hop bao cao so sanh...")
    generate_corruption_report(
        report_path=settings.paths.comparison_report,
        baseline_metrics=baseline_metrics,
        corrupted_metrics=corrupted_metrics,
        repaired_metrics=repaired_metrics,
        corrupted_quality=corrupted_quality,
        repaired_quality=repaired_quality,
        corrupted_freshness=corrupted_freshness,
        repaired_freshness=repaired_freshness
    )
    
    print("\nHoan tat! Da sinh ra file bao cao:")
    print(f"- {settings.paths.comparison_report}")

if __name__ == "__main__":
    main()
