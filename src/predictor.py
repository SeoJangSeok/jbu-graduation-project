import re
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import euclidean

from src.feature_extractor import extract_features
from src.model_loader import load_models

# 프로젝트 최상위 경로
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 학습 데이터 경로
DATA_PATH = PROJECT_ROOT / "data" / "phishing_url_features.csv"


# 저장된 모델 로드
MODELS, CLUSTER_LABELS = load_models()


# Agglomerative 군집 중심 계산에 사용할 학습 데이터
TRAINING_DATA = pd.read_csv(DATA_PATH)

X = TRAINING_DATA.drop(columns=["url", "label"], errors="ignore")


def is_valid_url(url):
    """
    입력된 문자열이 기본적인 URL 형식을 만족하는지 검사합니다.
    """

    pattern = re.compile(
        r"^(https?://|www\.|WWW\.)"
        r"[^\s/$.?#].[^\s]*$",
        re.IGNORECASE,
    )

    return bool(pattern.match(url))


def calculate_cluster_representatives(X_values, labels):
    """
    Agglomerative Clustering은 predict()와
    cluster_centers_를 제공하지 않기 때문에
    각 군집에 속한 데이터의 평균값을 대표점으로 사용합니다.
    """

    X_values = np.asarray(X_values)
    labels = np.asarray(labels)

    representatives = []

    for label in np.unique(labels):
        cluster_points = X_values[labels == label]

        representative = np.mean(cluster_points, axis=0)

        representatives.append(representative)

    return np.asarray(representatives)


def calculate_phishing_probability(features_array, cluster_centers):
    """
    입력 URL의 특징 벡터와 각 군집 중심 사이의 거리를 구한 뒤
    Softmax를 이용하여 피싱 군집의 확률을 계산합니다.
    """

    features_array = np.asarray(features_array).reshape(-1)

    cluster_centers = np.asarray(cluster_centers)

    # 각 군집 중심과 입력 URL 사이 거리 계산
    distances = [euclidean(features_array, center) for center in cluster_centers]

    # 거리가 가까울수록 높은 확률이 되도록 변환
    probabilities = np.exp(-np.asarray(distances))

    probabilities = probabilities / probabilities.sum()

    cluster_probabilities = {
        label: probability for label, probability in enumerate(probabilities)
    }

    # 기존 프로젝트 로직과 동일하게
    # 군집 1을 피싱 군집으로 사용
    phishing_probability = cluster_probabilities.get(1, 0)

    return phishing_probability * 100


def predict_phishing(url):
    """
    하나의 URL을 입력받아

    1. 15개 특징 추출
    2. 비지도학습 모델별 피싱 확률 계산
    3. 지도학습 모델 확률 계산
    4. 최종 정상/피싱 판정

    을 수행합니다.
    """

    if not is_valid_url(url):
        raise ValueError("유효하지 않은 URL 형식입니다.")

    # URL 특징값 추출
    features_df, features_array = extract_features(url)

    # 모델 가져오기
    kmeans = MODELS["kmeans"]
    gmm = MODELS["gmm"]
    meanshift = MODELS["meanshift"]

    random_forest = MODELS["random_forest"]

    logistic_regression = MODELS["logistic_regression"]

    # -----------------------------------
    # 비지도학습 모델의 군집 중심
    # -----------------------------------

    kmeans_centers = kmeans.cluster_centers_

    gmm_centers = gmm.means_

    meanshift_centers = meanshift.cluster_centers_

    agglomerative_centers = calculate_cluster_representatives(
        X.to_numpy(), CLUSTER_LABELS
    )

    # -----------------------------------
    # 비지도학습 모델 피싱 확률
    # -----------------------------------

    kmeans_prob = calculate_phishing_probability(features_array, kmeans_centers)

    gmm_prob = calculate_phishing_probability(features_array, gmm_centers)

    meanshift_prob = calculate_phishing_probability(features_array, meanshift_centers)

    agglomerative_prob = calculate_phishing_probability(
        features_array, agglomerative_centers
    )

    # -----------------------------------
    # 지도학습 모델 피싱 확률
    # -----------------------------------

    logistic_regression_prob = (
        logistic_regression.predict_proba(features_df)[0][1] * 100
    )

    random_forest_prob = random_forest.predict_proba(features_df)[0][1] * 100

    # -----------------------------------
    # 최종 비지도학습 피싱 확률
    # -----------------------------------

    cluster_probs = [kmeans_prob, gmm_prob, meanshift_prob, agglomerative_prob]

    # 원본 프로젝트 로직
    # 최고값과 최저값 제거
    trimmed_probs = cluster_probs.copy()

    trimmed_probs.remove(max(trimmed_probs))

    trimmed_probs.remove(min(trimmed_probs))

    # 남은 두 확률의 평균
    average_cluster_prob = sum(trimmed_probs) / len(trimmed_probs)

    # 70% 기준 최종 판정
    if average_cluster_prob > 70:
        site_status = "피싱 사이트"

    else:
        site_status = "정상 사이트"

    # GUI에서 사용할 수 있도록
    # 모든 결과를 하나의 딕셔너리로 반환
    return {
        "result": site_status,
        "features": features_df.iloc[0].to_dict(),
        "average_cluster_probability": average_cluster_prob,
        "probabilities": {
            "kmeans": kmeans_prob,
            "gmm": gmm_prob,
            "meanshift": meanshift_prob,
            "agglomerative": agglomerative_prob,
            "random_forest": random_forest_prob,
            "logistic_regression": logistic_regression_prob,
        },
    }
