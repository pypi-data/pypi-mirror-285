from volstreet.config import logger
from joblib import load
from importlib.resources import files


def load_iv_curve_model():
    resource_path = files("volstreet").joinpath("models")
    model_path = resource_path.joinpath("iv_curve_model_lite.joblib")
    try:
        model = load(model_path)
    except Exception as e:
        logger.warning(f"Unable to load IV curve model: {e}")
        model = None

    return model


iv_curve_model = load_iv_curve_model()
expiry_day_model = None
