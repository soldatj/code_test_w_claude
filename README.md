# Code Reviewer 📝

LangGraph 기반 파이썬 코드 리뷰어입니다. Claude AI를 활용하여 코드 품질을 자동으로 분석하고, 버그, 스타일, 성능, 보안 이슈를 찾아냅니다.

## ✨ 기능

- 🔍 **자동 파일 스캔**: 지정된 디렉토리에서 모든 Python 파일을 찾습니다
- 🤖 **AI 기반 분석**: Claude CLI (`claude --model sonnet`)로 각 파일을 분석합니다
- 📊 **다면적 리뷰**:
  - 🐛 버그 (Bugs)
  - 🎨 코드 스타일 (Code Style)
  - ⚡ 성능 (Performance)
  - 🔒 보안 (Security)
- 📝 **다양한 출력 형식**: JSON과 텍스트 두 가지 형식으로 리포트를 생성합니다
- 🔄 **LangGraph 워크플로우**: 상태 기반 그래프로 처리 파이프라인을 관리합니다

## 📋 요구사항

- Python 3.8+
- Claude CLI (설치: `brew install claude-code`)
- pip 패키지: `langgraph`, `langchain-core`, `typing-extensions`

## 🚀 설치

```bash
# 1. 리포지토리 복제
git clone <your-repo-url>
cd code-reviewer

# 2. 가상 환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt
```

## 💻 사용법

### 기본 사용법

```bash
python -m code_reviewer [디렉토리]
```

### 옵션

```bash
python -m code_reviewer [디렉토리] --output [출력디렉토리]
```

- `[디렉토리]`: 분석할 디렉토리 (기본값: 현재 디렉토리)
- `--output`, `-o`: 리포트 출력 디렉토리 (기본값: `review_output`)
- `--notion`: 리뷰 결과를 Notion 페이지로 전송
- `--notion-database`: 리뷰 결과를 Notion 데이터베이스에 저장
- `--notion-guide`: Notion 연동 설정 가이드 표시

### 예시

```bash
# 현재 디렉토리 리뷰
python -m code_reviewer

# 특정 디렉토리 리뷰
python -m code_reviewer ~/Projects/myapp/src

# 커스텀 출력 디렉토리
python -m code_reviewer myapp --output reports

# Notion 페이지로 전송
python -m code_reviewer myapp --notion

# Notion 데이터베이스에 저장
python -m code_reviewer myapp --notion-database
```

## 📊 Notion 연동

코드 리뷰 결과를 Notion에 자동으로 저장할 수 있습니다.

### 설정 방법

1. **Notion Integration 생성**:
   ```bash
   python -m code_reviewer --notion-guide
   ```

   가이드를 따라서 Integration을 생성하세요.

2. **환경변수 설정**:

   **Linux/macOS:**
   ```bash
   export NOTION_TOKEN="your_integration_token"
   export NOTION_PAGE_ID="your_page_id_or_database_id"
   ```

   **Windows (PowerShell):**
   ```powershell
   $env:NOTION_TOKEN = "your_integration_token"
   $env:NOTION_PAGE_ID = "your_page_id_or_database_id"
   ```

   **.env 파일 사용 (권장):**
   ```bash
   pip install python-dotenv
   echo 'NOTION_TOKEN=your_token' > .env
   echo 'NOTION_PAGE_ID=your_page_id' >> .env
   ```

3. **페이지/데이터베이스 연결**:
   - Notion에서 리뷰를 저장할 페이지/데이터베이스 열기
   - 우측 상단 "..." 메뉴 → "Add connections"
   - 생성한 Integration 선택

4. **데이터베이스 사용 시 컬럼 설정**:
   다음 컬럼이 필요합니다:
   - Title (title 타입)
   - Directory (text 타입)
   - Files (number 타입)
   - Bugs (number 타입)
   - Style Issues (number 타입)
   - Performance Issues (number 타입)
   - Security Issues (number 타입)
   - Date (date 타입)

## 📁 프로젝트 구조

```
code_reviewer/
├── __init__.py          # 패키지 초기화
├── __main__.py          # 진입점 (python -m code_reviewer)
├── graph.py             # LangGraph 워크플로우 정의
├── analyzer.py          # 파일 스캔 및 Claude 분석 로직
├── cli.py              # CLI 인터페이스
└── README.md           # 이 파일
```

## 🔄 워크플로우

```
START → scan_files → analyze_file (각 파일 반복) → aggregate_results → generate_report → END
                    ↓ (파일 없으면)
                 aggregate_results
```

### 각 노드 설명

| 노드 | 설명 |
|------|------|
| `scan_files` | 디렉토리를 스캔하여 Python 파일 목록을 생성 |
| `analyze_file` | 각 파일을 Claude로 분석하여 버그/스타일/성능/보안 이슈 식별 |
| `aggregate_results` | 모든 파일의 분석 결과를 집계하여 통계 생성 |
| `generate_report` | JSON과 텍스트 형식의 리포트를 생성 |

## 📄 출력

리포트는 지정된 출력 디렉토리에 생성됩니다:

### `review_report.json`

구조화된 JSON 형식의 리포트:

```json
{
  "total_files": 5,
  "total_bugs": 8,
  "total_style_issues": 12,
  "total_performance_issues": 3,
  "total_security_issues": 1,
  "all_analyses": [
    {
      "file": "/path/to/file.py",
      "bugs": ["버그 설명"],
      "code_style": ["스타일 이슈 설명"],
      "performance": ["성능 이슈 설명"],
      "security": ["보안 이슈 설명"],
      "summary": "전체 요약"
    }
  ]
}
```

### `review_report.txt`

사람이 읽기 쉬운 텍스트 형식의 리포트:

```
============================================================
CODE REVIEW REPORT
============================================================

Files analyzed    : 5
Bugs              : 8
Style issues      : 12
Performance issues: 3
Security issues   : 1

============================================================
DETAILED ANALYSIS
============================================================

File: /path/to/file.py
----------------------------------------
Summary: 전체 요약

Bugs:
  - 버그 설명
  - 또 다른 버그

Code Style:
  - 스타일 이슈
  - 또 다른 스타일 이슈
...
```

## 🎯 분석 카테고리

### 🐛 버그 (Bugs)
- 논리적 오류
- 예외 처리 누락
- 잘못된 동작
- 경계 조건 버그

### 🎨 코드 스타일 (Code Style)
- PEP 8 위반
- 명명 규칙
- 가독성 이슈
- 독스트링 누락

### ⚡ 성능 (Performance)
- 비효율적인 알고리즘
- 불필요한 연산
- 메모리 이슈
- 최적화 기회

### 🔒 보안 (Security)
- 취약점
- 안전하지 않은 연산
- 인젝션 리스크
- 민감 데이터 처리

## 🛠️ 개발

### LangGraph 워크플로우 수정

`code_reviewer/graph.py`에서 워크플로우를 커스터마이징할 수 있습니다:

```python
def build_graph():
    g = StateGraph(CodeReviewState)
    # 노드와 엣지 추가
    return g.compile()
```

### 프롬프트 수정

`code_reviewer/analyzer.py`의 `analyze_file_with_claude` 함수에서 분석 프롬프트를 수정할 수 있습니다.

## 📝 라이선스

MIT License

## 🤝 기여

환영합니다! Pull Request를 보내주세요.

## 📧 문의

이슈를 통해 버그를 신고하거나 기능을 요청해주세요.

---

Made with ❤️ by [장깽] & [잔디]
