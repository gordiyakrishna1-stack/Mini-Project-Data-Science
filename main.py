"""
Main Execution Script
Complete Chinese Disease Analysis Pipeline
"""

import sys
import warnings
warnings.filterwarnings('ignore')

from data_loader import DataLoader, get_clean_data
from indicators import HealthIndicators
from visualizations import DiseaseVisualizer
from analysis import DiseaseAnalyzer
from config import VERBOSE, OUTPUT_DIR
from indicators_exporter import IndicatorsExporter
from report_generator import ReportGenerator
from dashboard_generator import DashboardGenerator
from warehouse_etl import MedallionETL


def main():
    """Main execution pipeline"""
    
    print("\n" + "="*100)
    print("CHINESE DISEASE DATA ANALYSIS - COMPLETE PIPELINE")
    print("="*100)
    
    # PHASE 0: Bronze/Silver/Gold Warehouse ETL
    print("\n[PHASE 0: WAREHOUSE ETL (BRONZE/SILVER/GOLD)]")
    print("-" * 100)

    try:
        warehouse_etl = MedallionETL()
        warehouse_etl.run()
        print("✓ Phase 0 Complete: Warehouse ETL completed")
    except Exception as e:
        print(f"✗ Error during warehouse ETL: {e}")
        return False

    # PHASE 1: Load and Preprocess Data
    print("\n[PHASE 1: DATA LOADING & PREPROCESSING]")
    print("-" * 100)
    
    try:
        df = get_clean_data()
        print("\n✓ Phase 1 Complete: Data loaded and preprocessed")
    except Exception as e:
        print(f"\n✗ Error loading data: {e}")
        return False
    
    # PHASE 2: Calculate Health Indicators
    print("\n[PHASE 2: HEALTH INDICATORS CALCULATION]")
    print("-" * 100)
    
    try:
        indicators_calc = HealthIndicators(df)
        indicators = indicators_calc.calculate_all()
        print("✓ Phase 2 Complete: All 20 health indicators calculated")
    except Exception as e:
        print(f"✗ Error calculating indicators: {e}")
        return False
    
    # PHASE 3: Generate Visualizations
    print("\n[PHASE 3: VISUALIZATIONS]")
    print("-" * 100)
    
    try:
        visualizer = DiseaseVisualizer(df)
        visualizer.generate_all_visualizations()
        print("✓ Phase 3 Complete: All visualizations generated")
    except Exception as e:
        print(f"✗ Error generating visualizations: {e}")
        return False
    
    # PHASE 4: Comprehensive Analysis & Reporting
    print("\n[PHASE 4: COMPREHENSIVE ANALYSIS & REPORTING]")
    print("-" * 100)
    
    try:
        analyzer = DiseaseAnalyzer(df, indicators)
        report = analyzer.generate_full_report()
        print("✓ Phase 4 Complete: Full analysis report generated")
    except Exception as e:
        print(f"✗ Error generating analysis: {e}")
        return False
    
    # PHASE 5: Export Indicators to CSV
    print("\n[PHASE 5: EXPORTING INDICATORS TO CSV]")
    print("-" * 100)
    
    try:
        exporter = IndicatorsExporter(df, indicators)
        exporter.export_all()
        print("✓ Phase 5 Complete: All indicators exported to CSV format")
    except Exception as e:
        print(f"✗ Error exporting indicators: {e}")
        return False
    
    # PHASE 6: Generate PDF Reports & Executive Summary
    print("\n[PHASE 6: GENERATING PDF REPORTS & EXECUTIVE SUMMARY]")
    print("-" * 100)
    
    try:
        reporter = ReportGenerator(df, indicators)
        reporter.generate_all_reports()
        print("✓ Phase 6 Complete: PDF reports and executive summary generated")
    except Exception as e:
        print(f"✗ Error generating reports: {e}")
        return False
    
    # PHASE 7: Generate Interactive Dashboards
    print("\n[PHASE 7: GENERATING INTERACTIVE DASHBOARDS]")
    print("-" * 100)
    
    try:
        dashboard_gen = DashboardGenerator(df)
        dashboard_gen.generate_all_dashboards()
        print("✓ Phase 7 Complete: All interactive dashboards generated")
    except Exception as e:
        print(f"✗ Error generating dashboards: {e}")
        return False
    
    # Final Status
    print("\n" + "="*100)
    print("PIPELINE EXECUTION COMPLETE - ALL PHASES SUCCESSFUL")
    print("="*100)
    print(f"\n✓ All outputs saved to: {OUTPUT_DIR}")
    print(f"✓ Charts saved to: {OUTPUT_DIR}/charts")
    print(f"\n📊 GENERATED OUTPUTS:")
    print(f"   • CSV Indicators: indicators_summary.csv, disease_indicators.csv, etc.")
    print(f"   • PDF Reports: Analysis_Report_Full.pdf")
    print(f"   • Executive Summary: Executive_Summary.txt")
    print(f"   • Markdown Report: Analysis_Report.md")
    print(f"   • Interactive Dashboards: dashboard_master.html (and 5 specialized dashboards)")
    print(f"\n🌐 TO VIEW INTERACTIVE DASHBOARDS:")
    print(f"   • Open 'dashboard_master.html' in your web browser")
    print(f"   • All visualizations are fully interactive with hover tooltips")
    print(f"   • You can zoom, pan, and download charts as PNG files")
    print(f"\n✓ ANALYSIS COMPLETE - Ready for professional submission")
    
    return True


def run_analysis_only(data_path=None):
    """Run analysis only (without visualizations)"""
    print("\n[RUNNING ANALYSIS ONLY]")
    print("-" * 100)
    
    df = get_clean_data(data_path) if data_path else get_clean_data()
    analyzer = DiseaseAnalyzer(df)
    report = analyzer.generate_full_report()
    
    return report


def run_visualizations_only(data_path=None):
    """Run visualizations only (without analysis)"""
    print("\n[RUNNING VISUALIZATIONS ONLY]")
    print("-" * 100)
    
    df = get_clean_data(data_path) if data_path else get_clean_data()
    visualizer = DiseaseVisualizer(df)
    visualizer.generate_all_visualizations()
    
    return True


def run_reports_and_dashboards(data_path=None):
    """Generate reports and interactive dashboards only"""
    print("\n[GENERATING REPORTS AND DASHBOARDS]")
    print("-" * 100)
    
    df = get_clean_data(data_path) if data_path else get_clean_data()
    
    # Generate indicators export
    exporter = IndicatorsExporter(df)
    exporter.export_all()
    
    # Generate reports
    reporter = ReportGenerator(df)
    reporter.generate_all_reports()
    
    # Generate dashboards
    dashboard_gen = DashboardGenerator(df)
    dashboard_gen.generate_all_dashboards()
    
    print("\n✓ Reports and dashboards generated successfully!")
    print(f"📊 Open 'dashboard_master.html' in your browser to view interactive dashboards")
    
    return True


def run_etl_only():
    """Run only the warehouse ETL pipeline"""
    print("\n[RUNNING WAREHOUSE ETL ONLY]")
    print("-" * 100)
    etl = MedallionETL()
    etl.run()
    return True


if __name__ == "__main__":
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "analysis":
            run_analysis_only()
        elif command == "visualizations":
            run_visualizations_only()
        elif command == "reports":
            run_reports_and_dashboards()
        elif command == "etl":
            run_etl_only()
        elif command == "full":
            main()
        else:
            print(f"Unknown command: {command}")
            print("\nUsage:")
            print("  python main.py               - Run full pipeline (default)")
            print("  python main.py full          - Run full pipeline")
            print("  python main.py etl           - Run Bronze/Silver/Gold ETL only")
            print("  python main.py analysis      - Run analysis only")
            print("  python main.py visualizations - Run visualizations only")
            print("  python main.py reports       - Generate reports and dashboards only")
    else:
        # Default: run full pipeline
        success = main()
        sys.exit(0 if success else 1)
