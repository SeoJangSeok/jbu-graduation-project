import math
import tkinter as tk
from pathlib import Path
from threading import Thread
from tkinter import messagebox, ttk

from PIL import Image, ImageTk

from src.predictor import is_valid_url, predict_phishing

# 프로젝트 최상위 폴더
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 이미지 파일 폴더
ASSETS_DIR = PROJECT_ROOT / "app" / "assets"


def load_image(filename, size=(100, 100)):
    image = Image.open(ASSETS_DIR / filename)

    image = image.resize(size, Image.LANCZOS)

    return ImageTk.PhotoImage(image)


# ==========================================
# GUI 기본 설정
# ==========================================

root = tk.Tk()

root.title("피싱체크_V1")

root.geometry("900x900")


# 운영체제에 따라 ico가 지원되지 않을 수 있음
try:
    root.iconbitmap(ASSETS_DIR / "chk.ico")

except tk.TclError:
    pass


# ==========================================
# 상단 네비게이션 바
# ==========================================

nav_frame = tk.Frame(root, height=50)

nav_frame.grid(row=0, column=0, sticky="ew")

nav_frame.grid_columnconfigure(0, weight=1)

nav_frame.grid_columnconfigure(1, weight=1)

nav_frame.grid_columnconfigure(2, weight=1)


home_button = tk.Button(
    nav_frame,
    text="HOME",
    font=("Arial", 14, "bold"),
    borderwidth=0,
    command=lambda: show_frame(main_frame),
)

home_button.grid(row=0, column=0, sticky="ew", padx=5, pady=5)


info_button = tk.Button(
    nav_frame,
    text="INFO",
    font=("Arial", 14, "bold"),
    borderwidth=0,
    command=lambda: show_frame(info_frame),
)

info_button.grid(row=0, column=1, sticky="ew", padx=5, pady=5)


team_button = tk.Button(
    nav_frame,
    text="TEAM",
    font=("Arial", 14, "bold"),
    borderwidth=0,
    command=lambda: show_frame(team_frame),
)

team_button.grid(row=0, column=2, sticky="ew", padx=5, pady=5)


# ==========================================
# 페이지 프레임 생성
# ==========================================

main_frame = tk.Frame(root)
team_frame = tk.Frame(root)
info_frame = tk.Frame(root)


def setup_frame(frame):
    for i in range(8):
        frame.grid_rowconfigure(i, weight=1)

    for i in range(3):
        frame.grid_columnconfigure(i, weight=1)


for frame in (main_frame, team_frame, info_frame):
    setup_frame(frame)

    frame.grid(row=1, column=0, sticky="nsew")


root.grid_rowconfigure(1, weight=1)

root.grid_columnconfigure(0, weight=1)


def show_frame(frame):
    frame.tkraise()


# ==========================================
# HOME 페이지
# ==========================================


def create_main_widgets():

    # 타이틀 이미지
    title_image = load_image("타이틀.png", size=(600, 200))

    title_label = tk.Label(main_frame, image=title_image)

    title_label.image = title_image

    title_label.grid(row=0, column=0, columnspan=3, pady=20, sticky="n")

    # URL 입력 영역
    url_frame = tk.Frame(main_frame)

    url_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky="ew")

    tk.Label(url_frame, text="검사할 URL 입력:", font=("Malgun Gothic", 18)).grid(
        row=0, column=0, padx=20, pady=10, sticky="e"
    )

    global url_entry

    url_entry = tk.Entry(url_frame, width=40, font=("Malgun Gothic", 18))

    url_entry.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

    tk.Button(
        url_frame, text="확인", command=check_url, font=("Malgun Gothic", 18)
    ).grid(row=0, column=2, padx=10, pady=10, sticky="w")

    for column in range(3):
        url_frame.grid_columnconfigure(column, weight=1)

    # ======================================
    # 최종 판별 결과
    # ======================================

    result_frame = tk.Frame(main_frame, borderwidth=2, relief="groove", bg="white")

    result_frame.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="nsew")

    global result_label

    result_label = tk.Label(
        result_frame, text="", font=("Malgun Gothic", 14), bg="white"
    )

    result_label.pack(expand=True, fill="both")

    # ======================================
    # 제목
    # ======================================

    tk.Label(
        main_frame, text="▷ 특징별 판별 결과", font=("Malgun Gothic", 19, "bold")
    ).grid(row=4, column=2, pady=5, padx=10, sticky="w")

    tk.Label(main_frame, text="▷ 피싱확률", font=("Malgun Gothic", 19, "bold")).grid(
        row=4, column=0, pady=5, padx=10, sticky="w"
    )

    # ======================================
    # 특징 결과
    # ======================================

    features_frame = tk.Frame(main_frame, borderwidth=2, relief="groove", bg="white")

    features_frame.grid(row=5, column=2, padx=10, pady=10, sticky="nsew")

    global features_text

    features_text = tk.Text(
        features_frame,
        font=("Malgun Gothic", 15),
        bg="white",
        wrap="word",
        height=10,
        width=50,
    )

    features_text.pack(expand=True, fill="both")

    feature_names = [
        "having_ip_address",
        "url_length",
        "shortening_service",
        "having_at_symbol",
        "double_slash_redirecting",
        "prefix_suffix",
        "having_sub_domain",
        "domain_registration_length",
        "favicon",
        "port",
        "https_token",
        "age_of_domain",
        "dns_record",
        "count_redirection",
        "disabling_right_click",
    ]

    features_text.insert(
        tk.END,
        "\n".join(f"{index + 1}. {name}: " for index, name in enumerate(feature_names)),
    )

    features_text.config(state=tk.DISABLED)

    # ======================================
    # 모델별 확률 영역
    # ======================================

    global accuracy_frame

    accuracy_frame = tk.Frame(main_frame, borderwidth=2, relief="groove", bg="white")

    accuracy_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

    tk.Label(
        accuracy_frame,
        text=(
            "[비지도 학습]\n"
            "K-means: \n"
            "GMM: \n"
            "MeanShift: \n"
            "Agglomerative: \n\n"
            "[지도 학습]\n"
            "Random Forest: \n"
            "Logistic Regression: "
        ),
        font=("Malgun Gothic", 15),
        anchor="nw",
        justify="left",
        bg="white",
    ).grid(row=0, column=0, padx=10, pady=10, sticky="nw")

    tk.Label(
        main_frame,
        text=(
            "COPYRIGHT© 2024 JOONGBU UNIVERSITY "
            "INFORMATION SECURITY ENGINEERING "
            "4조. ALL RIGHTS RESERVED."
        ),
        font=("Malgun Gothic", 10),
        bg=main_frame.cget("bg"),
    ).grid(row=6, column=0, columnspan=3, pady=10, sticky="s")


# ==========================================
# URL 검사 시작
# ==========================================


def check_url():

    url = url_entry.get().strip()

    if not url:
        messagebox.showerror("오류", "URL을 입력해주세요.")

        return

    if not is_valid_url(url):
        messagebox.showerror("오류", "유효하지 않은 URL 형식입니다.")

        return

    show_loading_dialog()

    # 특징 추출 과정에서 네트워크 요청 등이 발생하므로
    # 별도 Thread에서 실행
    thread = Thread(target=background_check_url, args=(url,), daemon=True)

    thread.start()


# ==========================================
# 로딩 애니메이션
# ==========================================


class PulsatingLoading(tk.Canvas):
    def __init__(
        self,
        parent,
        size=100,
        arc_width=6,
        base_speed=8,
        color="green",
        *args,
        **kwargs,
    ):

        super().__init__(parent, width=size, height=size, *args, **kwargs)

        self.size = size
        self.arc_width = arc_width
        self.base_speed = base_speed
        self.color = color

        self.angle = 0
        self.base_arc_length = 90
        self.speed_variation = 0

        self.create_arc_shape()
        self.animate()

    def create_arc_shape(self):

        self.delete("all")

        pulsating_arc_length = (
            self.base_arc_length + math.sin(math.radians(self.angle)) * 30
        )

        self.create_arc(
            self.arc_width,
            self.arc_width,
            self.size - self.arc_width,
            self.size - self.arc_width,
            start=self.angle,
            extent=(pulsating_arc_length),
            outline=self.color,
            width=self.arc_width,
            style=tk.ARC,
        )

    def animate(self):

        self.speed_variation = math.sin(math.radians(self.angle)) * 1.5

        self.angle = (self.angle + self.base_speed + self.speed_variation) % 360

        self.create_arc_shape()

        self.after(20, self.animate)


def show_loading_dialog():

    global loading_dialog

    loading_dialog = tk.Toplevel(root)

    loading_dialog.title("처리중")

    dialog_width = 350
    dialog_height = 200

    root_width = root.winfo_width()

    root_height = root.winfo_height()

    root_x = root.winfo_rootx()

    root_y = root.winfo_rooty()

    x = root_x + (root_width - dialog_width) // 2

    y = root_y + (root_height - dialog_height) // 2

    loading_dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")

    tk.Label(
        loading_dialog, text=("잠시만 기다려 주세요..."), font=("Malgun Gothic", 12)
    ).pack(pady=10)

    loading = PulsatingLoading(
        loading_dialog, size=80, arc_width=6, base_speed=8, color="green"
    )

    loading.pack(pady=10)


# ==========================================
# 확률 Progress Bar
# ==========================================


def create_bar(parent_frame, label, value):

    inner_frame = tk.Frame(parent_frame, bg=parent_frame.cget("bg"))

    inner_frame.pack(fill="x", pady=5, padx=5)

    tk.Label(
        inner_frame,
        text=label,
        font=("Malgun Gothic", 15),
        width=30,
        anchor="w",
        bg=inner_frame.cget("bg"),
    ).pack(side=tk.LEFT, padx=(5, 0))

    bar = ttk.Progressbar(inner_frame, mode="determinate", maximum=100)

    bar["value"] = value

    bar.pack(side=tk.LEFT, fill="x", expand=True, padx=(5, 0))

    style = ttk.Style()

    style.configure(
        "custom.Horizontal.TProgressbar", troughcolor="white", background="green"
    )

    bar["style"] = "custom.Horizontal.TProgressbar"

    tk.Label(
        inner_frame,
        text=f"{value:.2f}%",
        font=("Malgun Gothic", 15),
        bg=inner_frame.cget("bg"),
    ).pack(side=tk.RIGHT, padx=(10, 0))


# ==========================================
# 검사 결과 GUI 반영
# ==========================================


def update_gui(prediction):

    try:
        result = prediction["result"]

        features = prediction["features"]

        average_cluster_prob = prediction["average_cluster_probability"]

        probabilities = prediction["probabilities"]

        # 최종 결과
        result_text = (
            f"URL: '{url_entry.get()}'\n"
            f"피싱확률: "
            f"{average_cluster_prob:.2f}%\n"
            f"피싱여부: "
            f"{result}"
        )

        if result == "정상 사이트":
            result_color = "#0000FF"

        else:
            result_color = "red"

        result_label.config(
            text=result_text,
            fg=result_color,
            justify="left",
            font=("Malgun Gothic", 23, "bold"),
        )

        # ==================================
        # 15개 특징 표시
        # ==================================

        features_text.config(state=tk.NORMAL)

        features_text.delete(1.0, tk.END)

        features_text.tag_configure("black", foreground="black")

        features_text.tag_configure("red", foreground="red")

        features_text.tag_configure("orange", foreground="#FFA500")

        features_text.tag_configure("blue", foreground="blue")

        for index, (key, value) in enumerate(features.items()):
            if value == -1:
                color_tag = "red"
                status_text = "피싱"

            elif value == 0:
                color_tag = "orange"
                status_text = "의심"

            else:
                color_tag = "blue"
                status_text = "정상"

            features_text.insert(tk.END, f"{index + 1}. {key}: ", "black")

            features_text.insert(tk.END, status_text, color_tag)

            features_text.insert(tk.END, "\n")

        features_text.config(state=tk.DISABLED)

        # ==================================
        # 기존 모델 결과 초기화
        # ==================================

        for widget in accuracy_frame.winfo_children():
            widget.destroy()

        # ==================================
        # 비지도학습
        # ==================================

        unsupervised_frame = tk.Frame(accuracy_frame, bg=accuracy_frame.cget("bg"))

        unsupervised_frame.pack(fill="x", pady=2, padx=2)

        tk.Label(
            unsupervised_frame,
            text="[비지도 학습]",
            font=("Malgun Gothic", 16, "bold"),
            bg=unsupervised_frame.cget("bg"),
        ).pack(anchor="w", padx=2, pady=2)

        create_bar(unsupervised_frame, "K-means 피싱확률", probabilities["kmeans"])

        create_bar(unsupervised_frame, "GMM 피싱확률", probabilities["gmm"])

        create_bar(unsupervised_frame, "MeanShift 피싱확률", probabilities["meanshift"])

        create_bar(
            unsupervised_frame, "Agglomerative 피싱확률", probabilities["agglomerative"]
        )

        tk.Label(
            unsupervised_frame,
            text=(f"비지도학습 평균 피싱확률: {average_cluster_prob:.2f}%"),
            font=("Malgun Gothic", 15, "bold"),
            bg=unsupervised_frame.cget("bg"),
        ).pack(pady=2, padx=5, anchor="e", side="top")

        # ==================================
        # 지도학습
        # ==================================

        supervised_frame = tk.Frame(accuracy_frame, bg=accuracy_frame.cget("bg"))

        supervised_frame.pack(fill="x", pady=2, padx=2)

        tk.Label(
            supervised_frame,
            text="[지도 학습]",
            font=("Malgun Gothic", 16, "bold"),
            bg=supervised_frame.cget("bg"),
        ).pack(anchor="w", padx=2, pady=2)

        create_bar(
            supervised_frame, "Random Forest 피싱확률", probabilities["random_forest"]
        )

        create_bar(
            supervised_frame,
            "Logistic Regression 피싱확률",
            probabilities["logistic_regression"],
        )

        supervised_average = (
            probabilities["random_forest"] + probabilities["logistic_regression"]
        ) / 2

        tk.Label(
            supervised_frame,
            text=(f"지도학습 평균 피싱확률: {supervised_average:.2f}%"),
            font=("Malgun Gothic", 15, "bold"),
            bg=supervised_frame.cget("bg"),
        ).pack(pady=2, padx=5, anchor="e", side="top")

        if loading_dialog.winfo_exists():
            loading_dialog.destroy()

    except Exception as error:
        print(f"Error in update_gui: {error}")


# ==========================================
# 백그라운드 URL 분석
# ==========================================


def background_check_url(url):

    try:
        prediction = predict_phishing(url)

        root.after(0, update_gui, prediction)

    except Exception as error:
        print(f"Error during prediction: {error}")

        root.after(0, handle_prediction_error, str(error))


def handle_prediction_error(message):

    if loading_dialog.winfo_exists():
        loading_dialog.destroy()

    messagebox.showerror("오류", f"URL 분석 중 오류가 발생했습니다.\n{message}")


# ==========================================
# TEAM 페이지
# ==========================================


def create_team_member_box(frame, photo, name, description, row, col):

    member_frame = tk.Frame(frame, borderwidth=2, relief="groove")

    member_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    tk.Label(member_frame, image=photo).grid(
        row=0, column=0, padx=10, pady=5, sticky="nw"
    )

    description_text = f"{name}\n{description}"

    tk.Label(
        member_frame,
        text=description_text,
        font=("Malgun Gothic", 12),
        anchor="w",
        justify="left",
    ).grid(row=0, column=1, padx=10, pady=5, sticky="nw")

    member_frame.grid_rowconfigure(0, weight=1)

    member_frame.grid_columnconfigure(1, weight=1)

    frame.grid_columnconfigure(col, weight=1)


def create_team_page():

    photo1 = load_image("맹구.png")

    photo2 = load_image("짱구.png")

    photo3 = load_image("철수.png")

    photo4 = load_image("유리.png")

    photo5 = load_image("원장.png")

    # 이미지가 Garbage Collection 되는 것을 방지
    team_frame.photos = [photo1, photo2, photo3, photo4, photo5]

    tk.Label(team_frame, text="담당교수", font=("Malgun Gothic", 20, "bold")).grid(
        row=0, column=0, columnspan=2, pady=10, padx=10, sticky="ew"
    )

    create_team_member_box(
        team_frame, photo5, "▷양환석 교수님", "▷역할: 총괄 감독 및 도움", 1, 0
    )

    tk.Label(team_frame, text="팀원 소개", font=("Malgun Gothic", 20, "bold")).grid(
        row=2, column=0, columnspan=2, pady=10, padx=10, sticky="ew"
    )

    create_team_member_box(
        team_frame,
        photo1,
        "▷정여진(조장)",
        "▷학번: 92015441\n▷역할: GMM 클러스터",
        3,
        0,
    )

    create_team_member_box(
        team_frame, photo2, "▷양승원", "▷학번: 91913737\n▷역할: K-MEANS 클러스터", 3, 1
    )

    create_team_member_box(
        team_frame,
        photo4,
        "▷정채영",
        "▷학번: 92015465\n▷역할: Agglomerative 클러스터",
        4,
        0,
    )

    create_team_member_box(
        team_frame,
        photo3,
        "▷서장석",
        "▷학번: 91913543\n▷역할: MEANSHIFT 클러스터",
        4,
        1,
    )


# ==========================================
# INFO 페이지
# ==========================================


def create_info_algorithm_box(
    frame, name, name_explanation, description, row, col, percentage
):

    algo_frame = tk.Frame(frame, borderwidth=2, relief="groove", padx=10, pady=10)

    algo_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    name_frame = tk.Frame(algo_frame)

    name_frame.grid(row=0, column=0, padx=10, sticky="w")

    tk.Label(name_frame, text=name, font=("Malgun Gothic", 18, "bold")).pack(
        side="left"
    )

    tk.Label(name_frame, text=name_explanation, font=("Malgun Gothic", 10)).pack(
        side="left"
    )

    tk.Label(
        algo_frame,
        text=description,
        font=("Malgun Gothic", 12),
        anchor="w",
        justify="left",
    ).grid(row=1, column=0, padx=10, pady=5, sticky="nw")

    canvas = tk.Canvas(
        algo_frame, width=250, height=30, bg="white", highlightthickness=0
    )

    canvas.grid(row=2, column=0, padx=10, pady=5, sticky="w")

    canvas.create_rectangle(5, 5, 245, 25, outline="black", width=2)

    fill_width = 240 * percentage / 100

    canvas.create_rectangle(5, 5, 5 + fill_width, 25, fill="lightblue", outline="")

    canvas.create_text(
        125,
        15,
        text=f"{percentage}%",
        fill="darkblue",
        font=("Malgun Gothic", 10, "bold"),
    )

    algo_frame.grid_columnconfigure(0, weight=1)

    frame.grid_columnconfigure(col, weight=1)


def create_info_page():

    canvas = tk.Canvas(info_frame, width=880, height=880)

    scrollbar = tk.Scrollbar(info_frame, orient="vertical", command=canvas.yview)

    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda event: canvas.configure(scrollregion=(canvas.bbox("all")))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.grid(row=0, column=0, sticky="nsew")

    scrollbar.grid(row=0, column=1, sticky="ns")

    info_frame.grid_rowconfigure(0, weight=1)

    info_frame.grid_columnconfigure(0, weight=1)

    # ======================================
    # 비지도학습
    # ======================================

    tk.Label(
        scrollable_frame, text="※ 비지도학습 정보", font=("Malgun Gothic", 25, "bold")
    ).grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="w")

    create_info_algorithm_box(
        scrollable_frame,
        "1) GMM",
        "(가우시안 혼합 모델)",
        "▶설명\n"
        "여러 개의 가우시안 분포를 혼합하여 "
        "데이터의 분포를 모델링하는 방법입니다.\n\n"
        "▶동작과정\n"
        "EM 알고리즘을 이용하여 각 군집의 "
        "평균과 분산 등을 반복적으로 추정합니다.\n\n"
        "※학습률\n"
        "- 정상 15,000개 / 피싱 7,000개 "
        "총 22,000개 데이터",
        1,
        0,
        91.67,
    )

    create_info_algorithm_box(
        scrollable_frame,
        "2) K-Means",
        "(K-평균 군집화)",
        "▶설명\n"
        "K개의 중심점을 기준으로 가까운 "
        "데이터를 군집화하는 방법입니다.\n\n"
        "▶동작과정\n"
        "데이터를 K개의 군집으로 분류하고 "
        "각 군집의 중심을 반복적으로 "
        "재계산합니다.\n\n"
        "※학습률\n"
        "- 정상 15,000개 / 피싱 7,000개 "
        "총 22,000개 데이터",
        2,
        0,
        91.72,
    )

    create_info_algorithm_box(
        scrollable_frame,
        "3) MeanShift",
        "(평균 이동 군집화)",
        "▶설명\n"
        "데이터의 밀도가 높은 영역을 찾아 "
        "군집을 형성하는 방법입니다.\n\n"
        "▶동작과정\n"
        "각 데이터 포인트를 밀도가 높은 "
        "방향으로 이동시키며 "
        "군집 중심을 찾습니다.\n\n"
        "※학습률\n"
        "- 정상 15,000개 / 피싱 7,000개 "
        "총 22,000개 데이터",
        3,
        0,
        88.26,
    )

    create_info_algorithm_box(
        scrollable_frame,
        "4) Agglomerative",
        "(병합 군집화)",
        "▶설명\n"
        "각 데이터를 하나의 군집으로 시작해 "
        "가까운 군집을 단계적으로 병합하는 "
        "계층적 군집화 방법입니다.\n\n"
        "▶동작과정\n"
        "가장 가까운 군집을 반복적으로 "
        "병합하여 최종 군집을 구성합니다.\n\n"
        "※학습률\n"
        "- 정상 15,000개 / 피싱 7,000개 "
        "총 22,000개 데이터",
        4,
        0,
        88.37,
    )

    # ======================================
    # 지도학습
    # ======================================

    tk.Label(
        scrollable_frame, text="※ 지도학습 정보", font=("Malgun Gothic", 25, "bold")
    ).grid(row=6, column=0, columnspan=2, pady=10, padx=10, sticky="w")

    create_info_algorithm_box(
        scrollable_frame,
        "1) RandomForest",
        "(앙상블 학습)",
        "▶설명\n"
        "여러 개의 결정 트리를 조합하여 "
        "최종 결과를 도출하는 "
        "앙상블 학습 방법입니다.\n\n"
        "▶동작과정\n"
        "여러 결정 트리를 각각 학습한 뒤 "
        "각 결과를 종합하여 "
        "최종 예측값을 결정합니다.\n\n"
        "※학습률\n"
        "- 정상 15,000개 / 피싱 7,000개 "
        "총 22,000개 데이터",
        7,
        0,
        96.91,
    )

    create_info_algorithm_box(
        scrollable_frame,
        "2) LogisticRegression",
        "(이진 분류 모델)",
        "▶설명\n"
        "데이터가 특정 클래스에 속할 "
        "확률을 계산하는 "
        "이진 분류 모델입니다.\n\n"
        "▶동작과정\n"
        "선형 결합 결과에 시그모이드 "
        "함수를 적용하여 0~1 사이의 "
        "확률로 변환합니다.\n\n"
        "※학습률\n"
        "- 정상 15,000개 / 피싱 7,000개 "
        "총 22,000개 데이터",
        8,
        0,
        95.36,
    )


# ==========================================
# GUI 생성
# ==========================================

create_main_widgets()
create_team_page()
create_info_page()


# 시작 화면
show_frame(main_frame)


if __name__ == "__main__":
    root.mainloop()
