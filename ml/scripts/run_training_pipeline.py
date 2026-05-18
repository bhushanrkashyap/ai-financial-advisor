"""
Master Training Pipeline Script.
Orchestrates all data preprocessing and model training steps.
Runs: preprocessing -> market features -> house price models -> portfolio optimization.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).parent.parent.parent
SCRIPTS_DIR = Path(__file__).parent


def run_stage(stage_name, script_path):
    """Run a single training stage."""
    logger.info(f"\n{'='*60}")
    logger.info(f"STAGE: {stage_name}")
    logger.info(f"{'='*60}")
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("stage_module", script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["stage_module"] = module
        spec.loader.exec_module(module)
        
        # Run main function if it exists
        if hasattr(module, 'main'):
            result = module.main()
            logger.info(f"✓ {stage_name} completed successfully")
            return result
        else:
            logger.warning(f"No main() function found in {script_path}")
            return None
    
    except Exception as e:
        logger.error(f"✗ {stage_name} failed with error: {e}")
        raise


def main():
    """Run complete training pipeline."""
    logger.info(f"Starting ML Training Pipeline at {datetime.now()}")
    logger.info(f"Project directory: {PROJECT_DIR}")
    
    stages = [
        ("House Price Data Preprocessing", SCRIPTS_DIR / "01_house_price_preprocessing.py"),
        ("Market Features Extraction", SCRIPTS_DIR / "02_market_features_extraction.py"),
        ("House Price Model Training", SCRIPTS_DIR / "03_train_house_price_models.py"),
        ("Portfolio Optimization", SCRIPTS_DIR / "04_portfolio_optimization.py"),
    ]
    
    results = {}
    failed_stages = []
    
    for stage_name, script_path in stages:
        try:
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                failed_stages.append(stage_name)
                continue
            
            result = run_stage(stage_name, script_path)
            results[stage_name] = result
            
        except Exception as e:
            logger.error(f"Failed at stage: {stage_name}")
            logger.error(f"Error: {e}")
            failed_stages.append(stage_name)
            # Continue to next stage instead of stopping
            continue
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TRAINING PIPELINE SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total stages: {len(stages)}")
    logger.info(f"Completed: {len(stages) - len(failed_stages)}")
    logger.info(f"Failed: {len(failed_stages)}")
    
    if failed_stages:
        logger.warning(f"Failed stages: {', '.join(failed_stages)}")
        return False
    else:
        logger.info("✓ All stages completed successfully!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
