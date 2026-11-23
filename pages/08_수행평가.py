
# =====================================
# CSV 파일 경로 및 불러오기 수정
# =====================================

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

POSSIBLE_DIRS = [
    BASE_DIR,
    BASE_DIR.parent,
    BASE_DIR.parent.parent
]


def find_file(filename):

    for folder in POSSIBLE_DIRS:

        path = folder / filename

        if path.is_file():

            # 빈 파일은 제외
            if path.stat().st_size > 0:
                return path

    return None


def read_csv_file(path):

    if path is None:
        raise FileNotFoundError(
            "CSV 파일 경로를 찾을 수 없습니다."
        )

    if not path.exists():
        raise FileNotFoundError(
            f"파일이 존재하지 않습니다: {path}"
        )

    if path.stat().st_size == 0:
        raise ValueError(
            f"CSV 파일이 비어 있습니다: {path.name}"
        )

    encodings = [
        "cp949",
        "utf-8-sig",
        "euc-kr",
        "utf-8"
    ]

    for encoding in encodings:

        try:
            data = pd.read_csv(
                path,
                encoding=encoding
            )

            if data.empty:
                raise ValueError(
                    f"{path.name} 파일에 데이터가 없습니다."
                )

            return data

        except UnicodeDecodeError:
            continue

        except pd.errors.EmptyDataError:
            raise ValueError(
                f"{path.name} 파일이 비어 있거나 "
                "CSV 형식이 올바르지 않습니다."
            )

    raise ValueError(
        "CSV 인코딩을 확인할 수 없습니다."
    )
