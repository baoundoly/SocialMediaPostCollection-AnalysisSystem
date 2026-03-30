import io
import csv
from datetime import date, datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.post import Post
from app.models.post_analysis import PostAnalysis
from app.models.platform import Platform

class ReportService:
    def __init__(self, db: Session):
        self.db = db

    def _get_posts_with_analysis(self, start_date=None, end_date=None, platform_id=None):
        q = self.db.query(Post, PostAnalysis).outerjoin(PostAnalysis, Post.id == PostAnalysis.post_id)
        if start_date:
            q = q.filter(Post.collected_at >= datetime.combine(start_date, datetime.min.time()))
        if end_date:
            q = q.filter(Post.collected_at <= datetime.combine(end_date, datetime.max.time()))
        if platform_id:
            q = q.filter(Post.platform_id == platform_id)
        return q.all()

    def daily_report(self, report_date=None):
        target = report_date or date.today()
        start = datetime.combine(target, datetime.min.time())
        end = datetime.combine(target, datetime.max.time())
        q = self.db.query(Post, PostAnalysis).outerjoin(PostAnalysis, Post.id == PostAnalysis.post_id).filter(
            Post.collected_at >= start, Post.collected_at <= end
        )
        results = q.all()
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for _, analysis in results:
            if analysis and analysis.sentiment_label:
                sentiments[analysis.sentiment_label] = sentiments.get(analysis.sentiment_label, 0) + 1
        return {"date": str(target), "total_posts": len(results), "sentiments": sentiments,
                "avg_likes": sum(p.likes_count for p, _ in results) / max(len(results), 1)}

    def weekly_report(self, start_date=None):
        end = date.today()
        start = start_date or (end - timedelta(days=7))
        results = self._get_posts_with_analysis(start, end)
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        for _, analysis in results:
            if analysis and analysis.sentiment_label:
                sentiments[analysis.sentiment_label] = sentiments.get(analysis.sentiment_label, 0) + 1
        return {"start_date": str(start), "end_date": str(end), "total_posts": len(results), "sentiments": sentiments}

    def export_csv(self, start_date=None, end_date=None, platform_id=None):
        results = self._get_posts_with_analysis(start_date, end_date, platform_id)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id","platform_id","author_name","content","posted_at","likes_count","sentiment","sentiment_score"])
        for post, analysis in results:
            writer.writerow([post.id, post.platform_id, post.author_name, (post.content or "")[:200],
                post.posted_at, post.likes_count,
                analysis.sentiment_label if analysis else "", analysis.sentiment_score if analysis else ""])
        return output.getvalue().encode("utf-8")

    def export_excel(self, start_date=None, end_date=None, platform_id=None):
        import openpyxl
        results = self._get_posts_with_analysis(start_date, end_date, platform_id)
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Posts"
        ws.append(["id","platform_id","author_name","content","posted_at","likes_count","sentiment","sentiment_score"])
        for post, analysis in results:
            ws.append([post.id, post.platform_id, post.author_name, (post.content or "")[:200],
                str(post.posted_at), post.likes_count,
                analysis.sentiment_label if analysis else "", analysis.sentiment_score if analysis else ""])
        output = io.BytesIO()
        wb.save(output)
        return output.getvalue()

    def export_pdf(self, start_date=None, end_date=None):
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        results = self._get_posts_with_analysis(start_date, end_date)
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [Paragraph("Social Media Posts Report", styles["Title"])]
        data = [["ID","Author","Sentiment","Likes","Posted At"]]
        for post, analysis in results[:100]:
            data.append([str(post.id), post.author_name or "",
                analysis.sentiment_label if analysis else "", str(post.likes_count),
                str(post.posted_at)[:10] if post.posted_at else ""])
        table = Table(data)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.grey),("TEXTCOLOR",(0,0),(-1,0),colors.whitesmoke),
            ("ALIGN",(0,0),(-1,-1),"CENTER"),("FONTSIZE",(0,0),(-1,0),12),
            ("GRID",(0,0),(-1,-1),1,colors.black)]))
        elements.append(table)
        doc.build(elements)
        return output.getvalue()
