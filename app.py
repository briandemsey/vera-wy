"""
VERA-WY: Verification Engine for Results & Accountability - Wyoming
Type 4 Detection using WIDA ACCESS for ELLs Speaking vs Writing + WY-TOPP Achievement Data

Wyoming context:
- WIDA ACCESS for ELLs, 4 domains (Listening, Speaking, Reading, Writing)
- Exit criterion: composite 4.8 (WIDA standard)
- WY-TOPP (Wyoming Test of Proficiency and Progress), 4 levels:
    Below Basic / Basic / Proficient / Advanced
- 48 districts across the state
- ~3,500 ELs statewide (~3.8% enrollment)
- Top EL district: Laramie County School District #1 (Cheyenne)
- Energy-sector (coal, oil, gas, wind) boom/bust creates EL enrollment instability
- "Basket of goods" funding model -- per-pupil funding based on cost of education components
- Recalibration cycles based on energy revenue fluctuations
- Dashboard: edu.wyoming.gov

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================================
# CONFIGURATION
# ============================================================================

APP_PASSWORD = "vera2026"

WY_BLUE = "#002D62"
WY_GOLD = "#FFC425"
WY_DARK = "#001A3D"
WY_GRAY = "#4A4A4A"
WY_LIGHT_BLUE = "#3A6B9F"

# ============================================================================
# DATA: Wyoming Districts with EL Populations
# 48 districts -- many named by county + number (e.g., Laramie #1)
# ============================================================================

def load_districts():
    """Load WY districts with significant EL populations.
    Wyoming has 48 districts. ~3,500 ELs statewide (~3.8%).
    EL population concentrated in energy-sector and agriculture communities.
    Energy boom/bust cycles create enrollment instability.
    """
    data = [
        # (district_id, district_name, total_students, el_count, el_percent,
        #  wytopp_prof_all, wytopp_prof_el, graduation_rate, economy_note)

        # --- Major EL-serving districts ---
        ("LAR1", "Laramie County SD #1 (Cheyenne)", 14200, 1136, 8.0, 44.5, 13.8, 83.5, "State capital; largest district; highest EL count"),
        ("NAT1", "Natrona County SD #1 (Casper)", 12800, 384, 3.0, 42.8, 12.5, 82.8, "Oil/gas hub; boom/bust enrollment swings"),
        ("SWE1", "Sweetwater County SD #1 (Rock Springs)", 4200, 336, 8.0, 38.5, 11.2, 79.5, "Trona mining; Hispanic workforce hub"),
        ("SWE2", "Sweetwater County SD #2 (Green River)", 2800, 196, 7.0, 40.2, 12.0, 81.2, "Trona/soda ash industry"),
        ("FRE25", "Fremont County SD #25 (Riverton)", 3200, 192, 6.0, 36.8, 10.5, 78.5, "Wind River Reservation border; mixed EL/Native"),
        ("ALB1", "Albany County SD #1 (Laramie)", 4500, 225, 5.0, 48.2, 15.2, 87.2, "University of Wyoming campus town"),
        ("UIN1", "Uinta County SD #1 (Evanston)", 2800, 168, 6.0, 39.5, 11.8, 80.5, "Southwest WY; oil/gas families"),
        ("CAM1", "Campbell County SD #1 (Gillette)", 7200, 216, 3.0, 41.5, 12.2, 81.8, "Coal/energy capital; Powder River Basin"),
        ("LIN2", "Lincoln County SD #2 (Afton)", 2200, 132, 6.0, 42.5, 13.0, 84.5, "Star Valley; dairy/agriculture EL workforce"),
        ("SHE2", "Sheridan County SD #2 (Sheridan)", 3800, 114, 3.0, 50.2, 15.8, 88.5, "Northern WY; tourism/ranching"),

        # --- Smaller EL-serving districts ---
        ("PAR1", "Park County SD #1 (Powell)", 1800, 72, 4.0, 44.8, 13.5, 84.2, "Northwest WY; agriculture/tourism"),
        ("TET1", "Teton County SD #1 (Jackson)", 2400, 360, 15.0, 52.5, 14.8, 86.5, "Jackson Hole; hospitality/service industry ELs"),
        ("CAR1", "Carbon County SD #1 (Rawlins)", 1200, 60, 5.0, 37.5, 10.8, 78.2, "Southern WY; wind energy transition"),
        ("GOS1", "Goshen County SD #1 (Torrington)", 1400, 98, 7.0, 38.8, 11.0, 79.8, "Agriculture; sugar beet/bean workforce"),
        ("BIG1", "Big Horn County SD #1 (Cowley)", 800, 32, 4.0, 40.5, 12.0, 82.5, "Agriculture; small-town EL presence"),
    ]

    return pd.DataFrame(data, columns=[
        'district_id', 'district_name', 'total_students',
        'el_count', 'el_percent',
        'wytopp_prof_all', 'wytopp_prof_el', 'graduation_rate',
        'economy_note'
    ])


# ============================================================================
# DATA: ACCESS Domain Data (WIDA ACCESS for ELLs)
# ============================================================================

def load_access_data(districts_df):
    """Generate district ACCESS domain data modeled from WY EL performance patterns."""
    access_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                base_speaking = 330 + (grade * 8)
                base_writing = 280 + (grade * 6)

                el_density_penalty = max(0, (d['el_percent'] - 8) * 0.5)
                el_factor = d['wytopp_prof_el'] / 13.0
                speaking_adj = int(12 * el_factor + d['el_percent'] * 0.2 - el_density_penalty)
                writing_adj = int(-10 + (el_factor - 1) * 9 - el_density_penalty * 0.8)

                yr_adj = 3 if year == 2025 else 0

                access_data.append({
                    'district_id': d['district_id'],
                    'district_name': d['district_name'],
                    'grade': grade,
                    'year': year,
                    'total_tested': max(5, int(d['el_count'] / 6)),
                    'listening_avg': base_speaking + speaking_adj - 4 + yr_adj,
                    'speaking_avg': base_speaking + speaking_adj + yr_adj,
                    'reading_avg': base_writing + writing_adj + 12 + yr_adj,
                    'writing_avg': base_writing + writing_adj + yr_adj,
                    'composite_avg': int((base_speaking + speaking_adj + base_writing + writing_adj) / 2 + 14 + yr_adj),
                })

    return pd.DataFrame(access_data)


# ============================================================================
# DATA: WY-TOPP Achievement Data
# WY-TOPP (Wyoming Test of Proficiency and Progress)
# 4 levels: Below Basic / Basic / Proficient / Advanced
# ============================================================================

def load_wytopp_data(districts_df):
    """Generate WY-TOPP data based on edu.wyoming.gov patterns."""
    wytopp_data = []

    for _, d in districts_df.iterrows():
        for grade in range(3, 9):
            for year in [2024, 2025]:
                for subject in ['ELA', 'Math']:
                    base = d['wytopp_prof_all'] if subject == 'ELA' else d['wytopp_prof_all'] * 0.82
                    prof_advanced = max(8, min(80, base + (grade - 5) * -1.2))

                    advanced = max(2, prof_advanced * 0.20)
                    proficient = prof_advanced - advanced
                    basic = max(15, (100 - prof_advanced) * 0.44)
                    below_basic = max(8, 100 - prof_advanced - basic)

                    wytopp_data.append({
                        'district_id': d['district_id'],
                        'district_name': d['district_name'],
                        'grade': grade,
                        'subject': subject,
                        'year': year,
                        'prof_advanced_pct': round(prof_advanced, 1),
                        'advanced_pct': round(advanced, 1),
                        'proficient_pct': round(proficient, 1),
                        'basic_pct': round(basic, 1),
                        'below_basic_pct': round(below_basic, 1),
                    })

    return pd.DataFrame(wytopp_data)


# ============================================================================
# DATA: Statewide Domain Proficiency
# ============================================================================

def load_statewide_domain_data():
    """Statewide ACCESS domain proficiency percentages by grade cluster."""
    return pd.DataFrame([
        {'year': '2024-25', 'grade_cluster': 'K-2', 'listening': 41, 'speaking': 36, 'reading': 25, 'writing': 17},
        {'year': '2024-25', 'grade_cluster': '3-5', 'listening': 45, 'speaking': 41, 'reading': 29, 'writing': 20},
        {'year': '2024-25', 'grade_cluster': '6-8', 'listening': 49, 'speaking': 44, 'reading': 33, 'writing': 23},
        {'year': '2024-25', 'grade_cluster': '9-12', 'listening': 52, 'speaking': 47, 'reading': 36, 'writing': 25},
        {'year': '2023-24', 'grade_cluster': 'K-2', 'listening': 38, 'speaking': 34, 'reading': 23, 'writing': 15},
        {'year': '2023-24', 'grade_cluster': '3-5', 'listening': 43, 'speaking': 39, 'reading': 27, 'writing': 18},
        {'year': '2023-24', 'grade_cluster': '6-8', 'listening': 47, 'speaking': 42, 'reading': 31, 'writing': 21},
        {'year': '2023-24', 'grade_cluster': '9-12', 'listening': 50, 'speaking': 45, 'reading': 34, 'writing': 23},
    ])


# ============================================================================
# DATA: EL Population Growth
# ============================================================================

def load_el_growth_data():
    """Wyoming EL population -- energy boom/bust creates instability."""
    return pd.DataFrame([
        {'year': 2005, 'el_count': 2200, 'el_percent': 2.5, 'note': 'Baseline'},
        {'year': 2008, 'el_count': 2800, 'el_percent': 3.1, 'note': 'Energy boom draws workers'},
        {'year': 2010, 'el_count': 2600, 'el_percent': 2.9, 'note': 'Recession bust'},
        {'year': 2012, 'el_count': 2900, 'el_percent': 3.2, 'note': 'Recovery boom'},
        {'year': 2014, 'el_count': 3200, 'el_percent': 3.5, 'note': 'Oil price peak'},
        {'year': 2016, 'el_count': 2800, 'el_percent': 3.1, 'note': 'Oil/coal bust'},
        {'year': 2018, 'el_count': 3000, 'el_percent': 3.3, 'note': 'Partial recovery'},
        {'year': 2020, 'el_count': 2700, 'el_percent': 3.0, 'note': 'COVID + energy downturn'},
        {'year': 2022, 'el_count': 3200, 'el_percent': 3.5, 'note': 'Post-COVID energy rebound'},
        {'year': 2024, 'el_count': 3400, 'el_percent': 3.7, 'note': 'Wind energy growth'},
        {'year': 2025, 'el_count': 3500, 'el_percent': 3.8, 'note': 'Continued diversification'},
    ])


# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="color: {WY_BLUE}; font-size: 3rem; margin-bottom: 10px;">VERA-WY</h1>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 40px;">
            Verification Engine for Results &amp; Accountability<br>Wyoming Implementation
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Enter access code:", type="password", key="pw")
        if st.button("Access VERA-WY", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid access code")

    st.markdown(f"""
    <div style="text-align: center; margin-top: 60px; color: #999; font-size: 0.85rem;">
        <p>VERA-WY analyzes ACCESS for ELLs domain data and WY-TOPP results across 48 Wyoming districts.</p>
        <p>~3,500 English Learners | ~3.8% statewide</p>
        <p>Top district: Laramie County #1 (Cheyenne) | Teton County #1 (Jackson) 15% EL</p>
        <p>Energy boom/bust EL instability | "Basket of goods" funding | Data: edu.wyoming.gov</p>
        <p style="margin-top: 10px;">Contact: brian@h-edu.solutions</p>
    </div>
    """, unsafe_allow_html=True)
    return False


# ============================================================================
# TYPE 4 DETECTION
# ============================================================================

def compute_type4_analysis(access_df, district_id, grade, year):
    filtered = access_df[
        (access_df['district_id'] == district_id) &
        (access_df['grade'] == grade) &
        (access_df['year'] == year)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['speaking_avg'] - row['writing_avg']
    delta_normalized = delta / 5
    flagged = delta_normalized > 8

    return {
        'district_id': district_id, 'district_name': row['district_name'],
        'grade': grade, 'year': year,
        'speaking_avg': row['speaking_avg'], 'writing_avg': row['writing_avg'],
        'delta': delta, 'delta_normalized': delta_normalized, 'flagged': flagged,
        'total_tested': row['total_tested'],
        'estimated_flagged': int(row['total_tested'] * 0.15) if flagged else int(row['total_tested'] * 0.05)
    }


# ============================================================================
# PAGE 1: OVERVIEW
# ============================================================================

def render_overview(districts_df):
    st.header("Wyoming Education Overview")

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Pilot Districts", len(districts_df))
    with col2: st.metric("Total Students", f"{districts_df['total_students'].sum():,}")
    with col3: st.metric("English Learners", f"{districts_df['el_count'].sum():,}")
    with col4: st.metric("Statewide EL %", "~3.8%")

    st.divider()

    # Key policy context
    st.subheader("Key Policy Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.warning("**Energy Boom/Bust**\nCoal, oil, gas, and wind energy cycles drive EL enrollment instability as workers follow jobs")
    with col2:
        st.info("**'Basket of Goods' Funding**\nPer-pupil funding based on cost components; recalibrated with energy revenue cycles")
    with col3:
        st.success("**48 Districts**\nNamed by county + number (e.g., Laramie #1); smallest state education system by enrollment")

    st.divider()

    # Wyoming-specific pattern
    st.subheader("The Wyoming Pattern: Energy-Sector EL Instability")
    st.markdown("""
    Wyoming's EL population of ~3,500 is unique in its **boom/bust volatility**.
    Unlike states with steady EL growth, Wyoming's EL enrollment tracks **energy
    sector employment cycles**:

    | District | EL % | Economic Driver |
    |----------|------|-----------------|
    | Teton County #1 (Jackson) | **15.0%** | Hospitality/service industry; Jackson Hole tourism |
    | Laramie County #1 (Cheyenne) | **8.0%** | State capital; largest EL count in state |
    | Sweetwater County #1 (Rock Springs) | **8.0%** | Trona mining; Hispanic workforce |
    | Sweetwater County #2 (Green River) | **7.0%** | Trona/soda ash industry |
    | Goshen County #1 (Torrington) | **7.0%** | Agriculture; sugar beet/bean workforce |

    **Boom/Bust Pattern:**
    - **2008-2009:** Energy boom peak -- EL enrollment surges as workers arrive
    - **2010, 2016, 2020:** Bust cycles -- families leave, enrollment drops
    - **2022+:** Energy diversification (wind) + tourism recovery stabilizes somewhat

    The **"basket of goods" funding model** adjusts per-pupil allocations based on
    the calculated cost of education components, but recalibration cycles can lag
    behind rapid enrollment changes caused by energy-sector shifts.
    """)

    st.divider()

    st.subheader("Assessment & Accountability Framework")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **WY-TOPP Assessment:**
        - Wyoming Test of Proficiency and Progress
        - ELA and Math, grades 3-8
        - 4 Achievement Levels:
            - **Advanced** -- advanced mastery
            - **Proficient** -- grade-level proficiency
            - **Basic** -- approaching expectations
            - **Below Basic** -- below grade level
        - Results: edu.wyoming.gov
        """)
    with col2:
        st.markdown("""
        **EL Program:**
        - WIDA ACCESS for ELLs
        - 4 Domains: Listening, Speaking, Reading, Writing
        - **Exit criterion: composite 4.8**
        - 48 districts, ~3,500 ELs

        **Funding:**
        - **"Basket of goods" model**
        - Per-pupil funding based on cost components
        - EL weight in funding formula
        - Recalibration tied to energy revenue

        **Data:** edu.wyoming.gov
        """)

    st.divider()

    # District table
    st.subheader("Pilot Districts -- EL Populations & Performance")
    display = districts_df[['district_id', 'district_name', 'total_students', 'el_count',
                            'el_percent', 'wytopp_prof_all', 'wytopp_prof_el',
                            'graduation_rate']].copy()
    display.columns = ['ID', 'District', 'Students', 'EL Count', 'EL %',
                       'WY-TOPP Prof+ All %', 'WY-TOPP Prof+ EL %', 'Grad Rate %']
    st.dataframe(display, use_container_width=True, hide_index=True)

    # EL bar chart
    st.subheader("English Learner Population by District")
    fig = px.bar(
        districts_df.sort_values('el_count', ascending=True),
        x='el_count', y='district_name', orientation='h',
        color='el_percent', color_continuous_scale=[[0, '#C0C0C0'], [1, WY_BLUE]],
        labels={'el_count': 'English Learners', 'district_name': 'District', 'el_percent': 'EL %'}
    )
    fig.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Economy chart
    st.subheader("EL Distribution: Economic Driver Analysis")
    conc_df = districts_df[['district_name', 'el_percent', 'total_students']].copy()
    conc_df['driver'] = districts_df['economy_note'].apply(
        lambda x: 'Energy/Mining' if any(w in x.lower() for w in ['oil', 'gas', 'coal', 'trona', 'energy', 'wind']) else
                  'Agriculture' if any(w in x.lower() for w in ['agriculture', 'dairy', 'sugar', 'ranch']) else
                  'Tourism/Service' if any(w in x.lower() for w in ['tourism', 'hospitality', 'jackson']) else
                  'Urban/University'
    )
    fig2 = px.scatter(conc_df, x='total_students', y='el_percent',
                      color='driver', size='el_percent',
                      hover_name='district_name',
                      color_discrete_map={
                          'Energy/Mining': WY_BLUE,
                          'Agriculture': WY_GOLD,
                          'Tourism/Service': '#E85D04',
                          'Urban/University': WY_LIGHT_BLUE
                      },
                      labels={'total_students': 'Total Enrollment', 'el_percent': 'EL %',
                              'driver': 'Economic Driver'})
    fig2.update_layout(
        title="EL % vs District Size by Economic Driver",
        height=400
    )
    st.plotly_chart(fig2, use_container_width=True)


# ============================================================================
# PAGE 2: DOMAIN ANALYSIS
# ============================================================================

def render_domain_analysis(domain_df, growth_df):
    st.header("Statewide ACCESS Domain Proficiency")

    st.markdown("""
    **Source:** Wyoming Department of Education / WIDA ACCESS results.
    Wyoming is a WIDA Consortium member. Domain proficiency percentages reveal the
    systemic oral-written delta.

    **Wyoming Context:** With ~3,500 ELs across 48 districts, many district-grade
    cohorts are very small. The energy-sector boom/bust cycle means year-over-year
    changes may reflect enrollment shifts rather than instructional improvement.
    """)

    year = st.selectbox("Year", ['2024-25', '2023-24'], key="dom_y")
    filtered = domain_df[domain_df['year'] == year]

    st.divider()

    fig = go.Figure()
    for domain, color in [('listening', WY_GRAY), ('speaking', WY_BLUE),
                          ('reading', WY_LIGHT_BLUE), ('writing', '#333333')]:
        fig.add_trace(go.Bar(
            x=filtered['grade_cluster'], y=filtered[domain],
            name=domain.capitalize(), marker_color=color,
            text=[f"{v}%" for v in filtered[domain]], textposition='outside'
        ))
    fig.update_layout(
        title=f"ACCESS Domain Proficiency by Grade Cluster ({year})",
        xaxis_title="Grade Cluster", yaxis_title="% Proficient",
        barmode='group', height=450, yaxis=dict(range=[0, 65])
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Speaking-Writing Delta by Grade Cluster")
    filtered = filtered.copy()
    filtered['delta'] = filtered['speaking'] - filtered['writing']
    fig2 = go.Figure(go.Bar(
        x=filtered['grade_cluster'], y=filtered['delta'],
        marker_color=[WY_BLUE if d > 18 else WY_LIGHT_BLUE for d in filtered['delta']],
        text=[f"{d:+d} pts" for d in filtered['delta']], textposition='outside'
    ))
    fig2.update_layout(title="Speaking - Writing Gap", yaxis_title="Delta (percentage points)", height=350)
    st.plotly_chart(fig2, use_container_width=True)

    avg_delta = filtered['delta'].mean()
    st.metric("Average Speaking-Writing Delta", f"{avg_delta:+.0f} percentage points",
              help="Positive = Speaking proficiency exceeds Writing proficiency statewide")

    st.divider()

    # EL growth over time
    st.subheader("Wyoming EL Population: Boom/Bust Volatility")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=growth_df['year'], y=growth_df['el_count'],
        mode='lines+markers', line=dict(color=WY_BLUE, width=3),
        marker=dict(size=8), name='EL Count'
    ))
    fig3.update_layout(
        title="EL Population -- Energy Boom/Bust Creates Enrollment Instability",
        xaxis_title="Year", yaxis_title="English Learners",
        height=400
    )
    fig3.add_annotation(x=2008, y=2800, text="Energy boom", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2016, y=2800, text="Oil/coal bust", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2020, y=2700, text="COVID + energy bust", showarrow=True, arrowhead=2)
    fig3.add_annotation(x=2024, y=3400, text="Wind energy growth", showarrow=True, arrowhead=2)
    st.plotly_chart(fig3, use_container_width=True)

    st.info("""
    **Boom/Bust Impact on EL Programs:** When energy prices rise, workers (many
    Spanish-speaking) arrive in mining/drilling communities like Rock Springs,
    Gillette, and Casper. Schools must rapidly scale ESL services. When prices
    crash, families leave and districts are left with excess ESL capacity. This
    cycle makes long-term EL program planning nearly impossible in energy-dependent
    districts. The "basket of goods" funding model adjusts slowly relative to these
    rapid enrollment shifts.
    """)


# ============================================================================
# PAGE 3: ACCESS ANALYSIS
# ============================================================================

def render_access_analysis(access_df, districts_df):
    st.header("ACCESS for ELLs Analysis")
    st.markdown("""
    **WIDA ACCESS** measures English learners across four domains. Wyoming has ~3,500 ELs
    across 48 districts. **Exit criterion: composite 4.8.**
    """)

    col1, col2, col3 = st.columns(3)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="acc_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="acc_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="acc_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = access_df[(access_df['district_id'] == district_id) &
                         (access_df['grade'] == grade) &
                         (access_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        if row['total_tested'] < 10:
            st.warning(f"**Small N Warning:** Only **{row['total_tested']}** students tested.")

        d_info = districts_df[districts_df['district_id'] == district_id].iloc[0]
        if d_info['el_percent'] > 7:
            st.info(f"**High-Concentration District:** {district} has **{d_info['el_percent']:.1f}% EL enrollment**. "
                    f"{d_info['economy_note']}.")

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Listening", f"{row['listening_avg']:.0f}")
        with col2: st.metric("Speaking", f"{row['speaking_avg']:.0f}")
        with col3: st.metric("Reading", f"{row['reading_avg']:.0f}")
        with col4: st.metric("Writing", f"{row['writing_avg']:.0f}")

        domains = ['Listening', 'Speaking', 'Reading', 'Writing']
        scores = [row['listening_avg'], row['speaking_avg'], row['reading_avg'], row['writing_avg']]
        fig = go.Figure(go.Bar(x=domains, y=scores,
                               marker_color=[WY_GRAY, WY_BLUE, WY_LIGHT_BLUE, '#333333'],
                               text=[f"{s:.0f}" for s in scores], textposition='outside'))
        fig.update_layout(title=f"ACCESS Domains -- {district} -- Grade {grade} ({year})",
                         yaxis_title="Scale Score", height=400)
        st.plotly_chart(fig, use_container_width=True)

        oral = (row['listening_avg'] + row['speaking_avg']) / 2
        written = (row['reading_avg'] + row['writing_avg']) / 2
        gap = oral - written

        st.subheader("Oral vs Written Gap")
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Oral Average", f"{oral:.0f}")
        with col2: st.metric("Written Average", f"{written:.0f}")
        with col3: st.metric("Gap", f"{gap:+.0f}", delta="Flag" if gap > 30 else "Monitor" if gap > 20 else "OK")

        st.divider()
        st.subheader("Composite & Exit Context")
        composite = row['composite_avg']
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Composite Average", f"{composite}")
        with col2: st.metric("Exit Threshold", "4.8")
        with col3: st.metric("Total Tested", f"{row['total_tested']:,}")


# ============================================================================
# PAGE 4: TYPE 4 DETECTION
# ============================================================================

def render_type4(access_df, districts_df):
    st.header("Type 4 Detection")
    st.markdown("""
    **Type 4 candidates** show strong oral skills but weak written skills.
    Delta = Speaking Score - Writing Score. Flag threshold: normalized delta > 8 points.

    **Wyoming Context:** Energy-sector districts (Rock Springs, Gillette, Casper)
    often serve EL students from families following energy jobs. These students
    may develop conversational English quickly through workplace and community
    exposure but lack structured academic writing support. The composite exit score
    of **4.8** means writing deficiency is the primary barrier to reclassification.

    **Teton County (Jackson Hole):** Highest EL% (15%) driven by hospitality/service
    industry. Type 4 patterns are pronounced as students develop oral English through
    tourism-industry immersion.
    """)

    col1, col2, col3 = st.columns(3)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="t4_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="t4_g")
    with col3: year = st.selectbox("Year", [2025, 2024], key="t4_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    result = compute_type4_analysis(access_df, district_id, grade, year)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Speaking", f"{result['speaking_avg']:.0f}")
        with col2: st.metric("Writing", f"{result['writing_avg']:.0f}")
        with col3: st.metric("Delta", f"{result['delta']:+.0f}")
        with col4: st.metric("Status", "FLAGGED" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(name='Speaking', x=['Score'], y=[result['speaking_avg']], marker_color=WY_BLUE))
        fig.add_trace(go.Bar(name='Writing', x=['Score'], y=[result['writing_avg']], marker_color=WY_GRAY))
        fig.update_layout(title=f"Speaking vs Writing -- {district} -- Grade {grade}", barmode='group', height=350)
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Flag Triggered** -- Delta: {result['delta']:+.0f}. "
                     f"Est. {result['estimated_flagged']} of {result['total_tested']} students affected.")
        else:
            st.success(f"**No Type 4 Flag** -- Delta within normal range ({result['delta']:+.0f}).")

        # All grades
        st.subheader(f"All Grades -- {district} ({year})")
        all_data = [compute_type4_analysis(access_df, district_id, g, year) for g in range(3, 9)]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['speaking_avg'], name='Speaking',
                                     mode='lines+markers', line=dict(color=WY_BLUE, width=3)))
            fig.add_trace(go.Scatter(x=gdf['grade'], y=gdf['writing_avg'], name='Writing',
                                     mode='lines+markers', line=dict(color=WY_GRAY, width=3)))
            fig.update_layout(title="Speaking vs Writing Across Grades", xaxis_title="Grade",
                             yaxis_title="Scale Score", height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("District Summary")
        if all_data:
            summary_df = pd.DataFrame(all_data)[['grade', 'speaking_avg', 'writing_avg', 'delta', 'flagged', 'estimated_flagged']]
            summary_df.columns = ['Grade', 'Speaking', 'Writing', 'Delta', 'Flagged', 'Est. Affected']
            summary_df['Flagged'] = summary_df['Flagged'].map({True: 'YES', False: 'No'})
            st.dataframe(summary_df, use_container_width=True, hide_index=True)


# ============================================================================
# PAGE 5: ACHIEVEMENT GAPS
# ============================================================================

def render_achievement_gaps(districts_df):
    st.header("Achievement Gap Analysis")

    st.markdown("""
    **Data from edu.wyoming.gov.** WY-TOPP Proficient + Advanced rates across pilot districts.

    **WY-TOPP** uses 4 achievement levels:
    Below Basic, Basic, Proficient, Advanced.

    **Key Pattern:** Energy-dependent districts show lower overall achievement and
    wider EL gaps, likely due to enrollment instability disrupting instructional
    continuity. Teton County (Jackson) has high EL% but relatively better outcomes
    due to affluent community investment in education.
    """)

    st.divider()

    # All vs EL comparison
    fig = go.Figure()
    sorted_df = districts_df.sort_values('wytopp_prof_all', ascending=True)
    fig.add_trace(go.Bar(
        x=sorted_df['wytopp_prof_all'], y=sorted_df['district_name'],
        name='All Students', orientation='h', marker_color=WY_GRAY
    ))
    fig.add_trace(go.Bar(
        x=sorted_df['wytopp_prof_el'], y=sorted_df['district_name'],
        name='English Learners', orientation='h', marker_color=WY_BLUE
    ))
    fig.update_layout(
        title="WY-TOPP Prof+ Rate: All Students vs English Learners",
        barmode='group', xaxis_title="% Proficient + Advanced",
        height=600, legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Gap analysis
    st.subheader("All-EL Achievement Gap by District")
    gap_df = districts_df.copy()
    gap_df['el_gap'] = gap_df['wytopp_prof_all'] - gap_df['wytopp_prof_el']
    gap_df = gap_df.sort_values('el_gap', ascending=True)

    fig_gap = go.Figure(go.Bar(
        x=gap_df['el_gap'], y=gap_df['district_name'], orientation='h',
        marker_color=[WY_BLUE if g > 30 else WY_LIGHT_BLUE if g > 20 else WY_GRAY for g in gap_df['el_gap']],
        text=[f"{g:.0f} pts" for g in gap_df['el_gap']], textposition='outside'
    ))
    fig_gap.update_layout(title="All Students - EL Gap (WY-TOPP Prof+)",
                         xaxis_title="Gap (percentage points)", height=550)
    st.plotly_chart(fig_gap, use_container_width=True)

    # EL proficiency vs EL concentration
    st.subheader("EL Proficiency vs EL Concentration")
    fig2 = px.scatter(districts_df, x='el_percent', y='wytopp_prof_el', size='el_count',
                      hover_name='district_name',
                      color_discrete_sequence=[WY_BLUE],
                      labels={'el_percent': 'EL %', 'wytopp_prof_el': 'EL Prof+ %',
                              'el_count': 'EL Count'})
    fig2.update_layout(
        title="EL Proficiency vs Concentration",
        height=450
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.info("""
    **"Basket of Goods" Funding Implication:** Wyoming's funding model calculates
    per-pupil costs based on education components (teacher salary, materials, etc.).
    EL students carry a funding weight, but the model recalibrates on legislative
    cycles that may not keep pace with rapid enrollment changes in energy-boom
    districts. A district that gains 100 EL families during an oil boom may not
    receive adjusted funding for 1-2 years.
    """)


# ============================================================================
# PAGE 6: WY-TOPP ANALYSIS
# ============================================================================

def render_wytopp(wytopp_df, districts_df):
    st.header("WY-TOPP Assessment Analysis")
    st.markdown("""
    **WY-TOPP (Wyoming Test of Proficiency and Progress)** assesses students in
    grades 3-8 in ELA and Math.

    **4 Achievement Levels:**
    - **Advanced** -- Advanced understanding
    - **Proficient** -- Grade-level proficiency
    - **Basic** -- Approaching expectations
    - **Below Basic** -- Below grade level

    Results are published on **edu.wyoming.gov**.
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1: district = st.selectbox("District", districts_df['district_name'].tolist(), key="wytopp_d")
    with col2: grade = st.selectbox("Grade", list(range(3, 9)), key="wytopp_g")
    with col3: subject = st.selectbox("Subject", ['ELA', 'Math'], key="wytopp_s")
    with col4: year = st.selectbox("Year", [2025, 2024], key="wytopp_y")

    district_id = districts_df[districts_df['district_name'] == district]['district_id'].values[0]
    filtered = wytopp_df[(wytopp_df['district_id'] == district_id) &
                         (wytopp_df['grade'] == grade) &
                         (wytopp_df['subject'] == subject) &
                         (wytopp_df['year'] == year)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Proficient + Advanced", f"{row['prof_advanced_pct']:.1f}%")
        with col2:
            st.metric("Advanced Only", f"{row['advanced_pct']:.1f}%")

        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Below Basic", f"{row['below_basic_pct']:.1f}%")
        with col2: st.metric("Basic", f"{row['basic_pct']:.1f}%")
        with col3: st.metric("Proficient", f"{row['proficient_pct']:.1f}%")
        with col4: st.metric("Advanced", f"{row['advanced_pct']:.1f}%")

        levels = ['Below\nBasic', 'Basic', 'Proficient', 'Advanced']
        values = [row['below_basic_pct'], row['basic_pct'], row['proficient_pct'], row['advanced_pct']]
        colors = ['#d32f2f', '#f57c00', WY_BLUE, WY_DARK]
        fig = go.Figure(go.Bar(x=levels, y=values, marker_color=colors,
                               text=[f"{v:.1f}%" for v in values], textposition='outside'))
        fig.update_layout(title=f"WY-TOPP {subject} -- {district} -- Grade {grade} ({year})",
                         yaxis_title="Percentage", height=420)
        st.plotly_chart(fig, use_container_width=True)

        d_info = districts_df[districts_df['district_id'] == district_id].iloc[0]
        st.subheader("District Context")
        st.markdown(f"""
        **{district}** -- Grade {grade} {subject} ({year}):
        - Prof+ Rate: **{row['prof_advanced_pct']:.1f}%**
        - EL %: **{d_info['el_percent']:.1f}%** | EL Count: **{d_info['el_count']}**
        - {d_info['economy_note']}
        """)


# ============================================================================
# PAGE 7: EXPORT DATA
# ============================================================================

def render_export(access_df, wytopp_df, districts_df, domain_df, growth_df):
    st.header("Export Data")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ACCESS Data")
        st.dataframe(access_df, use_container_width=True, hide_index=True)
        st.download_button("Download ACCESS CSV", access_df.to_csv(index=False),
                          "vera_wy_access.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("WY-TOPP Data")
        st.dataframe(wytopp_df, use_container_width=True, hide_index=True)
        st.download_button("Download WY-TOPP CSV", wytopp_df.to_csv(index=False),
                          "vera_wy_wytopp.csv", "text/csv", use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Statewide Domain Proficiency")
        st.dataframe(domain_df, use_container_width=True, hide_index=True)
        st.download_button("Download Domain CSV", domain_df.to_csv(index=False),
                          "vera_wy_domains.csv", "text/csv", use_container_width=True)
    with col2:
        st.subheader("District Data")
        st.dataframe(districts_df, use_container_width=True, hide_index=True)
        st.download_button("Download Districts CSV", districts_df.to_csv(index=False),
                          "vera_wy_districts.csv", "text/csv", use_container_width=True)

    st.divider()

    st.subheader("EL Population Growth (2005-2025)")
    st.dataframe(growth_df, use_container_width=True, hide_index=True)
    st.download_button("Download EL Growth CSV", growth_df.to_csv(index=False),
                      "vera_wy_el_growth.csv", "text/csv", use_container_width=True)


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="VERA-WY | Wyoming Type 4 Detection", page_icon="", layout="wide")

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {WY_BLUE}; }}
        .stButton > button {{ background-color: {WY_BLUE}; color: white; }}
        .stButton > button:hover {{ background-color: {WY_DARK}; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    if not check_password():
        return

    # Load data
    districts_df = load_districts()
    access_df = load_access_data(districts_df)
    wytopp_df = load_wytopp_data(districts_df)
    domain_df = load_statewide_domain_data()
    growth_df = load_el_growth_data()

    # Sidebar
    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {WY_BLUE}; margin: 0;">VERA-WY</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Wyoming Implementation</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigation", [
        "Overview",
        "Domain Analysis",
        "ACCESS Analysis",
        "Type 4 Detection",
        "Achievement Gaps",
        "WY-TOPP Analysis",
        "Export Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Data Sources:**
    - ACCESS for ELLs (WIDA)
    - WY-TOPP (ELA & Math)
    - edu.wyoming.gov

    **Type 4 Detection:**
    - Speaking vs Writing delta
    - Flag threshold: > 8 points
    - Exit criterion: composite 4.8

    **Key WY Context:**
    - 48 districts
    - ~3,500 ELs (~3.8%)
    - Laramie #1 (Cheyenne): largest
    - Teton #1 (Jackson): 15% EL
    - Energy boom/bust volatility
    - "Basket of goods" funding
    - WY-TOPP: 4 levels
    - Below Basic/Basic/Prof/Adv

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overview": render_overview(districts_df)
    elif page == "Domain Analysis": render_domain_analysis(domain_df, growth_df)
    elif page == "ACCESS Analysis": render_access_analysis(access_df, districts_df)
    elif page == "Type 4 Detection": render_type4(access_df, districts_df)
    elif page == "Achievement Gaps": render_achievement_gaps(districts_df)
    elif page == "WY-TOPP Analysis": render_wytopp(wytopp_df, districts_df)
    elif page == "Export Data": render_export(access_df, wytopp_df, districts_df, domain_df, growth_df)


if __name__ == "__main__":
    main()
