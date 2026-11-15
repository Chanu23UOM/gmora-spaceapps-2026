"""Static guards for accessibility properties of the buildless dashboard.

These assert the source declarations behind fixes that were verified in a real
browser (axe-core plus measured target sizes at a 390px layout viewport). They
are regression guards, not a substitute for a browser or screen-reader pass.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / 'web_app' / 'style.css').read_text()
HTML = (ROOT / 'web_app' / 'index.html').read_text()


def media_block(max_width):
    """Body of the @media (max-width: Npx) block, brace-matched."""
    start = CSS.index(f'@media (max-width: {max_width}px)')
    depth, i = 0, CSS.index('{', start)
    begin = i + 1
    while i < len(CSS):
        if CSS[i] == '{':
            depth += 1
        elif CSS[i] == '}':
            depth -= 1
            if depth == 0:
                return CSS[begin:i]
        i += 1
    raise AssertionError('unterminated media block')


def rule(block, selector):
    match = re.search(r'(?:^|\})\s*' + re.escape(selector) + r'\s*(?:,[^{]*)?\{([^}]*)\}', block, re.S)
    if not match:
        match = re.search(r'([^{}]*\b' + re.escape(selector.lstrip('.')) + r'\b[^{}]*)\{([^}]*)\}', block, re.S)
        return match.group(2) if match else ''
    return match.group(1)


class TouchTargetTests(unittest.TestCase):
    """Calendar controls must keep a 24px minimum target on small screens.

    A 31-column day grid cannot give each day 24px at phone width, so the
    calendar scrolls horizontally instead of shrinking tiles to ~5px.
    """

    def setUp(self):
        self.mobile = media_block(650)

    def test_day_tiles_keep_a_24px_target(self):
        self.assertIn('height: 24px', rule(self.mobile, '.day-tile'))

    def test_day_grid_columns_are_24px(self):
        self.assertIn('repeat(31, 24px)', rule(self.mobile, '.month-days'))

    def test_month_buttons_keep_a_24px_target(self):
        self.assertIn('min-height: 24px', rule(self.mobile, '.month-btn'))

    def test_calendar_scrolls_instead_of_overflowing_the_page(self):
        self.assertIn('overflow-x: auto', rule(self.mobile, '.calendar-list'))
        self.assertIn('min-width: max-content', rule(self.mobile, '.calendar-row'))

    def test_disclosure_summaries_meet_the_minimum_target(self):
        # The bare `summary {` rule, not the grouped `summary:focus-visible` one.
        body = re.search(r'(?:^|\n)summary\s*\{([^}]*)\}', CSS, re.S)
        self.assertIsNotNone(body, 'no bare summary rule found')
        self.assertIn('min-height: 24px', body.group(1))


class MapSemanticsTests(unittest.TestCase):
    def test_map_is_a_group_so_its_cells_stay_reachable(self):
        """role="img" is a leaf for assistive technology; the map holds
        focusable cells, so it must not be an image (axe nested-interactive)."""
        svg = re.search(r'<svg[^>]*id="map".*?</svg>', HTML, re.S).group(0)
        self.assertIn('role="group"', svg)
        self.assertNotIn('role="img"', svg)

    def test_pure_chart_svgs_remain_images(self):
        for svg_id in ('activity-chart', 'forecast-chart'):
            svg = re.search(r'<svg[^>]*id="' + svg_id + r'".*?</svg>', HTML, re.S).group(0)
            self.assertIn('role="img"', svg)


if __name__ == '__main__':
    unittest.main()
