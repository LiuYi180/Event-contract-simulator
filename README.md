# Event-contract-simulator
一个基于 Web 的加密货币价格预测小游戏，用户可以预测指定加密货币（BTC/USDT、ETH/USDT）的价格走势，测试自己的预测能力并记录历史表现。
# 加密货币价格预测游戏

一个基于Web的加密货币价格预测小游戏，用户可以预测指定加密货币（BTC/USDT、ETH/USDT）的价格走势，测试自己的预测能力并记录历史表现。

## 项目简介

该应用通过调用Binance期货公共API获取实时加密货币价格和K线数据，提供直观的图表展示，并允许用户对未来价格走势（上涨/下跌）进行预测下注。系统会自动结算到期的预测并统计胜率，适合作为加密货币市场分析的趣味练习工具。

## 功能特点

- 实时K线图表展示，支持多种时间周期
- 实时价差图表分析，辅助预测决策
- 多预测周期选择（10分钟、30分钟、1小时、1天）
- 支持BTCUSDT和ETHUSDT两种交易对切换
- 自动记录所有预测历史和结果
- 实时统计胜率和总游戏轮数
- 响应式设计，适配各种设备屏幕

## 技术栈

- **后端**：Python + Flask
- **前端**：HTML5 + Tailwind CSS + JavaScript
- **图表可视化**：Plotly.js
- **数据来源**：Binance Futures Public API
- **样式工具**：Font Awesome 图标库

## 安装与运行

### 前提条件

- Python 3.7+
- pip（Python包管理工具）

### 步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/yourusername/crypto-prediction-game.git
   cd crypto-prediction-game
   ```

2. 安装依赖
   ```bash
   pip install flask requests
   ```

3. 启动应用
   ```bash
   python app.py
   ```

4. 在浏览器中访问
   ```
   http://localhost:8080
   ```

## 使用说明

1. **选择预测周期**：在"选择预测周期"区域点击所需的时间周期（10分钟、30分钟、1小时或1天）
2. **下注**：点击"看涨"（预测价格上涨）或"看跌"（预测价格下跌）按钮提交预测
3. **查看进度**：当前下注会显示在"当前状态"区域，包含剩余时间倒计时
4. **切换交易对**：点击顶部导航栏的"BTCUSDT"或"ETHUSDT"按钮切换加密货币
5. **查看历史**：页面底部的"历史记录"区域展示所有已结算的预测结果
6. **重置游戏**：点击"重置游戏"按钮可清除所有历史记录和当前下注

## 注意事项

- 本应用仅用于学习和娱乐，不构成任何投资建议
- 数据来源于Binance公共API，可能存在一定延迟
- 应用会在本地保存游戏状态（`game_state.json`文件），重置游戏会清除该文件

## 界面预览

<img width="1326" height="897" alt="image" src="https://github.com/user-attachments/assets/4a22ecfa-ffce-4083-b1d4-0445283a3f41" />
<img width="1355" height="898" alt="image" src="https://github.com/user-attachments/assets/2cb6212b-f4dd-4c39-a86a-7a741e64d251" />
