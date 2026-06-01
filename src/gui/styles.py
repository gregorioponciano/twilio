WHATSAPP_GREEN = "#075E54"
WHATSAPP_GREEN_DARK = "#054D44"
WHATSAPP_TEAL = "#128C7E"
WHATSAPP_LIGHT_GREEN = "#25D366"
WHATSAPP_BG = "#ECE5DD"
WHATSAPP_DARK_BG = "#111B21"
WHATSAPP_DARK_CHAT_BG = "#0B141A"
WHATSAPP_DARK_SIDEBAR = "#111B21"
WHATSAPP_DARK_HEADER = "#202C33"
WHATSAPP_DARK_INPUT = "#2A3942"
WHATSAPP_DARK_BUBBLE_SENT = "#005C4B"
WHATSAPP_DARK_BUBBLE_RECEIVED = "#1F2C33"
WHATSAPP_DARK_TEXT = "#E9EDEF"
WHATSAPP_DARK_TEXT_SECONDARY = "#8696A0"
WHATSAPP_DARK_HOVER = "#2A3942"
WHATSAPP_DARK_DIVIDER = "#313D45"
WHATSAPP_DARK_ACTIVE = "#2A3942"
WHATSAPP_DARK_HEADER_BORDER = "#182229"

COR_SUCCESS = "#25D366"
COR_ERROR = "#EF4444"
COR_WARNING = "#F59E0B"
COR_INFO = "#3B82F6"
COR_SENT = "#53BDEB"
COR_DELIVERED = "#25D366"
COR_FAILED = "#EF4444"

FONT_FAMILY = "Segoe UI"
FONT_SIZE_XS = 10
FONT_SIZE_SMALL = 11
FONT_SIZE_NORMAL = 13
FONT_SIZE_LARGE = 15
FONT_SIZE_XL = 17
FONT_SIZE_TITLE = 19
FONT_SIZE_AVATAR = 13

AVATAR_SIZE = 48
AVATAR_SIZE_SMALL = 36
BORDER_RADIUS = 8
BORDER_RADIUS_SM = 6
BORDER_RADIUS_BTN = 18
BORDER_RADIUS_BUBBLE = 6
MAX_SMS_CHARS = 160
CONTACT_ITEM_HEIGHT = 70
HEADER_HEIGHT = 56
INPUT_HEIGHT = 62

TOAST_DURATION = 3000


import platform

def fix_mousewheel(scroll_frame, delay_ms=100):
    def _on_mousewheel(e):
        try:
            canvas = scroll_frame._parent_canvas
        except AttributeError:
            return
        if platform.system() == "Linux":
            if e.num == 4:
                canvas.yview_scroll(-3, "units")
            elif e.num == 5:
                canvas.yview_scroll(3, "units")
        else:
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

    def _bind(widget):
        widget.bind("<MouseWheel>", _on_mousewheel, add="+")
        widget.bind("<Button-4>", _on_mousewheel, add="+")
        widget.bind("<Button-5>", _on_mousewheel, add="+")
        for child in widget.winfo_children():
            _bind(child)

    scroll_frame.after(delay_ms, lambda: _bind(scroll_frame))

