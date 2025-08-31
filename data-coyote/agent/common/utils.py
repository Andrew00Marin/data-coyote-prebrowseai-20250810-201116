import os
import yaml
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(f"Data Coyote | {name}")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
        logger.addHandler(ch)
    return logger

def _expand_env_in_obj(obj):
    if isinstance(obj, dict): return {k:_expand_env_in_obj(v) for k,v in obj.items()}
    if isinstance(obj, list): return [_expand_env_in_obj(v) for v in obj]
    if isinstance(obj, str):  return os.path.expandvars(obj)
    return obj

def load_config(path: str = "config/config.yaml") -> dict:
    with open(path, "r") as f:
        cfg = yaml.safe_load(f)
    return _expand_env_in_obj(cfg)

def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)

def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
