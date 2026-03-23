@echo off
echo ========================================
echo 星巴克戰報 - 自動同步腳本 (GitHub -> 本機)
echo ========================================
cd /d "D:\Coding Antigravity\starbucks project"

echo [1/2] 正在向雲端請求最新報告...
git pull origin main

echo [2/2] 報告已成功匯入 Obsidian 庫！
echo (視窗將在 5 秒後關閉)
timeout /t 5 >nul
exit
