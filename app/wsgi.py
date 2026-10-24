"""Điểm vào cho gunicorn khi deploy:  gunicorn app.wsgi:app

Mặc định chạy chế độ công khai (chỉ Haiku, giới hạn lượt). Biến môi trường:
    APP_PUBLIC=0   tắt chế độ công khai (không nên khi app mở ra Internet)
    APP_FAKE=1     không gọi AI, dùng luật từ khóa (thử deploy khi chưa có API key)
"""
import os

from app.main import create_app

app = create_app(fake=os.environ.get("APP_FAKE") == "1", public=os.environ.get("APP_PUBLIC", "1") != "0")
