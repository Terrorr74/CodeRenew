"""
EPSS Service - Exploit Prediction Scoring System Integration

Integrates with FIRST.org EPSS API to fetch exploitation probability scores for CVEs.
API Documentation: https://www.first.org/epss/api

Key Features:
- Batch CVE queries (efficient bulk lookups)
- Async HTTP requests with retry logic
- Daily caching (EPSS scores update once per day)
- Graceful error handling for missing CVEs
"""

import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class EPSSData:
    """EPSS score data for a CVE"""
    cve: str
    epss_score: float
    percentile: float
    date: str


class EPSSService:
    """
    Service for fetching EPSS scores from FIRST.org API

    Usage:
        service = EPSSService()
        scores = await service.get_epss_scores(['CVE-2021-44228', 'CVE-2024-1234'])
    """

    BASE_URL = "https://api.first.org/data/v1/epss"
    REQUEST_TIMEOUT = 30.0
    MAX_RETRIES = 3

    def __init__(self, cache_ttl_hours: int = 24):
        """
        Initialize EPSS service

        Args:
            cache_ttl_hours: Cache TTL in hours (default: 24, EPSS updates daily)
        """
        self.cache_ttl = timedelta(hours=cache_ttl_hours)
        self._cache: Dict[str, EPSSData] = {}
        self._cache_timestamp: Optional[datetime] = None

    async def get_epss_score(self, cve: str) -> Optional[EPSSData]:
        """
        Get EPSS score for a single CVE

        Args:
            cve: CVE identifier (e.g., 'CVE-2021-44228')

        Returns:
            EPSSData if found, None if CVE not in EPSS database
        """
        scores = await self.get_epss_scores([cve])
        return scores.get(cve)

    async def get_epss_scores(self, cves: List[str]) -> Dict[str, EPSSData]:
        """
        Get EPSS scores for multiple CVEs (batch query)

        Args:
            cves: List of CVE identifiers

        Returns:
            Dictionary mapping CVE -> EPSSData
            Missing CVEs are not included in the result
        """
        if not cves:
            return {}

        # Check cache first
        if self._is_cache_valid():
            cached_results = {cve: self._cache[cve] for cve in cves if cve in self._cache}
            if len(cached_results) == len(cves):
                logger.info(f"Returning {len(cached_results)} EPSS scores from cache")
                return cached_results

        # Fetch from API
        try:
            results = await self._fetch_from_api(cves)

            # Update cache
            self._cache.update(results)
            self._cache_timestamp = datetime.utcnow()

            logger.info(f"Fetched {len(results)} EPSS scores for {len(cves)} CVEs")
            return results

        except Exception as e:
            logger.error(f"Error fetching EPSS scores: {e}")
            # Return cached results if available, even if stale
            return {cve: self._cache[cve] for cve in cves if cve in self._cache}

    async def _fetch_from_api(self, cves: List[str]) -> Dict[str, EPSSData]:
        """
        Fetch EPSS scores from FIRST.org API with retry logic

        Args:
            cves: List of CVE identifiers

        Returns:
            Dictionary mapping CVE -> EPSSData
        """
        # Build query parameter (comma-separated CVEs)
        cve_param = ",".join(cves)

        async with httpx.AsyncClient(timeout=self.REQUEST_TIMEOUT) as client:
            for attempt in range(self.MAX_RETRIES):
                try:
                    response = await client.get(
                        self.BASE_URL,
                        params={"cve": cve_param}
                    )
                    response.raise_for_status()

                    data = response.json()
                    return self._parse_response(data)

                except httpx.HTTPStatusError as e:
                    logger.warning(f"EPSS API HTTP error (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                    if attempt == self.MAX_RETRIES - 1:
                        raise

                except httpx.RequestError as e:
                    logger.warning(f"EPSS API request error (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                    if attempt == self.MAX_RETRIES - 1:
                        raise

        return {}

    def _parse_response(self, data: dict) -> Dict[str, EPSSData]:
        """
        Parse EPSS API response

        Response format:
        {
            "status": "OK",
            "data": [
                {
                    "cve": "CVE-2021-44228",
                    "epss": "0.944500000",
                    "percentile": "0.999890000",
                    "date": "2025-11-21"
                }
            ]
        }
        """
        results = {}

        if data.get("status") != "OK":
            logger.error(f"EPSS API returned non-OK status: {data.get('status')}")
            return results

        for item in data.get("data", []):
            try:
                epss_data = EPSSData(
                    cve=item["cve"],
                    epss_score=float(item["epss"]),
                    percentile=float(item["percentile"]),
                    date=item["date"]
                )
                results[epss_data.cve] = epss_data

            except (KeyError, ValueError) as e:
                logger.warning(f"Error parsing EPSS data for item {item}: {e}")
                continue

        return results

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid based on TTL"""
        if self._cache_timestamp is None:
            return False

        age = datetime.utcnow() - self._cache_timestamp
        return age < self.cache_ttl

    def clear_cache(self):
        """Clear the EPSS score cache"""
        self._cache.clear()
        self._cache_timestamp = None
        logger.info("EPSS cache cleared")


# Singleton instance for reuse across requests
_epss_service_instance: Optional[EPSSService] = None


def get_epss_service() -> EPSSService:
    """
    Get singleton EPSS service instance

    Usage in FastAPI endpoints:
        from app.services.epss import get_epss_service

        epss = get_epss_service()
        score = await epss.get_epss_score('CVE-2021-44228')
    """
    global _epss_service_instance

    if _epss_service_instance is None:
        _epss_service_instance = EPSSService()

    return _epss_service_instance
