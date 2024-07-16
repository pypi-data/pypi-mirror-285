from typing import List, Optional, Dict, Iterable
import aspose.pycore
import aspose.pydrawing
import aspose.cellsgridjs
import aspose.cellsgridjs.chart

class AreaObject:
    '''internal use'''
    
    @property
    def color(self) -> str:
        '''color'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''color'''
        ...
    
    ...

class AxisLineObject:
    '''internal use'''
    
    @property
    def color(self) -> str:
        '''color'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''color'''
        ...
    
    @property
    def weight_px(self) -> float:
        ...
    
    @weight_px.setter
    def weight_px(self, value : float):
        ...
    
    @property
    def style(self) -> str:
        '''style'''
        ...
    
    @style.setter
    def style(self, value : str):
        '''style'''
        ...
    
    ...

class AxisObject:
    '''internal use'''
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def title(self) -> aspose.cellsgridjs.chart.TitleObject:
        '''title'''
        ...
    
    @title.setter
    def title(self, value : aspose.cellsgridjs.chart.TitleObject):
        '''title'''
        ...
    
    @property
    def category_data(self) -> List[aspose.cellsgridjs.chart.CellData]:
        ...
    
    @category_data.setter
    def category_data(self, value : List[aspose.cellsgridjs.chart.CellData]):
        ...
    
    @property
    def axis_line(self) -> aspose.cellsgridjs.chart.AxisLineObject:
        ...
    
    @axis_line.setter
    def axis_line(self, value : aspose.cellsgridjs.chart.AxisLineObject):
        ...
    
    ...

class BackgroundColorObject:
    '''internal use'''
    
    ...

class BorderObject:
    '''internal use'''
    
    @property
    def weight_px(self) -> float:
        ...
    
    @weight_px.setter
    def weight_px(self, value : float):
        ...
    
    @property
    def color(self) -> str:
        '''color'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''color'''
        ...
    
    @property
    def style(self) -> str:
        '''style'''
        ...
    
    @style.setter
    def style(self, value : str):
        '''style'''
        ...
    
    ...

class CellData:
    '''internal use'''
    
    @property
    def name(self) -> str:
        '''name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''name'''
        ...
    
    @property
    def sheet_name(self) -> str:
        ...
    
    @sheet_name.setter
    def sheet_name(self, value : str):
        ...
    
    @property
    def sheet_index(self) -> int:
        ...
    
    @sheet_index.setter
    def sheet_index(self, value : int):
        ...
    
    ...

class ChartDimensionObject:
    '''internal use'''
    
    @property
    def width(self) -> float:
        '''width'''
        ...
    
    @width.setter
    def width(self, value : float):
        '''width'''
        ...
    
    @property
    def height(self) -> float:
        '''height'''
        ...
    
    @height.setter
    def height(self, value : float):
        '''height'''
        ...
    
    @property
    def x(self) -> float:
        '''x'''
        ...
    
    @x.setter
    def x(self, value : float):
        '''x'''
        ...
    
    @property
    def y(self) -> float:
        '''y'''
        ...
    
    @y.setter
    def y(self, value : float):
        '''y'''
        ...
    
    @property
    def upper_left_column(self) -> int:
        ...
    
    @upper_left_column.setter
    def upper_left_column(self, value : int):
        ...
    
    @property
    def upper_left_row(self) -> int:
        ...
    
    @upper_left_row.setter
    def upper_left_row(self, value : int):
        ...
    
    ...

class ColorStop:
    '''internal use'''
    
    @property
    def offset(self) -> float:
        '''offset'''
        ...
    
    @offset.setter
    def offset(self, value : float):
        '''offset'''
        ...
    
    @property
    def color(self) -> str:
        '''color'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''color'''
        ...
    
    ...

class DataLabelsObject:
    '''internal use'''
    
    @property
    def show_value(self) -> bool:
        ...
    
    @show_value.setter
    def show_value(self, value : bool):
        ...
    
    @property
    def position(self) -> str:
        '''position'''
        ...
    
    @position.setter
    def position(self, value : str):
        '''position'''
        ...
    
    ...

class FontObject:
    '''internal use'''
    
    @property
    def color(self) -> str:
        '''color'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''color'''
        ...
    
    @property
    def is_italic(self) -> bool:
        ...
    
    @is_italic.setter
    def is_italic(self, value : bool):
        ...
    
    @property
    def is_bold(self) -> bool:
        ...
    
    @is_bold.setter
    def is_bold(self, value : bool):
        ...
    
    @property
    def name(self) -> str:
        '''name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''name'''
        ...
    
    @property
    def size(self) -> float:
        '''size'''
        ...
    
    @size.setter
    def size(self, value : float):
        '''size'''
        ...
    
    ...

class GradientBackground(BackgroundColorObject):
    '''internal use'''
    
    @property
    def type(self) -> str:
        '''type'''
        ...
    
    @type.setter
    def type(self, value : str):
        '''type'''
        ...
    
    @property
    def color_stops(self) -> List[aspose.cellsgridjs.chart.ColorStop]:
        ...
    
    @color_stops.setter
    def color_stops(self, value : List[aspose.cellsgridjs.chart.ColorStop]):
        ...
    
    @property
    def x(self) -> Optional[float]:
        '''x'''
        ...
    
    @x.setter
    def x(self, value : Optional[float]):
        '''x'''
        ...
    
    @property
    def y(self) -> Optional[float]:
        '''y'''
        ...
    
    @y.setter
    def y(self, value : Optional[float]):
        '''y'''
        ...
    
    @property
    def x2(self) -> Optional[float]:
        '''x2'''
        ...
    
    @x2.setter
    def x2(self, value : Optional[float]):
        '''x2'''
        ...
    
    @property
    def y2(self) -> Optional[float]:
        '''y2'''
        ...
    
    @y2.setter
    def y2(self, value : Optional[float]):
        '''y2'''
        ...
    
    @property
    def r(self) -> Optional[float]:
        '''r'''
        ...
    
    @r.setter
    def r(self, value : Optional[float]):
        '''r'''
        ...
    
    ...

class GridChartResponseType:
    '''internal use'''
    
    @property
    def title(self) -> aspose.cellsgridjs.chart.TitleObject:
        '''title'''
        ...
    
    @title.setter
    def title(self, value : aspose.cellsgridjs.chart.TitleObject):
        '''title'''
        ...
    
    @property
    def category_axis(self) -> aspose.cellsgridjs.chart.AxisObject:
        ...
    
    @category_axis.setter
    def category_axis(self, value : aspose.cellsgridjs.chart.AxisObject):
        ...
    
    @property
    def value_axis(self) -> aspose.cellsgridjs.chart.AxisObject:
        ...
    
    @value_axis.setter
    def value_axis(self, value : aspose.cellsgridjs.chart.AxisObject):
        ...
    
    @property
    def legend(self) -> aspose.cellsgridjs.chart.LegendObject:
        '''legend'''
        ...
    
    @legend.setter
    def legend(self, value : aspose.cellsgridjs.chart.LegendObject):
        '''legend'''
        ...
    
    @property
    def n_series(self) -> List[aspose.cellsgridjs.chart.NSeriesDetails]:
        ...
    
    @n_series.setter
    def n_series(self, value : List[aspose.cellsgridjs.chart.NSeriesDetails]):
        ...
    
    @property
    def id(self) -> int:
        '''id'''
        ...
    
    @id.setter
    def id(self, value : int):
        '''id'''
        ...
    
    @property
    def background_color(self) -> aspose.cellsgridjs.chart.BackgroundColorObject:
        ...
    
    @background_color.setter
    def background_color(self, value : aspose.cellsgridjs.chart.BackgroundColorObject):
        ...
    
    @property
    def name(self) -> str:
        '''name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''name'''
        ...
    
    @property
    def type(self) -> str:
        '''type'''
        ...
    
    @type.setter
    def type(self, value : str):
        '''type'''
        ...
    
    @property
    def chart_object(self) -> aspose.cellsgridjs.chart.ChartDimensionObject:
        ...
    
    @chart_object.setter
    def chart_object(self, value : aspose.cellsgridjs.chart.ChartDimensionObject):
        ...
    
    @property
    def worksheet(self) -> aspose.cellsgridjs.chart.WorksheetObject:
        '''worksheet'''
        ...
    
    @worksheet.setter
    def worksheet(self, value : aspose.cellsgridjs.chart.WorksheetObject):
        '''worksheet'''
        ...
    
    ...

class LegendObject:
    '''internal use'''
    
    @property
    def show_legend(self) -> bool:
        ...
    
    @show_legend.setter
    def show_legend(self, value : bool):
        ...
    
    @property
    def position(self) -> str:
        '''position'''
        ...
    
    @position.setter
    def position(self, value : str):
        '''position'''
        ...
    
    ...

class NSeriesDetails:
    '''internal use'''
    
    @property
    def data(self) -> List[aspose.cellsgridjs.chart.CellData]:
        '''data'''
        ...
    
    @data.setter
    def data(self, value : List[aspose.cellsgridjs.chart.CellData]):
        '''data'''
        ...
    
    @property
    def values(self) -> str:
        '''values'''
        ...
    
    @values.setter
    def values(self, value : str):
        '''values'''
        ...
    
    @property
    def name(self) -> aspose.cellsgridjs.chart.CellData:
        '''name'''
        ...
    
    @name.setter
    def name(self, value : aspose.cellsgridjs.chart.CellData):
        '''name'''
        ...
    
    @property
    def area(self) -> aspose.cellsgridjs.chart.AreaObject:
        '''area'''
        ...
    
    @area.setter
    def area(self, value : aspose.cellsgridjs.chart.AreaObject):
        '''area'''
        ...
    
    @property
    def data_labels(self) -> aspose.cellsgridjs.chart.DataLabelsObject:
        ...
    
    @data_labels.setter
    def data_labels(self, value : aspose.cellsgridjs.chart.DataLabelsObject):
        ...
    
    @property
    def is_filtered(self) -> bool:
        ...
    
    @is_filtered.setter
    def is_filtered(self, value : bool):
        ...
    
    ...

class SolidBackground(BackgroundColorObject):
    '''internal use'''
    
    @property
    def color(self) -> str:
        '''color'''
        ...
    
    @color.setter
    def color(self, value : str):
        '''color'''
        ...
    
    ...

class TitleObject:
    '''internal use'''
    
    @property
    def text(self) -> str:
        '''text'''
        ...
    
    @text.setter
    def text(self, value : str):
        '''text'''
        ...
    
    @property
    def is_visible(self) -> bool:
        ...
    
    @is_visible.setter
    def is_visible(self, value : bool):
        ...
    
    @property
    def text_horizontal_alignment(self) -> str:
        ...
    
    @text_horizontal_alignment.setter
    def text_horizontal_alignment(self, value : str):
        ...
    
    @property
    def text_vertical_alignment(self) -> str:
        ...
    
    @text_vertical_alignment.setter
    def text_vertical_alignment(self, value : str):
        ...
    
    @property
    def font(self) -> aspose.cellsgridjs.chart.FontObject:
        '''font'''
        ...
    
    @font.setter
    def font(self, value : aspose.cellsgridjs.chart.FontObject):
        '''font'''
        ...
    
    @property
    def border(self) -> aspose.cellsgridjs.chart.BorderObject:
        '''border'''
        ...
    
    @border.setter
    def border(self, value : aspose.cellsgridjs.chart.BorderObject):
        '''border'''
        ...
    
    @property
    def x(self) -> float:
        '''x'''
        ...
    
    @x.setter
    def x(self, value : float):
        '''x'''
        ...
    
    @property
    def y(self) -> float:
        '''y'''
        ...
    
    @y.setter
    def y(self, value : float):
        '''y'''
        ...
    
    ...

class WorksheetObject:
    '''internal use'''
    
    @property
    def name(self) -> str:
        '''name'''
        ...
    
    @name.setter
    def name(self, value : str):
        '''name'''
        ...
    
    ...

