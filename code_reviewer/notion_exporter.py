# notion_exporter.py

import os
import json
from typing import Optional
from datetime import datetime

try:
    from notion_client import Client, APIResponseError
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False


class NotionExporter:
    """코드 리뷰 결과를 Notion 페이지로 내보내기"""

    def __init__(self, token: Optional[str] = None, page_id: Optional[str] = None):
        """
        Args:
            token: Notion Integration Token (기본값: NOTION_TOKEN 환경변수)
            page_id: Notion Page ID (기본값: NOTION_PAGE_ID 환경변수)
        """
        if not NOTION_AVAILABLE:
            raise ImportError(
                "notion-client 패키지가 설치되지 않았습니다. "
                "pip install notion-client 로 설치해주세요."
            )

        self.token = token or os.environ.get("NOTION_TOKEN")
        self.page_id = page_id or os.environ.get("NOTION_PAGE_ID")

        if not self.token or not self.page_id:
            raise ValueError(
                "NOTION_TOKEN and NOTION_PAGE_ID 환경변수가 필요합니다.\n"
                "Notion Integration에서 토큰을 발급받고, "
                "페이지 URL에서 ID를 복사하세요."
            )

        self.client = Client(auth=self.token)

    def export_report(
        self,
        review_data: dict,
        directory: str,
        report_name: Optional[str] = None
    ) -> str:
        """
        리뷰 리포트를 Notion 페이지에 추가

        Args:
            review_data: 리뷰 데이터 (JSON 형식)
            directory: 분석된 디렉토리 경로
            report_name: 리포트 이름 (기본값: 자동 생성)

        Returns:
            생성된 Notion 블록 ID
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = report_name or f"코드 리뷰 - {directory} ({timestamp})"

        # 헤딩 생성
        children = [
            {
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": title}}]
                }
            }
        ]

        # 요약 테이블
        summary = f"""
| 항목 | 개수 |
|------|------|
| 📁 분석 파일 | {review_data.get('total_files', 0)} |
| 🐛 버그 | {review_data.get('total_bugs', 0)} |
| 🎨 스타일 이슈 | {review_data.get('total_style_issues', 0)} |
| ⚡ 성능 이슈 | {review_data.get('total_performance_issues', 0)} |
| 🔒 보안 이슈 | {review_data.get('total_security_issues', 0)} |
"""
        children.append({
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [{"type": "text", "text": {"content": f"📊 리뷰 요약\n\n{summary}"}}]
            }
        })

        # 각 파일별 상세 분석
        for file_analysis in review_data.get('all_analyses', []):
            file_name = file_analysis.get('file', 'Unknown')
            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": f"📄 {file_name}"}}]
                }
            })

            summary_text = file_analysis.get('summary', '')
            if summary_text:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": f"📝 {summary_text}"}}]
                    }
                })

            # 버그
            bugs = file_analysis.get('bugs', [])
            if bugs:
                children.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "🐛 버그"}}]
                    }
                })
                for bug in bugs:
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": bug}}]
                        }
                    })

            # 코드 스타일
            style_issues = file_analysis.get('code_style', [])
            if style_issues:
                children.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "🎨 코드 스타일"}}]
                    }
                })
                for issue in style_issues:
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": issue}}]
                        }
                    })

            # 성능
            performance_issues = file_analysis.get('performance', [])
            if performance_issues:
                children.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "⚡ 성능"}}]
                    }
                })
                for issue in performance_issues:
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": issue}}]
                        }
                    })

            # 보안
            security_issues = file_analysis.get('security', [])
            if security_issues:
                children.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {
                        "rich_text": [{"type": "text", "text": {"content": "🔒 보안"}}]
                    }
                })
                for issue in security_issues:
                    children.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": issue}}]
                        }
                    })

            # 구분선
            children.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })

        # Notion에 블록 추가
        try:
            response = self.client.blocks.children.append(
                block_id=self.page_id,
                children=children
            )
            print(f"✅ Notion 페이지에 리뷰가 전송되었습니다!")
            return response.get("id", "")
        except APIResponseError as e:
            print(f"❌ Notion API 오류: {e}")
            raise

    def export_to_database(
        self,
        review_data: dict,
        directory: str
    ) -> Optional[str]:
        """
        리뷰 결과를 Notion 데이터베이스에 저장

        Args:
            review_data: 리뷰 데이터
            directory: 분석된 디렉토리

        Returns:
            생성된 페이지 ID (실패 시 None)

        참고:
            데이터베이스에 다음 컬럼이 있어야 합니다:
            - Title (title)
            - Directory (text)
            - Files (number)
            - Bugs (number)
            - Style Issues (number)
            - Performance Issues (number)
            - Security Issues (number)
            - Date (date)
        """
        timestamp = datetime.now().isoformat()
        title = f"리뷰 - {directory.split('/')[-1]}"

        try:
            response = self.client.pages.create(
                parent={"database_id": self.page_id},
                properties={
                    "Title": {"title": [{"text": {"content": title}}]},
                    "Directory": {"rich_text": [{"text": {"content": directory}}]},
                    "Files": {"number": review_data.get('total_files', 0)},
                    "Bugs": {"number": review_data.get('total_bugs', 0)},
                    "Style Issues": {"number": review_data.get('total_style_issues', 0)},
                    "Performance Issues": {"number": review_data.get('total_performance_issues', 0)},
                    "Security Issues": {"number": review_data.get('total_security_issues', 0)},
                    "Date": {"date": {"start": timestamp}}
                }
            )
            print(f"✅ Notion 데이터베이스에 리뷰가 저장되었습니다!")
            return response.get("id", "")
        except APIResponseError as e:
            print(f"❌ Notion 데이터베이스 오류: {e}")
            print("💡 데이터베이스에 필요한 컬럼이 있는지 확인하세요.")
            return None


def create_notion_integration_guide():
    """Notion Integration 설정 가이드 출력"""
    guide = """
📘 Notion Integration 설정 가이드
=====================================

1. Notion에서 Integration 생성:
   - https://www.notion.so/my-integrations 로 이동
   - "+ New integration" 클릭
   - Integration 이름 입력 (예: Code Reviewer)
   - Capabilities에서 "Read content", "Update content" 활성화
   - "Submit" 클릭 후 내부 Integration Token 복사

2. 페이지에 연결:
   - Notion에서 리뷰를 저장할 페이지 열기
   - 페이지 우측 상단 "..." 메뉴 클릭
   - "Add connections" → 방금 만든 Integration 선택

3. 환경변수 설정:
   export NOTION_TOKEN="your_integration_token"
   export NOTION_PAGE_ID="your_page_id"

   또는 .env 파일에 저장:
   NOTION_TOKEN=your_integration_token
   NOTION_PAGE_ID=your_page_id

4. 페이지 ID 찾기:
   - 페이지 URL에서 ID 복사
   - 예: https://www.notion.so/username/Page-Name-32자리-ID?v=xxx
   - 32자리 ID가 필요합니다

5. 데이터베이스 사용 시 (선택사항):
   - 데이터베이스에 다음 컬럼이 필요합니다:
     * Title (title 타입)
     * Directory (text 타입)
     * Files (number 타입)
     * Bugs (number 타입)
     * Style Issues (number 타입)
     * Performance Issues (number 타입)
     * Security Issues (number 타입)
     * Date (date 타입)
   - 데이터베이스 연결도 2번과 동일하게 진행
"""
    print(guide)


if __name__ == "__main__":
    create_notion_integration_guide()
