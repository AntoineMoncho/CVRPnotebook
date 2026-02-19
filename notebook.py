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
    # Capacitated Logistics Demo

    This notebook illustrates a simple **logistics assignment problem**:
    - Assign packages to vehicles
    - Each vehicle has a limited capacity
    - Parameters are controlled interactively

    Two solutions are currently implemented
    - An exact solution using a MIlP solver from the pulp package
    - An approximate solution using the Clark and Wright heuristic
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    We generate a random instance of the problem and display the customers on a grid.
    - Customers are modelized by points on the 2D plane.
    - Vehicles can freely navigate from customer to customer without obstacles (the graph is complete i.e. fully connected).
    - We use the euclidean distance as a cost function associated by each node between customers.

    This corresponds to a fleet of vehicles navigating on a free terrain and trying to minimize the total distance covered during the tour.

    This said, the model does not have to be interpreted as a literal distance in the 2D plane:
    - customers can live in a more complex and notes can be assigned a more complex cost function
    - the following can be seen as a representation of customers that maps them to points in a way that matches their distance on the plane to the cost associated to each node.

    Even with this slight conceptual extension, such a representation is not surjective. many problem settings may not be represented by an instance of this model: for instance non-planar or simply incomplete graphs, or costs functions that are not tied to an implicit planar distance.

    Exact MilP solvers as well as the Clark and Wright heuristics are designed to handle arbitrary graphs and cost functions and the code can be easily adapted to work in this more general setting.
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
