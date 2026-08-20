TRANSITION_COLORS = {
	"LINK": "#5dade2",
	"TYPED": "#f4d03f",
	"AUTO_BOOKMARK": "#58d68d",
	"FORM_SUBMIT": "#af7ac5",
	"GENERATED": "#ec7063",
	"KEYWORD": "#48c9b0",
	"KEYWORD_GENERATED": "#45b39d",
	"RELOAD": "#f5b041",
	"AUTO_TOPLEVEL": "#bb8fce",
	"AUTO_SUBFRAME": "#7f8c8d",
	"MANUAL_SUBFRAME": "#95a5a6",
	"UNKNOWN": "#555878",
}

def transition_color(transition_core):
	return TRANSITION_COLORS.get(
		str(transition_core).upper(),
		TRANSITION_COLORS["UNKNOWN"],
	)

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
	"UNKNOWN": "unknown"
}

def transition_label(transition_core):
	return TRANSITION_LABELS.get(str(transition_core).upper(), str(transition_core))


EDGE_STYLE = {
	"redirect": dict(color="#ff8a3d", width=2.5, dash="dash"),
	"back_forward": dict(color="#c86bfa", width=2, dash="longdash"),
	"tab": dict(color="#555878", width=1.3, dash="dot"),
}


NORMAL_BORDER_WIDTH = 2
ADDRESS_BAR_BORDER_WIDTH = 3
