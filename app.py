from flask import Flask, jsonify, request, send_from_directory
import requests
import datetime
import time
import json
import os

app = Flask(__name__, static_folder='.')

# === 游戏配置 ===
REFRESH_INTERVAL = 10  # 刷新间隔（秒）

# === 游戏状态 ===
game_state = {
    'rounds': 0,
    'wins': 0,
    'bets': [],  # 支持多个下注
    'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'symbol': 'BTCUSDT'  # 合约交易对
}

# 数据文件路径
DATA_FILE = 'game_state.json'

# 加载保存的游戏状态
def load_game_state():
    global game_state
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                game_state = json.load(f)
            # 检查是否有活跃下注
            check_and_settle_bets()
        except Exception as e:
            print(f"加载游戏状态失败: {e}")
            reset_game_state()

# 保存游戏状态
def save_game_state():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(game_state, f)
    except Exception as e:
        print(f"保存游戏状态失败: {e}")

# 重置游戏状态
def reset_game_state():
    global game_state
    game_state = {
        'rounds': 0,
        'wins': 0,
        'bets': [],
        'last_updated': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'symbol': 'BTCUSDT'
    }
    save_game_state()

# 获取合约K线数据（无需API签名）
def get_kline_data(symbol, interval, limit=181):
    valid_intervals = ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w', '1M']
    if interval not in valid_intervals:
        print(f"无效的interval参数: {interval}")
        return []

    # 合约K线API (Binance Futures Public API)
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
    except requests.exceptions.RequestException as e:
        print(f"获取K线数据时出错: {e}")
        return []

    ohlc = []
    for item in data:
        timestamp = datetime.datetime.fromtimestamp(item[0] / 1000)
        open_price = float(item[1])
        high = float(item[2])
        low = float(item[3])
        close = float(item[4])
        ohlc.append((timestamp, open_price, high, low, close))

    return ohlc

# 获取当前合约价格（无需API签名）
def get_current_price(symbol):
    # 合约最新价格API (Binance Futures Public API)
    url = "https://fapi.binance.com/fapi/v1/ticker/price"
    params = {"symbol": symbol}
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        price = float(res.json()['price'])
        return price
    except Exception as e:
        print(f"获取当前价格失败: {e}")
        return None

# 检查并结算到期的下注
def check_and_settle_bets():
    global game_state
    now = time.time()
    unsettled_bets = []
    
    for bet in game_state['bets']:
        if bet.get('settled', False):
            continue
            
        elapsed_time = now - bet['start_time']
        if elapsed_time >= bet['prediction_window'] * 60:  # 下注时间已过，结算
            final_price = get_current_price(game_state['symbol'])
            if final_price is None:
                unsettled_bets.append(bet)  # 无法获取价格，保持未结算状态
                continue
                
            result = False
            if bet['direction'] == 'up':
                result = final_price > bet['price']
            else:
                result = final_price < bet['price']
                
            bet['final_price'] = final_price
            bet['result'] = result
            bet['settled'] = True
            
            game_state['rounds'] += 1
            if result:
                game_state['wins'] += 1
        else:
            unsettled_bets.append(bet)  # 未到期，继续保留
            
    game_state['bets'] = unsettled_bets
    game_state['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_game_state()
    
    return unsettled_bets

# 下注
def place_bet(direction, prediction_window):
    global game_state
    price = get_current_price(game_state['symbol'])
    if price is None:
        return False, "无法获取当前价格，无法下注"
    
    new_bet = {
        'id': len(game_state['bets']) + 1,
        'direction': direction,
        'price': price,
        'start_time': time.time(),
        'prediction_window': prediction_window,  # 分钟
        'settled': False
    }
    
    game_state['bets'].append(new_bet)
    game_state['last_updated'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    save_game_state()
    
    return True, {
        'bet_id': new_bet['id'],
        'bet_time': datetime.datetime.fromtimestamp(new_bet['start_time']).strftime('%Y-%m-%d %H:%M:%S'),
        'bet_price': price,
        'direction': direction,
        'prediction_window': prediction_window
    }

# 切换交易对
def switch_symbol(symbol):
    global game_state
    game_state['symbol'] = symbol
    save_game_state()
    return True, f"已切换到 {symbol}"

# === API路由 ===
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/state')
def get_state():
    check_and_settle_bets()  # 先检查是否需要结算
    return jsonify({
        'success': True,
        'state': game_state,
        'refresh_interval': REFRESH_INTERVAL
    })

@app.route('/api/kline/<symbol>/<interval>')
def get_kline(symbol, interval):
    ohlc = get_kline_data(symbol, interval)
    if not ohlc:
        return jsonify({
            'success': False,
            'message': '无法获取K线数据'
        })
    
    # 格式化数据
    formatted_data = []
    for item in ohlc:
        formatted_data.append({
            'timestamp': item[0].strftime('%Y-%m-%d %H:%M:%S'),
            'open': item[1],
            'high': item[2],
            'low': item[3],
            'close': item[4]
        })
    
    return jsonify({
        'success': True,
        'data': formatted_data
    })

@app.route('/api/bet/<direction>/<int:window>')
def api_place_bet(direction, window):
    if direction not in ['up', 'down']:
        return jsonify({
            'success': False,
            'message': '无效的下注方向，必须是"up"或"down"'
        }), 400
    
    if window not in [10, 30, 60, 1440]:
        return jsonify({
            'success': False,
            'message': '无效的预测周期，必须是10、30、60或1440分钟'
        }), 400
    
    success, result = place_bet(direction, window)
    return jsonify({
        'success': success,
        'result': result
    })

@app.route('/api/reset')
def api_reset_game():
    reset_game_state()
    return jsonify({
        'success': True,
        'message': '游戏状态已重置'
    })

@app.route('/api/price/<symbol>')
def api_current_price(symbol):
    price = get_current_price(symbol)
    return jsonify({
        'success': True,
        'price': price
    })

@app.route('/api/switch_symbol/<symbol>')
def api_switch_symbol(symbol):
    if symbol not in ['BTCUSDT', 'ETHUSDT']:
        return jsonify({
            'success': False,
            'message': '无效的交易对，必须是"BTCUSDT"或"ETHUSDT"'
        }), 400
    
    success, result = switch_symbol(symbol)
    return jsonify({
        'success': success,
        'result': result
    })

if __name__ == '__main__':
    load_game_state()  # 加载保存的游戏状态
    app.run(host='0.0.0.0', port=8080, debug=True)