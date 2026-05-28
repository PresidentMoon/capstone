"""
전진개미 — 기업 위험 모니터링 대시보드 v2
==========================================
실행:
    streamlit run 04_monitoring_dashboard.py

필요 파일 (같은 폴더):
    integrated_results_final.csv
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title='전진개미 리스크 모니터',
    page_icon='◈',
    layout='wide',
    initial_sidebar_state='expanded'
)

# ── 커스텀 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', 'Malgun Gothic', sans-serif;
}

/* 전체 배경 */
.stApp {
    background-color: #F7F6F2;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #1A1A1A;
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: #E8E8E4 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {
    color: #999990 !important;
    font-size: 11px !important;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* 헤더 타이틀 */
.dash-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #1A1A1A;
    letter-spacing: -0.02em;
    line-height: 1.1;
    margin-bottom: 2px;
}
.dash-subtitle {
    font-size: 13px;
    color: #888880;
    font-weight: 400;
    letter-spacing: 0.04em;
    margin-bottom: 20px;
}

/* KPI 카드 */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E8E8E0;
    border-radius: 4px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
}
.kpi-danger::before  { background: #FF3B3B; }
.kpi-caution::before { background: #FF9500; }
.kpi-normal::before  { background: #00C274; }
.kpi-trap::before    { background: #8B5CF6; }

.kpi-label {
    font-size: 11px;
    font-weight: 500;
    color: #999990;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.kpi-value {
    font-family: 'DM Mono', monospace;
    font-size: 32px;
    font-weight: 500;
    color: #1A1A1A;
    line-height: 1;
}
.kpi-sub {
    font-size: 12px;
    color: #AAAAAA;
    margin-top: 6px;
}

/* 섹션 헤더 */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 16px;
    font-weight: 700;
    color: #1A1A1A;
    letter-spacing: -0.01em;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #1A1A1A;
}

/* 탭 스타일 */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0;
    border-bottom: 1px solid #E0E0D8;
}
.stTabs [data-baseweb="tab"] {
    font-size: 13px;
    font-weight: 500;
    color: #888880;
    padding: 10px 20px;
    border-bottom: 2px solid transparent;
    background: transparent;
    letter-spacing: 0.02em;
}
.stTabs [aria-selected="true"] {
    color: #1A1A1A !important;
    border-bottom: 2px solid #1A1A1A !important;
    background: transparent !important;
}

/* 태그 배지 */
.tag {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 2px;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.05em;
}
.tag-danger  { background: #FFF0F0; color: #FF3B3B; border: 1px solid #FFD0D0; }
.tag-caution { background: #FFF8EC; color: #FF9500; border: 1px solid #FFE5B0; }
.tag-normal  { background: #EDFAF5; color: #00A862; border: 1px solid #B8EDD8; }
.tag-trap    { background: #F3F0FF; color: #7C3AED; border: 1px solid #DDD6FE; }

/* 매트릭스 셀 */
.matrix-cell {
    border: 1px solid #E8E8E0;
    border-radius: 4px;
    padding: 14px;
    text-align: center;
    font-family: 'DM Sans', sans-serif;
}
.matrix-count {
    font-family: 'DM Mono', monospace;
    font-size: 24px;
    font-weight: 500;
    line-height: 1;
    margin-bottom: 4px;
}
.matrix-label {
    font-size: 11px;
    color: #888880;
}

/* 데이터프레임 */
.stDataFrame {
    border: 1px solid #E8E8E0 !important;
    border-radius: 4px !important;
}

/* 사이드바 구분선 */
.sidebar-divider {
    border: none;
    border-top: 1px solid #333330;
    margin: 16px 0;
}

/* AUC 배지 */
.auc-badge {
    background: #1A1A1A;
    color: #00C274;
    font-family: 'DM Mono', monospace;
    font-size: 20px;
    font-weight: 500;
    padding: 12px 16px;
    border-radius: 4px;
    display: inline-block;
    margin-bottom: 4px;
}
.auc-label {
    font-size: 10px;
    color: #666660;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

/* 검색 입력 */
.stTextInput input {
    border: 1px solid #E0E0D8;
    border-radius: 4px;
    background: #FFFFFF;
    font-family: 'DM Sans', sans-serif;
}

/* 플로팅 숫자 강조 */
.mono { font-family: 'DM Mono', monospace; }
</style>
""", unsafe_allow_html=True)

# ── Plotly 공통 테마 ──────────────────────────────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#FFFFFF',
    font=dict(family='DM Sans, Malgun Gothic, sans-serif', color='#1A1A1A'),
    margin=dict(l=16, r=16, t=24, b=16),
)

CLUSTER_COLOR = {
    'EHS': '#FF6B6B', 'HS': '#4ECDC4', 'NG': '#45B7D1',
    'LR':  '#96CEB4', 'WG': '#FFEAA7', 'FD': '#DDA0DD',
}
CLUSTER_DESC = {
    'EHS': '외형성장-고부채', 'HS': '고안정', 'NG': '일반성장',
    'LR':  '저수익',       'WG': '취약성장', 'FD': '부실',
}

# ── 데이터 로드 & 전처리 ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('integrated_results_final.csv', encoding='utf-8-sig')
    df['stock_code'] = df['stock_code'].astype(str).str.zfill(6)
    df['year'] = df['year'].astype(int)

    # risk_grade 파생
    if 'risk_grade' not in df.columns:
        df['risk_grade'] = df['anomaly_grade'].map({
            'Critical': '위험', 'High Risk': '위험',
            'Medium Risk': '주의', 'Watchlist': '주의',
            'Normal': '정상'
        }).fillna('정상')

    # val_grade_filled
    if 'val_grade_filled' not in df.columns:
        if 'val_grade' in df.columns:
            df['val_grade_filled'] = df['val_grade'].fillna('평가불가')
        else:
            df['val_grade_filled'] = '평가불가'

    # integrated_score
    if 'integrated_score' not in df.columns:
        df['integrated_score'] = df.get('anomaly_score', pd.Series(0, index=df.index))

    # is_anomaly_integrated
    if 'is_anomaly_integrated' not in df.columns:
        df['is_anomaly_integrated'] = df.get('is_anomaly', False)

    return df

df = load_data()

# ── 사이드바 ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:8px 0 20px"><span style="font-family:Syne,sans-serif;font-size:18px;font-weight:800;color:#F7F6F2;letter-spacing:-0.02em">◈ 전진개미</span><br><span style="font-size:11px;color:#666660;letter-spacing:0.06em">RISK MONITOR</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    sel_year = st.multiselect(
        '연도', options=sorted(df['year'].unique(), reverse=True),
        default=[df['year'].max()]
    )
    sel_cluster = st.multiselect(
        '군집', options=sorted(df['cluster_label'].unique()),
        default=sorted(df['cluster_label'].unique())
    )
    sel_risk = st.multiselect(
        'Risk 등급', options=['위험', '주의', '정상'],
        default=['위험', '주의', '정상']
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown('<div class="auc-label">ROC-AUC (통합)</div>', unsafe_allow_html=True)
    st.markdown('<div class="auc-badge">0.7411</div>', unsafe_allow_html=True)
    st.markdown('<div class="auc-label" style="margin-top:4px;color:#00C274">▲ +0.0094 vs 기존</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown(f'<div style="font-size:11px;color:#444440">{len(df):,}개 관측치<br>{df["year"].min()}–{df["year"].max()}</div>', unsafe_allow_html=True)

# 필터
mask = (
    df['year'].isin(sel_year) &
    df['cluster_label'].isin(sel_cluster) &
    df['risk_grade'].isin(sel_risk)
)
df_f = df[mask].copy()

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="dash-title">기업 리스크 모니터링</div>', unsafe_allow_html=True)
st.markdown(f'<div class="dash-subtitle">{", ".join(map(str, sorted(sel_year)))}년 · {len(df_f):,}개 종목 표시 중</div>', unsafe_allow_html=True)

# ── 탭 ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(['전체 현황', '고위험 종목', '종목 상세', '가치평가 스캐너'])

# ════════════════════════════════
# 탭 1 — 전체 현황
# ════════════════════════════════
with tab1:

    # KPI 카드
    n_danger  = (df_f['risk_grade'] == '위험').sum()
    n_caution = (df_f['risk_grade'] == '주의').sum()
    n_normal  = (df_f['risk_grade'] == '정상').sum()
    n_vt      = ((df_f['risk_grade'] == '위험') & (df_f['val_grade_filled'] == '저평가')).sum()
    total     = len(df_f) or 1

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="kpi-card kpi-danger">
            <div class="kpi-label">위험</div>
            <div class="kpi-value">{n_danger}</div>
            <div class="kpi-sub">{n_danger/total*100:.1f}% of total</div>
        </div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="kpi-card kpi-caution">
            <div class="kpi-label">주의</div>
            <div class="kpi-value">{n_caution}</div>
            <div class="kpi-sub">{n_caution/total*100:.1f}% of total</div>
        </div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="kpi-card kpi-normal">
            <div class="kpi-label">정상</div>
            <div class="kpi-value">{n_normal}</div>
            <div class="kpi-sub">{n_normal/total*100:.1f}% of total</div>
        </div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="kpi-card kpi-trap">
            <div class="kpi-label">Value Trap</div>
            <div class="kpi-value">{n_vt}</div>
            <div class="kpi-sub">위험 × 저평가</div>
        </div>''', unsafe_allow_html=True)

    st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

    col_l, col_r = st.columns([1, 1])

    # 9칸 매트릭스
    with col_l:
        st.markdown('<div class="section-title">리스크 매트릭스</div>', unsafe_allow_html=True)

        risk_order = ['위험', '주의', '정상']
        val_order  = ['고평가', '적정', '저평가']
        MATRIX_META = {
            ('위험','고평가'):('즉시 회피','#FFF0F0','#FF3B3B'),
            ('위험','적정'):  ('위험 지속','#FFF8EC','#FF9500'),
            ('위험','저평가'):('Value Trap','#FFF8F0','#FF6B00'),
            ('주의','고평가'):('회피 검토','#FFF8EC','#FF9500'),
            ('주의','적정'):  ('관찰 필요','#FAFAF8','#888880'),
            ('주의','저평가'):('기회 or Trap','#F0FFF8','#00A862'),
            ('정상','고평가'):('과열 주의','#F0F0FF','#6366F1'),
            ('정상','적정'):  ('관망','#FAFAF8','#888880'),
            ('정상','저평가'):('진성 저평가','#EDFAF5','#00A862'),
        }

        for r in risk_order:
            cols = st.columns(3)
            for i, v in enumerate(val_order):
                n = ((df_f['risk_grade']==r)&(df_f['val_grade_filled']==v)).sum()
                label, bg, clr = MATRIX_META.get((r,v), ('-','#FAFAF8','#888880'))
                if i == 0:
                    cols[i].markdown(
                        f'<div style="background:{bg};border:1px solid #E8E8E0;border-radius:4px;padding:14px;text-align:center">'
                        f'<div style="font-size:10px;color:#999990;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">{r} × {v}</div>'
                        f'<div style="font-family:DM Mono,monospace;font-size:26px;font-weight:500;color:{clr};line-height:1">{n}</div>'
                        f'<div style="font-size:11px;color:{clr};margin-top:4px">{label}</div>'
                        f'</div>', unsafe_allow_html=True)
                else:
                    cols[i].markdown(
                        f'<div style="background:{bg};border:1px solid #E8E8E0;border-radius:4px;padding:14px;text-align:center">'
                        f'<div style="font-size:10px;color:#999990;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:4px">{r} × {v}</div>'
                        f'<div style="font-family:DM Mono,monospace;font-size:26px;font-weight:500;color:{clr};line-height:1">{n}</div>'
                        f'<div style="font-size:11px;color:{clr};margin-top:4px">{label}</div>'
                        f'</div>', unsafe_allow_html=True)

    # 연도별 추이
    with col_r:
        st.markdown('<div class="section-title">연도별 위험 종목 추이</div>', unsafe_allow_html=True)
        trend = df.groupby(['year','risk_grade']).size().reset_index(name='n')
        fig_trend = px.bar(
            trend, x='year', y='n', color='risk_grade',
            color_discrete_map={'위험':'#FF3B3B','주의':'#FF9500','정상':'#00C274'},
            barmode='stack',
            labels={'year':'','n':'종목 수','risk_grade':''},
        )
        fig_trend.update_layout(
            **PLOT_THEME, height=340,
            legend=dict(orientation='h', y=1.08, x=0, font=dict(size=12)),
            bargap=0.25,
            xaxis=dict(tickfont=dict(family='DM Mono')),
            yaxis=dict(gridcolor='#F0F0E8'),
        )
        fig_trend.update_traces(marker_line_width=0)
        st.plotly_chart(fig_trend, use_container_width=True)

    # 군집별 integrated_score 분포
    st.markdown('<div class="section-title">군집별 Integrated Score 분포</div>', unsafe_allow_html=True)
    fig_box = px.box(
        df_f, x='cluster_label', y='integrated_score',
        color='cluster_label',
        category_orders={'cluster_label':['EHS','HS','NG','LR','WG','FD']},
        color_discrete_map=CLUSTER_COLOR,
        labels={'cluster_label':'','integrated_score':'Integrated Score'},
        points='outliers',
    )
    fig_box.update_layout(
        **PLOT_THEME, height=300, showlegend=False,
        yaxis=dict(gridcolor='#F0F0E8'),
    )
    fig_box.update_traces(marker_size=3, line_color='#1A1A1A', line_width=1.2)
    st.plotly_chart(fig_box, use_container_width=True)

# ════════════════════════════════
# 탭 2 — 고위험 종목
# ════════════════════════════════
with tab2:
    st.markdown('<div class="section-title">고위험 종목 리스트</div>', unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns([2,2,1])
    with col_f1:
        sort_col = st.selectbox('정렬 기준',
            [c for c in ['integrated_score','anomaly_score','val_score_rank'] if c in df_f.columns])
    with col_f2:
        show_anomaly = st.checkbox('이상탐지 종목만', value=True)
    with col_f3:
        top_n = st.number_input('표시 수', 10, 500, 50, step=10)

    df_show = df_f.copy()
    if show_anomaly and 'is_anomaly_integrated' in df_show.columns:
        df_show = df_show[df_show['is_anomaly_integrated'] == True]

    df_show = df_show.sort_values(sort_col, ascending=False).head(int(top_n))

    show_cols = ['corp_name','stock_code','year','cluster_label',
                 'risk_grade','val_grade_filled','integrated_score',
                 'anomaly_score','anomaly_taxonomy','integrated_risk_signal']
    show_cols = [c for c in show_cols if c in df_show.columns]

    rename = {
        'corp_name':'기업명','stock_code':'종목코드','year':'연도',
        'cluster_label':'군집','risk_grade':'Risk','val_grade_filled':'가치평가',
        'integrated_score':'통합점수','anomaly_score':'재무점수',
        'anomaly_taxonomy':'이상유형','integrated_risk_signal':'위험신호',
    }

    fmt = {}
    if 'integrated_score' in show_cols: fmt['통합점수'] = '{:.3f}'
    if 'anomaly_score' in show_cols:    fmt['재무점수'] = '{:.3f}'

    def style_risk(val):
        m = {'위험':'color:#FF3B3B;font-weight:600',
             '주의':'color:#FF9500;font-weight:600',
             '정상':'color:#00A862'}
        return m.get(val,'')

    styled = (df_show[show_cols].rename(columns=rename)
              .style
              .applymap(style_risk, subset=['Risk'] if 'Risk' in df_show.rename(columns=rename).columns else [])
              .format(fmt, na_rep='-'))
    st.dataframe(styled, use_container_width=True, height=480)

    # Value Trap 섹션
    vt = df_f[(df_f['risk_grade']=='위험')&(df_f['val_grade_filled']=='저평가')].copy()
    if not vt.empty:
        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="section-title">⚠ Value Trap 의심 — {len(vt)}개</div>', unsafe_allow_html=True)
        st.caption('재무 위험 + 저평가 조합. 싸 보이지만 실제로 위험한 종목.')
        vt_cols = [c for c in ['corp_name','stock_code','year','cluster_label',
                                'integrated_score','pbr','momentum_12m','anomaly_taxonomy'] if c in vt.columns]
        vt_rename = {**rename, 'pbr':'PBR', 'momentum_12m':'12m 수익률'}
        vt_fmt = {k:v for k,v in {'통합점수':'{:.3f}','PBR':'{:.2f}','12m 수익률':'{:.1%}'}.items()}
        st.dataframe(
            vt.sort_values('integrated_score',ascending=False)[vt_cols]
              .rename(columns=vt_rename)
              .style.format(vt_fmt, na_rep='-'),
            use_container_width=True, height=280
        )

# ════════════════════════════════
# 탭 3 — 종목 상세
# ════════════════════════════════
with tab3:
    col_inp, _ = st.columns([2,3])
    with col_inp:
        query = st.text_input('', placeholder='종목코드 또는 기업명 검색')

    if query:
        hits = df[(df['stock_code'].str.contains(query, na=False)) |
                  (df['corp_name'].str.contains(query, na=False))]['corp_name'].unique()
        if len(hits) == 0:
            st.warning('검색 결과가 없습니다.')
            sel_corp = None
        elif len(hits) == 1:
            sel_corp = hits[0]
        else:
            sel_corp = st.selectbox('기업 선택', hits)
    else:
        sel_corp = None

    if sel_corp:
        dc = df[df['corp_name'] == sel_corp].sort_values('year')
        latest = dc.iloc[-1]
        code = dc['stock_code'].iloc[0]
        cluster = latest['cluster_label']

        st.markdown(f'<div style="margin:16px 0 4px"><span style="font-family:Syne,sans-serif;font-size:22px;font-weight:800;color:#1A1A1A">{sel_corp}</span> <span style="font-family:DM Mono,monospace;font-size:14px;color:#888880">{code}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:12px;color:#888880;margin-bottom:20px">{cluster} — {CLUSTER_DESC.get(cluster,"")}</div>', unsafe_allow_html=True)

        # 핵심 지표
        m1,m2,m3,m4 = st.columns(4)
        risk_col = {'위험':'#FF3B3B','주의':'#FF9500','정상':'#00A862'}.get(latest.get('risk_grade','정상'),'#888880')
        for col, label, val in [
            (m1, 'Risk 등급', latest.get('risk_grade','-')),
            (m2, '가치평가', latest.get('val_grade_filled','-')),
            (m3, '통합 점수', f"{latest.get('integrated_score',0):.3f}" if pd.notna(latest.get('integrated_score')) else '-'),
            (m4, '최근 연도', str(int(latest['year']))),
        ]:
            col.markdown(f'<div style="background:#FFF;border:1px solid #E8E8E0;border-radius:4px;padding:16px 20px"><div style="font-size:10px;color:#999990;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:6px">{label}</div><div style="font-family:DM Mono,monospace;font-size:20px;font-weight:500;color:#1A1A1A">{val}</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)
        col_d1, col_d2 = st.columns(2)

        # 점수 추이
        with col_d1:
            st.markdown('<div class="section-title">연도별 점수 추이</div>', unsafe_allow_html=True)
            fig_corp = go.Figure()
            score_cols = [
                ('integrated_score', '통합점수', '#1A1A1A', 'solid', 2.5),
                ('anomaly_score_rank' if 'anomaly_score_rank' in dc.columns else 'anomaly_score', '재무점수', '#FF3B3B', 'dash', 1.5),
                ('val_score_rank', '가치평가점수', '#0066FF', 'dot', 1.5),
            ]
            for col_name, name, color, dash, width in score_cols:
                if col_name in dc.columns:
                    fig_corp.add_trace(go.Scatter(
                        x=dc['year'], y=dc[col_name],
                        name=name, mode='lines+markers',
                        line=dict(color=color, width=width, dash=dash),
                        marker=dict(size=7, color=color),
                    ))
            fig_corp.update_layout(
                **PLOT_THEME, height=280,
                legend=dict(orientation='h', y=1.12, font=dict(size=11)),
                yaxis=dict(range=[0,1], gridcolor='#F0F0E8'),
                xaxis=dict(tickfont=dict(family='DM Mono')),
            )
            st.plotly_chart(fig_corp, use_container_width=True)

        # 레이더 차트
        with col_d2:
            st.markdown('<div class="section-title">재무 레이더 (최근)</div>', unsafe_allow_html=True)
            radar_cols = [c for c in ['roa','roe','current_ratio','operating_margin',
                                       'net_profit_margin','ocf_to_assets'] if c in dc.columns]
            if radar_cols:
                vals = dc.iloc[-1][radar_cols].fillna(0).values.astype(float)
                vals = (np.clip(vals, -2, 2) + 2) / 4
                fig_radar = go.Figure(go.Scatterpolar(
                    r=vals.tolist()+[vals[0]],
                    theta=radar_cols+[radar_cols[0]],
                    fill='toself',
                    fillcolor='rgba(0,102,255,0.08)',
                    line=dict(color='#0066FF', width=2),
                    marker=dict(size=5, color='#0066FF'),
                ))
                fig_radar.update_layout(
                    **PLOT_THEME, height=280,
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0,1], gridcolor='#E8E8E0'),
                        angularaxis=dict(gridcolor='#E8E8E0'),
                        bgcolor='#FFFFFF',
                    ),
                )
                st.plotly_chart(fig_radar, use_container_width=True)

        # 히스토리 테이블
        st.markdown('<div class="section-title">연도별 현황</div>', unsafe_allow_html=True)
        hist_cols = [c for c in ['year','cluster_label','risk_grade','val_grade_filled',
                                   'integrated_score','anomaly_grade','integrated_risk_signal'] if c in dc.columns]
        st.dataframe(
            dc[hist_cols].rename(columns={**rename,'anomaly_grade':'재무등급'})
              .style.format({'통합점수':'{:.3f}'}, na_rep='-'),
            use_container_width=True, hide_index=True
        )
    else:
        st.markdown('<div style="padding:60px 0;text-align:center;color:#AAAAAA;font-size:14px">종목코드 또는 기업명을 입력하세요</div>', unsafe_allow_html=True)

# ════════════════════════════════
# 탭 4 — 가치평가 스캐너
# ════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">가치평가 스캐너</div>', unsafe_allow_html=True)
    st.caption('PBR vs 12개월 모멘텀 · 군집별 색상 · integrated_score 상위 30 강조')

    sc_year = st.selectbox('연도', sorted(df['year'].unique(), reverse=True), key='sc_year')
    df_sc = df[(df['year']==sc_year) & df['pbr'].notna() & df['momentum_12m'].notna()].copy()
    df_sc = df_sc[df_sc['pbr'] < df_sc['pbr'].quantile(0.97)].copy()

    top30 = df_sc.nlargest(30, 'integrated_score').index
    df_sc['구분'] = '일반'
    df_sc.loc[top30, '구분'] = '상위 30'
    df_sc.loc[(df_sc['risk_grade']=='위험')&(df_sc['val_grade_filled']=='저평가'), '구분'] = 'Value Trap'

    fig_sc = px.scatter(
        df_sc, x='pbr', y='momentum_12m',
        color='cluster_label',
        symbol='구분',
        symbol_map={'일반':'circle','상위 30':'star','Value Trap':'x'},
        size='integrated_score', size_max=18,
        color_discrete_map=CLUSTER_COLOR,
        hover_data=['corp_name','stock_code','risk_grade','val_grade_filled','integrated_score'],
        labels={'pbr':'PBR','momentum_12m':'12개월 수익률','cluster_label':'군집'},
        opacity=0.75,
    )
    fig_sc.add_hline(y=0,  line_dash='dot', line_color='#CCCCCC', line_width=1)
    fig_sc.add_vline(x=1,  line_dash='dot', line_color='#CCCCCC', line_width=1)
    fig_sc.add_shape(type='rect', x0=0, x1=1, y0=-2, y1=0,
                     fillcolor='rgba(0,194,116,0.04)', line=dict(width=0))
    fig_sc.update_layout(
        **PLOT_THEME, height=500,
        yaxis=dict(tickformat='.0%', gridcolor='#F0F0E8'),
        xaxis=dict(gridcolor='#F0F0E8'),
        legend=dict(orientation='v', x=1.01, font=dict(size=11)),
    )
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown(f'<div class="section-title">Integrated Score 상위 30 · {sc_year}년</div>', unsafe_allow_html=True)
    top30_df = df_sc.loc[top30].sort_values('integrated_score', ascending=False)
    t_cols = [c for c in ['corp_name','stock_code','cluster_label','risk_grade',
                           'val_grade_filled','integrated_score','pbr','momentum_12m'] if c in top30_df.columns]
    t_rename = {**rename,'pbr':'PBR','momentum_12m':'12m 수익률'}
    st.dataframe(
        top30_df[t_cols].rename(columns=t_rename)
          .style.format({'통합점수':'{:.3f}','PBR':'{:.2f}','12m 수익률':'{:.1%}'}, na_rep='-'),
        use_container_width=True, height=380
    )
