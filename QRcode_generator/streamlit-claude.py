import streamlit as st
import time
import math
import random

st.title("Exponential Dot Growth (2^x)")
st.write("Watch as each dot creates 2 new dots every 2 seconds!")

# Initialize session state
if 'dots' not in st.session_state:
    st.session_state.dots = [{'x': 400, 'y': 300, 'generation': 0, 'parent': None}]
    st.session_state.last_update = time.time()
    st.session_state.generation = 0

# Create placeholder for the canvas
canvas = st.empty()

# Control buttons
col1, col2 = st.columns(2)
with col1:
    if st.button("Reset"):
        st.session_state.dots = [{'x': 400, 'y': 300, 'generation': 0, 'parent': None}]
        st.session_state.last_update = time.time()
        st.session_state.generation = 0
        st.rerun()

with col2:
    st.write(f"Generation: {st.session_state.generation} | Total Dots: {len(st.session_state.dots)}")

# Check if it's time to create new dots
current_time = time.time()
if current_time - st.session_state.last_update >= 2.0:
    # Find all dots from the current generation
    current_gen_dots = [i for i, dot in enumerate(st.session_state.dots) 
                        if dot['generation'] == st.session_state.generation]
    
    # Create 2 new dots for each dot in current generation
    new_dots = []
    for parent_idx in current_gen_dots:
        parent = st.session_state.dots[parent_idx]
        
        # Create 2 children with random positions around parent
        for _ in range(2):
            angle = random.uniform(0, 2 * math.pi)
            distance = 80
            new_x = parent['x'] + distance * math.cos(angle)
            new_y = parent['y'] + distance * math.sin(angle)
            
            # Keep within bounds
            new_x = max(50, min(750, new_x))
            new_y = max(50, min(550, new_y))
            
            new_dots.append({
                'x': new_x,
                'y': new_y,
                'generation': st.session_state.generation + 1,
                'parent': parent_idx
            })
    
    st.session_state.dots.extend(new_dots)
    st.session_state.generation += 1
    st.session_state.last_update = current_time
    st.rerun()

# Draw the dots and connections
svg_lines = ""
for dot in st.session_state.dots:
    if dot['parent'] is not None:
        parent = st.session_state.dots[dot['parent']]
        svg_lines += f'<line x1="{parent["x"]}" y1="{parent["y"]}" x2="{dot["x"]}" y2="{dot["y"]}" stroke="gray" stroke-width="2"/>'

svg_dots = ""
for dot in st.session_state.dots:
    color = f"hsl({dot['generation'] * 30 % 360}, 70%, 50%)"
    svg_dots += f'<circle cx="{dot["x"]}" cy="{dot["y"]}" r="8" fill="{color}" stroke="white" stroke-width="2"/>'

svg = f'''
<svg width="800" height="600" style="border: 2px solid #ccc; background-color: #f9f9f9;">
    {svg_lines}
    {svg_dots}
</svg>
'''

canvas.markdown(svg, unsafe_allow_html=True)

# Auto-refresh every 0.5 seconds to check for updates
time.sleep(0.5)
st.rerun()