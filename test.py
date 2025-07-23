import joblib
import lightgbm as lgb
import os

# Import the required classes
from app.models import EnsembleClassifier, LGBMWrapper  # Adjust the import path if needed

# Paths (using raw strings to handle Windows paths safely)
ENSEMBLE_MODEL_PATH = r"D:\Canada\Subjects\Semester -2\AIDI-2005-02 CAPSTONE TERM ll\Bot_detector\app\models\ensemble_classifier.pkl"
NETWORK_MODEL_PATH = r"D:\Canada\Subjects\Semester -2\AIDI-2005-02 CAPSTONE TERM ll\Bot_detector\app\models\final_lightgbm_tuned.txt"  # Note: This path might need correction based on your structure

# Verify file existence
if not os.path.exists(ENSEMBLE_MODEL_PATH):
    print(f"❌ File does not exist: {ENSEMBLE_MODEL_PATH}")
else:
    # Load ensemble model
    try:
        ensemble = joblib.load(ENSEMBLE_MODEL_PATH)
        print(f"✅ Loaded ensemble model from {ENSEMBLE_MODEL_PATH}")
    except Exception as e:
        print(f"❌ Error loading ensemble model: {e}")

# Load network model
try:
    network_model = lgb.Booster(model_file=NETWORK_MODEL_PATH)
    print(f"✅ Loaded network model from {NETWORK_MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading network model: {e}")