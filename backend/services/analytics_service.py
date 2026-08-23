import hashlib
from datetime import datetime, timezone, timedelta
from flask import request
from backend.models import db, AnalyticsVisit

class AnalyticsService:
    @staticmethod
    def record_visit(page: str = "/"):
        """Records an anonymized visit count without storing personal information."""
        raw_ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1')
        user_agent = request.headers.get('User-Agent', '')
        
        # 1-way anonymized daily salt hash (cannot be reversed, expires identity daily)
        today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        ip_hash = hashlib.sha256(f"{raw_ip}_{user_agent}_{today_str}".encode('utf-8')).hexdigest()[:16]

        visit = AnalyticsVisit(
            page=page,
            ip_hash=ip_hash
        )
        db.session.add(visit)
        db.session.commit()

    @staticmethod
    def get_analytics_summary():
        """Returns visitor metrics for the admin dashboard."""
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)
        seven_days_ago = now - timedelta(days=7)

        total_views = AnalyticsVisit.query.count()
        last_30_days = AnalyticsVisit.query.filter(AnalyticsVisit.timestamp >= thirty_days_ago).count()
        last_7_days = AnalyticsVisit.query.filter(AnalyticsVisit.timestamp >= seven_days_ago).count()

        # Approximate unique visitors in last 30 days based on unique daily hashes
        unique_visitors = db.session.query(db.func.count(db.func.distinct(AnalyticsVisit.ip_hash))).scalar() or 0

        return {
            'total_page_views': total_views,
            'last_30_days_views': last_30_days,
            'last_7_days_views': last_7_days,
            'estimated_unique_visitors': unique_visitors
        }
