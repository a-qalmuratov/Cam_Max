"""
Auto Analysis Module
Avtomatik tahlil va hisobot yuborish.
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
import json
import os

from utils.logger import logger


@dataclass
class AnalysisReport:
    """Tahlil hisoboti."""
    report_id: int
    user_id: int
    period: str  # 'daily', 'weekly', 'monthly'
    generated_at: datetime
    
    # Statistics
    people_count: int = 0
    vehicle_count: int = 0
    total_events: int = 0
    anomalies_count: int = 0
    
    # Details
    peak_hours: List[str] = field(default_factory=list)
    camera_stats: Dict[str, dict] = field(default_factory=dict)
    
    # Alerts
    alerts: List[dict] = field(default_factory=list)
    
    # Recommendations
    recommendations: List[str] = field(default_factory=list)


class AutoAnalyzer:
    """Avtomatik tahlil va hisobot."""
    
    def __init__(self, data_dir: str = "data/reports"):
        self.data_dir = data_dir
        self.reports: List[AnalysisReport] = []
        self.next_report_id = 1
        
        # Scheduled tasks
        self.scheduled_users: Dict[int, dict] = {}  # user_id -> schedule config
        self._running = False
        self._task = None
        
        # Callbacks
        self.send_callback: Optional[Callable] = None
        
        os.makedirs(data_dir, exist_ok=True)
        self._load_schedules()
    
    def _load_schedules(self):
        """Jadvallarni yuklash."""
        try:
            schedule_file = os.path.join(self.data_dir, "schedules.json")
            if os.path.exists(schedule_file):
                with open(schedule_file, 'r') as f:
                    self.scheduled_users = json.load(f)
                logger.info(f"Loaded schedules for {len(self.scheduled_users)} users")
        except Exception as e:
            logger.error(f"Error loading schedules: {e}")
    
    def _save_schedules(self):
        """Jadvallarni saqlash."""
        try:
            schedule_file = os.path.join(self.data_dir, "schedules.json")
            with open(schedule_file, 'w') as f:
                json.dump(self.scheduled_users, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving schedules: {e}")
    
    def set_send_callback(self, callback: Callable):
        """Telegram'ga yuborish callback'ini sozlash."""
        self.send_callback = callback
    
    def schedule_daily_report(self, user_id: int, hour: int = 8,
                               enabled: bool = True):
        """Kunlik hisobot jadvalini sozlash."""
        self.scheduled_users[str(user_id)] = {
            'type': 'daily',
            'hour': hour,
            'enabled': enabled,
            'last_sent': None
        }
        self._save_schedules()
        logger.info(f"Scheduled daily report for user {user_id} at {hour}:00")
    
    def schedule_weekly_report(self, user_id: int, day: int = 0,
                                hour: int = 9, enabled: bool = True):
        """Haftalik hisobot jadvalini sozlash (day: 0=Monday)."""
        self.scheduled_users[str(user_id)] = {
            'type': 'weekly',
            'day': day,
            'hour': hour,
            'enabled': enabled,
            'last_sent': None
        }
        self._save_schedules()
    
    def disable_reports(self, user_id: int):
        """Hisobotlarni o'chirish."""
        if str(user_id) in self.scheduled_users:
            self.scheduled_users[str(user_id)]['enabled'] = False
            self._save_schedules()
    
    async def generate_daily_report(self, user_id: int,
                                     date: datetime = None) -> AnalysisReport:
        """Kunlik hisobot yaratish."""
        if date is None:
            date = datetime.now() - timedelta(days=1)  # Yesterday
        
        report = AnalysisReport(
            report_id=self.next_report_id,
            user_id=user_id,
            period='daily',
            generated_at=datetime.now()
        )
        self.next_report_id += 1
        
        try:
            # Get data from database
            from database.models import db
            from database.v2_models import v2db
            
            user = db.get_user(user_id)
            if not user:
                return report
            
            org_id = user.get('organization_id')
            cameras = db.get_cameras_by_organization(org_id) or []
            
            start = date.replace(hour=0, minute=0, second=0)
            end = date.replace(hour=23, minute=59, second=59)
            
            hourly_activity = {h: 0 for h in range(24)}
            
            for camera in cameras:
                try:
                    events = v2db.get_detection_events(
                        camera_id=camera['id'],
                        start_time=start,
                        end_time=end
                    )
                    
                    cam_stats = {
                        'people': 0,
                        'vehicles': 0,
                        'events': len(events)
                    }
                    
                    for event in events:
                        obj_type = str(event.get('object_type', '')).lower()
                        
                        if 'person' in obj_type or 'odam' in obj_type:
                            report.people_count += 1
                            cam_stats['people'] += 1
                        elif any(v in obj_type for v in ['car', 'mashina', 'vehicle']):
                            report.vehicle_count += 1
                            cam_stats['vehicles'] += 1
                        
                        report.total_events += 1
                        
                        # Track hourly activity
                        event_time = event.get('timestamp')
                        if isinstance(event_time, datetime):
                            hourly_activity[event_time.hour] += 1
                    
                    report.camera_stats[camera['name']] = cam_stats
                    
                except Exception as e:
                    logger.warning(f"Error processing camera {camera['id']}: {e}")
            
            # Find peak hours
            if any(hourly_activity.values()):
                sorted_hours = sorted(hourly_activity.items(), 
                                     key=lambda x: x[1], reverse=True)
                report.peak_hours = [f"{h:02d}:00" for h, _ in sorted_hours[:3] if sorted_hours]
            
            # Get anomalies
            try:
                from ai.anomaly_detector import anomaly_detector
                alerts = anomaly_detector.get_recent_alerts(24)
                report.anomalies_count = len(alerts)
                report.alerts = [
                    {
                        'type': a.type.value,
                        'description': a.description,
                        'timestamp': a.timestamp.isoformat()
                    }
                    for a in alerts[:10]
                ]
            except:
                pass
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report)
            
        except Exception as e:
            logger.error(f"Error generating daily report: {e}")
        
        self.reports.append(report)
        return report
    
    def _generate_recommendations(self, report: AnalysisReport) -> List[str]:
        """Tavsiyalar yaratish."""
        recommendations = []
        
        if report.anomalies_count > 5:
            recommendations.append(
                "⚠️ Oxirgi 24 soatda ko'p anomal hodisa kuzatildi. "
                "Xavfsizlik sozlamalarini ko'rib chiqing."
            )
        
        if report.people_count > 100:
            recommendations.append(
                "👥 Yuqori trafik kuzatildi. Qo'shimcha kameralar qo'shishni o'ylab ko'ring."
            )
        
        if not report.peak_hours:
            recommendations.append(
                "📊 Statistika yig'ish uchun kameralar faol ishlayotganini tekshiring."
            )
        
        if not recommendations:
            recommendations.append("✅ Barcha ko'rsatkichlar normal holatda.")
        
        return recommendations
    
    def format_daily_report(self, report: AnalysisReport) -> str:
        """Hisobotni formatlash."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%d.%m.%Y')
        
        text = (
            f"📊 *KUNLIK HISOBOT*\n"
            f"📅 {yesterday}\n"
            f"━━━━━━━━━━━━━━━━\n\n"
            f"👥 *Odamlar:* {report.people_count} ta\n"
            f"🚗 *Mashinalar:* {report.vehicle_count} ta\n"
            f"📦 *Jami hodisalar:* {report.total_events} ta\n"
        )
        
        if report.anomalies_count > 0:
            text += f"⚠️ *Anomaliyalar:* {report.anomalies_count} ta\n"
        
        if report.peak_hours:
            text += f"\n⏰ *Eng faol vaqt:* {', '.join(report.peak_hours)}\n"
        
        if report.camera_stats:
            text += f"\n📹 *Kameralar bo'yicha:*\n"
            for cam_name, stats in list(report.camera_stats.items())[:5]:
                text += f"  • {cam_name}: {stats['people']}👤 {stats['vehicles']}🚗\n"
        
        if report.recommendations:
            text += f"\n💡 *Tavsiyalar:*\n"
            for rec in report.recommendations[:3]:
                text += f"{rec}\n"
        
        text += f"\n━━━━━━━━━━━━━━━━\n"
        text += f"🤖 _Avtomatik tahlil - Cam Max Pro_"
        
        return text
    
    async def send_scheduled_reports(self):
        """Jadvaldagi hisobotlarni yuborish."""
        if not self.send_callback:
            return
        
        current = datetime.now()
        
        for user_id_str, schedule in self.scheduled_users.items():
            if not schedule.get('enabled', True):
                continue
            
            user_id = int(user_id_str)
            schedule_type = schedule.get('type', 'daily')
            hour = schedule.get('hour', 8)
            
            # Check if it's time
            if current.hour != hour:
                continue
            
            # Check if already sent today
            last_sent = schedule.get('last_sent')
            if last_sent:
                last_sent_date = datetime.fromisoformat(last_sent).date()
                if last_sent_date == current.date():
                    continue
            
            # For weekly, check day
            if schedule_type == 'weekly':
                day = schedule.get('day', 0)
                if current.weekday() != day:
                    continue
            
            # Generate and send report
            try:
                report = await self.generate_daily_report(user_id)
                text = self.format_daily_report(report)
                
                await self.send_callback(user_id, text)
                
                # Update last sent
                self.scheduled_users[user_id_str]['last_sent'] = current.isoformat()
                self._save_schedules()
                
                logger.info(f"Sent {schedule_type} report to user {user_id}")
                
            except Exception as e:
                logger.error(f"Error sending report to user {user_id}: {e}")
    
    async def start_scheduler(self):
        """Hisobot schedulerni boshlash."""
        if self._running:
            return
        
        self._running = True
        logger.info("Auto analysis scheduler started")
        
        while self._running:
            try:
                await self.send_scheduled_reports()
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
            
            # Check every hour
            await asyncio.sleep(3600)
    
    def stop_scheduler(self):
        """Schedulerni to'xtatish."""
        self._running = False
        if self._task:
            self._task.cancel()
    
    def get_user_schedule(self, user_id: int) -> Optional[dict]:
        """Foydalanuvchi jadvalini olish."""
        return self.scheduled_users.get(str(user_id))
    
    async def generate_quick_summary(self, user_id: int) -> str:
        """Tezkor xulosa yaratish."""
        try:
            from database.models import db
            
            user = db.get_user(user_id)
            if not user:
                return "❌ Foydalanuvchi topilmadi"
            
            org_id = user.get('organization_id')
            cameras = db.get_cameras_by_organization(org_id) or []
            stats = db.get_statistics(org_id)
            
            text = (
                f"🔍 *TEZKOR XULOSA*\n"
                f"━━━━━━━━━━━━\n\n"
                f"📹 Kameralar: {len(cameras)} ta\n"
                f"👥 Bugun odamlar: {stats['people_today']} ta\n"
                f"🚗 Bugun mashinalar: {stats['vehicles_today']} ta\n"
                f"📊 Jami hodisalar: {stats['detections_today']} ta\n"
            )
            
            # Zone summary
            try:
                from ai.zone_monitor import zone_monitor
                zone_summary = zone_monitor.get_summary(user_id)
                if zone_summary['total_zones'] > 0:
                    text += f"\n🗺️ Hududlar: {zone_summary['total_zones']} ta\n"
                    if zone_summary['intrusions'] > 0:
                        text += f"⚠️ Buzilishlar: {zone_summary['intrusions']} ta\n"
            except:
                pass
            
            # Anomaly summary
            try:
                from ai.anomaly_detector import anomaly_detector
                alerts = anomaly_detector.get_recent_alerts(1)
                if alerts:
                    text += f"\n🚨 Oxirgi 1 soatda: {len(alerts)} ta alert\n"
            except:
                pass
            
            return text
            
        except Exception as e:
            logger.error(f"Quick summary error: {e}")
            return "❌ Xulosa yaratishda xatolik"
    
    def get_report_history(self, user_id: int, limit: int = 10) -> List[AnalysisReport]:
        """Hisobot tarixi."""
        user_reports = [r for r in self.reports if r.user_id == user_id]
        return sorted(user_reports, key=lambda x: x.generated_at, reverse=True)[:limit]


# Global instance
auto_analyzer = AutoAnalyzer()
