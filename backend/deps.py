"""
依存性注入
"""

from database import get_db

# データベースセッション依存性注入
# FastAPI router で使用: Depends(get_db)
__all__ = ["get_db"]
