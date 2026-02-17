"""
ButterflyFX Reports Substrate
==============================

Derives charts, graphs, and data visualizations from kernel primitives.
All visualizations are mathematically derived from the underlying data geometry.

Chart Types:
    - Bar Charts: Categorical data as rectangular lengths
    - Pie Charts: Proportional data as angular sectors  
    - Trend Charts: Time series as connected line segments
    - Bell Curves: Normal distributions as Gaussian functions
    - Scatter Plots: Point distributions in 2D space
    - Area Charts: Filled regions under curves

Mathematical Foundations:
    - Bar height = data value mapped to Y-dimension
    - Pie angle = (value / total) × 2π radians
    - Trend slope = Δy/Δx (first derivative)
    - Bell curve = (1/σ√2π) × e^(-(x-μ)²/2σ²)

Copyright (c) 2024-2026 Kenneth Bingham
Licensed under ButterflyFX Commercial License
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any, Tuple, Union
from enum import Enum, auto
import math

from ..licensing import requires_license, LicenseTier
from ..substrates import Substrate, RGB, RGBA, Vector2D, Vector3D, Scalar


# =============================================================================
# CHART PRIMITIVES
# =============================================================================

@dataclass
class DataPoint:
    """A single data point with optional label and metadata"""
    value: float
    label: str = ""
    category: str = ""
    timestamp: Optional[float] = None
    color: Optional[RGB] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.color is None:
            # Derive color from value using hue mapping
            hue = (self.value * 30) % 360
            self.color = RGB.from_hue(hue) if hasattr(RGB, 'from_hue') else RGB(100, 150, 200)


@dataclass
class DataSeries:
    """A collection of data points with series metadata"""
    name: str
    points: List[DataPoint] = field(default_factory=list)
    color: RGB = field(default_factory=lambda: RGB(66, 133, 244))
    line_width: float = 2.0
    
    @property
    def values(self) -> List[float]:
        return [p.value for p in self.points]
    
    @property
    def labels(self) -> List[str]:
        return [p.label for p in self.points]
    
    @property
    def min_value(self) -> float:
        return min(self.values) if self.values else 0
    
    @property
    def max_value(self) -> float:
        return max(self.values) if self.values else 0
    
    @property
    def total(self) -> float:
        return sum(self.values)
    
    @property
    def mean(self) -> float:
        return self.total / len(self.values) if self.values else 0
    
    @property
    def variance(self) -> float:
        if not self.values:
            return 0
        mean = self.mean
        return sum((v - mean) ** 2 for v in self.values) / len(self.values)
    
    @property
    def std_dev(self) -> float:
        return math.sqrt(self.variance)
    
    def add(self, value: float, label: str = "", **kwargs) -> 'DataSeries':
        self.points.append(DataPoint(value=value, label=label, **kwargs))
        return self


@dataclass
class ChartAxis:
    """Axis definition for charts"""
    label: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    ticks: int = 5
    format_str: str = "{:.1f}"
    grid_lines: bool = True
    
    def get_tick_values(self, data_min: float, data_max: float) -> List[float]:
        """Calculate tick positions"""
        min_v = self.min_value if self.min_value is not None else data_min
        max_v = self.max_value if self.max_value is not None else data_max
        step = (max_v - min_v) / (self.ticks - 1) if self.ticks > 1 else 0
        return [min_v + i * step for i in range(self.ticks)]


class ChartType(Enum):
    """Types of charts/visualizations"""
    BAR = auto()
    BAR_HORIZONTAL = auto()
    BAR_STACKED = auto()
    PIE = auto()
    DONUT = auto()
    LINE = auto()
    AREA = auto()
    SCATTER = auto()
    BELL_CURVE = auto()
    HISTOGRAM = auto()
    CANDLESTICK = auto()
    RADAR = auto()


# =============================================================================
# CHART GEOMETRY - Mathematical derivations
# =============================================================================

@dataclass
class BarGeometry:
    """Geometric representation of a bar"""
    x: float
    y: float
    width: float
    height: float
    color: RGB
    label: str = ""
    value: float = 0
    
    def to_svg_rect(self) -> str:
        r, g, b = self.color.r, self.color.g, self.color.b
        return f'<rect x="{self.x}" y="{self.y}" width="{self.width}" height="{self.height}" fill="rgb({r},{g},{b})" />'


@dataclass
class PieSlice:
    """Geometric representation of a pie slice (angular sector)"""
    center: Vector2D
    radius: float
    start_angle: float  # radians
    end_angle: float    # radians
    color: RGB
    label: str = ""
    value: float = 0
    percentage: float = 0
    
    @property
    def mid_angle(self) -> float:
        return (self.start_angle + self.end_angle) / 2
    
    @property
    def arc_length(self) -> float:
        """Arc length = radius × angle"""
        return self.radius * abs(self.end_angle - self.start_angle)
    
    def label_position(self, offset: float = 1.2) -> Vector2D:
        """Calculate position for label (outside the slice)"""
        r = self.radius * offset
        return Vector2D(
            self.center.x + r * math.cos(self.mid_angle),
            self.center.y + r * math.sin(self.mid_angle)
        )
    
    def to_svg_path(self) -> str:
        """Generate SVG arc path"""
        large_arc = 1 if (self.end_angle - self.start_angle) > math.pi else 0
        
        x1 = self.center.x + self.radius * math.cos(self.start_angle)
        y1 = self.center.y + self.radius * math.sin(self.start_angle)
        x2 = self.center.x + self.radius * math.cos(self.end_angle)
        y2 = self.center.y + self.radius * math.sin(self.end_angle)
        
        r, g, b = self.color.r, self.color.g, self.color.b
        
        return f'''<path d="M {self.center.x} {self.center.y} L {x1} {y1} A {self.radius} {self.radius} 0 {large_arc} 1 {x2} {y2} Z" fill="rgb({r},{g},{b})" stroke="white" stroke-width="2" />'''


@dataclass
class LineSegment:
    """A segment in a line chart"""
    start: Vector2D
    end: Vector2D
    color: RGB
    width: float = 2.0
    
    @property
    def slope(self) -> float:
        """Δy/Δx - first derivative"""
        dx = self.end.x - self.start.x
        return (self.end.y - self.start.y) / dx if dx != 0 else float('inf')
    
    @property
    def length(self) -> float:
        return math.sqrt((self.end.x - self.start.x)**2 + (self.end.y - self.start.y)**2)
    
    def to_svg_line(self) -> str:
        r, g, b = self.color.r, self.color.g, self.color.b
        return f'<line x1="{self.start.x}" y1="{self.start.y}" x2="{self.end.x}" y2="{self.end.y}" stroke="rgb({r},{g},{b})" stroke-width="{self.width}" />'


@dataclass
class GaussianCurve:
    """Bell curve / Normal distribution"""
    mean: float       # μ - center of distribution
    std_dev: float    # σ - spread of distribution
    amplitude: float = 1.0  # scaling factor
    
    def evaluate(self, x: float) -> float:
        """
        Gaussian function: f(x) = A × (1/(σ√2π)) × e^(-(x-μ)²/(2σ²))
        """
        if self.std_dev == 0:
            return self.amplitude if x == self.mean else 0
        
        coefficient = self.amplitude / (self.std_dev * math.sqrt(2 * math.pi))
        exponent = -((x - self.mean) ** 2) / (2 * self.std_dev ** 2)
        return coefficient * math.exp(exponent)
    
    def sample_points(self, num_points: int = 100, 
                      range_sigmas: float = 4.0) -> List[Tuple[float, float]]:
        """Generate (x, y) points along the curve"""
        points = []
        x_min = self.mean - range_sigmas * self.std_dev
        x_max = self.mean + range_sigmas * self.std_dev
        step = (x_max - x_min) / (num_points - 1)
        
        for i in range(num_points):
            x = x_min + i * step
            y = self.evaluate(x)
            points.append((x, y))
        
        return points
    
    @property
    def peak_height(self) -> float:
        """Maximum height at mean"""
        return self.evaluate(self.mean)
    
    @property
    def fwhm(self) -> float:
        """Full Width at Half Maximum = 2σ√(2 ln 2) ≈ 2.355σ"""
        return 2 * self.std_dev * math.sqrt(2 * math.log(2))


# =============================================================================
# COLOR PALETTES - Derived from color wheel geometry
# =============================================================================

class ChartPalette:
    """Color palettes for charts - derived from color wheel angles"""
    
    # Standard palette
    STANDARD = [
        RGB(66, 133, 244),   # Blue
        RGB(234, 67, 53),    # Red
        RGB(251, 188, 4),    # Yellow
        RGB(52, 168, 83),    # Green
        RGB(255, 112, 67),   # Orange
        RGB(156, 39, 176),   # Purple
        RGB(0, 188, 212),    # Cyan
        RGB(255, 193, 7),    # Amber
    ]
    
    # Categorical (maximum perceptual distance)
    CATEGORICAL = [
        RGB(31, 119, 180),
        RGB(255, 127, 14),
        RGB(44, 160, 44),
        RGB(214, 39, 40),
        RGB(148, 103, 189),
        RGB(140, 86, 75),
        RGB(227, 119, 194),
        RGB(127, 127, 127),
    ]
    
    # Sequential (single hue gradient)
    BLUE_GRADIENT = [
        RGB(239, 243, 255),
        RGB(189, 215, 231),
        RGB(107, 174, 214),
        RGB(49, 130, 189),
        RGB(8, 81, 156),
    ]
    
    # Diverging (two opposing hues)
    DIVERGING = [
        RGB(178, 24, 43),
        RGB(239, 138, 98),
        RGB(253, 219, 199),
        RGB(209, 229, 240),
        RGB(103, 169, 207),
        RGB(33, 102, 172),
    ]
    
    @classmethod
    def generate_from_hue(cls, base_hue: float, count: int, 
                          saturation: float = 0.7, lightness: float = 0.5) -> List[RGB]:
        """Generate palette by rotating around color wheel"""
        colors = []
        hue_step = 360 / count
        
        for i in range(count):
            hue = (base_hue + i * hue_step) % 360
            colors.append(cls._hsl_to_rgb(hue, saturation, lightness))
        
        return colors
    
    @staticmethod
    def _hsl_to_rgb(h: float, s: float, l: float) -> RGB:
        """Convert HSL to RGB"""
        c = (1 - abs(2 * l - 1)) * s
        x = c * (1 - abs((h / 60) % 2 - 1))
        m = l - c / 2
        
        if h < 60:
            r, g, b = c, x, 0
        elif h < 120:
            r, g, b = x, c, 0
        elif h < 180:
            r, g, b = 0, c, x
        elif h < 240:
            r, g, b = 0, x, c
        elif h < 300:
            r, g, b = x, 0, c
        else:
            r, g, b = c, 0, x
        
        return RGB(int((r + m) * 255), int((g + m) * 255), int((b + m) * 255))


# =============================================================================
# REPORTS SUBSTRATE - Main Class
# =============================================================================

@requires_license("reports")
class ReportsSubstrate(Substrate):
    """
    Derives charts and visualizations from data using geometric principles.
    
    Mathematical Foundations:
    - Bar: Value → Height dimension
    - Pie: Value → Angular dimension (radians)
    - Line: Value sequence → Path through 2D plane
    - Bell: Statistical properties → Gaussian function
    
    All visualizations are derived from the underlying mathematical
    relationships, not arbitrary graphical choices.
    """
    
    def __init__(self, width: int = 800, height: int = 600):
        super().__init__("reports")
        self.width = width
        self.height = height
        self.padding = 60
        self.palette = ChartPalette.STANDARD
        
        # Chart area dimensions
        self.chart_left = self.padding
        self.chart_right = width - self.padding
        self.chart_top = self.padding
        self.chart_bottom = height - self.padding
        self.chart_width = self.chart_right - self.chart_left
        self.chart_height = self.chart_bottom - self.chart_top
    
    # =========================================================================
    # BAR CHART
    # =========================================================================
    
    def bar_chart(self, data: DataSeries, 
                  x_axis: Optional[ChartAxis] = None,
                  y_axis: Optional[ChartAxis] = None,
                  bar_spacing: float = 0.2,
                  horizontal: bool = False) -> List[BarGeometry]:
        """
        Derive bar chart geometry from data.
        
        Mathematical derivation:
            bar_height = (value / max_value) × chart_height
            bar_x = category_index × (bar_width + spacing)
        """
        if not data.points:
            return []
        
        bars = []
        n = len(data.points)
        max_val = max(p.value for p in data.points)
        min_val = min(min(p.value for p in data.points), 0)
        value_range = max_val - min_val if max_val != min_val else 1
        
        if horizontal:
            bar_height = self.chart_height / n * (1 - bar_spacing)
            spacing_height = self.chart_height / n * bar_spacing
            
            for i, point in enumerate(data.points):
                # Width derived from value
                normalized = (point.value - min_val) / value_range
                bar_width = normalized * self.chart_width
                
                bar = BarGeometry(
                    x=self.chart_left,
                    y=self.chart_top + i * (bar_height + spacing_height) + spacing_height / 2,
                    width=bar_width,
                    height=bar_height,
                    color=point.color or self.palette[i % len(self.palette)],
                    label=point.label,
                    value=point.value
                )
                bars.append(bar)
        else:
            bar_width = self.chart_width / n * (1 - bar_spacing)
            spacing_width = self.chart_width / n * bar_spacing
            
            for i, point in enumerate(data.points):
                # Height derived from value (the key mathematical relationship)
                normalized = (point.value - min_val) / value_range
                bar_height_px = normalized * self.chart_height
                
                bar = BarGeometry(
                    x=self.chart_left + i * (bar_width + spacing_width) + spacing_width / 2,
                    y=self.chart_bottom - bar_height_px,
                    width=bar_width,
                    height=bar_height_px,
                    color=point.color or self.palette[i % len(self.palette)],
                    label=point.label,
                    value=point.value
                )
                bars.append(bar)
        
        return bars
    
    def grouped_bar_chart(self, series_list: List[DataSeries],
                          bar_spacing: float = 0.1,
                          group_spacing: float = 0.2) -> List[List[BarGeometry]]:
        """Multiple bar series grouped by category"""
        if not series_list or not series_list[0].points:
            return []
        
        all_bars = []
        n_series = len(series_list)
        n_categories = len(series_list[0].points)
        
        # Find global max
        global_max = max(p.value for s in series_list for p in s.points)
        global_min = min(min(p.value for s in series_list for p in s.points), 0)
        value_range = global_max - global_min if global_max != global_min else 1
        
        group_width = self.chart_width / n_categories * (1 - group_spacing)
        bar_width = group_width / n_series * (1 - bar_spacing)
        
        for si, series in enumerate(series_list):
            series_bars = []
            for ci, point in enumerate(series.points):
                normalized = (point.value - global_min) / value_range
                bar_height_px = normalized * self.chart_height
                
                x = (self.chart_left + 
                     ci * self.chart_width / n_categories + 
                     self.chart_width / n_categories * group_spacing / 2 +
                     si * (bar_width + bar_width * bar_spacing))
                
                bar = BarGeometry(
                    x=x,
                    y=self.chart_bottom - bar_height_px,
                    width=bar_width,
                    height=bar_height_px,
                    color=series.color,
                    label=point.label,
                    value=point.value
                )
                series_bars.append(bar)
            all_bars.append(series_bars)
        
        return all_bars
    
    # =========================================================================
    # PIE CHART
    # =========================================================================
    
    def pie_chart(self, data: DataSeries,
                  center: Optional[Vector2D] = None,
                  radius: Optional[float] = None,
                  start_angle: float = -math.pi / 2,  # Start at top
                  donut_ratio: float = 0.0) -> List[PieSlice]:
        """
        Derive pie chart geometry from data.
        
        Mathematical derivation:
            slice_angle = (value / total) × 2π radians
            
        This is the fundamental angular proportion:
            The angle IS the proportion of the whole.
        """
        if not data.points:
            return []
        
        slices = []
        total = data.total
        if total == 0:
            return []
        
        # Default center and radius
        cx = center.x if center else self.width / 2
        cy = center.y if center else self.height / 2
        r = radius if radius else min(self.chart_width, self.chart_height) / 2 * 0.8
        
        current_angle = start_angle
        
        for i, point in enumerate(data.points):
            # THE KEY DERIVATION: value → angle
            # This is pure mathematical proportion
            proportion = point.value / total
            angle_span = proportion * 2 * math.pi
            
            slice_geom = PieSlice(
                center=Vector2D(cx, cy),
                radius=r,
                start_angle=current_angle,
                end_angle=current_angle + angle_span,
                color=point.color or self.palette[i % len(self.palette)],
                label=point.label,
                value=point.value,
                percentage=proportion * 100
            )
            slices.append(slice_geom)
            
            current_angle += angle_span
        
        return slices
    
    def donut_chart(self, data: DataSeries,
                    donut_ratio: float = 0.5,
                    **kwargs) -> Tuple[List[PieSlice], float]:
        """
        Donut chart - pie chart with inner radius.
        Returns slices and inner radius for rendering.
        """
        slices = self.pie_chart(data, **kwargs)
        if slices:
            inner_radius = slices[0].radius * donut_ratio
            return slices, inner_radius
        return [], 0
    
    # =========================================================================
    # TREND / LINE CHART
    # =========================================================================
    
    def trend_chart(self, data: DataSeries,
                    x_axis: Optional[ChartAxis] = None,
                    y_axis: Optional[ChartAxis] = None,
                    smooth: bool = False) -> Tuple[List[LineSegment], List[Vector2D]]:
        """
        Derive trend line geometry from data.
        
        Mathematical derivation:
            point_x = (index / count) × chart_width
            point_y = (value / max_value) × chart_height
            
        The line segments connect consecutive points,
        and their slopes represent rate of change (derivatives).
        """
        if len(data.points) < 2:
            return [], []
        
        segments = []
        points = []
        
        n = len(data.points)
        min_val = data.min_value
        max_val = data.max_value
        value_range = max_val - min_val if max_val != min_val else 1
        
        # Generate point coordinates
        for i, point in enumerate(data.points):
            # X: uniform spacing along timeline
            x = self.chart_left + (i / (n - 1)) * self.chart_width
            # Y: value mapped to height (inverted for screen coords)
            normalized = (point.value - min_val) / value_range
            y = self.chart_bottom - normalized * self.chart_height
            
            points.append(Vector2D(x, y))
        
        # Generate line segments
        for i in range(len(points) - 1):
            segment = LineSegment(
                start=points[i],
                end=points[i + 1],
                color=data.color,
                width=data.line_width
            )
            segments.append(segment)
        
        return segments, points
    
    def multi_trend_chart(self, series_list: List[DataSeries]) -> Dict[str, Tuple[List[LineSegment], List[Vector2D]]]:
        """Multiple trend lines on same chart"""
        # Find global min/max
        all_values = [p.value for s in series_list for p in s.points]
        if not all_values:
            return {}
        
        global_min = min(all_values)
        global_max = max(all_values)
        value_range = global_max - global_min if global_max != global_min else 1
        
        results = {}
        
        for series in series_list:
            if len(series.points) < 2:
                continue
                
            segments = []
            points = []
            n = len(series.points)
            
            for i, point in enumerate(series.points):
                x = self.chart_left + (i / (n - 1)) * self.chart_width
                normalized = (point.value - global_min) / value_range
                y = self.chart_bottom - normalized * self.chart_height
                points.append(Vector2D(x, y))
            
            for i in range(len(points) - 1):
                segment = LineSegment(
                    start=points[i],
                    end=points[i + 1],
                    color=series.color,
                    width=series.line_width
                )
                segments.append(segment)
            
            results[series.name] = (segments, points)
        
        return results
    
    # =========================================================================
    # AREA CHART
    # =========================================================================
    
    def area_chart(self, data: DataSeries,
                   fill_opacity: float = 0.3) -> Tuple[List[Vector2D], List[LineSegment]]:
        """
        Area chart - filled region under trend line.
        Returns polygon vertices and line segments.
        """
        segments, points = self.trend_chart(data)
        
        if not points:
            return [], []
        
        # Create closed polygon (add baseline)
        polygon = list(points)
        polygon.append(Vector2D(points[-1].x, self.chart_bottom))
        polygon.append(Vector2D(points[0].x, self.chart_bottom))
        
        return polygon, segments
    
    # =========================================================================
    # BELL CURVE / NORMAL DISTRIBUTION
    # =========================================================================
    
    def bell_curve(self, mean: float, std_dev: float,
                   num_points: int = 100,
                   color: Optional[RGB] = None,
                   fill: bool = True) -> Tuple[GaussianCurve, List[Vector2D], List[LineSegment]]:
        """
        Derive bell curve from statistical parameters.
        
        Mathematical formula (Gaussian):
            f(x) = (1/(σ√2π)) × e^(-(x-μ)²/(2σ²))
            
        Where:
            μ (mu) = mean (center)
            σ (sigma) = standard deviation (spread)
        """
        curve = GaussianCurve(mean=mean, std_dev=std_dev, amplitude=1.0)
        
        # Sample the curve
        raw_points = curve.sample_points(num_points)
        
        # Scale to chart dimensions
        x_values = [p[0] for p in raw_points]
        y_values = [p[1] for p in raw_points]
        
        x_min, x_max = min(x_values), max(x_values)
        y_max = max(y_values)
        
        x_range = x_max - x_min if x_max != x_min else 1
        
        # Map to chart coordinates
        points = []
        for x, y in raw_points:
            chart_x = self.chart_left + ((x - x_min) / x_range) * self.chart_width
            chart_y = self.chart_bottom - (y / y_max) * self.chart_height * 0.9
            points.append(Vector2D(chart_x, chart_y))
        
        # Generate line segments
        segments = []
        line_color = color or self.palette[0]
        for i in range(len(points) - 1):
            segment = LineSegment(
                start=points[i],
                end=points[i + 1],
                color=line_color,
                width=2.0
            )
            segments.append(segment)
        
        return curve, points, segments
    
    def bell_curve_from_data(self, data: DataSeries,
                              num_points: int = 100,
                              color: Optional[RGB] = None) -> Tuple[GaussianCurve, List[Vector2D], List[LineSegment]]:
        """
        Derive bell curve from actual data statistics.
        The curve is derived from the data's mean and standard deviation.
        """
        return self.bell_curve(
            mean=data.mean,
            std_dev=data.std_dev,
            num_points=num_points,
            color=color or data.color
        )
    
    def multiple_bell_curves(self, distributions: List[Tuple[float, float, RGB]],
                              num_points: int = 100) -> List[Tuple[GaussianCurve, List[Vector2D], List[LineSegment]]]:
        """
        Render multiple bell curves for comparison.
        Input: List of (mean, std_dev, color) tuples
        """
        results = []
        
        # Find global x range
        all_ranges = []
        for mean, std_dev, _ in distributions:
            all_ranges.extend([mean - 4*std_dev, mean + 4*std_dev])
        
        x_min, x_max = min(all_ranges), max(all_ranges)
        x_range = x_max - x_min
        
        for mean, std_dev, color in distributions:
            curve = GaussianCurve(mean=mean, std_dev=std_dev)
            raw_points = curve.sample_points(num_points)
            
            # Normalize y to [0, 1]
            y_max = curve.peak_height
            
            points = []
            for x, y in raw_points:
                chart_x = self.chart_left + ((x - x_min) / x_range) * self.chart_width
                chart_y = self.chart_bottom - (y / y_max) * self.chart_height * 0.8
                points.append(Vector2D(chart_x, chart_y))
            
            segments = []
            for i in range(len(points) - 1):
                segments.append(LineSegment(points[i], points[i+1], color, 2.0))
            
            results.append((curve, points, segments))
        
        return results
    
    # =========================================================================
    # SCATTER PLOT
    # =========================================================================
    
    def scatter_plot(self, x_data: List[float], y_data: List[float],
                     point_size: float = 5.0,
                     color: Optional[RGB] = None) -> List[Tuple[Vector2D, float, RGB]]:
        """
        Derive scatter plot from x,y coordinate pairs.
        Returns list of (position, size, color) tuples.
        """
        if len(x_data) != len(y_data) or not x_data:
            return []
        
        x_min, x_max = min(x_data), max(x_data)
        y_min, y_max = min(y_data), max(y_data)
        
        x_range = x_max - x_min if x_max != x_min else 1
        y_range = y_max - y_min if y_max != y_min else 1
        
        points = []
        c = color or self.palette[0]
        
        for x, y in zip(x_data, y_data):
            chart_x = self.chart_left + ((x - x_min) / x_range) * self.chart_width
            chart_y = self.chart_bottom - ((y - y_min) / y_range) * self.chart_height
            points.append((Vector2D(chart_x, chart_y), point_size, c))
        
        return points
    
    # =========================================================================
    # HISTOGRAM
    # =========================================================================
    
    def histogram(self, values: List[float],
                  bins: int = 10,
                  color: Optional[RGB] = None) -> Tuple[List[BarGeometry], List[float]]:
        """
        Derive histogram from raw values.
        Groups values into bins and shows frequency.
        """
        if not values:
            return [], []
        
        v_min, v_max = min(values), max(values)
        bin_width = (v_max - v_min) / bins if bins > 0 else 1
        
        # Count values in each bin
        counts = [0] * bins
        bin_edges = [v_min + i * bin_width for i in range(bins + 1)]
        
        for v in values:
            bin_idx = min(int((v - v_min) / bin_width), bins - 1)
            counts[bin_idx] += 1
        
        max_count = max(counts) if counts else 1
        
        # Generate bars
        bars = []
        c = color or self.palette[0]
        bar_pixel_width = self.chart_width / bins
        
        for i, count in enumerate(counts):
            normalized = count / max_count if max_count > 0 else 0
            bar_height = normalized * self.chart_height
            
            bar = BarGeometry(
                x=self.chart_left + i * bar_pixel_width,
                y=self.chart_bottom - bar_height,
                width=bar_pixel_width * 0.95,
                height=bar_height,
                color=c,
                label=f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}",
                value=count
            )
            bars.append(bar)
        
        return bars, bin_edges
    
    # =========================================================================
    # SVG GENERATION
    # =========================================================================
    
    def render_to_svg(self, elements: List[Any], 
                      title: str = "",
                      show_axes: bool = True,
                      show_grid: bool = True,
                      background: str = "#ffffff") -> str:
        """Render chart elements to SVG string"""
        parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">'
            f'<rect width="{self.width}" height="{self.height}" fill="{background}"/>'
        ]
        
        # Grid
        if show_grid:
            parts.append('<g class="grid" stroke="#e0e0e0" stroke-width="1">')
            for i in range(6):
                y = self.chart_top + i * self.chart_height / 5
                parts.append(f'<line x1="{self.chart_left}" y1="{y}" x2="{self.chart_right}" y2="{y}"/>')
            for i in range(6):
                x = self.chart_left + i * self.chart_width / 5
                parts.append(f'<line x1="{x}" y1="{self.chart_top}" x2="{x}" y2="{self.chart_bottom}"/>')
            parts.append('</g>')
        
        # Axes
        if show_axes:
            parts.append(f'<line x1="{self.chart_left}" y1="{self.chart_bottom}" x2="{self.chart_right}" y2="{self.chart_bottom}" stroke="#333" stroke-width="2"/>')
            parts.append(f'<line x1="{self.chart_left}" y1="{self.chart_top}" x2="{self.chart_left}" y2="{self.chart_bottom}" stroke="#333" stroke-width="2"/>')
        
        # Title
        if title:
            parts.append(f'<text x="{self.width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">{title}</text>')
        
        # Render elements
        for elem in elements:
            if isinstance(elem, BarGeometry):
                parts.append(elem.to_svg_rect())
                # Value label
                parts.append(f'<text x="{elem.x + elem.width/2}" y="{elem.y - 5}" text-anchor="middle" font-size="12" fill="#333">{elem.value:.1f}</text>')
            elif isinstance(elem, PieSlice):
                parts.append(elem.to_svg_path())
            elif isinstance(elem, LineSegment):
                parts.append(elem.to_svg_line())
            elif isinstance(elem, list):
                for sub in elem:
                    if isinstance(sub, (BarGeometry, PieSlice, LineSegment)):
                        if isinstance(sub, BarGeometry):
                            parts.append(sub.to_svg_rect())
                        elif isinstance(sub, PieSlice):
                            parts.append(sub.to_svg_path())
                        elif isinstance(sub, LineSegment):
                            parts.append(sub.to_svg_line())
        
        parts.append('</svg>')
        return '\n'.join(parts)
    
    def render_bar_chart_svg(self, data: DataSeries, title: str = "Bar Chart") -> str:
        """Convenience method for bar chart SVG"""
        bars = self.bar_chart(data)
        return self.render_to_svg(bars, title=title)
    
    def render_pie_chart_svg(self, data: DataSeries, title: str = "Pie Chart") -> str:
        """Convenience method for pie chart SVG"""
        slices = self.pie_chart(data)
        
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">',
            f'<rect width="{self.width}" height="{self.height}" fill="#ffffff"/>',
            f'<text x="{self.width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">{title}</text>'
        ]
        
        for slice_geom in slices:
            svg.append(slice_geom.to_svg_path())
            # Label
            label_pos = slice_geom.label_position(1.15)
            svg.append(f'<text x="{label_pos.x}" y="{label_pos.y}" text-anchor="middle" font-size="11" fill="#333">{slice_geom.label} ({slice_geom.percentage:.1f}%)</text>')
        
        svg.append('</svg>')
        return '\n'.join(svg)
    
    def render_trend_chart_svg(self, data: DataSeries, title: str = "Trend Chart") -> str:
        """Convenience method for trend chart SVG"""
        segments, points = self.trend_chart(data)
        
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">',
            f'<rect width="{self.width}" height="{self.height}" fill="#ffffff"/>'
        ]
        
        # Grid
        svg.append('<g class="grid" stroke="#e0e0e0" stroke-width="1">')
        for i in range(6):
            y = self.chart_top + i * self.chart_height / 5
            svg.append(f'<line x1="{self.chart_left}" y1="{y}" x2="{self.chart_right}" y2="{y}"/>')
        svg.append('</g>')
        
        # Axes
        svg.append(f'<line x1="{self.chart_left}" y1="{self.chart_bottom}" x2="{self.chart_right}" y2="{self.chart_bottom}" stroke="#333" stroke-width="2"/>')
        svg.append(f'<line x1="{self.chart_left}" y1="{self.chart_top}" x2="{self.chart_left}" y2="{self.chart_bottom}" stroke="#333" stroke-width="2"/>')
        
        svg.append(f'<text x="{self.width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">{title}</text>')
        
        # Line
        for seg in segments:
            svg.append(seg.to_svg_line())
        
        # Points
        for i, pt in enumerate(points):
            r, g, b = data.color.r, data.color.g, data.color.b
            svg.append(f'<circle cx="{pt.x}" cy="{pt.y}" r="4" fill="rgb({r},{g},{b})"/>')
        
        svg.append('</svg>')
        return '\n'.join(svg)
    
    def render_bell_curve_svg(self, mean: float, std_dev: float, 
                               title: str = "Bell Curve",
                               show_stats: bool = True) -> str:
        """Convenience method for bell curve SVG"""
        curve, points, segments = self.bell_curve(mean, std_dev)
        
        svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">',
            f'<rect width="{self.width}" height="{self.height}" fill="#ffffff"/>'
        ]
        
        # Grid
        svg.append('<g class="grid" stroke="#e0e0e0" stroke-width="1">')
        for i in range(6):
            y = self.chart_top + i * self.chart_height / 5
            svg.append(f'<line x1="{self.chart_left}" y1="{y}" x2="{self.chart_right}" y2="{y}"/>')
        svg.append('</g>')
        
        svg.append(f'<text x="{self.width/2}" y="30" text-anchor="middle" font-size="18" font-weight="bold" fill="#333">{title}</text>')
        
        # Fill area under curve
        fill_points = [(self.chart_left, self.chart_bottom)]
        fill_points.extend([(p.x, p.y) for p in points])
        fill_points.append((self.chart_right, self.chart_bottom))
        
        path_d = f"M {fill_points[0][0]} {fill_points[0][1]} "
        path_d += " ".join(f"L {x} {y}" for x, y in fill_points[1:])
        path_d += " Z"
        svg.append(f'<path d="{path_d}" fill="rgba(66,133,244,0.2)" stroke="none"/>')
        
        # Line
        for seg in segments:
            svg.append(seg.to_svg_line())
        
        # Statistics
        if show_stats:
            svg.append(f'<text x="{self.width - 20}" y="{self.chart_top + 20}" text-anchor="end" font-size="12" fill="#666">μ = {mean:.2f}</text>')
            svg.append(f'<text x="{self.width - 20}" y="{self.chart_top + 38}" text-anchor="end" font-size="12" fill="#666">σ = {std_dev:.2f}</text>')
            svg.append(f'<text x="{self.width - 20}" y="{self.chart_top + 56}" text-anchor="end" font-size="12" fill="#666">FWHM = {curve.fwhm:.2f}</text>')
        
        svg.append('</svg>')
        return '\n'.join(svg)


# =============================================================================
# DEMO / TEST
# =============================================================================

def demo_reports_substrate():
    """Demonstrate the reports substrate"""
    print("=" * 60)
    print("ButterflyFX REPORTS SUBSTRATE DEMO")
    print("=" * 60)
    print()
    
    substrate = ReportsSubstrate(width=800, height=500)
    
    # --- BAR CHART ---
    print("1. BAR CHART")
    print("   Value → Height mapping (dimensional derivation)")
    
    sales_data = DataSeries(name="Monthly Sales")
    sales_data.add(120, "Jan").add(150, "Feb").add(180, "Mar")
    sales_data.add(140, "Apr").add(200, "May").add(220, "Jun")
    
    bars = substrate.bar_chart(sales_data)
    print(f"   Generated {len(bars)} bars")
    for bar in bars[:3]:
        print(f"     {bar.label}: value={bar.value}, height={bar.height:.1f}px")
    
    bar_svg = substrate.render_bar_chart_svg(sales_data, "Monthly Sales")
    print(f"   SVG: {len(bar_svg)} chars")
    
    # --- PIE CHART ---
    print("\n2. PIE CHART")
    print("   Value → Angular sector (proportion × 2π)")
    
    market_data = DataSeries(name="Market Share")
    market_data.add(35, "Product A").add(25, "Product B")
    market_data.add(20, "Product C").add(15, "Product D").add(5, "Other")
    
    slices = substrate.pie_chart(market_data)
    print(f"   Generated {len(slices)} slices")
    for s in slices:
        angle_deg = math.degrees(s.end_angle - s.start_angle)
        print(f"     {s.label}: {s.percentage:.1f}% = {angle_deg:.1f}°")
    
    pie_svg = substrate.render_pie_chart_svg(market_data, "Market Share")
    print(f"   SVG: {len(pie_svg)} chars")
    
    # --- TREND CHART ---
    print("\n3. TREND CHART")
    print("   Value sequence → Connected points (slope = rate of change)")
    
    growth_data = DataSeries(name="Growth", color=RGB(52, 168, 83))
    for i in range(12):
        growth_data.add(100 + i * 15 + (i % 3) * 10, f"M{i+1}")
    
    segments, points = substrate.trend_chart(growth_data)
    print(f"   Generated {len(segments)} line segments")
    print(f"   Sample slopes:")
    for seg in segments[:3]:
        print(f"     Slope: {seg.slope:.2f} (Δy/Δx)")
    
    trend_svg = substrate.render_trend_chart_svg(growth_data, "Growth Trend")
    print(f"   SVG: {len(trend_svg)} chars")
    
    # --- BELL CURVE ---
    print("\n4. BELL CURVE (Gaussian Distribution)")
    print("   f(x) = (1/(σ√2π)) × e^(-(x-μ)²/(2σ²))")
    
    curve, points, segments = substrate.bell_curve(mean=50, std_dev=10)
    print(f"   Mean (μ): {curve.mean}")
    print(f"   Std Dev (σ): {curve.std_dev}")
    print(f"   Peak height: {curve.peak_height:.4f}")
    print(f"   FWHM: {curve.fwhm:.2f}")
    print(f"   Generated {len(points)} curve points")
    
    bell_svg = substrate.render_bell_curve_svg(50, 10, "Normal Distribution")
    print(f"   SVG: {len(bell_svg)} chars")
    
    # --- HISTOGRAM ---
    print("\n5. HISTOGRAM")
    print("   Raw values → Bin frequencies")
    
    import random
    random.seed(42)
    sample_values = [random.gauss(50, 15) for _ in range(1000)]
    
    hist_bars, bin_edges = substrate.histogram(sample_values, bins=15)
    print(f"   Generated {len(hist_bars)} bins")
    print(f"   Value range: {min(sample_values):.1f} - {max(sample_values):.1f}")
    
    # --- SCATTER PLOT ---
    print("\n6. SCATTER PLOT")
    print("   (x, y) pairs → Point distribution")
    
    x_vals = [random.uniform(0, 100) for _ in range(50)]
    y_vals = [x * 0.8 + random.gauss(0, 10) for x in x_vals]  # Linear with noise
    
    scatter_points = substrate.scatter_plot(x_vals, y_vals)
    print(f"   Generated {len(scatter_points)} points")
    
    print("\n" + "=" * 60)
    print("REPORTS SUBSTRATE DEMO COMPLETE")
    print("=" * 60)
    
    return {
        'bar_svg': bar_svg,
        'pie_svg': pie_svg,
        'trend_svg': trend_svg,
        'bell_svg': bell_svg
    }


if __name__ == "__main__":
    demo_reports_substrate()
