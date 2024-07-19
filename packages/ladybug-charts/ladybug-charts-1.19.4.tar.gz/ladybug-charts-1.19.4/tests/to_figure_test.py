from plotly.graph_objects import Figure
from ladybug_comfort.degreetime import heating_degree_time, cooling_degree_time
from ladybug.datacollection import HourlyContinuousCollection
from ladybug.datatype.temperaturetime import HeatingDegreeTime, CoolingDegreeTime
from ladybug_charts.to_figure import bar_chart, bar_chart_with_table
from ladybug_charts.utils import Strategy
from ladybug.color import Color, Colorset
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.sunpath import Sunpath
from ladybug_comfort.chart.polygonpmv import PolygonPMV
from ladybug.legend import LegendParameters
# heat maps


def test_hourly_continuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.heat_map()
    assert isinstance(fig, Figure)


def test_hourly_discontinuous_to_heatmap(epw):
    fig = epw.dry_bulb_temperature.filter_by_conditional_statement('a>25').heat_map()
    assert isinstance(fig, Figure)

# bar charts


def test_monthly_to_bar_chart(epw):
    fig = epw.dry_bulb_temperature.average_monthly().bar_chart()
    assert isinstance(fig, Figure)


def test_daily_to_bar_chart(epw):
    fig = epw.dry_bulb_temperature.average_daily().bar_chart()
    assert isinstance(fig, Figure)


def test_bar_chart_multiple_monthly_data(epw):
    dbt = epw.dry_bulb_temperature

    _heat_base_ = 18
    _cool_base_ = 23

    hourly_heat = HourlyContinuousCollection.compute_function_aligned(
        heating_degree_time, [dbt, _heat_base_],
        HeatingDegreeTime(), 'degC-hours')
    hourly_heat.convert_to_unit('degC-days')

    hourly_cool = HourlyContinuousCollection.compute_function_aligned(
        cooling_degree_time, [dbt, _cool_base_],
        CoolingDegreeTime(), 'degC-hours')
    hourly_cool.convert_to_unit('degC-days')

    fig = bar_chart([hourly_heat.total_monthly(),
                    hourly_cool.total_monthly()],
                    title='Degree-days', center_title=True,
                    colors=[Color(255, 0, 0), Color(0, 0, 255)], stack=True)
    assert isinstance(fig, Figure)


def test_bar_chart_multiple_daily_data(epw):
    dbt = epw.dry_bulb_temperature.average_daily()
    rh = epw.relative_humidity.average_daily()
    fig = bar_chart([dbt, rh])
    assert isinstance(fig, Figure)

# line-chart


def test_hourly_to_line_chart(epw):
    fig = epw.dry_bulb_temperature.line_chart()
    assert isinstance(fig, Figure)

# diurnal-average-charts


def test_hourly_to_diurnal_average(epw):
    fig = epw.dry_bulb_temperature.diurnal_average_chart()
    assert isinstance(fig, Figure)


def test_epw_to_diurnal_average(epw):
    fig = epw.diurnal_average_chart()
    assert isinstance(fig, Figure)


def test_hourly_plot(epw):
    hp = HourlyPlot(epw.dry_bulb_temperature)
    fig = hp.plot()
    assert isinstance(fig, Figure)


def test_monthly_chart_plot(epw):
    dbt_monthly = epw.dry_bulb_temperature.average_monthly()
    rh_monthly = epw.relative_humidity.average_monthly()
    mc = MonthlyChart([dbt_monthly, rh_monthly])
    fig = mc.plot()
    assert isinstance(fig, Figure)


def test_wind_rose(epw):
    lb_wind_rose = WindRose(epw.wind_direction, epw.wind_speed)
    fig = lb_wind_rose.plot()
    assert isinstance(fig, Figure)

def test_wind_rose_with_less_than_eleven_legend_colors(epw):
    
    colors = list(Colorset.original())[:5]
    lp = LegendParameters(colors=colors, max = 60, segment_count=2)

    lb_wind_rose = WindRose(epw.wind_direction, epw.wind_speed)
    lb_wind_rose.legend_parameters = lp

    fig = lb_wind_rose.plot()
    assert isinstance(fig, Figure)


def test_psych_chart(epw):
    lb_psy = PsychrometricChart(epw.dry_bulb_temperature, epw.relative_humidity)
    fig = lb_psy.plot()
    assert isinstance(fig, Figure)


def test_psych_chart_with_data(epw):
    lb_psy = PsychrometricChart(epw.dry_bulb_temperature, epw.relative_humidity)
    pmv = PolygonPMV(lb_psy)
    fig = lb_psy.plot(data=epw.direct_normal_radiation, polygon_pmv=pmv,
                      strategies=[
                          Strategy.comfort,
                          Strategy.evaporative_cooling,
                          Strategy.mas_night_ventilation,
                          Strategy.occupant_use_of_fans,
                          Strategy.capture_internal_heat,
                          Strategy.passive_solar_heating, ],
                      solar_data=epw.direct_normal_radiation,)
    assert isinstance(fig, Figure)


def test_sunpath(epw):
    lb_sunpath = Sunpath.from_location(epw.location)
    fig = lb_sunpath.plot(data=epw.dry_bulb_temperature, colorset=Colorset.nuanced(),
                          min_range=0, max_range=50, title='SUNPATH', show_title=True)
    assert isinstance(fig, Figure)


def test_bar_charts_with_table(epw):

    dir = epw.direct_normal_radiation.average_monthly()
    diff = epw.diffuse_horizontal_radiation.average_monthly()
    glob = epw.global_horizontal_radiation.average_monthly()

    colors = [Color(255, 79, 56), Color(255, 139, 56), Color(255, 199, 56)]
    fig = bar_chart_with_table(data=[dir, diff, glob],
                               colors=colors, stack=True)
    assert isinstance(fig, Figure)
