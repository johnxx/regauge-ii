from lib import gauge_face
import lvgl
import fs_driver as fs

_WIDTH = 360
_HEIGHT = 360


class Detailed(gauge_face.GaugeFace):
    def __init__(self, name, options, resources):
        super().__init__(name, options, resources)
        stream_name = list(self.streams.keys())[0]
        stream = self.streams[stream_name]
        self._screen = lvgl.screen_active()

        # Setup
        self._screen.set_style_bg_color(lvgl.color_hex(0x000000), 0)
        big_font = lvgl.binfont_create("S:/NotoSansDisplay-Regular-96.bin")

        self._big_label = lvgl.label(self._screen)
        self._big_label.set_style_text_font(big_font, 0)
        self._big_label.set_style_text_color(lvgl.color_hex3(0xFFF), 0)
        self._big_label.set_text(str(''))
        self._big_label.align(lvgl.ALIGN.CENTER, 0, -90)


        self._gauge = lvgl.arc(self._screen)
        self._gauge.set_size(_WIDTH - 5, _HEIGHT - 5)
        self._gauge.set_range(stream.stream_spec.min_val, stream.stream_spec.max_val)
        gap_angle = 120
        self._gauge.set_rotation(90 + int(gap_angle / 2))
        self._gauge.set_bg_angles(0, 360 - gap_angle)
        self._gauge.remove_style(None, lvgl.PART.KNOB)
        # gauge.set_style_arc_color(lvgl.color_hex(0x900020), lvgl.PART.INDICATOR)
        self._gauge.set_style_arc_width(10, 0)
        self._gauge.set_style_arc_color(lvgl.color_hex(0x101010), 0)
        self._gauge.set_value(0)
        self._gauge.center()


        self._chart = lvgl.chart(self._screen)
        self._chart.set_size(260, 160)
        self._chart.align(lvgl.ALIGN.CENTER, 0, 35)
        self._chart.set_range(lvgl.chart.AXIS.PRIMARY_Y, stream.stream_spec.min_val, stream.stream_spec.max_val)

        self._chart.set_style_size(0, 0, lvgl.PART.INDICATOR)
        self._chart.set_style_bg_color(lvgl.color_hex(0x010101), lvgl.PART.MAIN | lvgl.STATE.DEFAULT)
        self._chart.set_style_line_color(lvgl.color_hex(0x101010), lvgl.PART.MAIN | lvgl.STATE.DEFAULT)
        self._chart.set_style_border_color(lvgl.color_hex(0x101010), lvgl.PART.MAIN | lvgl.STATE.DEFAULT)

        self._chart_series = self._chart.add_series(lvgl.color_hex(0x2196f3), lvgl.chart.AXIS.PRIMARY_Y)

        # self._chart.set_point_count(stream.upto_vals - 1)
        self._chart.set_point_count(len(stream.values))
        self._chart.set_ext_y_array(self._chart_series, stream.values)
        self._chart.refresh()


    def config_updated(self, message):
        pass
    
    async def update(self):
        stream_name = list(self.streams.keys())[0]
        stream = self.streams[stream_name]

        print("Displaying: {}".format(stream.value))
        self._gauge.set_value(stream.value)
        self._big_label.set_text(str(stream.value))
        self._chart.set_point_count(len(stream.values))
        print("Count: {}".format(len(stream.values)))
        self._chart.set_ext_y_array(self._chart_series, stream.values)
        self._chart.refresh()