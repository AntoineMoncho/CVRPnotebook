# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "uniformcvrpdemo",
# ]
#
#
# 
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Capacitated Vehicle Routing Problem — Interactive Demo

    This notebook presents a compact and interactive demonstration of a **capacitated logistics routing problem (CVRP)**.

    We consider the following setting:
    - A set of customers, each with a demand
    - A fleet of identical vehicles with limited capacity
    - The objective is to serve all customers while minimizing the total travel distance

    Two solution approaches are compared:

    - **Exact resolution** using a Mixed-Integer Linear Programming (MILP) formulation solved with *PuLP*
    - **Heuristic resolution** using the classical *Clarke & Wright savings algorithm*

    The goal of this notebook is not performance benchmarking, but rather to illustrate:
    - modeling choices,
    - trade-offs between exact and heuristic methods,
    - and qualitative differences in the resulting routes.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Problem modeling and assumptions

    We generate a random CVRP instance and represent customers as points in a two-dimensional plane.

    **Model assumptions:**
    - Customers are represented as points in \(\mathbb{R}^2\)
    - Each customer has an associated demand
    - Vehicles start and end at a depot
    - All vehicles have the same capacity
    - The transportation network is modeled as a **complete graph**
    - Travel costs correspond to **Euclidean distances**

    This setup can be interpreted as a fleet of vehicles moving freely on an open terrain, with the objective of minimizing total distance traveled.

    ### Interpretation and limitations

    Although distances are represented geometrically, the 2D embedding should be seen as a **proxy for a generic cost matrix**:
    - customers may represent delivery locations, warehouses, or aggregated demand points
    - distances may encode travel time, cost, or any other symmetric metric

    This representation is intentionally simple and **does not capture all real-world constraints**, such as:
    - non-complete or directed graphs
    - road networks
    - time windows
    - asymmetric or non-metric costs

    Both the MILP formulation and the Clarke & Wright heuristic are, however, applicable to more general graphs and cost structures.
    The code structure is designed so that the distance matrix can easily be replaced by any externally computed cost matrix.
    """)
    return


@app.cell
def _(mo):
    n_customers = mo.ui.number(
    start=1,
    stop=20,
    step=1,
    value=10,
    label="Number of customers"
    )

    vehicle_capacity = mo.ui.number(
        start=50,
        stop=300,
        step=10,
        value=120,
        label="Capacity per vehicle"
    )

    min_demand = mo.ui.number(
        value=5,
        label="Min demand",
        step=1,
    )

    max_demand = mo.ui.number(
        value=20,
        label="Max demand",
        step=1,
    )

    grid_dimension = mo.ui.number(
        value=100,
        label="Size of the grid (recommended: 100)",
        step=1,
    )

    mo.vstack([n_customers, vehicle_capacity, min_demand, max_demand, grid_dimension])
    return (
        grid_dimension,
        max_demand,
        min_demand,
        n_customers,
        vehicle_capacity,
    )


@app.cell
def _(grid_dimension, max_demand, min_demand, n_customers):
    from uniformcvrpdemo.data import CustomersList
    from uniformcvrpdemo.visualization import plot_customers_scatter

    customers = CustomersList.generate_random(n_customers.value, side=grid_dimension.value, demand_range=(min_demand.value,max_demand.value))
    customers.compute_distance_matrix()

    fig_customers = plot_customers_scatter(n_customers.value, customers.get_positions(), customers.get_demands(), vmin_demand=min_demand.value, vmax_demand=max_demand.value, side=grid_dimension.value)
    fig_customers
    print(customers.get_demands())
    return (customers,)


@app.cell
def _(mo):
    mo.md("""
    ## Exact resolution using MILP

    We first solve the CVRP using an exact Mixed-Integer Linear Programming formulation.
    This approach guarantees optimality (within the solver time limit), but scales poorly with problem size.
    """)
    return


@app.cell
def _(mo):
    n_vehicles = mo.ui.number(
    start=1,
    stop=10,
    step=1,
    value=3,
    label="Maximum number of vehicles"
    )

    time_limit = mo.ui.number(
        value=15,
        label="Time limit for the MILP solver (s)",
        step=0.1)


    mo.vstack([n_vehicles, time_limit])
    return n_vehicles, time_limit


@app.cell
def _(customers, n_vehicles, time_limit, vehicle_capacity):
    from uniformcvrpdemo.solver import solve_cvrp_fixed
    from uniformcvrpdemo.data import OrderedTour, VehicleRoute

    milp_routes = solve_cvrp_fixed(
            customers,
            customers.distance_matrix,
            vehicle_capacity.value,
            n_vehicles.value,
            time_limit.value
        )
    return OrderedTour, VehicleRoute, milp_routes


@app.cell
def _(OrderedTour, VehicleRoute, customers, milp_routes):
    print(milp_routes)


    labeled_routes = {
        chr(ord("A") + vid): VehicleRoute(chr(ord("A") + vid), route)
        for vid, route in milp_routes.items()
    }

    tour = OrderedTour(labeled_routes, customers.distance_matrix)
    visits = tour.compute_ordered_visits()

    for vehicle, customer, cum_dist in visits:
        print(vehicle, customer, cum_dist)
    return (visits,)


@app.cell
def _(mo, n_vehicles, visits):
    current_step = mo.ui.slider(
        value=0,
        label="Use this slider to display a tour interactively",
        start = 0,
        stop = len(visits)-n_vehicles.value,
        step=1,
    )



    mo.vstack([current_step])
    return (current_step,)


@app.cell
def _(current_step, customers, visits):
    from uniformcvrpdemo.visualization import plot_routes_up_to_step

    fig_milp, ax_milp = plot_routes_up_to_step(customers, visits, T=current_step.value)
    fig_milp
    return (plot_routes_up_to_step,)


@app.cell
def _(mo):
    mo.md("""
    ## Heuristic resolution using Clarke & Wright

    We now solve the same instance using the Clarke & Wright savings heuristic.
    This method is fast and widely used in practice, but it does not guarantee an optimal solution.
    In this formulation, the number of vehicles is not strictly constrained.
    """)
    return


@app.cell
def _(OrderedTour, VehicleRoute, customers, vehicle_capacity):
    from uniformcvrpdemo.solver import clarke_wright

    cw_routes = clarke_wright(customers, vehicle_capacity.value)
    labeled_cw_routes = {
        chr(ord("A") + i): VehicleRoute(chr(ord("A") + i), cw_routes[i])
        for i in range(len(cw_routes))
    }

    cw_tour = OrderedTour(labeled_cw_routes, customers.distance_matrix)
    cw_visits = cw_tour.compute_ordered_visits()

    for cw_vehicle, cw_customer, cw_cum_dist in cw_visits:
        print(cw_vehicle, cw_customer, cw_cum_dist)
    return (cw_visits,)


@app.cell
def _(cw_visits, mo):
    n_cw_vehicles = len(set(cw_v for cw_v, _, _ in cw_visits))

    current_cw_step = mo.ui.slider(
        value=0,
        label="Use this slider to display a tour interactively",
        start = 0,
        stop = len(cw_visits)-n_cw_vehicles,
        step=1,
    )



    mo.vstack([current_cw_step])
    return (current_cw_step,)


@app.cell
def _(current_cw_step, customers, cw_visits, plot_routes_up_to_step):
    fig_cw, ax_cw = plot_routes_up_to_step(customers, cw_visits, T=current_cw_step.value)
    fig_cw
    return


if __name__ == "__main__":
    app.run()
