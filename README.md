EADME가 가장 잘 맞아.
# 중부대학교 졸업작품

## 비지도학습 기반 피싱 URL 탐지 시스템

Python 기반 머신러닝을 활용하여 URL의 구조적 특징, 도메인 정보,
웹페이지 특성을 분석하고 피싱 URL을 탐지하는 시스템입니다.

중부대학교 정보보호학과 졸업작품으로 진행한 팀 프로젝트입니다.

---

## 1. 프로젝트 개요

기존 피싱 URL 탐지 방식은 이미 알려진 악성 URL이나
레이블이 존재하는 데이터를 기반으로 탐지하는 경우가 많습니다.

본 프로젝트에서는 URL에서 피싱 사이트가 가지는 특징을 추출한 후
비지도학습 알고리즘을 적용하여 정상 URL과 피싱 URL의 패턴을 분석하고
새로운 URL의 피싱 가능성을 판단하는 시스템을 구현했습니다.

최종적으로 사용자가 URL을 입력하면 특징값을 추출하고,
각 머신러닝 모델의 결과를 기반으로 피싱 여부를 확인할 수 있는
GUI 프로그램을 구현했습니다.

---

## 2. 주요 기능

- URL 기반 15개 특징값 추출
- K-Means 기반 URL 군집화
- Gaussian Mixture Model(GMM) 기반 URL 군집화
- MeanShift 기반 URL 군집화
- Agglomerative Clustering 기반 URL 군집화
- Random Forest 및 Logistic Regression 비교
- 모델별 피싱 확률 계산
- GUI 기반 URL 입력 및 분석 결과 확인

---

## 3. Feature Engineering

URL에서 총 15개의 특징을 추출하여 머신러닝 모델의 입력값으로 사용했습니다.

### URL 구조적 특징

- IP 주소 포함 여부
- URL 길이
- URL 단축 서비스 사용 여부
- `@` 문자 포함 여부
- `//` 리다이렉션 사용 여부
- 도메인의 `-` 사용 여부
- 서브도메인 사용 여부

### 도메인 및 보안 특징

- 도메인 등록 기간
- Favicon 위치
- Port 사용 여부
- HTTPS Token
- 도메인 수명
- DNS Record

### 웹페이지 행동 특징

- Redirect 횟수
- 우클릭 방지 여부

---

## 4. Dataset

총 22,000개의 URL 데이터를 활용했습니다.

| 구분 | 데이터 수 |
|---|---:|
| 정상 URL | 15,000 |
| 피싱 URL | 7,000 |
| 총 데이터 | 22,000 |

---

## 5. 담당 역할

본 프로젝트는 4인 팀 프로젝트로 진행되었습니다.

### 담당 업무

- MeanShift 기반 비지도학습 모델 구현 및 성능 확인
- URL 데이터 전처리 및 학습 데이터 구성 참여
- URL Feature 추출 과정 구현 참여
- 팀원 코드 오류 분석 및 수정
- 각 모듈 통합 과정 참여
- GUI 기반 URL 판별 프로그램 구현 참여

### 담당 알고리즘

**MeanShift Clustering**

MeanShift는 데이터의 밀도가 높은 영역을 탐색하여
클러스터 중심을 찾아가는 비지도학습 알고리즘입니다.

본 프로젝트에서는 URL에서 추출한 15개 특징값을 기반으로
정상 URL과 피싱 URL의 패턴을 군집화하는 데 활용했습니다.

## 모델 성능 평가

기존 졸업작품에서는 전체 22,000건의 데이터를 이용하여 모델을 학습하고
동일 데이터에서 성능을 확인하였습니다.

포트폴리오 정리 과정에서 보다 객관적인 일반화 성능을 확인하기 위해
데이터를 Train/Test로 분리하여 모델을 다시 학습하고 평가하였습니다.

### 평가 조건

- 전체 데이터: 22,000건
  - 정상 URL: 15,000건
  - 피싱 URL: 7,000건
- Train: 17,600건
- Test: 4,400건
  - 정상 URL: 3,000건
  - 피싱 URL: 1,400건
- Train/Test 비율: 8:2
- 동일 hostname이 Train과 Test에 동시에 포함되지 않도록 Group Split 적용
- Positive Class: 피싱 URL (`label=1`)

평가 지표로 Accuracy뿐만 아니라 클래스 불균형을 고려하기 위해
Balanced Accuracy, Precision, Recall, F1-score를 함께 확인하였습니다.

### Test Set 성능

| Model | Accuracy | Balanced Accuracy | Precision | Recall | F1-score |
|---|---:|---:|---:|---:|---:|
| Random Forest | **96.82%** | **96.45%** | **94.62%** | 95.43% | **95.02%** |
| Logistic Regression | 96.23% | 96.41% | 91.69% | 96.93% | 94.24% |
| K-Means | 91.73% | 93.69% | 79.80% | **99.07%** | 88.40% |
| GMM | 91.64% | 93.60% | 79.66% | 99.00% | 88.28% |
| Agglomerative Clustering* | 91.55% | 93.55% | 79.44% | **99.07%** | 88.18% |
| MeanShift | 82.93% | 75.50% | 86.34% | 55.07% | 67.25% |

\* Agglomerative Clustering은 새로운 데이터에 대한 `predict()` 기능을 제공하지 않기 때문에,
Train 데이터에서 생성된 군집의 중심점을 계산한 뒤 Test 데이터를 가장 가까운 군집 중심에
배정하는 nearest-centroid 방식으로 평가하였습니다.

### Confusion Matrix 결과

| Model | TN | FP | FN | TP |
|---|---:|---:|---:|---:|
| K-Means | 2,649 | 351 | 13 | 1,387 |
| GMM | 2,646 | 354 | 14 | 1,386 |
| MeanShift | 2,878 | 122 | 629 | 771 |
| Agglomerative Clustering | 2,641 | 359 | 13 | 1,387 |
| Random Forest | 2,924 | 76 | 64 | 1,336 |
| Logistic Regression | 2,877 | 123 | 43 | 1,357 |

### 결과 분석

**Random Forest**는 Accuracy 96.82%, Balanced Accuracy 96.45%,
F1-score 95.02%로 전체 모델 중 가장 균형 잡힌 성능을 보였습니다.
정상 URL을 피싱으로 잘못 분류한 경우(FP)는 76건,
피싱 URL을 정상으로 놓친 경우(FN)는 64건으로 두 클래스 모두 안정적으로 분류하였습니다.

**Logistic Regression**은 Accuracy 96.23%, Recall 96.93%를 기록했습니다.
Random Forest보다 전체적인 F1-score는 조금 낮았지만,
피싱 URL을 놓치는 FN이 43건으로 지도학습 모델 중 가장 적었습니다.

**K-Means와 GMM**은 각각 99.07%, 99.00%의 높은 Recall을 기록하여
피싱 URL을 거의 놓치지 않았습니다.
다만 Precision은 약 80%로, 정상 URL을 피싱으로 잘못 판단하는
False Positive가 상대적으로 많이 발생했습니다.

**Agglomerative Clustering** 역시 Recall 99.07%로 피싱 탐지율은 높았지만,
False Positive가 359건 발생하여 K-Means, GMM과 유사하게
정상 URL을 피싱으로 과도하게 판단하는 경향을 보였습니다.

**MeanShift**는 Precision 86.34%에 비해 Recall이 55.07%로 낮았습니다.
피싱 URL 1,400건 중 629건을 정상으로 분류하여,
현재 Bandwidth 설정에서는 다른 모델보다 피싱 탐지 성능이 낮은 것으로 확인되었습니다.

### 졸업작품 당시 결과

졸업작품 보고서에서는 전체 22,000건의 데이터를 기반으로 다음과 같은 결과를 기록했습니다.

| Model | 보고서 기록 결과 |
|---|---:|
| K-Means | 91.72% |
| GMM | 91.67% |
| MeanShift | 88.26% |
| Agglomerative Clustering | 88.37% |
| Random Forest | 96.91% |
| Logistic Regression | 95.36% |

당시에는 학습 데이터와 독립된 Test Set을 별도로 구성하지 않아
모델의 일반화 성능을 충분히 검증하지 못했다는 한계가 있었습니다.

이후 포트폴리오 정리 과정에서 hostname 기반 Train/Test 분리를 적용하고,
Precision, Recall, F1-score 등 추가 지표를 사용하여 모델을 재평가하였습니다.