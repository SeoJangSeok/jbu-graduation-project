from pathlib import Path

import joblib

# 프로젝트 최상위 폴더
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 모델 저장 폴더
MODELS_DIR = PROJECT_ROOT / "models"


def load_models():
    """
    학습이 완료된 모델들을 models 폴더에서 불러옵니다.
    """

    models = {
        "kmeans": joblib.load(MODELS_DIR / "kmeans.pkl"),
        "gmm": joblib.load(MODELS_DIR / "gmm.pkl"),
        "meanshift": joblib.load(MODELS_DIR / "meanshift.pkl"),
        "agglomerative": joblib.load(MODELS_DIR / "agglomerative.pkl"),
        "random_forest": joblib.load(MODELS_DIR / "random_forest.pkl"),
        "logistic_regression": joblib.load(MODELS_DIR / "logistic_regression.pkl"),
    }

    # Agglomerative는 새로운 데이터에 predict()를 사용할 수 없기 때문에
    # 학습 당시의 군집 레이블도 별도로 불러옵니다.
    cluster_labels = joblib.load(MODELS_DIR / "agglomerative_labels.pkl")

    return models, cluster_labels
