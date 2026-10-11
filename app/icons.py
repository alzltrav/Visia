from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

_STROKE = 'fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round"'


def _svg(body, color, width=1.8, fill="none"):
    attrs = _STROKE.format(c=color, w=width).replace('fill="none"', f'fill="{fill}"')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" {attrs}>{body}</svg>'


def home(color, filled=False):
    return _svg('<path d="M3 9.5L12 3l9 6.5V20a1 1 0 01-1 1H4a1 1 0 01-1-1V9.5z"/><path d="M9 21V12h6v9"/>',
                color, fill=color if filled else "none")


def transactions(color):
    return _svg('<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>', color)


def settings(color):
    return _svg(
        '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0'
        'l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4'
        'a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 '
        '01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06'
        'A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 '
        '001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 '
        '01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/>', color)


def email(color="#555552"):
    return _svg('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="M2 8l10 6 10-6"/>', color)


def lock(color="#555552"):
    return _svg('<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/>', color)


def trash(color="#B83232"):
    return _svg('<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>'
                '<path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 011-1h4a1 1 0 011 1v2"/>', color)


def logout(color="#FFFFFF"):
    return _svg('<path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/>'
                '<line x1="21" y1="12" x2="9" y2="12"/>', color)


def chevron_right(color="#BBBBBB"):
    return _svg('<polyline points="9 18 15 12 9 6"/>', color, width=2)


ILLUSTRATION = """<svg xmlns="http://www.w3.org/2000/svg" width="300" height="230" viewBox="0 0 300 230" fill="none">
<rect x="18" y="70" width="190" height="115" rx="14" fill="#D8D8D4" fill-opacity="0.55"/>
<rect x="36" y="50" width="190" height="115" rx="14" fill="#C8C8C4" fill-opacity="0.65"/>
<rect x="54" y="28" width="190" height="115" rx="14" fill="#111110"/>
<rect x="74" y="52" width="30" height="22" rx="4" fill="#888884" fill-opacity="0.8"/>
<line x1="74" y1="63" x2="104" y2="63" stroke="#6A6A66" stroke-width="1"/>
<line x1="89" y1="52" x2="89" y2="74" stroke="#6A6A66" stroke-width="1"/>
<path d="M210 55 Q218 63 210 71" stroke="#666662" stroke-width="2" fill="none" stroke-linecap="round"/>
<path d="M215 50 Q227 63 215 76" stroke="#555552" stroke-width="2" fill="none" stroke-linecap="round"/>
<circle cx="74" cy="108" r="4.5" fill="#444440"/><circle cx="89" cy="108" r="4.5" fill="#444440"/>
<circle cx="104" cy="108" r="4.5" fill="#444440"/><circle cx="119" cy="108" r="4.5" fill="#444440"/>
<circle cx="140" cy="108" r="4.5" fill="#555552"/><circle cx="155" cy="108" r="4.5" fill="#555552"/>
<circle cx="170" cy="108" r="4.5" fill="#555552"/><circle cx="185" cy="108" r="4.5" fill="#555552"/>
<text x="74" y="133" font-family="DM Mono" font-size="8" fill="#666662" letter-spacing="0.5">VALID THRU</text>
<text x="74" y="144" font-family="DM Mono" font-size="11" font-weight="500" fill="#999995">09/29</text>
<text x="218" y="130" font-family="Inter" font-size="22" font-weight="600" fill="#FFFFFF">₱</text>
<rect x="24" y="175" width="28" height="44" rx="5" fill="#D4D4D0"/>
<rect x="60" y="158" width="28" height="61" rx="5" fill="#C4C4C0"/>
<rect x="96" y="166" width="28" height="53" rx="5" fill="#B4B4B0" fill-opacity="0.9"/>
<rect x="132" y="148" width="28" height="71" rx="5" fill="#111110" fill-opacity="0.2"/>
<rect x="168" y="136" width="28" height="83" rx="5" fill="#111110" fill-opacity="0.35"/>
<rect x="204" y="118" width="28" height="101" rx="5" fill="#111110" fill-opacity="0.6"/>
<rect x="240" y="104" width="28" height="115" rx="5" fill="#111110" fill-opacity="0.85"/>
<polyline points="38,192 74,173 110,181 146,163 182,151 218,133 254,119" stroke="#111110" stroke-opacity="0.5" stroke-width="2.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
<circle cx="254" cy="119" r="5" fill="#111110" fill-opacity="0.7"/>
</svg>"""


def pixmap(svg, w, h=None):
    h = h or w
    dpr = QApplication.instance().devicePixelRatio() if QApplication.instance() else 1.0
    dpr = max(dpr, 2.0)
    pm = QPixmap(int(w * dpr), int(h * dpr))
    pm.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(p, QRectF(0, 0, w * dpr, h * dpr))
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


def icon(svg, size=18):
    return QIcon(pixmap(svg, size))
