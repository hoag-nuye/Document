@echo off

echo.
echo [CLEANUP] Cleaning up unused Docker data...
# Xóa dangling images và cache
docker system prune -f

echo.
echo [CLEANUP] Pruning BuildKit cache...
# Xóa cả volumes, networks không dùng
docker system prune --volumes -f

echo.
echo All Docker cleanup completed.
pause
