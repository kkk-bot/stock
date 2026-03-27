"""SEC EDGAR 轻量公告客户端。"""

from __future__ import annotations

from typing import Any

import requests


class SecEdgarClient:
    """封装 SEC EDGAR 接口请求与公告解析。"""

    TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
    SUBMISSIONS_URL_TEMPLATE = "https://data.sec.gov/submissions/CIK{cik}.json"

    def __init__(self, user_agent: str | None = None) -> None:
        self.user_agent = user_agent or "MultiMarketAnalyzer/1.0 (research@example.com)"
        self._ticker_cik_cache: dict[str, str] = {}
        self._default_cik_map = {
            "NVDA": "0001045810",
            "QQQ": "0001067839",
        }

    def _request_json(self, url: str) -> dict[str, Any] | None:
        """发起 GET 请求并返回 JSON。"""
        try:
            response = requests.get(
                url,
                timeout=10,
                headers={
                    "User-Agent": self.user_agent,
                    "Accept": "application/json",
                },
            )
            response.raise_for_status()
            payload = response.json()
            if isinstance(payload, dict):
                return payload
        except Exception:
            return None
        return None

    def _get_ticker_cik_map(self) -> dict[str, str]:
        """读取 ticker -> CIK 映射，并缓存结果。"""
        if self._ticker_cik_cache:
            return self._ticker_cik_cache

        payload = self._request_json(self.TICKERS_URL)
        if not payload:
            self._ticker_cik_cache = self._default_cik_map.copy()
            return self._ticker_cik_cache

        mapping: dict[str, str] = {}
        for item in payload.values():
            ticker = str(item.get("ticker", "")).upper().strip()
            cik_number = str(item.get("cik_str", "")).strip()
            if not ticker or not cik_number:
                continue
            mapping[ticker] = cik_number.zfill(10)

        if not mapping:
            mapping = self._default_cik_map.copy()
        else:
            for ticker, cik in self._default_cik_map.items():
                mapping.setdefault(ticker, cik)
        self._ticker_cik_cache = mapping
        return mapping

    def _resolve_cik(self, ticker: str) -> str | None:
        """根据 ticker 获取 CIK。"""
        normalized_ticker = ticker.upper().strip()
        if not normalized_ticker:
            return None
        return self._get_ticker_cik_map().get(normalized_ticker) or self._default_cik_map.get(normalized_ticker)

    def get_recent_filings(
        self,
        ticker: str,
        market: str = "美股",
        theme: str | None = None,
        limit: int = 6,
        forms: tuple[str, ...] = ("8-K", "10-K", "10-Q", "6-K", "20-F"),
    ) -> list[dict[str, Any]] | None:
        """获取指定 ticker 最近公告并映射到统一新闻结构。"""
        cik = self._resolve_cik(ticker)
        if not cik:
            return None

        payload = self._request_json(self.SUBMISSIONS_URL_TEMPLATE.format(cik=cik))
        if not payload:
            return None

        recent = ((payload.get("filings") or {}).get("recent") or {})
        form_list = recent.get("form") or []
        accession_list = recent.get("accessionNumber") or []
        filing_date_list = recent.get("filingDate") or []
        report_date_list = recent.get("reportDate") or []
        document_list = recent.get("primaryDocument") or []
        desc_list = recent.get("primaryDocDescription") or []

        if not form_list:
            return None

        results: list[dict[str, Any]] = []
        forms_set = {form.strip().upper() for form in forms}
        ticker_upper = ticker.upper().strip()
        for index, form in enumerate(form_list):
            form_text = str(form).upper().strip()
            if form_text not in forms_set:
                continue
            accession = str(accession_list[index] if index < len(accession_list) else "").strip()
            primary_document = str(document_list[index] if index < len(document_list) else "").strip()
            if not accession or not primary_document:
                continue
            accession_no_dash = accession.replace("-", "")
            cik_no_leading = str(int(cik))
            filing_date = str(filing_date_list[index] if index < len(filing_date_list) else "").strip()
            report_date = str(report_date_list[index] if index < len(report_date_list) else "").strip()
            description = str(desc_list[index] if index < len(desc_list) else "").strip()
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_no_leading}/{accession_no_dash}/{primary_document}"
            title = f"{ticker_upper} {form_text} 披露"
            if description:
                title = f"{title} - {description}"

            results.append(
                {
                    "title": title,
                    "source": "SEC EDGAR",
                    "publish_time": filing_date or report_date,
                    "summary": f"{ticker_upper} 最新 {form_text} 披露，详情请查看官方文件链接。",
                    "url": filing_url,
                    "sentiment_hint": "",
                    "market": market,
                    "theme": theme or "公司公告",
                    "symbol": ticker_upper,
                    "source_provider": "SEC EDGAR",
                    "data_source": "real",
                }
            )
            if len(results) >= max(1, limit):
                break

        return results or None
