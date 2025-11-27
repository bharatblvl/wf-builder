import streamlit as st
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import math

# Page header with modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #4a90e2;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .fact-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .metric-container {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4a90e2;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🌌 The Universe is So Big 🌌</h1>', unsafe_allow_html=True)

# Introduction section
st.markdown("""
Welcome to an exploration of the mind-boggling scale of our universe. From the smallest particles to the largest structures, 
the cosmos spans distances and contains numbers that challenge human comprehension.
""")

# Interactive scale selector
st.markdown('<h2 class="section-header">🔭 Explore Different Scales</h2>', unsafe_allow_html=True)

scale_option = st.selectbox(
    "Choose a scale to explore:",
    ["Solar System", "Milky Way Galaxy", "Observable Universe", "Cosmic Structures"],
    help="Select different scales to understand the vastness of space"
)

# Create columns for better layout
col1, col2 = st.columns([2, 1])

with col1:
    if scale_option == "Solar System":
        st.markdown("### 🪐 Our Solar System")
        
        # Solar system data
        planets_data = {
            'Planet': ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune'],
            'Distance from Sun (AU)': [0.39, 0.72, 1.00, 1.52, 5.20, 9.54, 19.22, 30.06],
            'Diameter (km)': [4879, 12104, 12756, 6792, 142984, 120536, 51118, 49528]
        }
        
        df_planets = pd.DataFrame(planets_data)
        
        # Interactive plot
        fig = px.scatter(df_planets, x='Distance from Sun (AU)', y='Diameter (km)',
                        hover_name='Planet', size='Diameter (km)',
                        title='Planets: Distance vs Size',
                        color='Distance from Sun (AU)',
                        color_continuous_scale='viridis')
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info("💡 **Fun Fact**: If Earth were the size of a marble, the Sun would be about 3 meters away and the size of a large beach ball!")

    elif scale_option == "Milky Way Galaxy":
        st.markdown("### 🌌 The Milky Way Galaxy")
        
        # Galaxy visualization
        theta = np.linspace(0, 4*np.pi, 1000)
        r = np.exp(theta/10) + np.random.normal(0, 0.1, 1000)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=r*np.cos(theta), y=r*np.sin(theta),
                               mode='markers', marker=dict(size=2, color=theta, colorscale='viridis'),
                               name='Stars'))
        
        fig.update_layout(title='Spiral Structure of the Milky Way (Simplified)',
                         xaxis_title='Distance (kpc)', yaxis_title='Distance (kpc)',
                         showlegend=False)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.warning("🌟 **Mind-Blowing**: Our galaxy contains 100-400 billion stars, and it would take 100,000 years to cross it at light speed!")

    elif scale_option == "Observable Universe":
        st.markdown("### 🔮 The Observable Universe")
        
        # Timeline of the universe
        universe_timeline = {
            'Event': ['Big Bang', 'First Stars', 'First Galaxies', 'Solar System Formation', 'Today'],
            'Time (Billion Years Ago)': [13.8, 13.6, 13.2, 4.6, 0],
            'Temperature (K)': [1e32, 1000, 100, 3000, 2.7]
        }
        
        df_timeline = pd.DataFrame(universe_timeline)
        
        fig = px.line(df_timeline, x='Time (Billion Years Ago)', y='Temperature (K)',
                     hover_data=['Event'], title='Universe Timeline & Temperature',
                     log_y=True)
        
        fig.update_traces(mode='markers+lines', marker=dict(size=10))
        
        for i, row in df_timeline.iterrows():
            fig.add_annotation(x=row['Time (Billion Years Ago)'], y=row['Temperature (K)'],
                             text=row['Event'], showarrow=True, arrowhead=2)
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.error("🤯 **Incomprehensible**: The observable universe is 93 billion light-years in diameter and contains at least 2 trillion galaxies!")

    else:  # Cosmic Structures
        st.markdown("### 🕳️ Cosmic Structures")
        
        # Cosmic web simulation
        np.random.seed(42)
        n_points = 500
        x = np.random.normal(0, 1, n_points)
        y = np.random.normal(0, 1, n_points)
        z = np.random.normal(0, 1, n_points)
        
        # Create clusters
        cluster_centers = [(2, 2, 0), (-2, -2, 0), (2, -2, 0), (-2, 2, 0)]
        for center in cluster_centers:
            cluster_x = np.random.normal(center[0], 0.3, 50)
            cluster_y = np.random.normal(center[1], 0.3, 50)
            cluster_z = np.random.normal(center[2], 0.3, 50)
            x = np.concatenate([x, cluster_x])
            y = np.concatenate([y, cluster_y])
            z = np.concatenate([z, cluster_z])
        
        fig = go.Figure(data=go.Scatter3d(x=x, y=y, z=z, mode='markers',
                                        marker=dict(size=3, color=z, colorscale='plasma')))
        
        fig.update_layout(title='Cosmic Web Structure (Simplified 3D View)',
                         scene=dict(xaxis_title='X (Mpc)', yaxis_title='Y (Mpc)', zaxis_title='Z (Mpc)'))
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.success("🕸️ **Cosmic Web**: Matter in the universe forms a web-like structure with vast cosmic voids between galaxy filaments!")

with col2:
    st.markdown("### 📊 Mind-Bending Numbers")
    
    # Metrics with error handling
    try:
        st.metric("Observable Universe Diameter", "93 billion light-years", "🌌")
        st.metric("Estimated Galaxies", "2+ trillion", "🌟")
        st.metric("Stars in Milky Way", "100-400 billion", "⭐")
        st.metric("Age of Universe", "13.8 billion years", "⏰")
    except Exception as e:
        st.error(f"Error displaying metrics: {str(e)}")

    # Interactive calculator
    st.markdown("### 🧮 Scale Calculator")
    
    distance_input = st.number_input("Enter distance in light-years:", 
                                   min_value=0.0, value=1.0, step=0.1)
    
    if distance_input > 0:
        try:
            # Conversions
            km = distance_input * 9.461e12
            au = distance_input * 63241
            earth_diameters = distance_input * 7.42e8
            
            st.write(f"**{distance_input:,.1f} light-years equals:**")
            st.write(f"• {km:.2e} kilometers")
            st.write(f"• {au:.2e} Astronomical Units")
            st.write(f"• {earth_diameters:.2e} Earth diameters")
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")

# Fun facts section
st.markdown('<h2 class="section-header">🎯 Amazing Universe Facts</h2>', unsafe_allow_html=True)

facts = [
    "If you could travel at the speed of light, it would take 4.37 years to reach the nearest star (Proxima Centauri)",
    "There are more stars in the universe than grains of sand on all Earth's beaches",
    "A black hole can have the mass of billions of suns compressed into a point smaller than an atom",
    "The cosmic microwave background radiation we detect today is light from when the universe was only 380,000 years old",
    "Dark matter makes up about 27% of the universe, but we can't see it directly"
]

selected_fact = st.selectbox("Choose a mind-blowing fact:", 
                           [f"Fact {i+1}" for i in range(len(facts))],
                           format_func=lambda x: f"🔍 {x}")

fact_index = int(selected_fact.split()[1]) - 1
st.markdown(f'<div class="fact-card">{facts[fact_index]}</div>', unsafe_allow_html=True)

# Interactive quiz section
st.markdown('<h2 class="section-header">🧠 Test Your Knowledge</h2>', unsafe_allow_html=True)

quiz_question = st.radio(
    "How long would it take light to travel across the Milky Way galaxy?",
    ["1,000 years", "10,000 years", "100,000 years", "1 million years"],
    help="Think about the size of our galaxy!"
)

if st.button("Check Answer"):
    if quiz_question == "100,000 years":
        st.success("🎉 Correct! The Milky Way is about 100,000 light-years in diameter.")
    else:
        st.error("❌ Not quite! The correct answer is 100,000 years.")

# Conclusion with call to action
st.markdown("---")
st.markdown("""
### 🌠 The Journey Continues

The universe's vastness reminds us of our place in the cosmos - tiny yet significant. Every time you look up at the night sky, 
you're seeing light that has traveled incredible distances across space and time to reach your eyes.

**Keep exploring, keep wondering, and never stop being amazed by the universe! 🚀**
""")

# Add a timestamp
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")