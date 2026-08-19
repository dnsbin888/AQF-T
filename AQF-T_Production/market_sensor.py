"""
Market Sensor Shadow v1.0 (2026-08-09)
======================================
AVP 冻结期 — 只采集，不决策。

数据源:
  P0: 两融余额 (akshare) → leverage/margin trend
  P1: 龙虎榜 (akshare)  → institution flow quality
  P2: ETF 价格强弱 (pytdx) → risk appetite (small vs large cap)
  P3: 南向资金 (eastmoney) → cross-border sentiment
  P4: 潜龙情绪 (sentiment/cycle/llm) → 板块情绪+市场情绪+LLM情绪解读

输出:
  reports/sensor/YYYYMMDD_sensor.json  ← 每日报告
  reports/sensor/latest_sensor.json    ← 最新快照

禁止事项:
  ❌ 改 AQF-T regime / Gate / LGBM / XGB / CatBoost
  ❌ 生成交易信号
  ✅ 每日记录 + 和 regime 对齐分析
"""
import json, sys, time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

ROOT = Path(__file__).parent
SENSOR_DIR = ROOT / "reports" / "sensor"
SENSOR_DIR.mkdir(parents=True, exist_ok=True)

# ── 工具函数 ──────────────────────────────────────

def _safe_float(v, default=0.0) -> float:
    try:
        return float(v) if v is not None else default
    except (ValueError, TypeError):
        return default

def _pct_change(curr: float, prev: float) -> float:
    """百分比变化，prev=0 时返回 0"""
    if prev and prev != 0:
        return (curr - prev) / abs(prev) * 100
    return 0.0

# ═══════════════════════════════════════════════════
# P0: Margin Sensor (两融)
# ═══════════════════════════════════════════════════

class MarginSensor:
    """融资融券 — 杠杆资金风险偏好"""

    def collect(self) -> dict:
        try:
            import akshare as ak
            sh = ak.macro_china_market_margin_sh()
            sz = ak.macro_china_market_margin_sz()

            latest_sh = sh.iloc[-1]
            latest_sz = sz.iloc[-1]

            total_balance = _safe_float(latest_sh['融资余额']) + _safe_float(latest_sz['融资余额'])
            total_buy = _safe_float(latest_sh['融资买入额']) + _safe_float(latest_sz['融资买入额'])

            # 5日趋势
            if len(sh) >= 6 and len(sz) >= 6:
                bal_5d = _safe_float(sh.iloc[-6]['融资余额']) + _safe_float(sz.iloc[-6]['融资余额'])
                buy_5d = _safe_float(sh.iloc[-6]['融资买入额']) + _safe_float(sz.iloc[-6]['融资买入额'])
                bal_change_5d = _pct_change(total_balance, bal_5d)
                buy_change_5d = _pct_change(total_buy, buy_5d)
            else:
                bal_change_5d = buy_change_5d = 0.0

            # 20日趋势
            if len(sh) >= 21 and len(sz) >= 21:
                bal_20d = _safe_float(sh.iloc[-21]['融资余额']) + _safe_float(sz.iloc[-21]['融资余额'])
                bal_change_20d = _pct_change(total_balance, bal_20d)
            else:
                bal_change_20d = 0.0

            # 趋势判断
            if bal_change_5d > 1.0 and bal_change_20d > 0:
                trend = "expanding"       # 杠杆扩张
            elif bal_change_5d < -1.0:
                trend = "contracting"     # 去杠杆
            else:
                trend = "stable"

            # 强度评分 (0-100)
            score = 50.0
            score += min(bal_change_5d * 4, 20)    # 5日趋势 ±20
            score += min(bal_change_20d * 1, 15)    # 20日趋势 ±15
            score -= abs(bal_change_5d) * 0.5 if abs(bal_change_5d) > 3 else 0  # 波动惩罚
            score = max(0, min(100, score))

            return {
                "total_balance": round(total_balance / 1e8, 2),    # 亿
                "total_buy_amount": round(total_buy / 1e8, 2),     # 亿
                "balance_change_5d_pct": round(bal_change_5d, 2),
                "buy_change_5d_pct": round(buy_change_5d, 2),
                "balance_change_20d_pct": round(bal_change_20d, 2),
                "trend": trend,
                "strength_score": round(score, 1),
                "latest_date": str(latest_sh['日期']),
            }
        except Exception as e:
            return {"error": f"MarginSensor failed: {e}"}

# ═══════════════════════════════════════════════════
# P1: Institution Sensor (龙虎榜)
# ═══════════════════════════════════════════════════

class LHBSensor:
    """龙虎榜 — 机构资金行为"""

    def collect(self) -> dict:
        try:
            import akshare as ak

            # 个股统计（汇总）
            ggtj = ak.stock_lhb_ggtj_sina()
            total_buy = _safe_float(ggtj['累积购买额'].sum())
            total_sell = _safe_float(ggtj['累积卖出额'].sum())
            net_flow = total_buy - total_sell
            stocks_on_board = len(ggtj)

            # 机构买卖明细
            jgmx = ak.stock_lhb_jgmx_sina()
            inst_buy = _safe_float(jgmx['机构席位买入额'].sum())
            inst_sell = _safe_float(jgmx['机构席位卖出额'].sum())
            inst_net = inst_buy - inst_sell
            inst_record_count = len(jgmx)

            # 机构流向判断
            if inst_net > 0:
                inst_flow = "positive"
            elif inst_net < 0:
                inst_flow = "negative"
            else:
                inst_flow = "neutral"

            # 机构参与度
            inst_participation = (inst_buy + inst_sell) / (total_buy + total_sell) * 100 if (total_buy + total_sell) > 0 else 0

            return {
                "total_buy": round(total_buy, 2),           # 万元
                "total_sell": round(total_sell, 2),
                "net_flow": round(net_flow, 2),
                "stocks_on_board": int(stocks_on_board),
                "institution_buy": round(inst_buy, 2),
                "institution_sell": round(inst_sell, 2),
                "institution_net": round(inst_net, 2),
                "institution_records": int(inst_record_count),
                "institution_flow": inst_flow,
                "institution_participation_pct": round(inst_participation, 1),
            }
        except Exception as e:
            return {"error": f"LHBSensor failed: {e}"}

# ═══════════════════════════════════════════════════
# P2: ETF Risk Appetite Sensor
# ═══════════════════════════════════════════════════

class ETFSensor:
    """ETF 相对强弱 — 大小盘风险偏好"""

    # 关键ETF
    TARGETS = [
        ('510050', 'sh', '上证50',    'large'),
        ('510300', 'sh', '沪深300',   'large'),
        ('510500', 'sh', '中证500',   'mid'),
        ('512100', 'sh', '中证1000',  'small'),
        ('588000', 'sh', '科创50',    'small'),
        ('159915', 'sz', '创业板',     'small'),
    ]

    def collect(self) -> dict:
        try:
            sys.path.insert(0, str(Path('D:/quant_web')))
            from tdx_realtime import fetch_batch

            symbols = [(c, m) for c, m, _, _ in self.TARGETS]
            quotes = fetch_batch(symbols)

            etf_data = {}
            large_chg = []
            small_chg = []

            for code, mkt, name, category in self.TARGETS:
                if code in quotes:
                    q = quotes[code]
                    chg = q.get('change_pct', 0)
                    etf_data[code] = {
                        "name": name,
                        "category": category,
                        "close": q.get('close', 0),
                        "change_pct": round(chg, 2),
                        "volume": int(q.get('volume', 0)),
                    }
                    if category == 'large':
                        large_chg.append(chg)
                    elif chg != 0:  # 排除停牌/零值
                        small_chg.append(chg)

            # 风险偏好 = 小盘涨幅 - 大盘涨幅
            avg_large = sum(large_chg) / len(large_chg) if large_chg else 0
            avg_small = sum(small_chg) / len(small_chg) if small_chg else 0

            risk_spread = round(avg_small - avg_large, 2)

            if risk_spread > 0.5:
                risk_appetite = "recovering"    # 小盘强 → 风险偏好恢复
            elif risk_spread < -0.5:
                risk_appetite = "risk_off"      # 大盘强 → 避险
            else:
                risk_appetite = "neutral"

            return {
                "etfs": etf_data,
                "avg_large_cap_chg": round(avg_large, 2),
                "avg_small_cap_chg": round(avg_small, 2),
                "risk_spread": risk_spread,
                "risk_appetite": risk_appetite,
                "data_source": quotes.get(list(quotes.keys())[0], {}).get('source', 'unknown') if quotes else 'no_data',
            }
        except Exception as e:
            return {"error": f"ETFSensor failed: {e}"}

# ═══════════════════════════════════════════════════
# P3: Cross-Border Sensor (南向)
# ═══════════════════════════════════════════════════

class SouthboundSensor:
    """南向资金 — 跨市场情绪 (东方财富 API)"""

    def collect(self) -> dict:
        try:
            import requests

            url = 'https://push2.eastmoney.com/api/qt/kamt.kline/get'
            results = {}

            channels = {
                'sh2hk': ('1.000002', '沪市→港股通'),
                'sz2hk': ('1.000004', '深市→港股通'),
            }

            for key, (secid, label) in channels.items():
                r = requests.get(url, params={
                    'fields1': 'f1,f2', 'fields2': 'f51,f52',
                    'klt': '101', 'lmt': '10', 'secid': secid
                }, timeout=10)
                data = r.json().get('data', {})
                klines = data.get(key, [])

                values = []
                for line in klines[-5:]:  # 最近5天
                    parts = line.split(',')
                    if len(parts) >= 2:
                        values.append({
                            "date": parts[0],
                            "quota_remaining": _safe_float(parts[1]),
                        })
                results[key] = {
                    "label": label,
                    "recent_5d": values,
                }

            # 南向趋势 — 用最新一天 vs 前一天
            all_recent = results.get('sh2hk', {}).get('recent_5d', [])
            if len(all_recent) >= 2:
                curr = all_recent[-1]['quota_remaining']
                prev = all_recent[-2]['quota_remaining']
                # 余额减少 = 资金南下（流入港股）
                chg = _pct_change(curr, prev)
            else:
                chg = 0.0

            if chg < -1.0:
                trend = "southbound_increase"  # 资金南下增加
            elif chg > 1.0:
                trend = "southbound_decrease"  # 资金南下减少
            else:
                trend = "stable"

            return {
                "channels": results,
                "trend": trend,
                "note": "南向资金权重低，仅作为跨市场情绪辅助参考",
            }
        except Exception as e:
            return {"error": f"SouthboundSensor failed: {e}"}

# ═══════════════════════════════════════════════════
# P4: Sentiment Sensor (潜龙情绪系统镜像)
# ═══════════════════════════════════════════════════

class SentimentSensor:
    r"""潜龙情绪三层 — 板块情绪 + 市场情绪 + LLM情绪解读
    数据源: D:\quant_framework\ (sentiment.py, sentiment_cycle.py, llm_sentiment.py)
    AVP规则: 只采集、只记录、不改变 Gate
    """

    def collect(self) -> dict:
        market = self._collect_market()
        cycle = self._collect_cycle()
        llm = self._collect_llm()

        result = {
            "market_sentiment": market,
            "cycle": cycle,
            "llm_sentiment": llm,
        }

        # ── 分组聚合: sentiment_confidence (避免线性累加) ──
        result["sentiment_confidence"] = self._compute_confidence(market, cycle)

        # ── 情绪极端检测 ──
        result["sentiment_extreme"] = self._compute_extreme(market, cycle)

        # ── 情绪变化速度 ──
        result["sentiment_velocity"] = self._compute_velocity(market)

        return result

    def _compute_confidence(self, market: dict, cycle: dict) -> dict:
        """将多层情绪聚合为单一 sentiment_confidence (0-100)
        避免在 _build_summary 中与 margin/etf/lhb 线性累加。
        """
        if "error" in market and "error" in cycle:
            return {"value": 50.0, "status": "no_data", "reason": "情绪数据不可用"}

        score = 50.0
        signals = []

        # 市场情绪 (权重 0.5)
        if "error" not in market:
            mkt_score = market.get("score", 50)
            mkt_label = str(market.get("label", ""))
            if mkt_score >= 75:
                score -= 10  # 过热 → 谨慎
                signals.append("市场情绪过热")
            elif mkt_score >= 60:
                score += 10  # 乐观
                signals.append("市场情绪乐观")
            elif mkt_score < 20:
                score -= 15  # 恐慌
                signals.append("市场情绪恐慌")
            elif mkt_score < 35:
                score -= 5   # 偏冷
                signals.append("市场情绪偏冷")
            # 35-60 中性区间不调整
            # 涨跌比和宽度作为辅助
            breadth = market.get("breadth_pct", 50)
            if breadth > 65:
                score += 5
            elif breadth < 35:
                score -= 5

        # 情绪周期 (权重 0.5)
        if "error" not in cycle:
            stage = cycle.get("stage", "")
            stage_adj = {
                "ferment": 10,    # 最佳参与期
                "startup": 5,     # 试错期
                "climax": -10,    # 高潮末期 → 风险
                "retreat": -15,   # 退潮 → 空仓
            }
            adj = stage_adj.get(stage, 0)
            score += adj
            if adj != 0:
                signals.append(f"周期:{cycle.get('label', stage)}")

        score = max(0, min(100, score))

        if score >= 65:
            status = "favorable"
        elif score <= 35:
            status = "unfavorable"
        else:
            status = "neutral"

        return {
            "value": round(score, 1),
            "status": status,
            "signals": signals,
        }

    def _compute_extreme(self, market: dict, cycle: dict) -> dict:
        """情绪极端状态检测 — 极端值往往是拐点"""
        if "error" in market:
            return {"state": "unknown", "score": None}

        mkt_score = market.get("score", 50)
        limit_up = market.get("limit_up", 0)
        limit_down = market.get("limit_down", 0)

        if mkt_score >= 85:
            state, desc = "overheat", "情绪极端过热，警惕见顶"
        elif mkt_score >= 75:
            state, desc = "hot", "情绪偏热，注意高潮切换"
        elif mkt_score <= 15:
            state, desc = "panic", "情绪极端恐慌，可能见底"
        elif mkt_score <= 25:
            state, desc = "cold", "情绪偏冷，等待回暖信号"
        else:
            state, desc = "normal", "情绪在正常区间"

        # 辅助：涨跌停极端比
        limit_ratio = market.get("limit_ratio", 1)
        if limit_ratio > 10 and state == "normal":
            state, desc = "hot", "涨停远超跌停，情绪亢奋"
        elif limit_down > 100 and state == "normal":
            state, desc = "cold", "百股跌停，情绪骤冷"

        return {
            "state": state,
            "description": desc,
            "score": mkt_score,
            "limit_up": limit_up,
            "limit_down": limit_down,
        }

    def _compute_velocity(self, market: dict) -> dict:
        """情绪变化速度 — 1日/5日变化量，比绝对值更重要"""
        result = {"change_1d": None, "change_5d": None, "note": ""}

        if "error" in market:
            result["note"] = "市场情绪数据不可用"
            return result

        current_score = market.get("score", None)
        if current_score is None:
            return result

        today = datetime.now()

        # 尝试读昨日 sensor 获取 1d 变化
        try:
            yesterday = (today - timedelta(days=1)).strftime("%Y%m%d")
            yesterday_file = SENSOR_DIR / f"{yesterday}_sensor.json"
            if yesterday_file.exists():
                prev = json.loads(yesterday_file.read_text(encoding="utf-8"))
                prev_sent = prev.get("sensors", {}).get("sentiment", {})
                prev_mkt = prev_sent.get("market_sentiment", {})
                prev_score = prev_mkt.get("score")
                if prev_score is not None and "error" not in prev_mkt:
                    result["change_1d"] = round(current_score - prev_score, 1)
        except Exception:
            pass

        # 尝试读 5 天前 sensor 获取 5d 变化
        try:
            day_5ago = (today - timedelta(days=5)).strftime("%Y%m%d")
            day5_file = SENSOR_DIR / f"{day_5ago}_sensor.json"
            if day5_file.exists():
                prev5 = json.loads(day5_file.read_text(encoding="utf-8"))
                prev5_sent = prev5.get("sensors", {}).get("sentiment", {})
                prev5_mkt = prev5_sent.get("market_sentiment", {})
                prev5_score = prev5_mkt.get("score")
                if prev5_score is not None and "error" not in prev5_mkt:
                    result["change_5d"] = round(current_score - prev5_score, 1)
        except Exception:
            pass

        # 描述
        chg = result["change_1d"]
        if chg is not None:
            if chg > 10:
                result["note"] = f"情绪急涨(+{chg})，注意加速赶顶"
            elif chg > 5:
                result["note"] = f"情绪回暖(+{chg})"
            elif chg < -10:
                result["note"] = f"情绪骤降({chg})，警惕恐慌蔓延"
            elif chg < -5:
                result["note"] = f"情绪转冷({chg})"
            else:
                result["note"] = "情绪稳定"

        return result

    def _collect_market(self) -> dict:
        """市场情绪 + 板块情绪 — V2 实时数据优先, EOD parquet 保底
        交易日优先从 V2 /api/market-regime 拉取实时 eastmoney 数据；
        V2 不可达时回退到 sentiment.py + stock_data.parquet EOD 计算。
        """
        # ── 优先: V2 实时数据 (eastmoney 实时推送) ──
        try:
            import urllib.request, json as _json
            req = urllib.request.Request(
                "http://127.0.0.1:5002/api/market-regime",
                headers={"User-Agent": "AQF-T-MarketSensor/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                v2_data = _json.loads(resp.read().decode("utf-8"))
            v2_sent = v2_data.get("sentiment", {})
            if v2_sent and v2_sent.get("total", 0) >= 100:
                result = {
                    "score": v2_sent.get("score", 50),
                    "label": v2_sent.get("label", "未知"),
                    "advance_ratio_pct": v2_sent.get("advance_ratio", 0),
                    "breadth_pct": v2_sent.get("breadth", 0),
                    "limit_up": v2_sent.get("limit_up", 0),
                    "limit_down": v2_sent.get("limit_down", 0),
                    "limit_ratio": v2_sent.get("limit_ratio", 0),
                    "total_stocks": v2_sent.get("total", 0),
                    "hot_sectors": v2_sent.get("hot_sectors", []),
                    "cold_sectors": v2_sent.get("cold_sectors", []),
                    "_source": "V2-realtime",
                    "_news_time": (v2_sent.get("news") or {}).get("time", ""),
                    "_news_label": (v2_sent.get("news") or {}).get("label", ""),
                }
                print(f"[MarketSensor] 实时数据源: V2 (eastmoney) | "
                      f"score={result['score']} LU={result['limit_up']} LD={result['limit_down']} "
                      f"news={result['_news_time']}")
                return result
        except Exception as e:
            print(f"[MarketSensor] V2 实时数据不可达 ({e}), 回退 EOD parquet")

        # ── 保底: EOD parquet 计算 ──
        try:
            import sys as _sys
            _sys.path.insert(0, r"D:\quant_framework")
            _sys.path.insert(0, r"D:\quant_web")
            from data_loader import load_stock_data_cache
            from sentiment import get_market_sentiment

            sd = load_stock_data_cache(
                r"D:\quant_web\stock_data.parquet", keep_days=30
            )
            if not sd:
                return {"error": "stock_data.parquet 为空"}

            sent = get_market_sentiment(sd)

            result = {
                "score": sent.get("score", 50),
                "label": sent.get("label", "未知"),
                "advance_ratio_pct": sent.get("advance_ratio", 0),
                "breadth_pct": sent.get("breadth", 0),
                "limit_up": sent.get("limit_up", 0),
                "limit_down": sent.get("limit_down", 0),
                "limit_ratio": sent.get("limit_ratio", 0),
                "total_stocks": sent.get("total", 0),
                "hot_sectors": sent.get("hot_sectors", []),
                "cold_sectors": sent.get("cold_sectors", []),
                "_source": "EOD-parquet",
            }

            # 非交易日回退: 数据不足时查找最近有效 sensor 数据保底
            if sent.get("label") == "数据不足" or sent.get("total", 0) < 100:
                fallback = self._get_last_valid_market_sentiment()
                if fallback:
                    return fallback

            return result
        except Exception as e:
            return {"error": f"MarketSentiment failed: {e}"}

    def _get_last_valid_market_sentiment(self) -> Optional[dict]:
        """查找最近一个有效交易日的市场情绪数据 (游资战法保底)
        遍历历史 *_sensor.json，返回最近有效的 market_sentiment。
        如果数据本身已是回退数据，保留原始 _fallback_date。
        """
        try:
            files = sorted(SENSOR_DIR.glob("*_sensor.json"), reverse=True)
            for f in files:
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    mkt = data.get("sensors", {}).get("sentiment", {}).get("market_sentiment", {})
                    if not mkt or "error" in mkt:
                        continue
                    total = mkt.get("total_stocks", 0)
                    label = mkt.get("label", "")
                    score = mkt.get("score", 50)
                    # 有效数据: 有足够的股票数, 且不是"数据不足"(非交易日哨兵值)
                    # score=50 可能是真实中性日, 不排除
                    if total >= 100 and label != "数据不足":
                        # 保留原始数据日期: 如果数据本身已是从更早日期回退的，沿用原始日期
                        if not mkt.get("_fallback_date"):
                            mkt["_fallback_date"] = f.stem.replace("_sensor", "")
                        mkt["_fallback"] = True
                        print(f"[MarketSensor] 非交易日，使用缓存: {mkt['_fallback_date']} "
                              f"(score={score}, total={total}, label={label})")
                        return mkt
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def _collect_cycle(self) -> dict:
        """情绪周期 (sentiment_cycle.py) — 四阶段判定"""
        try:
            import sys as _sys
            _sys.path.insert(0, r"D:\quant_framework")
            _sys.path.insert(0, r"D:\quant_web")
            from data_loader import load_stock_data_cache
            from sentiment_cycle import classify

            sd = load_stock_data_cache(
                r"D:\quant_web\stock_data.parquet", keep_days=30
            )
            if not sd:
                return {"error": "stock_data.parquet 为空"}

            cycle = classify(sd)

            return {
                "stage": cycle.get("stage", "unknown"),
                "label": cycle.get("label", "未知"),
                "position_scale": cycle.get("position_scale", 0),
                "sentiment_score": cycle.get("sentiment_score", 0),
                "limit_up": cycle.get("limit_up", 0),
                "limit_down": cycle.get("limit_down", 0),
                "advance_ratio": cycle.get("advance_ratio", 0),
                "breadth": cycle.get("breadth", 0),
                "regime": cycle.get("regime", "unknown"),
                "advice": cycle.get("advice", ""),
            }
        except Exception as e:
            return {"error": f"SentimentCycle failed: {e}"}

    def _collect_llm(self) -> dict:
        """LLM情绪解读 (llm_sentiment.py) — DeepSeek 分析东财头条"""
        try:
            import sys as _sys
            _sys.path.insert(0, r"D:\quant_framework")
            from llm_sentiment import get_llm_sentiment

            llm = get_llm_sentiment()

            return {
                "score": llm.get("score", 0),
                "label": llm.get("label", "未知"),
                "reason": llm.get("reason", ""),
            }
        except Exception as e:
            return {"error": f"LLMSentiment failed: {e}"}


# ═══════════════════════════════════════════════════
# Market Sensor Engine
# ═══════════════════════════════════════════════════

class MarketSensorEngine:
    """汇总所有 Sensor，输出 market_sensor.json"""

    def __init__(self):
        self.margin = MarginSensor()
        self.lhb = LHBSensor()
        self.etf = ETFSensor()
        self.southbound = SouthboundSensor()
        self.sentiment = SentimentSensor()

    def run(self) -> dict:
        """采集所有 Sensor 数据，不干预任何交易决策"""
        today = datetime.now().strftime("%Y-%m-%d")
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result = {
            "report_type": "market_sensor",
            "version": "1.0",
            "status": "shadow",  # AVP 冻结期
            "date": today,
            "timestamp": ts,
            "sensors": {},
            "summary": {},
            "warnings": [],
        }

        # P0: 两融
        margin_data = self.margin.collect()
        result["sensors"]["margin"] = margin_data

        # P1: 龙虎榜
        lhb_data = self.lhb.collect()
        result["sensors"]["lhb"] = lhb_data

        # P2: ETF
        etf_data = self.etf.collect()
        result["sensors"]["etf"] = etf_data

        # P3: 南向
        sb_data = self.southbound.collect()
        result["sensors"]["southbound"] = sb_data

        # P4: 潜龙情绪 (板块情绪 + 市场情绪 + LLM情绪)
        sentiment_data = self.sentiment.collect()
        result["sensors"]["sentiment"] = sentiment_data

        # ── 综合判断 (规则，非 ML) ──
        summary = self._build_summary(result["sensors"])
        result["summary"] = summary

        # ── 写入文件 ──
        self._write(result, today)

        return result

    def _build_summary(self, sensors: dict) -> dict:
        """基于规则的综合市场感知摘要（纯规则，不涉及 ML）"""
        signals = []
        confidence_items = []

        # Margin 信号
        margin = sensors.get("margin", {})
        if "error" not in margin:
            margin_trend = margin.get("trend", "stable")
            if margin_trend == "expanding":
                signals.append("杠杆扩张")
                confidence_items.append(1)
            elif margin_trend == "contracting":
                signals.append("去杠杆")
                confidence_items.append(-1)
            else:
                confidence_items.append(0)

        # LHB 信号
        lhb = sensors.get("lhb", {})
        if "error" not in lhb:
            inst_flow = lhb.get("institution_flow", "neutral")
            if inst_flow == "positive":
                signals.append("机构净买入")
                confidence_items.append(1)
            elif inst_flow == "negative":
                signals.append("机构净卖出")
                confidence_items.append(-1)
            else:
                confidence_items.append(0)

        # ETF 信号
        etf = sensors.get("etf", {})
        if "error" not in etf:
            appetite = etf.get("risk_appetite", "neutral")
            if appetite == "recovering":
                signals.append("风险偏好恢复")
                confidence_items.append(1)
            elif appetite == "risk_off":
                signals.append("资金避险")
                confidence_items.append(-1)
            else:
                confidence_items.append(0)

        # 潜龙情绪信号 (分组聚合, 避免与 margin/etf/lhb 线性累加)
        sentiment = sensors.get("sentiment", {})
        if "error" not in sentiment:
            # 使用分组后的 sentiment_confidence，单值输入
            sent_conf = sentiment.get("sentiment_confidence", {})
            if sent_conf:
                sent_value = sent_conf.get("value", 50)
                # 映射到 -1~1 区间 (50→0, 100→1, 0→-1)
                confidence_items.append((sent_value - 50) / 50)
                for sig in sent_conf.get("signals", []):
                    signals.append(sig)

            # 极端检测 — 极值本身是额外信号
            extreme = sentiment.get("sentiment_extreme", {})
            ext_state = extreme.get("state", "normal")
            if ext_state in ("overheat", "panic"):
                signals.append(f"⚠️情绪极端:{extreme.get('description', '')}")

            # 速度信号 — 变化比绝对值重要
            velocity = sentiment.get("sentiment_velocity", {})
            chg_1d = velocity.get("change_1d")
            if chg_1d is not None and abs(chg_1d) > 5:
                signals.append(velocity.get("note", ""))

            # LLM情绪: 只记录到 signals, 不参与 confidence (AVP铁律)
            llm = sentiment.get("llm_sentiment", {})
            if "error" not in llm:
                llm_score = llm.get("score", 0)
                if abs(llm_score) > 50:
                    signals.append(f"LLM:{llm.get('label', '')}({llm_score})")

        # 综合评分
        raw_score = 0.0
        if confidence_items:
            raw_score = sum(confidence_items) / len(confidence_items)  # -1 to 1
            confidence = round((raw_score + 1) * 50, 1)  # 0 to 100
        else:
            confidence = 50.0

        # 综合状态
        if raw_score > 0.3:
            risk_appetite = "expanding"
            description = "市场资金环境偏暖，杠杆/机构/风险偏好共振向上"
        elif raw_score < -0.3:
            risk_appetite = "contracting"
            description = "市场资金环境偏冷，多指标指向谨慎"
        else:
            risk_appetite = "mixed"
            description = "市场资金信号分化，方向不明确"

        return {
            "risk_appetite": risk_appetite,
            "confidence": confidence,
            "signals": signals,
            "description": description,
            "note": "AVP Shadow — 仅供参考，不参与交易决策",
        }

    def _write(self, result: dict, today: str):
        """写入报告文件"""
        date_key = today.replace("-", "")

        # 每日报告
        daily_file = SENSOR_DIR / f"{date_key}_sensor.json"
        daily_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[MarketSensor] Daily report: {daily_file}")

        # 最新快照
        latest_file = SENSOR_DIR / "latest_sensor.json"
        latest_file.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"[MarketSensor] Latest snapshot: {latest_file}")


# ── CLI ───────────────────────────────────────────

def main():
    print(f"\n{'='*50}")
    print(f"  Market Sensor Shadow v1.0")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  AVP 冻结期 — 只采集，不决策")
    print(f"{'='*50}\n")

    engine = MarketSensorEngine()
    result = engine.run()

    # 打印摘要
    summary = result["summary"]
    print(f"\n  Market Sensor Summary:")
    print(f"    Risk Appetite: {summary['risk_appetite']}")
    print(f"    Confidence:    {summary['confidence']:.0f}")
    print(f"    Signals:       {', '.join(summary['signals']) if summary['signals'] else '无'}")
    print(f"    Description:   {summary['description']}")

    # 传感器状态
    for name, s in result["sensors"].items():
        status = "❌" if "error" in s else "✅"
        print(f"    {status} {name}")

    print(f"\n  {summary['note']}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
