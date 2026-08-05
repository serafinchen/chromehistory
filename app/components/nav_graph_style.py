import plotly.colors as pcolors


LANE_PALETTE = (
	pcolors.qualitative.Set3
	+ pcolors.qualitative.Pastel
	+ pcolors.qualitative.Set2
)

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
	"LINK": "Link clicked",
	"TYPED": "URL typed",
	"AUTO_BOOKMARK": "Bookmark opened",
	"FORM_SUBMIT": "Form submitted",
	"GENERATED": "Search suggestion",
	"KEYWORD": "Search engine keyword",
	"KEYWORD_GENERATED": "Search engine keyword",
	"RELOAD": "Page reloaded",
	"AUTO_TOPLEVEL": "New tab / homepage",
	"AUTO_SUBFRAME": "Subframe (automatic)",
	"MANUAL_SUBFRAME": "Subframe (manual)",
}


def transition_symbol(transition_core):
	return TRANSITION_SYMBOLS.get(str(transition_core).upper(), DEFAULT_SYMBOL)


def transition_label(transition_core):
	return TRANSITION_LABELS.get(str(transition_core).upper(), str(transition_core))


EDGE_STYLE = {
	"redirect": dict(color="#ff8a3d", width=2.5, dash="dash"),
	"back_forward": dict(color="#c86bfa", width=2, dash="longdash"),
	"tab": dict(color="#555878", width=1.3, dash="dot"),
}

EDGE_LABELS = {
	"lane": "Normal navigation",
	"redirect": "Automatic redirect (client/server)",
	"back_forward": "Back/Forward button used",
	"tab": "Opened in new tab/window",
}


ERROR_BORDER_COLOR = "#ff4d4d"
ERROR_BORDER_WIDTH = 3
NORMAL_BORDER_WIDTH = 2
ADDRESS_BAR_BORDER_WIDTH = 3

ERROR_LABEL = "Error response (HTTP ≥ 400)"
ADDRESS_BAR_LABEL = "Triggered manually via address bar"

CACHED_SYMBOL_SUFFIX = "-open"

CACHED_LABEL = "Loaded from cache (outline symbol only)"
FRESH_LABEL = "Loaded fresh from server (filled symbol)"
