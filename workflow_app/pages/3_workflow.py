import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page title and description
st.title("🪐 Jupyter Workflow - Planet Explorer")
st.markdown("""
Welcome to the **Jupyter Workflow** for exploring planetary data! This interactive dashboard 
showcases fascinating features of planets in our solar system with modern data visualization.
""")

# Sidebar for workflow controls
st.sidebar.header("🔧 Jupyter Workflow Controls")
st.sidebar.markdown("Configure your planetary analysis workflow")

# Planet data
planets_data = {
    'Planet': ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'],
    'Distance_from_Sun_AU': [0.39, 0.72, 1.00, 1.52, 5.20, 9.54, 19.19, 30.07],
    'Diameter_km': [4879, 12104, 12756, 6792, 142984, 120536, 51118, 49528],
    'Mass_Earth_units': [0.055, 0.815, 1.000, 0.107, 317.8, 95.2, 14.5, 17.1],
    'Orbital_Period_years': [0.24, 0.62, 1.00, 1.88, 11.86, 29.46, 84.01, 164.8],
    'Temperature_C': [167, 464, 15, -65, -110, -140, -195, -200],
    'Moons': [0, 0, 1, 2, 79, 82, 27, 14],
    'Type': ['Terrestrial', 'Terrestrial', 'Terrestrial', 'Terrestrial', 'Gas Giant', 'Gas Giant', 'Ice Giant', 'Ice Giant'],
    'Notable_Features': [
        'Extreme temperature variations, heavily cratered surface',
        'Hottest planet, thick atmosphere, retrograde rotation',
        'Only known planet with life, liquid water',
        'Red color from iron oxide, polar ice caps',
        'Largest planet, Great Red Spot storm',
        'Prominent ring system, lowest density',
        'Tilted 98°, faint rings, methane atmosphere',
        'Strongest winds, deep blue color from methane'
    ]
}

df_planets = pd.DataFrame(planets_data)

# Workflow Step 1: Data Overview
st.header("📊 Step 1: Planetary Data Overview")
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Planet Comparison Table")
    selected_features = st.multiselect(
        "Select features to display:",
        options=['Distance_from_Sun_AU', 'Diameter_km', 'Mass_Earth_units', 'Orbital_Period_years', 
                'Temperature_C', 'Moons', 'Type'],
        default=['Distance_from_Sun_AU', 'Diameter_km', 'Mass_Earth_units', 'Moons']
    )
    
    if selected_features:
        display_columns = ['Planet'] + selected_features
        st.dataframe(df_planets[display_columns], use_container_width=True)
    else:
        st.warning("Please select at least one feature to display.")

with col2:
    st.subheader("Quick Stats")
    st.metric("Total Planets", len(df_planets))
    st.metric("Terrestrial Planets", len(df_planets[df_planets['Type'] == 'Terrestrial']))
    st.metric("Gas/Ice Giants", len(df_planets[df_planets['Type'].isin(['Gas Giant', 'Ice Giant'])]))
    st.metric("Total Known Moons", df_planets['Moons'].sum())

# Workflow Step 2: Interactive Visualizations
st.header("📈 Step 2: Interactive Planet Analysis")

# Tabs for different visualizations
tab1, tab2, tab3, tab4 = st.tabs(["🌍 Size Comparison", "🚀 Distance & Orbit", "🌡️ Temperature Analysis", "🌙 Moon Count"])

with tab1:
    st.subheader("Planet Size Comparison")
    
    # Create bubble chart for size comparison
    fig_size = px.scatter(df_planets, 
                         x='Distance_from_Sun_AU', 
                         y='Mass_Earth_units',
                         size='Diameter_km',
                         color='Type',
                         hover_name='Planet',
                         hover_data={'Diameter_km': ':,', 'Mass_Earth_units': ':.3f'},
                         title="Planet Size vs Distance from Sun",
                         labels={'Distance_from_Sun_AU': 'Distance from Sun (AU)',
                                'Mass_Earth_units': 'Mass (Earth units)'})
    
    fig_size.update_layout(height=500)
    st.plotly_chart(fig_size, use_container_width=True)
    
    st.info("💡 **Insight**: Bubble size represents planet diameter. Notice how gas giants are much larger but farther from the Sun!")

with tab2:
    st.subheader("Orbital Characteristics")
    
    # Dual axis plot for distance and orbital period
    fig_orbit = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig_orbit.add_trace(
        go.Scatter(x=df_planets['Planet'], 
                  y=df_planets['Distance_from_Sun_AU'],
                  name="Distance from Sun (AU)",
                  line=dict(color="orange", width=3),
                  marker=dict(size=8)),
        secondary_y=False,
    )
    
    fig_orbit.add_trace(
        go.Scatter(x=df_planets['Planet'], 
                  y=df_planets['Orbital_Period_years'],
                  name="Orbital Period (years)",
                  line=dict(color="blue", width=3),
                  marker=dict(size=8)),
        secondary_y=True,
    )
    
    fig_orbit.update_xaxes(title_text="Planets")
    fig_orbit.update_yaxis(title_text="Distance from Sun (AU)", secondary_y=False)
    fig_orbit.update_yaxis(title_text="Orbital Period (years)", secondary_y=True)
    fig_orbit.update_layout(title_text="Distance vs Orbital Period", height=500)
    
    st.plotly_chart(fig_orbit, use_container_width=True)

with tab3:
    st.subheader("Temperature Analysis")
    
    # Temperature bar chart with color coding
    fig_temp = px.bar(df_planets, 
                     x='Planet', 
                     y='Temperature_C',
                     color='Temperature_C',
                     color_continuous_scale='RdYlBu_r',
                     title="Average Surface Temperature by Planet",
                     labels={'Temperature_C': 'Temperature (°C)'})
    
    fig_temp.update_layout(height=500)
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # Temperature insights
    hottest_planet = df_planets.loc[df_planets['Temperature_C'].idxmax(), 'Planet']
    coldest_planet = df_planets.loc[df_planets['Temperature_C'].idxmin(), 'Planet']
    
    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🔥 **Hottest Planet**: {hottest_planet} ({df_planets[df_planets['Planet'] == hottest_planet]['Temperature_C'].values[0]}°C)")
    with col2:
        st.info(f"🧊 **Coldest Planet**: {coldest_planet} ({df_planets[df_planets['Planet'] == coldest_planet]['Temperature_C'].values[0]}°C)")

with tab4:
    st.subheader("Moon Count Analysis")
    
    # Moon count visualization
    fig_moons = px.pie(df_planets, 
                      values='Moons', 
                      names='Planet',
                      title="Distribution of Moons in Solar System",
                      hole=0.4)
    
    fig_moons.update_traces(textposition='inside', textinfo='percent+label')
    fig_moons.update_layout(height=500)
    st.plotly_chart(fig_moons, use_container_width=True)

# Workflow Step 3: Planet Spotlight
st.header("🔍 Step 3: Planet Spotlight")

selected_planet = st.selectbox(
    "Choose a planet to explore in detail:",
    df_planets['Planet'].tolist()
)

if selected_planet:
    planet_info = df_planets[df_planets['Planet'] == selected_planet].iloc[0]
    
    # Create spotlight layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader(f"{selected_planet}")
        st.image(f"https://via.placeholder.com/200x200/4A90E2/FFFFFF?text={selected_planet}", 
                caption=f"{selected_planet}", width=200)
        
        # Key metrics
        st.metric("Distance from Sun", f"{planet_info['Distance_from_Sun_AU']:.2f} AU")
        st.metric("Diameter", f"{planet_info['Diameter_km']:,} km")
        st.metric("Mass", f"{planet_info['Mass_Earth_units']:.3f} Earth units")
        st.metric("Moons", int(planet_info['Moons']))
    
    with col2:
        st.subheader("Detailed Information")
        
        # Planet type badge
        type_color = {"Terrestrial": "🪨", "Gas Giant": "🌪️", "Ice Giant": "🧊"}
        st.markdown(f"**Type**: {type_color.get(planet_info['Type'], '🌍')} {planet_info['Type']}")
        
        # Detailed stats
        stats_data = {
            'Property': ['Orbital Period', 'Average Temperature', 'Distance from Sun', 'Diameter', 'Mass'],
            'Value': [
                f"{planet_info['Orbital_Period_years']:.2f} years",
                f"{planet_info['Temperature_C']}°C",
                f"{planet_info['Distance_from_Sun_AU']:.2f} AU",
                f"{planet_info['Diameter_km']:,} km",
                f"{planet_info['Mass_Earth_units']:.3f} Earth units"
            ]
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.table(stats_df)
        
        # Notable features
        st.subheader("Notable Features")
        st.write(planet_info['Notable_Features'])

# Workflow Step 4: Comparison Tool
st.header("⚖️ Step 4: Planet Comparison Tool")

col1, col2 = st.columns(2)

with col1:
    planet1 = st.selectbox("Select first planet:", df_planets['Planet'].tolist(), key="planet1")

with col2:
    planet2 = st.selectbox("Select second planet:", df_planets['Planet'].tolist(), 
                          index=1 if len(df_planets) > 1 else 0, key="planet2")

if planet1 and planet2 and planet1 != planet2:
    st.subheader(f"Comparing {planet1} vs {planet2}")
    
    p1_data = df_planets[df_planets['Planet'] == planet1].iloc[0]
    p2_data = df_planets[df_planets['Planet'] == planet2].iloc[0]
    
    # Comparison metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Distance from Sun (AU)",
            f"{p1_data['Distance_from_Sun_AU']:.2f}",
            delta=f"{p1_data['Distance_from_Sun_AU'] - p2_data['Distance_from_Sun_AU']:.2f}"
        )
        st.caption(f"{planet2}: {p2_data['Distance_from_Sun_AU']:.2f}")
    
    with col2:
        st.metric(
            "Diameter (km)",
            f"{p1_data['Diameter_km']:,}",
            delta=f"{p1_data['Diameter_km'] - p2_data['Diameter_km']:,}"
        )
        st.caption(f"{planet2}: {p2_data['Diameter_km']:,}")
    
    with col3:
        st.metric(
            "Mass (Earth units)",
            f"{p1_data['Mass_Earth_units']:.3f}",
            delta=f"{p1_data['Mass_Earth_units'] - p2_data['Mass_Earth_units']:.3f}"
        )
        st.caption(f"{planet2}: {p2_data['Mass_Earth_units']:.3f}")
    
    with col4:
        st.metric(
            "Temperature (°C)",
            f"{p1_data['Temperature_C']}",
            delta=f"{p1_data['Temperature_C'] - p2_data['Temperature_C']}"
        )
        st.caption(f"{planet2}: {p2_data['Temperature_C']}")

# Workflow Summary
st.header("📋 Workflow Summary")

with st.expander("View Jupyter Workflow Summary", expanded=False):
    st.markdown("""
    ### Completed Analysis Steps:
    
    1. **Data Overview** ✅
       - Loaded and displayed planetary dataset
       - Provided interactive feature selection
       - Generated quick statistics
    
    2. **Interactive Visualizations** ✅
       - Size comparison bubble chart
       - Orbital characteristics analysis
       - Temperature distribution
       - Moon count analysis
    
    3. **Planet Spotlight** ✅
       - Detailed individual planet exploration
       - Comprehensive planet profiles
       - Notable features highlighting
    
    4. **Comparison Tool** ✅
       - Side-by-side planet comparison
       - Delta calculations for key metrics
       - Interactive planet selection
    
    ### Key Insights Discovered:
    - Venus is the hottest planet despite not being closest to the Sun
    - Jupiter and Saturn have the most moons in our solar system
    - Gas giants are significantly larger but much farther from the Sun
    - Terrestrial planets are smaller, denser, and closer to the Sun
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>🚀 Jupyter Workflow - Planet Explorer | Built with Streamlit & Plotly</p>
    <p>Explore the wonders of our solar system through interactive data analysis!</p>
</div>
""", unsafe_allow_html=True)