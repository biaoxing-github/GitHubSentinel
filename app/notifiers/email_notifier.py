"""
邮件通知器
支持HTML邮件发送和模板渲染
"""

import asyncio
import smtplib
import ssl
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional, Dict, Any

from app.core.config import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class EmailNotifier:
    """邮件通知器"""
    
    def __init__(self):
        self.settings = get_settings()
        self.notification_config = self.settings.notification
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """创建SMTP连接"""
        try:
            logger.info(f"📧 尝试连接SMTP服务器: {self.notification_config.email_smtp_host}:{self.notification_config.email_smtp_port}")
            
            # 创建SMTP连接
            server = smtplib.SMTP(
                self.notification_config.email_smtp_host,
                self.notification_config.email_smtp_port,
                timeout=30  # 添加超时设置
            )
            
            # 设置调试级别（可选）
            # server.set_debuglevel(1)
            
            logger.info("📧 SMTP连接建立成功，开始TLS握手")
            
            # 启用TLS加密
            context = ssl.create_default_context()
            server.starttls(context=context)
            
            logger.info("📧 TLS握手成功，开始认证")
            
            # 登录
            server.login(
                self.notification_config.email_username,
                self.notification_config.email_password
            )
            
            logger.info(f"✅ SMTP连接和认证成功: {self.notification_config.email_smtp_host}")
            return server
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"📧 SMTP认证失败: {str(e)} - 用户名: {self.notification_config.email_username}")
            raise
        except smtplib.SMTPConnectError as e:
            logger.error(f"📧 SMTP连接失败: {str(e)} - 服务器: {self.notification_config.email_smtp_host}:{self.notification_config.email_smtp_port}")
            raise
        except smtplib.SMTPServerDisconnected as e:
            logger.error(f"📧 SMTP服务器断开连接: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"📧 SMTP连接创建失败: {str(e)} - 类型: {type(e).__name__}")
            raise
    
    def _create_message(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> MIMEMultipart:
        """创建邮件消息"""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.notification_config.email_from
        message["To"] = ", ".join(to_emails)
        
        # 添加纯文本版本
        if text_content:
            text_part = MIMEText(text_content, "plain", "utf-8")
            message.attach(text_part)
        
        # 添加HTML版本
        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)
        
        return message
    
    def _send_email_sync(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """同步发送邮件"""
        try:
            # 检查配置
            if not self.notification_config.email_enabled:
                logger.warning("📧 邮件通知未启用，跳过发送")
                return False
            
            # 详细的配置检查
            missing_configs = []
            if not self.notification_config.email_smtp_host:
                missing_configs.append("SMTP主机")
            if not self.notification_config.email_username:
                missing_configs.append("用户名")
            if not self.notification_config.email_password:
                missing_configs.append("密码")
            if not self.notification_config.email_from:
                missing_configs.append("发件人地址")
            
            if missing_configs:
                logger.error(f"📧 邮件配置不完整，缺少: {', '.join(missing_configs)}")
                return False
            
            logger.info(f"📧 开始发送邮件: {subject} -> {', '.join(to_emails)}")
            logger.info(f"📧 SMTP配置: {self.notification_config.email_smtp_host}:{self.notification_config.email_smtp_port}")
            
            # 创建邮件消息
            message = self._create_message(to_emails, subject, html_content, text_content)
            
            # 发送邮件
            with self._create_smtp_connection() as server:
                server.send_message(message)
            
            logger.info(f"✅ 邮件发送成功: {subject} -> {', '.join(to_emails)}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"📧 SMTP认证失败: {str(e)} - 请检查用户名和密码")
            return False
        except smtplib.SMTPConnectError as e:
            logger.error(f"📧 SMTP连接失败: {str(e)} - 请检查主机和端口")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"📧 SMTP错误: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"📧 邮件发送失败: {str(e)}")
            return False
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """异步发送邮件"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._send_email_sync,
            to_emails,
            subject,
            html_content,
            text_content
        )
    
    def _generate_report_html(self, report_data: Dict[str, Any]) -> str:
        """生成报告HTML内容"""
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>GitHub Sentinel 报告</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f8f9fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .section {{
                    background: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #007bff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .ai-section {{
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    color: white;
                    padding: 25px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .stats {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 15px;
                    margin: 20px 0;
                }}
                .stat-card {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    text-align: center;
                    border: 1px solid #e9ecef;
                    transition: transform 0.2s;
                }}
                .stat-card:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }}
                .stat-number {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #007bff;
                    margin-bottom: 5px;
                }}
                .stat-label {{
                    font-size: 14px;
                    color: #666;
                    font-weight: 500;
                }}
                .activity-item {{
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 6px;
                    margin-bottom: 10px;
                    border-left: 3px solid #28a745;
                    transition: background 0.2s;
                }}
                .activity-item:hover {{
                    background: #e9ecef;
                }}
                .activity-title {{
                    font-weight: 600;
                    margin-bottom: 5px;
                    color: #495057;
                }}
                .activity-meta {{
                    font-size: 14px;
                    color: #6c757d;
                }}
                .footer {{
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e9ecef;
                }}
                .ai-badge {{
                    display: inline-block;
                    background: rgba(255,255,255,0.2);
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                    margin-left: 8px;
                }}
                h2 {{
                    color: #495057;
                    border-bottom: 2px solid #e9ecef;
                    padding-bottom: 10px;
                }}
                .repo-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #495057;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 GitHub Sentinel 报告</h1>
                <p>📅 {report_type} - {date}</p>
                <p>🕒 生成时间: {generated_at}</p>
            </div>
            
            <div class="section">
                <h2>📊 统计概览</h2>
                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number">{total_repositories}</div>
                        <div class="stat-label">🏠 监控仓库</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_activities}</div>
                        <div class="stat-label">📈 总活动数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_commits}</div>
                        <div class="stat-label">💻 提交数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">{total_issues}</div>
                        <div class="stat-label">🐛 Issues</div>
                    </div>
                </div>
            </div>
            
            {repositories_content}
            
            <div class="footer">
                <p>此报告由 GitHub Sentinel 自动生成</p>
                <p>如有问题，请联系系统管理员</p>
            </div>
        </body>
        </html>
        """
        
        # 处理仓库内容
        repositories_content = ""
        for repo in report_data.get('repositories', []):
            repo_html = f"""
            <div class="section">
                <div class="repo-title">📁 {repo['name']}</div>
                <p><strong>活动摘要:</strong> {repo.get('summary', '暂无摘要')}</p>
            """
            
            # 添加活动列表
            if repo.get('activities'):
                repo_html += "<h3>📋 最近活动</h3>"
                for activity in repo.get('activities', []):
                    activity_type_emoji = {
                        'commit': '💻',
                        'issue': '🐛', 
                        'pull_request': '🔀',
                        'release': '🚀'
                    }.get(activity.get('type', '').lower(), '📝')
                    
                    repo_html += f"""
                    <div class="activity-item">
                        <div class="activity-title">{activity_type_emoji} {activity.get('title', '无标题')}</div>
                        <div class="activity-meta">
                            👤 {activity.get('author', '未知')} • 🕒 {activity.get('created_at', '未知时间')}
                        </div>
                        {f'<p style="margin-top: 8px; color: #666;">{activity.get("description", "")}</p>' if activity.get('description') else ''}
                    </div>
                    """
            
            repo_html += "</div>"
            repositories_content += repo_html
        
        # 计算统计数据
        total_issues = sum(len([a for a in repo.get('activities', []) if a.get('type') == 'issue']) for repo in report_data.get('repositories', []))
        
        # 填充模板
        return html_template.format(
            report_type=report_data.get('type', '未知类型'),
            date=report_data.get('date', datetime.now().strftime('%Y-%m-%d')),
            total_repositories=len(report_data.get('repositories', [])),
            total_activities=sum(len(repo.get('activities', [])) for repo in report_data.get('repositories', [])),
            total_commits=sum(len([a for a in repo.get('activities', []) if a.get('type') == 'commit']) for repo in report_data.get('repositories', [])),
            total_issues=total_issues,
            repositories_content=repositories_content,
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def _generate_report_text(self, report_data: Dict[str, Any]) -> str:
        """生成报告纯文本内容"""
        text_content = f"""
GitHub Sentinel 报告
{report_data.get('type', '未知类型')} - {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}

统计信息:
- 监控仓库: {len(report_data.get('repositories', []))}
- 总活动数: {sum(len(repo.get('activities', [])) for repo in report_data.get('repositories', []))}

仓库详情:
"""
        
        for repo in report_data.get('repositories', []):
            text_content += f"\n📁 {repo['name']}\n"
            text_content += f"摘要: {repo.get('summary', '暂无摘要')}\n"
            
            for activity in repo.get('activities', []):
                text_content += f"  • [{activity.get('type', 'OTHER')}] {activity.get('title', '无标题')}\n"
                text_content += f"    作者: {activity.get('author', '未知')} | 时间: {activity.get('created_at', '未知时间')}\n"
        
        text_content += f"\n\n此报告由 GitHub Sentinel 自动生成\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return text_content
    
    async def send_report_notification(
        self,
        report_data: Dict[str, Any],
        to_emails: Optional[List[str]] = None
    ) -> bool:
        """发送报告通知邮件"""
        try:
            # 使用默认收件人列表
            if not to_emails:
                to_emails = self.notification_config.email_to
            
            if not to_emails:
                logger.warning("没有配置邮件收件人")
                return False
            
            # 生成邮件内容
            subject = f"GitHub Sentinel {report_data.get('type', '报告')} - {report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}"
            html_content = self._generate_report_html(report_data)
            text_content = self._generate_report_text(report_data)
            
            # 发送邮件
            return await self.send_email(to_emails, subject, html_content, text_content)
            
        except Exception as e:
            logger.error(f"发送报告通知失败: {str(e)}")
            return False
    
    async def send_subscription_notification(
        self,
        subscription_data: Dict[str, Any],
        to_emails: Optional[List[str]] = None
    ) -> bool:
        """发送订阅通知邮件"""
        try:
            if not to_emails:
                to_emails = self.notification_config.email_to
            
            if not to_emails:
                logger.warning("没有配置邮件收件人")
                return False
            
            subject = f"GitHub Sentinel 订阅通知 - {subscription_data.get('repository', '未知仓库')}"
            
            html_content = f"""
            <h2>📢 订阅通知</h2>
            <p>您订阅的仓库 <strong>{subscription_data.get('repository', '未知仓库')}</strong> 有新的活动:</p>
            <ul>
                <li>活动类型: {subscription_data.get('activity_type', '未知')}</li>
                <li>活动标题: {subscription_data.get('activity_title', '无标题')}</li>
                <li>活动时间: {subscription_data.get('activity_time', '未知时间')}</li>
            </ul>
            <p>详情请查看: <a href="{subscription_data.get('activity_url', '#')}">点击查看</a></p>
            """
            
            return await self.send_email(to_emails, subject, html_content)
            
        except Exception as e:
            logger.error(f"发送订阅通知失败: {str(e)}")
            return False
    
    async def test_connection(self) -> bool:
        """测试邮件连接"""
        try:
            with self._create_smtp_connection() as server:
                logger.info("邮件连接测试成功")
                return True
        except Exception as e:
            logger.error(f"邮件连接测试失败: {str(e)}")
            return False 