"""
전진개미 — 기업 위험 모니터링 대시보드 v3
Bloomberg/Morningstar 스타일
"""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

st.set_page_config(
    page_title='전진개미 리스크 스크리너',
    page_icon='◼',
    layout='wide',
    initial_sidebar_state='collapsed'
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

*, html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', 'Malgun Gothic', sans-serif !important;
}

.stApp { background: #F2F2EF; }

/* 최상단 헤더 바 */
.top-bar {
    background: #1C2B3A;
    color: #E8E8E0;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    gap: 32px;
    margin: -1rem -1rem 20px -1rem;
    border-bottom: 2px solid #2E4057;
}
.top-bar-title {
    font-size: 13px;
    font-weight: 600;
    color: #FFFFFF;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}
.top-bar-item {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #8BA0B4;
}
.top-bar-item span {
    color: #4FC3F7;
    font-weight: 500;
}
.top-bar-item.up span   { color: #4CAF82; }
.top-bar-item.down span { color: #E05454; }

/* 패널 */
.panel {
    background: #FFFFFF;
    border: 1px solid #D8D8D2;
    margin-bottom: 12px;
}
.panel-header {
    background: #1C2B3A;
    color: #8BA0B4;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 6px 12px;
    border-bottom: 1px solid #2E4057;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.panel-header span { color: #FFFFFF; }
.panel-body { padding: 12px; }

/* KPI 행 */
.kpi-row {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 1px;
    background: #D8D8D2;
    border: 1px solid #D8D8D2;
    margin-bottom: 12px;
}
.kpi-cell {
    background: #FFFFFF;
    padding: 10px 14px;
}
.kpi-cell-label {
    font-size: 9px;
    font-weight: 600;
    color: #8B8B80;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
}
.kpi-cell-value {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 500;
    color: #1C2B3A;
    line-height: 1;
}
.kpi-cell-sub {
    font-size: 10px;
    color: #AAAAAA;
    margin-top: 3px;
    font-family: 'IBM Plex Mono', monospace;
}
.kpi-danger  .kpi-cell-value { color: #E05454; }
.kpi-caution .kpi-cell-value { color: #D4860A; }
.kpi-normal  .kpi-cell-value { color: #2E8B5A; }
.kpi-trap    .kpi-cell-value { color: #7B5EA7; }
.kpi-auc     .kpi-cell-value { color: #1C2B3A; }

/* 매트릭스 테이블 */
.matrix-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}
.matrix-table th {
    background: #1C2B3A;
    color: #8BA0B4;
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 6px 10px;
    text-align: center;
    border: 1px solid #2E4057;
}
.matrix-table td {
    border: 1px solid #E0E0D8;
    padding: 10px 12px;
    text-align: center;
    vertical-align: middle;
}
.matrix-n {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 20px;
    font-weight: 500;
    display: block;
    line-height: 1;
}
.matrix-lbl {
    font-size: 9px;
    letter-spacing: 0.06em;
    display: block;
    margin-top: 3px;
    text-transform: uppercase;
    font-weight: 600;
}
.c-rh { background:#FFF2F2; } .c-rh .matrix-n { color:#E05454; } .c-rh .matrix-lbl { color:#E05454; }
.c-rm { background:#FFF8EE; } .c-rm .matrix-n { color:#D4860A; } .c-rm .matrix-lbl { color:#D4860A; }
.c-rl { background:#FFFDE8; } .c-rl .matrix-n { color:#B8860B; } .c-rl .matrix-lbl { color:#B8860B; }
.c-wh { background:#FFF8EE; } .c-wh .matrix-n { color:#D4860A; } .c-wh .matrix-lbl { color:#D4860A; }
.c-wm { background:#F8F8F5; } .c-wm .matrix-n { color:#666660; } .c-wm .matrix-lbl { color:#888880; }
.c-wl { background:#F0FBF5; } .c-wl .matrix-n { color:#2E8B5A; } .c-wl .matrix-lbl { color:#2E8B5A; }
.c-nh { background:#F0F4FF; } .c-nh .matrix-n { color:#4A6FBF; } .c-nh .matrix-lbl { color:#4A6FBF; }
.c-nm { background:#F8F8F5; } .c-nm .matrix-n { color:#666660; } .c-nm .matrix-lbl { color:#888880; }
.c-nl { background:#EDFBF3; } .c-nl .matrix-n { color:#2E8B5A; } .c-nl .matrix-lbl { color:#2E8B5A; }

/* 탭 */
.stTabs [data-baseweb="tab-list"] {
    background: #1C2B3A;
    gap: 0;
    padding: 0 8px;
}
.stTabs [data-baseweb="tab"] {
    font-size: 11px;
    font-weight: 500;
    color: #8BA0B4 !important;
    padding: 8px 16px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border-bottom: 2px solid transparent;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #FFFFFF !important;
    border-bottom: 2px solid #4FC3F7 !important;
}

/* 필터 바 */
.filter-bar {
    background: #FFFFFF;
    border: 1px solid #D8D8D2;
    padding: 8px 12px;
    display: flex;
    gap: 16px;
    align-items: center;
    margin-bottom: 12px;
    font-size: 11px;
    color: #666660;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: #1C2B3A;
}
section[data-testid="stSidebar"] * { color: #C8D8E4 !important; }
section[data-testid="stSidebar"] label {
    font-size: 9px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #8BA0B4 !important;
}

/* 데이터프레임 */
.stDataFrame { border: 1px solid #D8D8D2 !important; }
div[data-testid="stDataFrame"] table { font-size: 12px !important; }
div[data-testid="stDataFrame"] thead tr th {
    background: #1C2B3A !important;
    color: #8BA0B4 !important;
    font-size: 9px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* 입력 */
.stTextInput input {
    border: 1px solid #D0D0C8;
    background: #FFFFFF;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
}
.stSelectbox div { font-size: 12px; }
</style>
""", unsafe_allow_html=True)

PLOT_CFG = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='#FFFFFF',
    font=dict(family='IBM Plex Sans, Malgun Gothic', color='#1C2B3A', size=11),
    margin=dict(l=8, r=8, t=28, b=8),
)
CLUSTER_COLOR = {
    'EHS':'#E05454','HS':'#2E8B5A','NG':'#4A6FBF',
    'LR':'#D4860A', 'WG':'#7B5EA7','FD':'#888880',
}
CLUSTER_DESC = {
    'EHS':'외형성장-고부채','HS':'고안정','NG':'일반성장',
    'LR':'저수익','WG':'취약성장','FD':'부실',
}

@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base, 'integrated_results_final.csv'), encoding='utf-8-sig')
    df['stock_code'] = df['stock_code'].astype(str).str.zfill(6)
    df['year'] = df['year'].astype(int)
    if 'risk_grade' not in df.columns:
        df['risk_grade'] = df['anomaly_grade'].map({
            'Critical':'위험','High Risk':'위험',
            'Medium Risk':'주의','Watchlist':'주의','Normal':'정상'
        }).fillna('정상')
    if 'val_grade_filled' not in df.columns:
        df['val_grade_filled'] = df['val_grade'].fillna('평가불가') if 'val_grade' in df.columns else '평가불가'
    if 'integrated_score' not in df.columns:
        df['integrated_score'] = df.get('anomaly_score', 0)
    if 'is_anomaly_integrated' not in df.columns:
        df['is_anomaly_integrated'] = df.get('is_anomaly', False)
    return df

df = load_data()

# ── 상단 헤더 바 ──────────────────────────────────────────────────────────────
n_total   = len(df[df['year']==df['year'].max()])
n_danger  = (df[df['year']==df['year'].max()]['risk_grade']=='위험').sum()
n_vt      = ((df[df['year']==df['year'].max()]['risk_grade']=='위험')&
             (df[df['year']==df['year'].max()]['val_grade_filled']=='저평가')).sum()

st.markdown(f"""
<div class="top-bar">
    <div class="top-bar-title">◼ 전진개미 리스크 스크리너</div>
    <div class="top-bar-item">COVERAGE <span>{len(df):,}</span></div>
    <div class="top-bar-item">YEARS <span>{df['year'].min()}–{df['year'].max()}</span></div>
    <div class="top-bar-item down">DANGER ({df['year'].max()}) <span>{n_danger}</span></div>
    <div class="top-bar-item">VALUE TRAP <span>{n_vt}</span></div>
    <div class="top-bar-item up">ROC-AUC <span>0.7411</span></div>
    <div class="top-bar-item up">ΔvS BASELINE <span>+0.0094</span></div>
</div>
""", unsafe_allow_html=True)

# ── 사이드바 필터 ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="padding:12px 0 8px;font-size:10px;letter-spacing:0.14em;text-transform:uppercase;color:#8BA0B4">FILTERS</div>', unsafe_allow_html=True)
    sel_year    = st.multiselect('연도', sorted(df['year'].unique(), reverse=True), default=[df['year'].max()])
    sel_cluster = st.multiselect('군집', sorted(df['cluster_label'].unique()), default=sorted(df['cluster_label'].unique()))
    sel_risk    = st.multiselect('Risk', ['위험','주의','정상'], default=['위험','주의','정상'])

mask = df['year'].isin(sel_year) & df['cluster_label'].isin(sel_cluster) & df['risk_grade'].isin(sel_risk)
df_f = df[mask].copy()

# ── KPI 행 ────────────────────────────────────────────────────────────────────
n_d = (df_f['risk_grade']=='위험').sum()
n_w = (df_f['risk_grade']=='주의').sum()
n_n = (df_f['risk_grade']=='정상').sum()
n_t = ((df_f['risk_grade']=='위험')&(df_f['val_grade_filled']=='저평가')).sum()
tot = len(df_f) or 1

st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-cell kpi-danger">
        <div class="kpi-cell-label">위험</div>
        <div class="kpi-cell-value">{n_d}</div>
        <div class="kpi-cell-sub">{n_d/tot*100:.1f}%</div>
    </div>
    <div class="kpi-cell kpi-caution">
        <div class="kpi-cell-label">주의</div>
        <div class="kpi-cell-value">{n_w}</div>
        <div class="kpi-cell-sub">{n_w/tot*100:.1f}%</div>
    </div>
    <div class="kpi-cell kpi-normal">
        <div class="kpi-cell-label">정상</div>
        <div class="kpi-cell-value">{n_n}</div>
        <div class="kpi-cell-sub">{n_n/tot*100:.1f}%</div>
    </div>
    <div class="kpi-cell kpi-trap">
        <div class="kpi-cell-label">Value Trap</div>
        <div class="kpi-cell-value">{n_t}</div>
        <div class="kpi-cell-sub">위험×저평가</div>
    </div>
    <div class="kpi-cell kpi-auc">
        <div class="kpi-cell-label">ROC-AUC</div>
        <div class="kpi-cell-value">0.7411</div>
        <div class="kpi-cell-sub">▲ +0.94% vs base</div>
    </div>
    <div class="kpi-cell kpi-auc">
        <div class="kpi-cell-label">Avg Precision</div>
        <div class="kpi-cell-value">0.1269</div>
        <div class="kpi-cell-sub">▲ +43.1% vs base</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── 탭 ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(['OVERVIEW', 'SCREENER', 'COMPANY', 'VALUATION'])

# ════════════════
# OVERVIEW
# ════════════════
with tab1:
    col_l, col_r = st.columns([1, 1], gap='small')

    with col_l:
        # 매트릭스
        st.markdown("""
        <div class="panel">
        <div class="panel-header">RISK × VALUATION MATRIX <span>연도 전체 합산</span></div>
        <div class="panel-body">
        """, unsafe_allow_html=True)

        risk_order = ['위험','주의','정상']
        val_order  = ['고평가','적정','저평가']
        css_map = {
            ('위험','고평가'):'c-rh',('위험','적정'):'c-rm',('위험','저평가'):'c-rl',
            ('주의','고평가'):'c-wh',('주의','적정'):'c-wm',('주의','저평가'):'c-wl',
            ('정상','고평가'):'c-nh',('정상','적정'):'c-nm',('정상','저평가'):'c-nl',
        }
        lbl_map = {
            ('위험','고평가'):'AVOID ✗✗',('위험','적정'):'DANGER',('위험','저평가'):'VALUE TRAP',
            ('주의','고평가'):'AVOID ✗', ('주의','적정'):'WATCH', ('주의','저평가'):'CAUTION',
            ('정상','고평가'):'OVERVAL', ('정상','적정'):'NEUTRAL',('정상','저평가'):'BUY ✓',
        }
        rows_html = '<table class="matrix-table"><thead><tr><th></th>'
        for v in val_order:
            rows_html += f'<th>{v}</th>'
        rows_html += '</tr></thead><tbody>'
        for r in risk_order:
            rows_html += f'<tr><th style="text-align:left;width:60px">{r}</th>'
            for v in val_order:
                n   = ((df_f['risk_grade']==r)&(df_f['val_grade_filled']==v)).sum()
                css = css_map.get((r,v),'')
                lbl = lbl_map.get((r,v),'')
                rows_html += f'<td class="{css}"><span class="matrix-n">{n}</span><span class="matrix-lbl">{lbl}</span></td>'
            rows_html += '</tr>'
        rows_html += '</tbody></table>'
        st.markdown(rows_html + '</div></div>', unsafe_allow_html=True)

        # 군집별 박스
        st.markdown('<div class="panel"><div class="panel-header">CLUSTER DISTRIBUTION</div><div class="panel-body">', unsafe_allow_html=True)
        fig_box = px.box(
            df_f, x='cluster_label', y='integrated_score', color='cluster_label',
            category_orders={'cluster_label':['EHS','HS','NG','LR','WG','FD']},
            color_discrete_map=CLUSTER_COLOR,
            labels={'cluster_label':'','integrated_score':''},
            points='outliers',
        )
        fig_box.update_layout(**PLOT_CFG, height=220, showlegend=False,
                              yaxis=dict(gridcolor='#EEEEEA', tickfont=dict(family='IBM Plex Mono',size=10)),
                              xaxis=dict(tickfont=dict(size=11)))
        fig_box.update_traces(marker_size=3, line_width=1.2)
        st.plotly_chart(fig_box, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

    with col_r:
        # 연도별 추이
        st.markdown('<div class="panel"><div class="panel-header">RISK TREND BY YEAR</div><div class="panel-body">', unsafe_allow_html=True)
        trend = df.groupby(['year','risk_grade']).size().reset_index(name='n')
        fig_trend = px.bar(
            trend, x='year', y='n', color='risk_grade',
            color_discrete_map={'위험':'#E05454','주의':'#D4860A','정상':'#2E8B5A'},
            barmode='stack', labels={'year':'','n':'','risk_grade':''},
        )
        fig_trend.update_layout(**PLOT_CFG, height=220,
                                bargap=0.3,
                                legend=dict(orientation='h', y=1.12, font=dict(size=10)),
                                yaxis=dict(gridcolor='#EEEEEA', tickfont=dict(family='IBM Plex Mono',size=10)),
                                xaxis=dict(tickfont=dict(family='IBM Plex Mono',size=11)))
        fig_trend.update_traces(marker_line_width=0)
        st.plotly_chart(fig_trend, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

        # anomaly_grade 분포
        st.markdown('<div class="panel"><div class="panel-header">ANOMALY GRADE BREAKDOWN</div><div class="panel-body">', unsafe_allow_html=True)
        if 'anomaly_grade' in df_f.columns:
            grade_cnt = df_f['anomaly_grade'].value_counts().reset_index()
            grade_cnt.columns = ['grade','count']
            grade_order = ['Critical','High Risk','Medium Risk','Watchlist','Normal']
            grade_color = {'Critical':'#E05454','High Risk':'#E8855A',
                           'Medium Risk':'#D4860A','Watchlist':'#B8A020','Normal':'#2E8B5A'}
            fig_grade = px.bar(
                grade_cnt, x='count', y='grade', orientation='h',
                color='grade', color_discrete_map=grade_color,
                labels={'count':'','grade':''},
                category_orders={'grade':grade_order},
            )
            fig_grade.update_layout(**PLOT_CFG, height=220, showlegend=False,
                                    xaxis=dict(gridcolor='#EEEEEA', tickfont=dict(family='IBM Plex Mono',size=10)),
                                    yaxis=dict(tickfont=dict(size=11)))
            fig_grade.update_traces(marker_line_width=0)
            st.plotly_chart(fig_grade, use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

# ════════════════
# SCREENER
# ════════════════
with tab2:
    # 필터 옵션
    fc1, fc2, fc3, fc4 = st.columns([2,2,1,1])
    with fc1:
        sort_col = st.selectbox('정렬',
            [c for c in ['integrated_score','anomaly_score','val_score_rank'] if c in df_f.columns])
    with fc2:
        grade_filter = st.multiselect('Anomaly Grade',
            df_f['anomaly_grade'].unique().tolist() if 'anomaly_grade' in df_f.columns else [],
            default=df_f['anomaly_grade'].unique().tolist() if 'anomaly_grade' in df_f.columns else [])
    with fc3:
        show_flag = st.checkbox('이상탐지만', True)
    with fc4:
        top_n = st.number_input('표시 수', 10, 500, 100, step=10)

    df_sc = df_f.copy()
    if show_flag and 'is_anomaly_integrated' in df_sc.columns:
        df_sc = df_sc[df_sc['is_anomaly_integrated']==True]
    if grade_filter and 'anomaly_grade' in df_sc.columns:
        df_sc = df_sc[df_sc['anomaly_grade'].isin(grade_filter)]

    df_sc = df_sc.sort_values(sort_col, ascending=False).head(int(top_n))

    show_cols = [c for c in ['corp_name','stock_code','year','cluster_label',
                              'risk_grade','val_grade_filled','integrated_score',
                              'anomaly_score','anomaly_grade','anomaly_taxonomy',
                              'integrated_risk_signal'] if c in df_sc.columns]
    rename = {
        'corp_name':'기업명','stock_code':'종목코드','year':'연도',
        'cluster_label':'군집','risk_grade':'Risk','val_grade_filled':'가치평가',
        'integrated_score':'통합점수','anomaly_score':'재무점수',
        'anomaly_grade':'등급','anomaly_taxonomy':'유형',
        'integrated_risk_signal':'위험신호',
    }
    fmt = {k:v for k,v in {'통합점수':'{:.3f}','재무점수':'{:.3f}'}.items()
           if k in [rename.get(c,c) for c in show_cols]}

    def style_risk(val):
        return {'위험':'color:#E05454;font-weight:600',
                '주의':'color:#D4860A;font-weight:600',
                '정상':'color:#2E8B5A'}.get(str(val),'')

    tbl = df_sc[show_cols].rename(columns=rename)
    risk_col_name = 'Risk' if 'Risk' in tbl.columns else None

    styled = tbl.style.format(fmt, na_rep='-')
    if risk_col_name:
        styled = styled.map(style_risk, subset=[risk_col_name])

    st.dataframe(styled, use_container_width=True, height=520)

    # Value Trap
    vt = df_f[(df_f['risk_grade']=='위험')&(df_f['val_grade_filled']=='저평가')].copy()
    if not vt.empty:
        st.markdown(f'<div class="panel" style="margin-top:12px"><div class="panel-header" style="background:#5C2A2A;border-color:#7A3333">VALUE TRAP WATCHLIST <span>{len(vt)} NAMES</span></div><div class="panel-body">', unsafe_allow_html=True)
        vt_cols = [c for c in ['corp_name','stock_code','year','cluster_label',
                                'integrated_score','pbr','momentum_12m','anomaly_taxonomy'] if c in vt.columns]
        vt_r = {**rename,'pbr':'PBR','momentum_12m':'12M Rtn'}
        vt_fmt = {k:v for k,v in {'통합점수':'{:.3f}','PBR':'{:.2f}','12M Rtn':'{:.1%}'}.items()}
        st.dataframe(
            vt.sort_values('integrated_score',ascending=False)[vt_cols]
              .rename(columns=vt_r).style.format(vt_fmt, na_rep='-'),
            use_container_width=True, height=280
        )
        st.markdown('</div></div>', unsafe_allow_html=True)

# ════════════════
# COMPANY
# ════════════════
with tab3:
    q_col, _ = st.columns([2,3])
    with q_col:
        query = st.text_input('', placeholder='종목코드 / 기업명')

    if query:
        hits = df[(df['stock_code'].str.contains(query,na=False))|
                  (df['corp_name'].str.contains(query,na=False))]['corp_name'].unique()
        sel_corp = st.selectbox('기업', hits) if len(hits) else None
        if not len(hits): st.warning('검색 결과 없음')
    else:
        sel_corp = None

    if sel_corp:
        dc = df[df['corp_name']==sel_corp].sort_values('year')
        latest = dc.iloc[-1]
        code = dc['stock_code'].iloc[0]
        cl = latest['cluster_label']

        # 헤더
        st.markdown(f"""
        <div style="background:#1C2B3A;padding:12px 16px;margin-bottom:12px;display:flex;align-items:baseline;gap:12px">
            <span style="font-family:'IBM Plex Mono',monospace;font-size:18px;font-weight:500;color:#FFFFFF">{sel_corp}</span>
            <span style="font-family:'IBM Plex Mono',monospace;font-size:12px;color:#8BA0B4">{code}</span>
            <span style="font-size:11px;color:#8BA0B4;margin-left:8px">{cl} — {CLUSTER_DESC.get(cl,'')}</span>
        </div>
        """, unsafe_allow_html=True)

        # 지표 행
        m_items = [
            ('RISK GRADE',   latest.get('risk_grade','-')),
            ('VALUATION',    latest.get('val_grade_filled','-')),
            ('INT. SCORE',   f"{latest.get('integrated_score',0):.3f}" if pd.notna(latest.get('integrated_score')) else '-'),
            ('ANOM. GRADE',  latest.get('anomaly_grade','-')),
            ('RISK SIGNAL',  latest.get('integrated_risk_signal','-')),
        ]
        m_cols = st.columns(5)
        for col, (lbl, val) in zip(m_cols, m_items):
            col.markdown(f'<div style="background:#FFF;border:1px solid #D8D8D2;padding:10px 12px"><div style="font-size:9px;font-weight:600;color:#8B8B80;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:4px">{lbl}</div><div style="font-family:IBM Plex Mono,monospace;font-size:15px;font-weight:500;color:#1C2B3A">{val}</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        d1, d2 = st.columns(2, gap='small')

        with d1:
            st.markdown('<div class="panel"><div class="panel-header">SCORE HISTORY</div><div class="panel-body">', unsafe_allow_html=True)
            fig_h = go.Figure()
            for col_name, label, color, dash in [
                ('integrated_score','Integrated','#1C2B3A','solid'),
                ('anomaly_score_rank' if 'anomaly_score_rank' in dc.columns else 'anomaly_score','Financial','#E05454','dash'),
                ('val_score_rank','Valuation','#4A6FBF','dot'),
            ]:
                if col_name in dc.columns:
                    fig_h.add_trace(go.Scatter(
                        x=dc['year'], y=dc[col_name], name=label,
                        mode='lines+markers',
                        line=dict(color=color, width=1.8, dash=dash),
                        marker=dict(size=6, color=color),
                    ))
            fig_h.update_layout(**PLOT_CFG, height=240,
                                yaxis=dict(range=[0,1], gridcolor='#EEEEEA',
                                           tickfont=dict(family='IBM Plex Mono',size=10)),
                                xaxis=dict(tickfont=dict(family='IBM Plex Mono',size=11)),
                                legend=dict(orientation='h', y=1.14, font=dict(size=10)))
            st.plotly_chart(fig_h, use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        with d2:
            st.markdown('<div class="panel"><div class="panel-header">FINANCIAL RADAR</div><div class="panel-body">', unsafe_allow_html=True)
            r_cols = [c for c in ['roa','roe','current_ratio','operating_margin',
                                   'net_profit_margin','ocf_to_assets'] if c in dc.columns]
            if r_cols:
                vals = dc.iloc[-1][r_cols].fillna(0).values.astype(float)
                vals = (np.clip(vals, -2, 2) + 2) / 4
                fig_r = go.Figure(go.Scatterpolar(
                    r=vals.tolist()+[vals[0]], theta=r_cols+[r_cols[0]],
                    fill='toself',
                    fillcolor='rgba(28,43,58,0.08)',
                    line=dict(color='#1C2B3A', width=1.5),
                    marker=dict(size=4, color='#1C2B3A'),
                ))
                fig_r.update_layout(
                    **PLOT_CFG, height=240,
                    polar=dict(
                        radialaxis=dict(visible=True, range=[0,1], gridcolor='#E0E0D8',
                                        tickfont=dict(size=8)),
                        angularaxis=dict(gridcolor='#E0E0D8',
                                         tickfont=dict(size=9)),
                        bgcolor='#FFFFFF',
                    ),
                )
                st.plotly_chart(fig_r, use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

        # 히스토리 테이블
        st.markdown('<div class="panel"><div class="panel-header">ANNUAL HISTORY</div><div class="panel-body">', unsafe_allow_html=True)
        h_cols = [c for c in ['year','cluster_label','risk_grade','val_grade_filled',
                               'integrated_score','anomaly_grade','integrated_risk_signal'] if c in dc.columns]
        st.dataframe(
            dc[h_cols].rename(columns={**rename,'anomaly_grade':'재무등급'})
              .style.format({'통합점수':'{:.3f}'}, na_rep='-'),
            use_container_width=True, hide_index=True, height=200
        )
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:80px 0;text-align:center;color:#AAAAAA;font-size:12px;letter-spacing:0.08em">ENTER TICKER OR COMPANY NAME</div>', unsafe_allow_html=True)

# ════════════════
# VALUATION
# ════════════════
with tab4:
    v1, v2 = st.columns([3,1])
    with v1:
        sc_year = st.selectbox('연도', sorted(df['year'].unique(), reverse=True), key='sc_yr')
    with v2:
        show_top = st.checkbox('상위 30 강조', True)

    df_v = df[(df['year']==sc_year) & df['pbr'].notna() & df['momentum_12m'].notna()].copy()
    df_v = df_v[df_v['pbr'] < df_v['pbr'].quantile(0.97)].copy()

    if show_top:
        top30 = df_v.nlargest(30,'integrated_score').index
        df_v['구분'] = '일반'
        df_v.loc[top30, '구분'] = 'Top 30'
        df_v.loc[(df_v['risk_grade']=='위험')&(df_v['val_grade_filled']=='저평가'), '구분'] = 'Value Trap'
    else:
        df_v['구분'] = '일반'

    st.markdown('<div class="panel"><div class="panel-header">PBR vs 12M RETURN · CLUSTER VIEW</div><div class="panel-body">', unsafe_allow_html=True)
    fig_v = px.scatter(
        df_v, x='pbr', y='momentum_12m',
        color='cluster_label',
        symbol='구분',
        symbol_map={'일반':'circle','Top 30':'star','Value Trap':'x'},
        size='integrated_score', size_max=16,
        color_discrete_map=CLUSTER_COLOR,
        hover_data=['corp_name','stock_code','risk_grade','val_grade_filled','integrated_score'],
        labels={'pbr':'PBR','momentum_12m':'12M Return','cluster_label':''},
        opacity=0.72,
    )
    fig_v.add_hline(y=0, line_dash='dot', line_color='#CCCCCA', line_width=1)
    fig_v.add_vline(x=1, line_dash='dot', line_color='#CCCCCA', line_width=1)
    fig_v.add_shape(type='rect', x0=0, x1=1, y0=-2, y1=0,
                    fillcolor='rgba(46,139,90,0.04)', line=dict(width=0))
    fig_v.update_layout(
        **PLOT_CFG, height=440,
        yaxis=dict(tickformat='.0%', gridcolor='#EEEEEA',
                   tickfont=dict(family='IBM Plex Mono',size=10)),
        xaxis=dict(gridcolor='#EEEEEA',
                   tickfont=dict(family='IBM Plex Mono',size=10)),
        legend=dict(font=dict(size=10), x=1.01),
    )
    st.plotly_chart(fig_v, use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # Top 30 테이블
    if show_top and 'Top 30' in df_v['구분'].values:
        t30 = df_v[df_v['구분']=='Top 30'].sort_values('integrated_score', ascending=False)
        st.markdown(f'<div class="panel"><div class="panel-header">TOP 30 BY INTEGRATED SCORE · {sc_year} <span>{len(t30)} NAMES</span></div><div class="panel-body">', unsafe_allow_html=True)
        t_cols = [c for c in ['corp_name','stock_code','cluster_label','risk_grade',
                               'val_grade_filled','integrated_score','pbr','momentum_12m'] if c in t30.columns]
        t_r = {**rename,'pbr':'PBR','momentum_12m':'12M Rtn'}
        st.dataframe(
            t30[t_cols].rename(columns=t_r)
              .style.format({'통합점수':'{:.3f}','PBR':'{:.2f}','12M Rtn':'{:.1%}'}, na_rep='-'),
            use_container_width=True, height=360
        )
        st.markdown('</div></div>', unsafe_allow_html=True)
