

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(layout="wide")
st.title("Tech Mapping Dashboard")


# --- Folder upload for all required CSVs ---
import zipfile
import tempfile

st.sidebar.info(
    """
**Welcome to the Tessella demo!**

Explore interactive scientific keyword mapping, clustering, and visualization.\n\nThe bundled demo data has been automatically extracted from nearly 400k clean fuels publications.\n\nFind different filtering, scaling, and sorting options in the sidebar. Some charts may take a few seconds to load, and some data may not be shown due to the large dataset size.
"""
)

def check_file(file, name):
    if file is None:
        missing_files.append(name)
        return None
    try:
        df = pd.read_csv(file)
        if df.empty:
            empty_files.append(name)
        return df
    except Exception:
        missing_files.append(name)
        return None
def demo_path(filename):
    return os.path.join(DEMO_DATA_DIR, filename)
st.sidebar.markdown("### Upload Data Folder (ZIP)")
def get_csv_from_zip(zip_file, filename):
    if zip_file is None:
        # Fallback to demo data
        try:
            return open(demo_path(filename), "rb")
        except Exception:
            return None
    with zipfile.ZipFile(zip_file) as z:
        if filename in z.namelist():
            return z.open(filename)
        else:
            return None

st.sidebar.markdown("### Upload Data Folder (ZIP)")
# --- Welcome message in sidebar (robust for Streamlit Cloud) ---

uploaded_zip = st.sidebar.file_uploader("Upload a ZIP folder containing all 4 required CSVs", type=["zip"], key="main_zip_uploader")

# --- Demo data fallback logic ---
DEMO_DATA_DIR = os.path.join(os.path.dirname(__file__), "demo_data")
def demo_path(filename):
    return os.path.join(DEMO_DATA_DIR, filename)

def get_csv_from_zip(zip_file, filename):
    if zip_file is None:
        # Fallback to demo data
        try:
            return open(demo_path(filename), "rb")
        except Exception:
            return None
    with zipfile.ZipFile(zip_file) as z:
        if filename in z.namelist():
            return z.open(filename)
        else:
            return None

# --- Robust error/warning messages for missing or empty files ---
missing_files = []
empty_files = []
def check_file(file, name):
    if file is None:
        missing_files.append(name)
        return None
    try:
        df = pd.read_csv(file)
        if df.empty:
            empty_files.append(name)
        return df
    except Exception:
        missing_files.append(name)
        return None


# --- Move get_csv_from_zip definition above all uses ---
def get_csv_from_zip(zip_file, filename):
    if zip_file is None:
        # Fallback to demo data
        try:
            return open(demo_path(filename), "rb")
        except Exception:
            return None
    with zipfile.ZipFile(zip_file) as z:
        if filename in z.namelist():
            return z.open(filename)
        else:
            return None

occ = check_file(get_csv_from_zip(uploaded_zip, "lookup_occurrence.csv"), "lookup_occurrence.csv")
coocc = check_file(get_csv_from_zip(uploaded_zip, "lookup_cooccurrence.csv"), "lookup_cooccurrence.csv")
country = check_file(get_csv_from_zip(uploaded_zip, "lookup_country_occurrence.csv"), "lookup_country_occurrence.csv")
fact_alias_cluster = check_file(get_csv_from_zip(uploaded_zip, "fact_alias_cluster.csv"), "fact_alias_cluster.csv")

if uploaded_zip is not None:
    if missing_files:
        st.sidebar.error(f"Missing or unreadable file(s) in ZIP: {', '.join(missing_files)}. Please check the file names and format.")
    if empty_files:
        st.sidebar.warning(f"Empty file(s) in ZIP: {', '.join(empty_files)}. Charts may not display.")



# --- Main Dashboard Tabs (Sidebar tab selector for context-dependent controls) ---
tab_names = ["Occurrence", "CoOccurrence", "Geo Map", "Sankey"]
selected_tab = st.sidebar.radio("Select Chart", tab_names, key="main_tab_selector")

# --- Load Data ---

# Remove legacy load_csv and old variable assignments

def show_global_sidebar(tab_key=None):
    # --- Global Date Range Slider (works for all tabs) ---
    min_dates = []
    max_dates = []
    if occ is not None:
        occ['month'] = pd.to_datetime(occ['month'], errors='coerce')
        min_dates.append(occ['month'].min())
        max_dates.append(occ['month'].max())
    if coocc is not None and 'month' in coocc.columns:
        coocc['month'] = pd.to_datetime(coocc['month'], errors='coerce')
        min_dates.append(coocc['month'].min())
        max_dates.append(coocc['month'].max())
    if country is not None and 'month' in country.columns:
        country['month'] = pd.to_datetime(country['month'], errors='coerce')
        min_dates.append(country['month'].min())
        max_dates.append(country['month'].max())

    if min_dates and max_dates:
        global_min_date = min([d for d in min_dates if pd.notnull(d)]).date()
        global_max_date = max([d for d in max_dates if pd.notnull(d)]).date()
        # Allow passing a unique key for each tab
        slider_key = f"date_range_slider_{tab_key}" if tab_key else "global_date_range_slider"
        date_range = st.sidebar.slider(
            "Date Range",
            min_value=global_min_date,
            max_value=global_max_date,
            value=(global_min_date, global_max_date),
            format="YYYY-MM",
            key=slider_key
        )
    else:
        date_range = (None, None)
    return date_range
min_dates = []
max_dates = []
if occ is not None:
    occ['month'] = pd.to_datetime(occ['month'], errors='coerce')
    min_dates.append(occ['month'].min())
    max_dates.append(occ['month'].max())
if coocc is not None and 'month' in coocc.columns:
    coocc['month'] = pd.to_datetime(coocc['month'], errors='coerce')
    min_dates.append(coocc['month'].min())
    max_dates.append(coocc['month'].max())
if country is not None and 'month' in country.columns:
    country['month'] = pd.to_datetime(country['month'], errors='coerce')
    min_dates.append(country['month'].min())
    max_dates.append(country['month'].max())


# Remove duplicate global date range slider logic (already handled in show_global_sidebar)



## --- Main Dashboard ---

# --- Main Dashboard Content: Only show controls/content for the selected tab ---
if selected_tab == "Occurrence":
    date_range = show_global_sidebar(tab_key="occ")
    st.sidebar.header("Customization")
    color_scale = st.sidebar.selectbox("Color Scale", ["Viridis", "Inferno", "YlGnBu", "Cividis"], key="occ_color_scale")
    axis_scale = st.sidebar.radio("Axis Scale", ["Linear", "Log"], key="occ_axis_scale")
    if occ is not None:
        # --- Occurrence-specific filters ---
        aliases = sorted(occ['alias'].unique())
        occ_alias_filter = st.sidebar.multiselect("Filter by Alias", aliases, default=aliases, key="occ_alias_filter")
        cluster_names = []
        occ_cluster_filter = []
        if fact_alias_cluster is not None:
            cluster_names = sorted(fact_alias_cluster['cluster_name'].unique())
            occ_cluster_filter = st.sidebar.multiselect("Filter by Cluster", cluster_names, default=cluster_names, key="occ_cluster_filter")
        # --- Filter occurrence data using the selected filters ---
        occ_filtered = occ.copy()
        if occ_alias_filter:
            occ_filtered = occ_filtered[occ_filtered['alias'].isin(occ_alias_filter)]
        if fact_alias_cluster is not None and occ_cluster_filter:
            alias_to_cluster = fact_alias_cluster.set_index('alias')['cluster_name'].to_dict()
            occ_filtered['cluster_name'] = occ_filtered['alias'].map(alias_to_cluster)
            occ_filtered = occ_filtered[occ_filtered['cluster_name'].isin(occ_cluster_filter)]
        # --- Date range filter for occurrence plot ---
        if 'month' in occ_filtered.columns and date_range[0] is not None and date_range[1] is not None:
            occ_filtered = occ_filtered[(occ_filtered['month'] >= pd.to_datetime(date_range[0])) & (occ_filtered['month'] <= pd.to_datetime(date_range[1]))]
        # --- Only plot if data is available ---
        if not occ_filtered.empty:
            occ_filtered['year'] = occ_filtered['month'].dt.year
            grouped = occ_filtered.groupby(['alias', 'year'], as_index=False)['occurrence'].sum()
            sort_option = st.sidebar.selectbox("Sort Aliases By", ["Total Occurrence (Descending)", "Alias (A-Z)"], key="occ_sort_option")
            alias_totals = grouped.groupby('alias', as_index=False)['occurrence'].sum()
            if sort_option == "Total Occurrence (Descending)":
                sorted_aliases = alias_totals.sort_values('occurrence', ascending=False)['alias'].tolist()[::-1]
            else:
                sorted_aliases = sorted(alias_totals['alias'].tolist())[::-1]
            def truncate_label(label, width=40):
                return label if len(label) <= width else label[:width] + '...'
            alias_label_map = {alias: truncate_label(alias) for alias in sorted_aliases}
            grouped_visible = grouped[grouped['alias'].isin(sorted_aliases)].copy()
            grouped_visible['alias'] = pd.Categorical(grouped_visible['alias'], categories=sorted_aliases, ordered=True)
            if not grouped['occurrence'].empty:
                min_occ = int(grouped['occurrence'].min())
                max_occ = int(grouped['occurrence'].max())
            else:
                min_occ = 0
                max_occ = 1
            bar_stacks = grouped_visible.groupby('alias')['occurrence'].sum()
            if not bar_stacks.empty:
                min_stack = int(bar_stacks.min())
                max_stack = int(bar_stacks.max())
            else:
                min_stack = 0
                max_stack = 1
            col1, col2 = st.sidebar.columns(2)
            occ_color_min = col1.number_input("Occurrence Color Min", min_value=0, max_value=max_occ, value=min_occ, key="occ_color_min")
            occ_color_max = col2.number_input("Occurrence Color Max", min_value=0, max_value=max_occ, value=max_occ, key="occ_color_max")
            occ_xaxis_min = 0
            occ_xaxis_max = st.sidebar.number_input(
                "Occurrence X-Axis Max", min_value=1, max_value=int(max_stack*1.1), value=int(max_stack*1.05), key="occ_xaxis_max"
            )
            # Always set xaxis_min to 0, only xaxis_max is user-editable
            xaxis_min, xaxis_max = occ_xaxis_min, occ_xaxis_max
            color_seq = getattr(px.colors.sequential, color_scale) if hasattr(px.colors.sequential, color_scale) else px.colors.sequential.Viridis
            import plotly.graph_objects as go
            years = sorted(grouped_visible['year'].unique())
            fig = go.Figure()
            for year in years:
                year_data = grouped_visible[grouped_visible['year'] == year]
                norm_occ = (year_data['occurrence'] - occ_color_min) / max(1, (occ_color_max - occ_color_min))
                norm_occ = norm_occ.clip(0, 1)
                colors = [px.colors.sample_colorscale(color_seq, [v])[0] for v in norm_occ]
                y_labels = [alias_label_map.get(a, a) for a in year_data['alias']]
                hover_labels = year_data['alias']
                fig.add_trace(go.Bar(
                    x=year_data['occurrence'],
                    y=y_labels,
                    orientation='h',
                    name=str(year),
                    marker=dict(color=colors, showscale=False),
                    showlegend=False,
                    hovertemplate='Alias: %{customdata}<br>Year: '+str(year)+'<br>Occurrence: %{x}<extra></extra>',
                    customdata=hover_labels
                ))
            import numpy as np
            colorbar_vals = np.linspace(occ_color_min, occ_color_max, num=100)
            fig.add_trace(go.Scatter(
                x=[None]*len(colorbar_vals),
                y=[None]*len(colorbar_vals),
                mode='markers',
                marker=dict(
                    colorscale=color_seq,
                    cmin=occ_color_min,
                    cmax=occ_color_max,
                    color=colorbar_vals,
                    colorbar=dict(
                        title="Occurrence",
                        tickvals=[occ_color_min, occ_color_max],
                        ticktext=[str(occ_color_min), str(occ_color_max)],
                        lenmode='pixels',
                        len=200
                    ),
                    showscale=True,
                    size=0.1
                ),
                hoverinfo='none',
                showlegend=False
            ))
            # Remove redefinition of bar_stacks, min_stack, max_stack, and xaxis_min/xaxis_max here
            fig.update_layout(
                barmode='stack',
                title="Alias Occurrence Over Time (Color by Occurrence)",
                xaxis_title="Occurrence",
                yaxis_title=None,
                legend=dict(title="", itemsizing='constant', traceorder='normal', tracegroupgap=0, borderwidth=0, bgcolor='rgba(0,0,0,0)'),
                height=max(400, len(sorted_aliases) * 30 + 200),
                width=3600,
                margin=dict(l=40, r=40, t=100, b=40)
            )
            fig.update_xaxes(range=[xaxis_min, xaxis_max])
            fig.update_yaxes(categoryorder='array', categoryarray=[alias_label_map[a] for a in sorted_aliases])
            if axis_scale == "Log":
                fig.update_xaxes(type="log")
            st.plotly_chart(fig, use_container_width=True, key="occurrence_plot")
        else:
            st.warning("No occurrence data available for the selected date range or filters. Try adjusting the date range, alias, or cluster filters, or check your input file.")

elif selected_tab == "CoOccurrence":
    date_range = show_global_sidebar(tab_key="coocc")
    st.sidebar.header("Customization")
    color_scale = st.sidebar.selectbox("Color Scale", ["Viridis", "Inferno", "YlGnBu", "Cividis"], key="coocc_color_scale")
    axis_scale = st.sidebar.radio("Axis Scale", ["Linear", "Log"], key="coocc_axis_scale")
    if coocc is not None:
        # --- Cooccurrence-specific filters in sidebar (separate for alias 1 and alias 2) ---
        coocc_aliases_1 = sorted(coocc['alias_row'].unique())
        coocc_aliases_2 = sorted(coocc['alias_col'].unique())
        coocc_alias1_filter = st.sidebar.multiselect("Cooccurrence: Filter by Alias 1 (alias_row)", coocc_aliases_1, default=coocc_aliases_1, key="coocc_alias1_filter")
        coocc_alias2_filter = st.sidebar.multiselect("Cooccurrence: Filter by Alias 2 (alias_col)", coocc_aliases_2, default=coocc_aliases_2, key="coocc_alias2_filter")
        coocc_cluster_names_1 = []
        coocc_cluster_names_2 = []
        coocc_cluster1_filter = []
        coocc_cluster2_filter = []
        if fact_alias_cluster is not None:
            coocc_cluster_names_1 = sorted(fact_alias_cluster.set_index('alias').loc[coocc_aliases_1]['cluster_name'].unique())
            coocc_cluster_names_2 = sorted(fact_alias_cluster.set_index('alias').loc[coocc_aliases_2]['cluster_name'].unique())
            coocc_cluster1_filter = st.sidebar.multiselect("Cooccurrence: Filter by Cluster 1 (alias_row)", coocc_cluster_names_1, default=coocc_cluster_names_1, key="coocc_cluster1_filter")
            coocc_cluster2_filter = st.sidebar.multiselect("Cooccurrence: Filter by Cluster 2 (alias_col)", coocc_cluster_names_2, default=coocc_cluster_names_2, key="coocc_cluster2_filter")
        # --- Filtering for cooccurrence: by date, alias, and cluster (for both aliases separately) ---
        df = coocc[
            (coocc['month'] >= pd.to_datetime(date_range[0])) &
            (coocc['month'] <= pd.to_datetime(date_range[1]))
        ].copy()
        # Filter for alias_row and alias_col separately
        if coocc_alias1_filter:
            df = df[df['alias_row'].isin(coocc_alias1_filter)]
        if coocc_alias2_filter:
            df = df[df['alias_col'].isin(coocc_alias2_filter)]
        # Filter for clusters separately
        if fact_alias_cluster is not None and (coocc_cluster1_filter or coocc_cluster2_filter):
            alias_to_cluster = fact_alias_cluster.set_index('alias')['cluster_name'].to_dict()
            df['cluster_row'] = df['alias_row'].map(alias_to_cluster)
            df['cluster_col'] = df['alias_col'].map(alias_to_cluster)
            if coocc_cluster1_filter:
                df = df[df['cluster_row'].isin(coocc_cluster1_filter)]
            if coocc_cluster2_filter:
                df = df[df['cluster_col'].isin(coocc_cluster2_filter)]
        # --- Date range filter for cooccurrence plot ---
        if 'month' in df.columns and date_range[0] is not None and date_range[1] is not None:
            df = df[(df['month'] >= pd.to_datetime(date_range[0])) & (df['month'] <= pd.to_datetime(date_range[1]))]
        # --- Only plot if data is available ---
        if not df.empty:
            df['combo'] = df['alias_row'] + " & " + df['alias_col']
            df['year'] = df['month'].dt.year
            grouped = df.groupby(['combo', 'year'], as_index=False)['cooccurrence'].sum()
            sort_option = st.sidebar.selectbox(
                "Sort Combos By",
                ["Total Cooccurrence (Descending)", "Combo (A-Z)"],
                key="coocc_sort_option"
            )
            combo_totals = grouped.groupby('combo', as_index=False)['cooccurrence'].sum()
            if sort_option == "Total Cooccurrence (Descending)":
                sorted_combos = combo_totals.sort_values('cooccurrence', ascending=False)['combo'].tolist()[::-1]
            else:
                sorted_combos = sorted(combo_totals['combo'].tolist())[::-1]
            def truncate_combo(label, width=40):
                return label if len(label) <= width else label[:width] + '...'
            combo_label_map = {combo: truncate_combo(combo) for combo in sorted_combos}
            grouped_visible = grouped[grouped['combo'].isin(sorted_combos)].copy()
            grouped_visible['combo'] = pd.Categorical(grouped_visible['combo'], categories=sorted_combos, ordered=True)
            if not grouped['cooccurrence'].empty:
                min_coocc = int(grouped['cooccurrence'].min())
                max_coocc = int(grouped['cooccurrence'].max())
            else:
                min_coocc = 0
                max_coocc = 1
            bar_stacks = grouped_visible.groupby('combo')['cooccurrence'].sum()
            if not bar_stacks.empty:
                min_stack = int(bar_stacks.min())
                max_stack = int(bar_stacks.max())
            else:
                min_stack = 0
                max_stack = 1
            col1, col2 = st.sidebar.columns(2)
            coocc_color_min = col1.number_input("Cooccurrence Color Min", min_value=0, max_value=max_coocc, value=min_coocc, key="coocc_color_min")
            coocc_color_max = col2.number_input("Cooccurrence Color Max", min_value=0, max_value=max_coocc, value=max_coocc, key="coocc_color_max")
            coocc_xaxis_min = 0
            coocc_xaxis_max = st.sidebar.number_input(
                "Cooccurrence X-Axis Max", min_value=1, max_value=int(max_stack*1.1), value=int(max_stack*1.05), key="coocc_xaxis_max"
            )
            xaxis_min, xaxis_max = coocc_xaxis_min, coocc_xaxis_max
            color_seq = getattr(px.colors.sequential, color_scale) if hasattr(px.colors.sequential, color_scale) else px.colors.sequential.Viridis
            import plotly.graph_objects as go
            years = sorted(grouped_visible['year'].unique())
            fig = go.Figure()
            for year in years:
                year_data = grouped_visible[grouped_visible['year'] == year]
                norm_coocc = (year_data['cooccurrence'] - coocc_color_min) / max(1, (coocc_color_max - coocc_color_min))
                norm_coocc = norm_coocc.clip(0, 1)
                colors = [px.colors.sample_colorscale(color_seq, [v])[0] for v in norm_coocc]
                y_labels = [combo_label_map.get(c, c) for c in year_data['combo']]
                hover_labels = year_data['combo']
                fig.add_trace(go.Bar(
                    x=year_data['cooccurrence'],
                    y=y_labels,
                    orientation='h',
                    name=str(year),
                    marker=dict(color=colors, showscale=False),
                    showlegend=False,
                    hovertemplate='Combo: %{customdata}<br>Year: '+str(year)+'<br>Cooccurrence: %{x}<extra></extra>',
                    customdata=hover_labels
                ))
            import numpy as np
            colorbar_vals = np.linspace(coocc_color_min, coocc_color_max, num=100)
            fig.add_trace(go.Scatter(
                x=[None]*len(colorbar_vals),
                y=[None]*len(colorbar_vals),
                mode='markers',
                marker=dict(
                    colorscale=color_seq,
                    cmin=coocc_color_min,
                    cmax=coocc_color_max,
                    color=colorbar_vals,
                    colorbar=dict(
                        title="Cooccurrence",
                        tickvals=[coocc_color_min, coocc_color_max],
                        ticktext=[str(coocc_color_min), str(coocc_color_max)],
                        lenmode='pixels',
                        len=200
                    ),
                    showscale=True,
                    size=0.1
                ),
                hoverinfo='none',
                showlegend=False
            ))
            bar_stacks = grouped_visible.groupby('combo')['cooccurrence'].sum()
            max_stack = bar_stacks.max()
            min_stack = bar_stacks.min()
            xaxis_min, xaxis_max = coocc_xaxis_min, coocc_xaxis_max
            fig.update_layout(
                barmode='stack',
                title="Alias Co-Occurrence Over Time (Color by Cooccurrence)",
                xaxis_title="Cooccurrence",
                yaxis_title=None,
                legend=dict(title="", itemsizing='constant', traceorder='normal', tracegroupgap=0, borderwidth=0, bgcolor='rgba(0,0,0,0)'),
                height=max(400, len(sorted_combos) * 30 + 200),
                width=3600,
                margin=dict(l=40, r=40, t=100, b=40)
            )
            fig.update_xaxes(range=[xaxis_min, xaxis_max])
            fig.update_yaxes(categoryorder='array', categoryarray=[combo_label_map[c] for c in sorted_combos])
            if axis_scale == "Log":
                fig.update_xaxes(type="log")
            st.plotly_chart(fig, use_container_width=True, key="cooccurrence_plot")
        else:
            st.warning("No co-occurrence data available for the selected date range or filters. Try adjusting the date range, alias, or cluster filters, or check your input file.")

elif selected_tab == "Geo Map":
    date_range = show_global_sidebar(tab_key="geo")
    st.sidebar.header("Customization")
    color_scale = st.sidebar.selectbox("Color Scale", ["Viridis", "Inferno", "YlGnBu", "Cividis"], key="geo_color_scale")
    axis_scale = st.sidebar.radio("Axis Scale", ["Linear", "Log"], key="geo_axis_scale")
    if country is not None:
        # Sidebar filter for countries
        all_countries = sorted(country['country'].dropna().unique())
        country_filter = st.sidebar.multiselect("Filter by Country", all_countries, default=all_countries, key="geo_country_filter")
        # Aggregate by country and year for correct coloring
        df = country[
            (country['month'] >= pd.to_datetime(date_range[0])) &
            (country['month'] <= pd.to_datetime(date_range[1]))
        ].copy()
        if country_filter:
            df = df[df['country'].isin(country_filter)]
        if not df.empty:
            df['year'] = df['month'].dt.year
            # Drop NaN years and convert to int
            df = df.dropna(subset=['year'])
            df['year'] = df['year'].astype(int)
            agg = df.groupby(['country', 'year'], as_index=False)['occurrence'].sum()
            # Remove duplicate country/year rows (shouldn't exist, but just in case)
            agg = agg.drop_duplicates(subset=['country', 'year'])
            # Sort by year for clean animation
            agg = agg.sort_values('year')
            if not agg.empty:
                min_geo = int(agg['occurrence'].min())
                max_geo = int(agg['occurrence'].max())
                col1, col2 = st.sidebar.columns(2)
                geo_color_min = col1.number_input("Geo Color Min", min_value=0, max_value=max_geo, value=min_geo, key="geo_color_min")
                geo_color_max = col2.number_input("Geo Color Max", min_value=0, max_value=max_geo, value=max_geo, key="geo_color_max")
                geo_color_seq = getattr(px.colors.sequential, color_scale) if hasattr(px.colors.sequential, color_scale) else px.colors.sequential.Viridis
                # Use ISO-3 codes for locations to ensure all countries are mapped
                import pycountry
                def get_iso3(country_name):
                    try:
                        return pycountry.countries.lookup(country_name).alpha_3
                    except Exception:
                        return None
                agg['iso_alpha'] = agg['country'].apply(get_iso3)
                agg = agg.dropna(subset=['iso_alpha'])
                fig = px.choropleth(
                    agg,
                    locations="iso_alpha",
                    color="occurrence",
                    hover_name="country",
                    animation_frame="year",
                    color_continuous_scale=geo_color_seq,
                    range_color=(geo_color_min, geo_color_max),
                    title="Geographic Occurrence Heatmap"
                )
                st.plotly_chart(fig, use_container_width=True, key="geo_map_plot")
            else:
                st.warning("No aggregated data available for the selected date range. Try adjusting filters or check your input file.")
        else:
            st.warning("No country data available for the selected date range. Try adjusting filters or check your input file.")

elif selected_tab == "Sankey":
    date_range = show_global_sidebar(tab_key="sankey")
    st.sidebar.header("Customization")
    color_scale = st.sidebar.selectbox("Color Scale", ["Viridis", "Inferno", "YlGnBu", "Cividis"], key="sankey_color_scale")
    axis_scale = st.sidebar.radio("Axis Scale", ["Linear", "Log"], key="sankey_axis_scale")
    if coocc is not None and fact_alias_cluster is not None:
        if country is not None:
            # Sidebar filters for Sankey
            all_countries = sorted(country['country'].dropna().unique())
            # Compute top 5 countries by total occurrence for default
            top5_countries = []
            if not country.empty:
                country_totals = country.groupby('country')['occurrence'].sum().sort_values(ascending=False)
                top5_countries = country_totals.head(5).index.tolist()
            else:
                top5_countries = all_countries[:5]
            country_filter = st.sidebar.multiselect("Sankey: Filter by Country", all_countries, default=top5_countries, key="sankey_country_filter")
            all_clusters = []
            top5_clusters = []
            if fact_alias_cluster is not None:
                all_clusters = sorted(fact_alias_cluster['cluster_name'].dropna().unique())
                # Compute top 5 clusters by total occurrence for default
                if not country.empty:
                    geo_df_tmp = country.merge(fact_alias_cluster[['alias', 'cluster_name']], left_on='alias', right_on='alias', how='left')
                    cluster_totals = geo_df_tmp.groupby('cluster_name')['occurrence'].sum().sort_values(ascending=False)
                    top5_clusters = cluster_totals.head(5).index.tolist()
                else:
                    top5_clusters = all_clusters[:5]
            cluster_filter = st.sidebar.multiselect("Sankey: Filter by Cluster Name", all_clusters, default=top5_clusters, key="sankey_cluster_filter")
            geo_df = country.merge(fact_alias_cluster[['alias', 'cluster_name']], left_on='alias', right_on='alias', how='left')
            geo_df = geo_df[(geo_df['month'] >= pd.to_datetime(date_range[0])) & (geo_df['month'] <= pd.to_datetime(date_range[1]))].copy()
            # Apply country and cluster filters
            if country_filter:
                geo_df = geo_df[geo_df['country'].isin(country_filter)]
            if cluster_filter:
                geo_df = geo_df[geo_df['cluster_name'].isin(cluster_filter)]
            if not geo_df.empty:
                geo_df['year'] = geo_df['month'].dt.year
                sankey_df = geo_df.groupby(['country', 'cluster_name'], as_index=False)['occurrence'].sum()
                sankey_df = sankey_df.dropna(subset=['country', 'cluster_name'])
                if not sankey_df.empty:
                    countries = sankey_df['country'].unique().tolist()
                    clusters_list = sankey_df['cluster_name'].unique().tolist()
                    node_labels = countries + clusters_list
                    node_indices = {label: i for i, label in enumerate(node_labels)}
                    sankey_data = dict(
                        type='sankey',
                        node=dict(label=node_labels),
                        link=dict(
                            source=[node_indices[row['country']] for _, row in sankey_df.iterrows()],
                            target=[node_indices[row['cluster_name']] for _, row in sankey_df.iterrows()],
                            value=sankey_df['occurrence']
                        )
                    )
                    fig = go.Figure(data=[sankey_data])
                    fig.update_layout(title_text="Geo Sankey: Country to Cluster Name", font_size=10)
                    st.plotly_chart(fig, use_container_width=True, key="sankey_plot")
                else:
                    st.warning("No data available for Sankey plot after filtering. Try adjusting filters or check your data.")
            else:
                st.warning("No country data available for Sankey plot after filtering. Try adjusting filters or check your data.")


st.sidebar.markdown("---")
st.sidebar.info("This dashboard is powered by Streamlit and Plotly.")
