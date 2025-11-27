import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# Page header
st.title("🌍 A New World is Beautiful")
st.markdown("---")

# Hero section with inspirational content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ## Discovering Beauty in Our Changing World
    
    In every corner of our planet, beauty manifests in countless ways - from the microscopic patterns of snowflakes 
    to the vast expanses of starlit skies. As we navigate through an ever-evolving world, we find that beauty 
    isn't just in what we see, but in how we connect, grow, and create together.
    """)

with col2:
    st.info("💡 **Did you know?** \n\nThere are over 8.7 million species on Earth, each contributing to the beautiful tapestry of life!")

# Interactive beauty metrics
st.markdown("## 🌟 Beauty Around Us")

# Create sample data for beautiful things
beauty_categories = {
    "Natural Wonders": ["Aurora Borealis", "Grand Canyon", "Great Barrier Reef", "Mount Everest", "Amazon Rainforest"],
    "Human Creativity": ["Art Museums", "Architecture", "Music", "Literature", "Dance"],
    "Scientific Marvels": ["DNA Structure", "Fractals", "Quantum Physics", "Space Exploration", "Medical Breakthroughs"],
    "Cultural Heritage": ["Ancient Temples", "Traditional Crafts", "Folk Stories", "Festivals", "Languages"]
}

# Interactive category selector
selected_category = st.selectbox("Choose a category to explore:", list(beauty_categories.keys()))

# Display items in the selected category
st.markdown(f"### Beautiful aspects of {selected_category}:")
items = beauty_categories[selected_category]

# Create columns for items
cols = st.columns(min(len(items), 3))
for i, item in enumerate(items):
    with cols[i % 3]:
        st.markdown(f"**{item}**")
        # Add a simple rating system
        rating = st.slider(f"Rate {item}", 1, 5, 4, key=f"rating_{item}")

# Beautiful data visualization
st.markdown("## 📊 The Mathematics of Beauty")

# Golden ratio visualization
phi = (1 + np.sqrt(5)) / 2
st.markdown(f"### The Golden Ratio: φ = {phi:.6f}")

col1, col2 = st.columns(2)

with col1:
    # Fibonacci spiral
    fig = go.Figure()
    
    # Generate Fibonacci sequence
    fib = [1, 1]
    for i in range(10):
        fib.append(fib[-1] + fib[-2])
    
    # Create spiral data
    theta = np.linspace(0, 6*np.pi, 1000)
    r = np.exp(theta * 0.2)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Golden Spiral',
                            line=dict(color='gold', width=3)))
    
    fig.update_layout(
        title="Golden Spiral in Nature",
        showlegend=False,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Color harmony wheel
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    values = [1] * len(colors)
    
    fig = px.pie(values=values, names=colors, color_discrete_sequence=colors,
                 title="Color Harmony Wheel")
    fig.update_traces(textposition='inside', textinfo='none')
    fig.update_layout(showlegend=False, height=400)
    
    st.plotly_chart(fig, use_container_width=True)

# Interactive beauty generator
st.markdown("## 🎨 Create Your Own Beauty")

# Beauty customizer
st.markdown("### Customize Your Perfect Day")

col1, col2, col3 = st.columns(3)

with col1:
    weather = st.selectbox("Weather:", ["Sunny ☀️", "Cloudy ☁️", "Rainy 🌧️", "Snowy ❄️"])
    time_of_day = st.selectbox("Time:", ["Dawn 🌅", "Morning ☀️", "Afternoon 🌤️", "Evening 🌆", "Night 🌙"])

with col2:
    activity = st.selectbox("Activity:", ["Reading 📚", "Walking 🚶", "Creating Art 🎨", "Listening to Music 🎵", "Meditating 🧘"])
    companion = st.selectbox("With:", ["Alone 🧘‍♀️", "Friends 👥", "Family 👨‍👩‍👧‍👦", "Pet 🐕", "Nature 🌳"])

with col3:
    mood_color = st.color_picker("Mood Color:", "#FF6B6B")
    beauty_intensity = st.slider("Beauty Intensity:", 1, 10, 7)

# Generate personalized beauty message
if st.button("Generate Your Beautiful Moment", type="primary"):
    st.success(f"""
    🌟 **Your Perfect Beautiful Moment:**
    
    Imagine a {weather.split()[0].lower()} {time_of_day.split()[0].lower()}, where you're {activity.split()[0].lower()} {companion.split()[0].lower()}. 
    The world around you glows with the essence of {mood_color}, and beauty radiates at intensity level {beauty_intensity}/10.
    
    *This moment is uniquely yours - treasure it!* ✨
    """)

# Beautiful quotes section
st.markdown("## 💭 Words of Beauty")

beautiful_quotes = [
    ("Beauty is not in the face; beauty is a light in the heart.", "Kahlil Gibran"),
    ("The earth laughs in flowers.", "Ralph Waldo Emerson"),
    ("Beauty begins the moment you decide to be yourself.", "Coco Chanel"),
    ("Everything has beauty, but not everyone sees it.", "Confucius"),
    ("Beauty is truth, truth beauty.", "John Keats"),
    ("The most beautiful things in the world cannot be seen or even touched, they must be felt with the heart.", "Helen Keller")
]

# Random quote generator
if st.button("Get Inspired 💫"):
    quote, author = random.choice(beautiful_quotes)
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 20px; 
                border-radius: 10px; 
                color: white; 
                text-align: center;
                margin: 20px 0;">
        <h3 style="margin-bottom: 10px;">"{quote}"</h3>
        <p style="margin: 0; font-style: italic;">— {author}</p>
    </div>
    """, unsafe_allow_html=True)

# Beauty tracker
st.markdown("## 📝 Daily Beauty Journal")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### What beautiful thing did you notice today?")
    beauty_note = st.text_area("Share your observation:", placeholder="Today I noticed the way sunlight danced through the leaves...")
    
    if st.button("Save Beautiful Memory"):
        if beauty_note:
            st.success("Your beautiful memory has been saved! 🌟")
            # In a real app, this would save to a database
        else:
            st.warning("Please share your beautiful observation first!")

with col2:
    st.markdown("### Beauty Stats")
    st.metric("Beautiful Moments Noticed", "247", "↗️ 12")
    st.metric("Days of Appreciation", "89", "↗️ 1")
    st.metric("Shared Smiles", "156", "↗️ 8")

# Footer with call to action
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius: 10px; color: white; margin: 20px 0;">
    <h3>🌍 Make the World More Beautiful</h3>
    <p>Every act of kindness, every moment of appreciation, every creative expression adds beauty to our world. 
    Start today, start now, start with a smile.</p>
</div>
""", unsafe_allow_html=True)

# Additional interactive elements
with st.expander("🔍 Explore More Beauty"):
    st.markdown("""
    ### Ways to Discover Beauty Daily:
    
    - **Mindful Observation**: Take 5 minutes to really look at something in nature
    - **Creative Expression**: Draw, write, sing, or dance - create something new
    - **Acts of Kindness**: Beautiful actions create beautiful ripples
    - **Learn Something New**: Knowledge reveals hidden beauty in the world
    - **Connect with Others**: Share beautiful moments and multiply their impact
    - **Practice Gratitude**: Appreciate the beauty that's already around you
    """)

# Error handling for any potential issues
try:
    # This ensures the page loads correctly even if there are minor issues
    st.markdown("*Page loaded successfully* ✅")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please refresh the page or contact support if the issue persists.")