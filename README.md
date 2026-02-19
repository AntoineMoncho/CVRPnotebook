# Capacitated Vehicle Routing Problem Notebook (CVRP Notebook)

This repository contains an **interactive notebook** that demonstrates a Capacitated Vehicle Routing Problem (CVRP) using Python.  
It is intended as a **hands-on demo** for logistics and operations research applications.

You can view and run the notebook directly on **Molab**:
https://molab.marimo.io/github
with:
https://github.com/AntoineMoncho/CVRPnotebook/blob/main/notebook.py
---

## Features

- **Random problem instance generation**:
  - Specify number of customers
  - Randomized customer demand
  - Customizable 2D grid representing customer locations
- **Solution approaches**:
  1. **Exact MILP solver** (via `pulp`) guaranteeing optimality within a time limit
  2. **Clarke & Wright heuristic**, fast and practical but not guaranteed optimal
- **Interactive visualization**:
  - Step-by-step route display
  - Adjustable number of vehicles, vehicle capacity, and solver parameters
- **Visualization of customers and routes** on a 2D plane

---

## Dependencies

This notebook uses **UV** for package management. Install dependencies with:

```bash
uv add marimo>=0.19.11
uv add uniformcvrpdemo>=0.1.2
