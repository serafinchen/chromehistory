"""
Gemeinsame Styling-Konstanten für den Navigations-Graphen (nav_graph.py)
und die dazugehörige Dash-Legende (nav_graph_legend.py).

Alles, was visuell im Graphen codiert wird, ist hier zentral definiert,
damit Graph und Legende nie auseinanderlaufen.
"""

import plotly.colors as pcolors

# ---------------------------------------------------------------------------
# Lane-Farben (eine Farbe pro fortlaufender Browsing-Spur)
# ---------------------------------------------------------------------------

LANE_PALETTE = (
	pcolors.qualitative.Set3
	+ pcolors.qualitative.Pastel
	+ pcolors.qualitative.Set2
)


def lane_color(lane_id):
	return LANE_PALETTE[lane_id % len(LANE_PALETTE)]


# ---------------------------------------------------------------------------
# transition_core -> "Wie bin ich hierhergekommen?"
# (entspricht HistoryVisit.transition_core aus app/history.py)
# ---------------------------------------------------------------------------

TRANSITION_SYMBOLS = {
	"LINK": "circle",
	"TYPED": "diamond",
	"AUTO_BOOKMARK": "star",
	"FORM_SUBMIT": "square",
	"GENERATED": "triangle-up",
	"KEYWORD": "pentagon",
	"KEYWORD_GENERATED": "pentagon",
	"RELOAD": "hexagon",
	"AUTO_TOPLEVEL": "hourglass",
	"AUTO_SUBFRAME": "circle-open",
	"MANUAL_SUBFRAME": "circle-open",
}

DEFAULT_SYMBOL = "circle"

TRANSITION_LABELS = {
	"LINK": "Link angeklickt",
	"TYPED": "URL eingetippt",
	"AUTO_BOOKMARK": "Lesezeichen geöffnet",
	"FORM_SUBMIT": "Formular abgeschickt",
	"GENERATED": "Suchvorschlag (Omnibox)",
	"KEYWORD": "Suchmaschinen-Keyword",
	"KEYWORD_GENERATED": "Suchmaschinen-Keyword",
	"RELOAD": "Seite neu geladen",
	"AUTO_TOPLEVEL": "Neuer Tab / Startseite",
	"AUTO_SUBFRAME": "Subframe (automatisch)",
	"MANUAL_SUBFRAME": "Subframe (manuell)",
}


def transition_symbol(transition_core):
	return TRANSITION_SYMBOLS.get(str(transition_core).upper(), DEFAULT_SYMBOL)


def transition_label(transition_core):
	return TRANSITION_LABELS.get(str(transition_core).upper(), str(transition_core))


# ---------------------------------------------------------------------------
# Kanten: Beziehung zwischen zwei Visits
# ---------------------------------------------------------------------------

EDGE_STYLE = {
	# normale Navigation innerhalb einer Spur -> siehe LANE_PALETTE (dynamisch)
	"redirect": dict(color="#ff8a3d", width=2.5, dash="dash"),
	"back_forward": dict(color="#c86bfa", width=2, dash="longdash"),
	"tab": dict(color="#555878", width=1.3, dash="dot"),
}

EDGE_LABELS = {
	"lane": "Navigation (gleiche Spur, Farbe = Spur)",
	"redirect": "Automatischer Redirect (Client/Server)",
	"back_forward": "Zurück/Vorwärts-Button benutzt",
	"tab": "In neuem Tab/Fenster geöffnet",
}

# ---------------------------------------------------------------------------
# Knoten-Rand: Fehler / manuelle Adressleisten-Eingabe
# ---------------------------------------------------------------------------

ERROR_BORDER_COLOR = "#ff4d4d"
ERROR_BORDER_WIDTH = 3
NORMAL_BORDER_WIDTH = 2
ADDRESS_BAR_BORDER_WIDTH = 3

ERROR_LABEL = "Fehlerhafte Antwort (HTTP ≥ 400)"
ADDRESS_BAR_LABEL = "Bewusst über Adressleiste ausgelöst"

# ---------------------------------------------------------------------------
# Cache-Status: aus dem Netzwerk geladen vs. aus dem Chrome-Cache bedient
# ---------------------------------------------------------------------------

CACHED_SYMBOL_SUFFIX = "-open"

CACHED_LABEL = "Aus dem Cache geladen (Symbol nur als Umriss)"
FRESH_LABEL = "Frisch vom Server geladen (Symbol gefüllt)"