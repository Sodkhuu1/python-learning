import time
import math
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="2^x Dot Tree", layout="centered")

# --------- SESSION STATE SETUP ----------
if "generation" not in st.session_state:
    st.session_state.generation = 0          # start with generation 0 (1 dot)
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()
if "running" not in st.session_state:
    st.session_state.running = True          # auto-start animation

MAX_GENERATION = 20  # to avoid infinite growth (you can increase this)

st.title("Binary Growth: 2^x Dots")
st.caption("Every 2 seconds, each dot creates 2 new dots (like 2^x).")

# --------- UPDATE GENERATION EVERY 2 SECONDS ----------
now = time.time()
if st.session_state.running and st.session_state.generation < MAX_GENERATION:
    if now - st.session_state.last_update >= 2:  # 2-second period
        st.session_state.generation += 1
        st.session_state.last_update = now

gen = st.session_state.generation
num_nodes = 2 ** gen

st.write(f"**Generation:** {gen} — **Dots:** {num_nodes}")

# --------- BUILD NODE POSITIONS ----------
nodes = []   # (x, y)
edges = []   # ((x1, y1), (x2, y2))

for g in range(gen + 1):
    count = 2 ** g
    # center the nodes around x=0
    for i in range(count):
        x = i - (count - 1) / 2.0
        y = -g  # lower generations go down
        nodes.append((g, i, x, y))

# Create edges: each node (except root) connects to its parent
pos_dict = {(g, i): (x, y) for (g, i, x, y) in nodes}

for g in range(1, gen + 1):
    count = 2 ** g
    for i in range(count):
        child = (g, i)
        parent = (g - 1, i // 2)
        x1, y1 = pos_dict[parent]
        x2, y2 = pos_dict[child]
        edges.append(((x1, y1), (x2, y2)))

# --------- PLOT WITH MATPLOTLIB ----------
fig, ax = plt.subplots()
# Draw edges
for (x1, y1), (x2, y2) in edges:
    ax.plot([x1, x2], [y1, y2])

# Draw nodes
xs = [x for (_, _, x, _) in nodes]
ys = [y for (_, _, _, y) in nodes]
ax.scatter(xs, ys, s=80)

ax.set_aspect("equal")
ax.axis("off")

st.pyplot(fig)

# --------- AUTO-RERUN FOR ANIMATION ----------
# Stop auto rerun when reaching MAX_GENERATION
if st.session_state.generation < MAX_GENERATION:
    time.sleep(2)
    st.rerun()
else:
    st.success("Reached maximum generation. You can increase MAX_GENERATION in the code.")
