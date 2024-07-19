"""Recreating ladybug psychrometric chart using Plotly."""

import warnings
import plotly.io as pio
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from typing import List

from ._helper import rgb_to_hex, mesh_to_coordinates, verts_to_coordinates
from .utils import StrategyParameters, Strategy

from ladybug.datacollection import BaseCollection, HourlyContinuousCollection
from ladybug import psychrometrics as psy
from ladybug.psychchart import PsychrometricChart
from ladybug_comfort.chart.polygonpmv import PolygonPMV
from ladybug_geometry.geometry2d.pointvector import Point2D
from ladybug_geometry.geometry2d.line import LineSegment2D
from ladybug_geometry.geometry2d.arc import Arc2D
from ladybug_geometry.geometry2d.polyline import Polyline2D
from ladybug.color import Color
from ladybug.legend import LegendParameters

# set white background in all charts
pio.templates.default = 'plotly_white'


def merge_polygon_data(poly_data):
    """Merge an array of polygon comfort conditions into a single data list."""
    val_mtx = [dat.values for dat in poly_data]
    merged_values = []
    for hr_data in zip(*val_mtx):
        hr_val = 1 if 1 in hr_data else 0
        merged_values.append(hr_val)
    return merged_values


def strategy_warning(polygon_name: str) -> str:
    msg = f'Polygon "{polygon_name}" could not fit on the chart given the current'\
        ' location of the comfort polygon(s). Try moving the comfort polygon(s) by'\
        ' changing its criteria to see the missing polygon. \n'
    print(msg)


def _psych_chart(psych: PsychrometricChart, data: BaseCollection = None,
                 title: str = None, show_title: bool = False, 
                 polygon_pmv: PolygonPMV = None,
                 strategies: List[Strategy] = [Strategy.comfort],
                 strategy_parameters: StrategyParameters = StrategyParameters(),
                 solar_data: HourlyContinuousCollection = None,
                 colors: List[Color] = None) -> Figure:
    """Create a psychrometric chart.

    Args:
        psych: A ladybug PsychrometricChart object.
        data: A ladybug DataCollection object.
        title: A title for the plot. Defaults to None.
        show_title: A boolean to show or hide the title. Defaults to False.
        polygon_pmv: A ladybug PolygonPMV object. If provided, polygons will be drawn.
            Defaults to None.
        strategies: A list of strategies to be applied to the chart. Accepts a list of
            Stragegy objects. Defaults to out of the box StrategyParameters object.
        strategy_parameters: A StrategyParameters object. Defaults to None.
        solar_data: An annual hourly continuous data collection of irradiance
            (or radiation) in W/m2 (or Wh/m2) that aligns with the data
            points on the psychrometric chart. This is only required when
            plotting a "Passive Solar Heating" strategy polygon on the chart.
            The irradiance values should be incident on the orientation of
            the passive solar heated windows. So using global horizontal
            radiation assumes that all windows are skylights (like a
            greenhouse). Defaults to None.
        colors: A list of colors to be used for the comfort polygons. Defaults to None.

    Returns:
        A plotly figure.
    """
    if psych.use_ip and data:
        data = data.to_ip()

    temp_line_unit = ' F' if psych.use_ip else ' C'
    hor_title_unit = ' (°F)' if psych.use_ip else ' (°C)'

    hr_min, hr_max = (0.0, 0.03) # Here, the upper value comes from the default value
    # of the maximum humidity ratio on the ladybug PsychrometricChart
    t_min, t_max = (-5, 115) if psych.use_ip else (-20, 50) # Based on the same setting on
    # the LB PscychrometricChart component of LBT

    var_range_x = [t_min, t_max]
    var_range_y = [hr_min, hr_max]

    # Create a new psychrometric chart instance with a base point at the bottom left
    # corner of the chart
    psych_display = PsychrometricChart(
        psych.temperature,
        psych.relative_humidity,
        legend_parameters=psych.legend_parameters,
        base_point=Point2D(var_range_x[0], 0),
        y_dim=1,
        min_temperature=t_min,
        max_temperature=t_max,
        use_ip = psych.use_ip)

    fig = go.Figure()

    ###########################################################################
    # if no data is provided, plot frequency
    ###########################################################################
    if not data:
        chart_title = 'Psychrometric Chart - Frequency'
        # Plot colored mesh
        cords = mesh_to_coordinates(psych_display.colored_mesh)
        for count, cord in enumerate(cords):
            fig.add_trace(
                go.Scatter(
                    x=cord[0],
                    y=cord[1],
                    fill='toself',
                    fillcolor=rgb_to_hex(psych_display.colored_mesh.colors[count]),
                    line=dict(width=0),
                    showlegend=False,
                    mode='lines',
                )
            )

            # In plotly, it's not possible to have hover text on a filled shape
            # add another trace just to have hover text
            fig.add_trace(
                go.Scatter(
                    x=[psych_display.colored_mesh.face_centroids[count].x],
                    y=[psych_display.colored_mesh.face_centroids[count].y],
                    showlegend=False,
                    mode='markers',
                    opacity=0,
                    hovertemplate=str(int(psych_display.hour_values[count])) + ' hours' +
                    '<extra></extra>',
                )
            )

        # create a dummy trace to make the Legend
        colorbar_trace = go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=dict(
                colorscale=[rgb_to_hex(color)
                            for color in psych_display.legend_parameters.colors],
                showscale=True,
                cmin=psych_display.legend_parameters.min,
                cmax=psych_display.legend_parameters.max,
                colorbar=dict(thickness=10, title=psych_display.legend_parameters.title),
            ),
        )
        # add the dummy trace to the figure
        fig.add_trace(colorbar_trace)

    ###########################################################################
    # Load data
    ###########################################################################
    else:
        var = data.header.data_type.name
        chart_title = title if title else f'Psychrometric Chart - {var}'
        lp = LegendParameters(colors=psych_display.legend_parameters.colors)
        # add colored data mesh
        mesh, graphic_container = psych_display.data_mesh(data, lp)
        cords = mesh_to_coordinates(mesh)
        for count, cord in enumerate(cords):
            fig.add_trace(
                go.Scatter(
                    x=cord[0],
                    y=cord[1],
                    fill='toself',
                    fillcolor=rgb_to_hex(graphic_container.value_colors[count]),
                    line=dict(width=0),
                    showlegend=False,
                    mode='lines'
                ))

            # In plotly, it's not possible to have hover text on a filled shape
            # add another trace just to have hover text
            fig.add_trace(
                go.Scatter(
                    x=[mesh.face_centroids[count].x],
                    y=[mesh.face_centroids[count].y],
                    showlegend=False,
                    mode='markers',
                    opacity=0,
                    hovertemplate=str(
                        int(graphic_container.values[count])) + ' '
                    + graphic_container.legend_parameters.title +
                    '<extra></extra>',
                )
            )

        # create a dummy trace to make the Legend
        colorbar_trace = go.Scatter(
            x=[None],
            y=[None],
            mode='markers',
            showlegend=False,
            marker=dict(
                colorscale=[rgb_to_hex(color)
                            for color in graphic_container.legend_parameters.colors],
                showscale=True,
                cmin=graphic_container.legend_parameters.min,
                cmax=graphic_container.legend_parameters.max,
                colorbar=dict(
                    thickness=10, title=graphic_container.legend_parameters.title),
            ),
        )

        # add the dummy trace to the figure
        fig.add_trace(colorbar_trace)

    ###########################################################################
    # Add lines
    ###########################################################################

    # add relative humidity lines
    for count, polyline in enumerate(psych_display.rh_lines):
        # get cordinates from vertices of polygons
        x_cords, y_cords = verts_to_coordinates(polyline.vertices, close=False)
        fig.add_trace(
            go.Scatter(
                x=x_cords,
                y=y_cords,
                showlegend=False,
                mode="lines",
                name="",
                hovertemplate="RH " + psych_display.rh_labels[count] + "%",
                line=dict(width=1, color="#85837f"),
            )
        )

    # add enthalpy lines
    for count, line in enumerate(psych_display.enthalpy_lines):
        # get cordinates from vertices of polygons
        x_cords, y_cords = verts_to_coordinates(line.vertices, close=False)
        fig.add_trace(
            go.Scatter(
                x=x_cords,
                y=y_cords,
                showlegend=False,
                mode="lines",
                name="",
                hovertemplate="Enthalpy " + psych_display.enthalpy_labels[count],
                line=dict(width=1, color="#85837f"),
            )
        )

    # add temperature lines
    for count, line in enumerate(psych_display.temperature_lines):
        # get cordinates from vertices of polygons
        x_cords, y_cords = verts_to_coordinates(line.vertices, close=False)
        fig.add_trace(
            go.Scatter(
                x=x_cords,
                y=y_cords,
                showlegend=False,
                mode="lines",
                name="",
                hovertemplate="Temperature " +
                psych_display.temperature_labels[count] + temp_line_unit,
                line=dict(width=1, color="#85837f"),
            )
        )

    # add humidity ratio lines
    for count, line in enumerate(psych_display.hr_lines):
        # get cordinates from vertices of polygons
        x_cords, y_cords = verts_to_coordinates(line.vertices, close=False)
        fig.add_trace(
            go.Scatter(
                x=x_cords,
                y=y_cords,
                showlegend=False,
                mode="lines",
                name="",
                hovertemplate="Humidity Ratio " + psych_display.hr_labels[count],
                line=dict(width=1, color="#85837f"),
            )
        )

    ###########################################################################
    # add polygons if requested
    ###########################################################################
    if polygon_pmv:

        # Use colors if provided
        if colors:
            if len(colors) == len(strategies) and\
                    all([isinstance(color, Color) for color in colors]):
                strategy_colors = [rgb_to_hex(color) for color in colors]
            else:
                raise ValueError(
                    'colors must be a list of Color objects and match the'
                    ' length of strategies')
        else:
            # Defult colors for the comfort polygons
            strategy_colors = {
                'Evaporative Cooling': '#008dff',
                'Mass + Night Ventilation': '#333333',
                'Occupant Use of Fans': '#3d17ff',
                'Capture Internal Heat': '#f58700',
                'Passive Solar Heating': '#ff0400',
                'Comfort': '#009402'
            }

        poly_obj = PolygonPMV(psych_display,
                              polygon_pmv.rad_temperature,
                              polygon_pmv.air_speed,
                              polygon_pmv.met_rate,
                              polygon_pmv.clo_value,
                              polygon_pmv.external_work,
                              polygon_pmv.comfort_parameter)

        # collecting all the polygons
        polygons, polygon_names, polygon_data = [], [], []

        # If other strategies are applied, add their polygons
        if strategies:

            if Strategy.comfort in strategies:
                poly_name = Strategy.comfort.value
                comfort_poly = poly_obj.comfort_polygons[0]
                polygons.append(comfort_poly)
                polygon_names.append(poly_name)
                dat = poly_obj.evaluate_polygon(comfort_poly, tolerance=0.01)
                dat = dat[0] if len(
                    dat) == 1 else poly_obj.create_collection(dat, poly_name)
                polygon_data.append(dat)

            if Strategy.evaporative_cooling in strategies:
                poly_name = Strategy.evaporative_cooling.value
                ec_poly = poly_obj.evaporative_cooling_polygon()
                if ec_poly:
                    polygons.append(ec_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_polygon(ec_poly, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)
                else:
                    strategy_warning(poly_name)

            if Strategy.mas_night_ventilation in strategies:
                poly_name = Strategy.mas_night_ventilation.value
                nf_poly = poly_obj.night_flush_polygon(
                    strategy_parameters.day_above_comfort)
                if nf_poly:
                    polygons.append(nf_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_night_flush_polygon(
                        nf_poly, psych_display.temperature,
                        strategy_parameters.night_below_comfort,
                        strategy_parameters.time_constant, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)
                else:
                    strategy_warning(poly_name)

            if Strategy.occupant_use_of_fans in strategies:
                poly_name = Strategy.occupant_use_of_fans.value
                fan_poly = poly_obj.fan_use_polygon(strategy_parameters.fan_air_speed)
                if fan_poly:
                    polygons.append(fan_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_polygon(fan_poly, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)
                else:
                    strategy_warning(poly_name)

            if Strategy.capture_internal_heat in strategies:
                poly_name = Strategy.capture_internal_heat.value
                iht_poly = poly_obj.internal_heat_polygon(
                    strategy_parameters.balance_temperature)
                if iht_poly:
                    polygons.append(iht_poly)
                    polygon_names.append(poly_name)
                    dat = poly_obj.evaluate_polygon(iht_poly, tolerance=0.01)
                    dat = dat[0] if len(
                        dat) == 1 else poly_obj.create_collection(dat, poly_name)
                    polygon_data.append(dat)

            if Strategy.passive_solar_heating in strategies:
                poly_name = Strategy.passive_solar_heating.value
                if not solar_data:
                    warnings.warn('In order to plot a passive solar heating polygon, '
                                  'you need to provide a solar data object.')
                else:
                    bal_t = strategy_parameters.balance_temperature \
                        if Strategy.capture_internal_heat in strategies else None
                    dat, delta = poly_obj.evaluate_passive_solar(
                        solar_data, strategy_parameters.solar_heating_capacity,
                        strategy_parameters.time_constant, bal_t)
                    sol_poly = poly_obj.passive_solar_polygon(delta, bal_t)
                    if sol_poly:
                        polygons.append(sol_poly)
                        polygon_names.append(poly_name)
                        dat = dat[0] if len(
                            dat) == 1 else poly_obj.create_collection(dat, poly_name)
                        polygon_data.append(dat)
                    else:
                        strategy_warning(poly_name)

        else:
            raise ValueError('You need to provide at least one strategy')

        # compute comfrt and total comfort values
        polygon_comfort = [dat.average * 100 for dat in polygon_data] if \
            isinstance(polygon_data[0], BaseCollection) else \
            [dat * 100 for dat in polygon_data]
        if isinstance(polygon_data[0], BaseCollection):
            merged_vals = merge_polygon_data(polygon_data)
            total_comf_data = poly_obj.create_collection(merged_vals, 'Total Comfort')
            total_comfort = total_comf_data.average * 100
        else:
            total_comf_data = 1 if sum(polygon_data) > 0 else 0
            total_comfort = total_comf_data * 100

        # draw each polygon
        for count, polygon in enumerate(polygons):

            # find left , right, top and bottom sides of the polygon
            center_side_dict = {}
            for side in polygon:
                if isinstance(side, LineSegment2D):
                    center_side_dict[side.midpoint] = side
                else:
                    center_side_dict[side.center] = side
            left_key = sorted(list(center_side_dict.keys()), key=lambda x: x.x)[0]
            right_key = sorted(list(center_side_dict.keys()), key=lambda x: x.x)[-1]
            bottom_key = sorted(list(center_side_dict.keys()), key=lambda x: x.y)[0]
            top_key = sorted(list(center_side_dict.keys()), key=lambda x: x.y)[-1]

            # if the top side is a polyline and has 3 vertices
            if isinstance(center_side_dict[top_key], Polyline2D) and \
                    len(center_side_dict[top_key].vertices) == 3:

                # create a center point from the bottom side and a horizontal 
                # reference vector
                if isinstance(center_side_dict[bottom_key], LineSegment2D):
                    center_point = center_side_dict[bottom_key].midpoint
                else:
                    center_point = center_side_dict[bottom_key].center
                right_point = Point2D(center_point.x+100, center_point.y)
                ref_vector = LineSegment2D.from_end_points(center_point, right_point).v

                # sort vertices of polyline before creating the arc
                vertices = center_side_dict[top_key].vertices
                vectors = [LineSegment2D.from_end_points(
                    center_point, vert).v for vert in vertices]
                angles = [ref_vector.angle_counterclockwise(vec) for vec in vectors]
                angles_verts_dict = dict(zip(angles, vertices))
                vertices = [angles_verts_dict[angle]
                            for angle in sorted(angles_verts_dict.keys())]
                arc = Arc2D.from_start_mid_end(vertices[2], vertices[1], vertices[0])
                center_side_dict[top_key] = arc.to_polyline(10)

                # sort vertices of polyline created from arc
                top_verts = center_side_dict[top_key].vertices
                vectors = [LineSegment2D.from_end_points(
                    center_point, vert).v for vert in top_verts]
                angles = [ref_vector.angle_counterclockwise(vec) for vec in vectors]
                angles_verts_dict = dict(zip(angles, top_verts))
                anti_clockwise_sorted_top_verts = [angles_verts_dict[angle]
                                                   for angle in 
                                                   sorted(angles_verts_dict.keys())]

                # Collect all the vertices that should be in anti clockwise order
                verts = []
                for vert in center_side_dict[left_key].vertices:
                    verts.append(vert)
                for vert in center_side_dict[bottom_key].vertices:
                    verts.append(vert)
                for vert in center_side_dict[right_key].vertices:
                    verts.append(vert)
                verts += anti_clockwise_sorted_top_verts
            else:
                verts = [point for geo in polygon for point in geo.vertices]

            # get cordinates from vertices of polygons
            x_cords, y_cords = verts_to_coordinates(verts)

            # plot the actual polygons
            fig.add_trace(
                go.Scatter(
                    x=x_cords,
                    y=y_cords,
                    line=dict(
                        width=4,
                        color=strategy_colors[polygon_names[count]] if not colors 
                        else strategy_colors[count]),
                    showlegend=True,
                    name=polygon_names[count] + ': ' +
                    str(round(polygon_comfort[count])) + '% of time',
                    mode='lines',
                    hovertemplate='' + '<extra></extra>',
                ))

    # setting the title for the figure
    if show_title:
        fig_title = {
            'text': title if title else chart_title,
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        }
    else:
        if title:
            raise ValueError(
                f'Title is set to "{title}" but show_title is set to False.')
        fig_title = None

    fig.update_layout(
        template='plotly_white',
        margin=dict(l=20, r=20, t=33, b=20),
        title=fig_title,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    fig.update_xaxes(
        title_text=f'Temperature {hor_title_unit}',
        range=var_range_x,
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
        dtick=5
    )
    fig.update_yaxes(
        title_text='Humidity Ratio (KG water/KG air)',
        range=var_range_y,
        showline=True,
        linewidth=1,
        linecolor='black',
        mirror=True,
    )
    return fig
