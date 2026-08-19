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
	"LINK": "Link clicked (LINK)",
	"TYPED": "URL typed (TYPED)",
	"AUTO_BOOKMARK": "Bookmark opened (AUTO_BOOKMARK)",
	"FORM_SUBMIT": "Form submitted (FORM_SUBMIT)",
	"GENERATED": "Search suggestion (GENERATED)",
	"KEYWORD": "Search engine keyword (KEYWORD)",
	"KEYWORD_GENERATED": "Search engine keyword (KEYWORD_GENERATED)",
	"RELOAD": "Page reloaded (RELOAD)",
	"AUTO_TOPLEVEL": "New tab / homepage (AUTO_TOPLEVEL)",
	"AUTO_SUBFRAME": "Subframe (automatic) (AUTO_SUBFRAME)",
	"MANUAL_SUBFRAME": "Subframe (manual) (MANUAL_SUBFRAME)",
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


NORMAL_BORDER_WIDTH = 2
ADDRESS_BAR_BORDER_WIDTH = 3

ADDRESS_BAR_LABEL = "Triggered manually via address bar"
