import math
import streamlit as st

st.set_page_config(
    page_title="基金资产配置测算",
    page_icon="📊",
    layout="wide",
)

# -------------------------
# 基础样式
# -------------------------
st.markdown(
    """
    <style>
    .block-container {max-width: 1100px; padding-top: 1.4rem; padding-bottom: 3rem;}
    .hero {
        padding: 1.35rem 1.6rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #18324a, #2c536f);
        color: white;
        margin-bottom: 1.2rem;
    }
    .hero h1 {margin: 0; font-size: 2rem;}
    .hero p {margin: .55rem 0 0; color: #dce8ef; line-height: 1.7;}
    .metric-card {
        border: 1px solid #d9d5cd;
        border-radius: 16px;
        padding: 1rem 1.15rem;
        background: white;
        min-height: 128px;
    }
    .metric-title {color:#6f7478; font-size:.92rem; margin-bottom:.25rem;}
    .metric-value {color:#18324a; font-size:1.65rem; font-weight:800;}
    .fund-card {
        border-radius: 16px;
        padding: 1rem 1.15rem;
        line-height: 1.75;
        min-height: 245px;
    }
    .fund-debt {background:#e8f2f0; border:1px solid #bfd8d3;}
    .fund-index {background:#eaf1f5; border:1px solid #c4d4df;}
    .notice {
        background:#fff8ed;
        border:1px solid #e6c98e;
        border-radius:14px;
        padding: .9rem 1rem;
        line-height:1.7;
    }
    .risk {
        background:#fff2f0;
        border:1px solid #ddb1ab;
        border-radius:14px;
        padding: .9rem 1rem;
        color:#7f332e;
        line-height:1.7;
    }
    div[data-testid="stMetric"] {
        background:white;
        border:1px solid #dedbd4;
        padding: .85rem 1rem;
        border-radius:14px;
    }
    @media (max-width: 640px) {
        .hero h1 {font-size:1.55rem;}
        .hero {padding:1.1rem 1.15rem;}
        .block-container {padding-left: .8rem; padding-right:.8rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>015256＋004945 资产配置测算</h1>
      <p>输入客户可配置资金并选择客户类型，自动计算首次配置、后续目标仓位、分批投入金额与申购费。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

PROFILES = {
    "仅配置债基": {
        "desc": "适合只接受较低波动、暂不参与权益市场的客户，但债券基金仍不保本。",
        "initial": {"debt": 1.00, "index": 0.00, "liquid": 0.00},
        "target": {"debt": 1.00, "index": 0.00, "liquid": 0.00},
        "stages": [],
    },
    "保守型": {
        "desc": "以稳健为主，仅保留少量权益参与仓位。",
        "initial": {"debt": 0.70, "index": 0.05, "liquid": 0.25},
        "target": {"debt": 0.70, "index": 0.15, "liquid": 0.15},
        "stages": [("第1次补仓", 0.05, 0.08), ("第2次补仓", 0.05, 0.15)],
    },
    "一般 / 平衡型": {
        "desc": "兼顾稳健底仓与中长期收益弹性。",
        "initial": {"debt": 0.60, "index": 0.10, "liquid": 0.30},
        "target": {"debt": 0.60, "index": 0.30, "liquid": 0.10},
        "stages": [
            ("第1次补仓", 0.05, 0.05),
            ("第2次补仓", 0.05, 0.10),
            ("第3次补仓", 0.05, 0.15),
            ("第4次补仓", 0.05, 0.20),
        ],
    },
    "进取型": {
        "desc": "适合投资期限较长、能够承受较明显净值波动的客户。",
        "initial": {"debt": 0.40, "index": 0.20, "liquid": 0.40},
        "target": {"debt": 0.40, "index": 0.50, "liquid": 0.10},
        "stages": [
            ("第1次补仓", 0.10, 0.05),
            ("第2次补仓", 0.10, 0.10),
            ("第3次补仓", 0.10, 0.15),
        ],
    },
}

DEBT_RATE = 0.008
INDEX_RATE = 0.015


def money(value: float) -> str:
    return f"¥{value:,.0f}"


def percent(value: float) -> str:
    return f"{value * 100:.0f}%"


def subscription_fee(amount: float, rate: float) -> float:
    return amount - amount / (1 + rate)


# -------------------------
# 客户输入
# -------------------------
with st.container(border=True):
    c1, c2 = st.columns([1, 1])
    with c1:
        amount_wan = st.number_input(
            "客户可配置资金（万元）",
            min_value=0.1,
            value=20.0,
            step=0.1,
            format="%.1f",
        )
    with c2:
        profile_name = st.selectbox(
            "客户类型",
            options=list(PROFILES.keys()),
            index=2,
        )

profile = PROFILES[profile_name]
total = amount_wan * 10_000
initial = profile["initial"]
target = profile["target"]

st.info(f"**{profile_name}：**{profile['desc']}")

# -------------------------
# 首次配置
# -------------------------
st.subheader("首次配置结果")
cols = st.columns(4)
items = [
    ("客户总资金", total),
    ("015256 债基", total * initial["debt"]),
    ("004945 指增", total * initial["index"]),
    ("流动仓", total * initial["liquid"]),
]
for col, (label, value) in zip(cols, items):
    with col:
        st.metric(label, money(value))

if initial["liquid"] > 0:
    st.caption(
        f"流动仓约 {money(total * initial['liquid'])}，可暂放货币基金或现金管理类工具中，等待后续配置，不建议长期躺在活期账户。"
    )
else:
    st.caption("该方案不设置额外流动仓，请确认客户另有充足的应急资金。")

# -------------------------
# 产品介绍
# -------------------------
st.subheader("两只基金在组合中的分工")
f1, f2 = st.columns(2)
with f1:
    st.markdown(
        """
        <div class="fund-card fund-debt">
          <h3>015256｜鹏华畅享债券A</h3>
          <ul>
            <li>二级债基，债券资产不低于80%</li>
            <li>股票及存托凭证最高不超过20%</li>
            <li>主要负责降低组合波动、提供稳健底仓</li>
            <li>不保本，短期仍可能出现净值回撤</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
with f2:
    st.markdown(
        """
        <div class="fund-card fund-index">
          <h3>004945｜长信中证500指数增强A</h3>
          <ul>
            <li>股票指数增强基金，股票仓位不低于80%</li>
            <li>跟踪中证500并通过量化选股争取超额收益</li>
            <li>主要负责提升组合的权益收益弹性</li>
            <li>净值波动较大，更适合分批配置和长期持有</li>
          </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# -------------------------
# 目标仓位与分批金额
# -------------------------
st.subheader("后续目标结构")
t1, t2, t3 = st.columns(3)
with t1:
    st.metric("债基目标", f"{percent(target['debt'])} · {money(total * target['debt'])}")
with t2:
    st.metric("指增目标上限", f"{percent(target['index'])} · {money(total * target['index'])}")
with t3:
    st.metric("流动仓目标", f"{percent(target['liquid'])} · {money(total * target['liquid'])}")

if not profile["stages"]:
    st.markdown(
        '<div class="notice"><strong>后续安排：</strong>不配置中证500指数增强，不设置补仓计划。</div>',
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f'<div class="notice"><strong>分批配置：</strong>首次只建立部分004945仓位，剩余资金根据市场变化逐步投入；004945最终不超过总资金的{percent(target["index"])}。</div>',
        unsafe_allow_html=True,
    )
    stage_cols = st.columns(len(profile["stages"]))
    for col, (label, stage_pct, _) in zip(stage_cols, profile["stages"]):
        with col:
            st.metric(label, money(total * stage_pct), f"总资金的{percent(stage_pct)}", delta_color="off")

# -------------------------
# 客户沟通摘要
# -------------------------
summary_lines = [
    f"客户类型：{profile_name}",
    f"可配置资金：{money(total)}",
    f"015256首次配置：{percent(initial['debt'])}，{money(total * initial['debt'])}",
]
if initial["index"] > 0:
    summary_lines.append(
        f"004945首次配置：{percent(initial['index'])}，{money(total * initial['index'])}"
    )
if initial["liquid"] > 0:
    summary_lines.append(
        f"流动仓：{percent(initial['liquid'])}，{money(total * initial['liquid'])}"
    )
summary_lines.append(
    f"后续目标：债基{percent(target['debt'])}、指增{percent(target['index'])}、流动仓{percent(target['liquid'])}。"
)
summary_lines.append("提示：基金不保本，实际配置需结合客户风险测评与适当性要求。")

with st.expander("生成可复制的客户配置摘要"):
    st.text_area("配置摘要", value="\n".join(summary_lines), height=190)

# -------------------------
# 内部测算
# -------------------------
with st.expander("内部执行与有效户测算", expanded=False):
    debt_amount = total * initial["debt"]
    index_amount = total * initial["index"]
    debt_fee = subscription_fee(debt_amount, DEBT_RATE)
    index_fee = subscription_fee(index_amount, INDEX_RATE)
    total_fee = debt_fee + index_fee

    coef = initial["debt"] * (DEBT_RATE / (1 + DEBT_RATE)) + initial["index"] * (
        INDEX_RATE / (1 + INDEX_RATE)
    )
    min_capital = 200 / coef if coef > 0 else 0

    a, b, c = st.columns(3)
    with a:
        st.metric("预计首次申购费", money(total_fee))
    with b:
        st.metric("200元标准", "达到" if total_fee >= 200 else "未达到")
    with c:
        st.metric("理论最低资金", money(min_capital))

    st.caption(
        f"015256预计申购费：{money(debt_fee)}；004945预计申购费：{money(index_fee)}。费率口径：015256为0.80%，004945为1.50%。"
    )

    st.markdown("#### 可选：按首次建仓点计算内部补仓点位")
    p0 = st.number_input(
        "中证500首次建仓参考点位 P0",
        min_value=1,
        value=8100,
        step=10,
    )

    if not profile["stages"]:
        st.caption("该类型不配置004945，因此无补仓点位。")
    else:
        point_data = []
        for label, stage_pct, drop in profile["stages"]:
            point_data.append(
                {
                    "阶段": label,
                    "指数回撤": percent(drop),
                    "参考点位": round(p0 * (1 - drop)),
                    "投入比例": percent(stage_pct),
                    "投入金额": money(total * stage_pct),
                }
            )
        st.dataframe(point_data, use_container_width=True, hide_index=True)

    st.markdown(
        '<div class="risk"><strong>内部提醒：</strong>客户明确不能接受任何本金波动时，不应把015256或004945介绍为“零风险”或“保本”产品。</div>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "本工具用于辅助展示和内部测算，不构成收益承诺或个性化投资建议。实际配置应结合客户风险测评、资金期限、产品风险等级、下单页面费率及公司适当性要求。"
)
