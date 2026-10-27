"""Visual and copy defaults for gift-card tiles (palette, pattern, discount hints)."""

BRAND_CONFIG = {
    "EGVGBPVRC001": {
        "display": "PVR INOX",
        "discount": 12.0,
        "pal": ("#2442E6", "#6440E0"),
        "pt": "p-rings",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBDEGCS001": {
        "display": "Domino's",
        "discount": 4.5,
        "pal": ("#FF9F1C", "#F2542D"),
        "pt": "p-stars",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBMYNC001": {
        "display": "Myntra",
        "discount": 0.75,
        "pal": ("#7C3FD6", "#30177D"),
        "pt": "p-waves",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGVGBSTB001": {
        "display": "Starbucks",
        "discount": 3.75,
        "pal": ("#FF9F1C", "#F2542D"),
        "pt": "p-grid",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBUBER001": {
        "display": "Uber",
        "discount": 1.5,
        "pal": ("#2FA8FF", "#2350DB"),
        "pt": "p-lines",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGCGBCROM001": {
        "display": "Croma",
        "discount": 0.5,
        "pal": ("#2442E6", "#6440E0"),
        "pt": "p-grid",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBLVSS001": {
        "display": "Levi's",
        "discount": 5.25,
        "pal": ("#C2337A", "#541750"),
        "pt": "p-stars",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBSCLPL002": {
        "display": "Lenskart",
        "discount": 5.25,
        "pal": ("#7C3FD6", "#30177D"),
        "pt": "p-rings",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBCINE001": {
        "display": "Cinepolis",
        "discount": 16.5,
        "pal": ("#7C3FD6", "#30177D"),
        "pt": "p-grid",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBDCN003": {
        "display": "Decathlon",
        "discount": 2.0,
        "pal": ("#3A4160", "#14172F"),
        "pt": "p-rings",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBCCD001": {
        "display": "Cafe Coffee Day",
        "discount": 6.75,
        "pal": ("#E3A866", "#B4602F"),
        "pt": "p-stars",
        "use": "In-store",
        "use_icon": "i-store",
    },
    "EGVGBKFC001": {
        "display": "KFC",
        "discount": 2.75,
        "pal": ("#E3A866", "#B4602F"),
        "pt": "p-grid",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBPZH001": {
        "display": "Pizza Hut",
        "discount": 4.5,
        "pal": ("#E3A866", "#B4602F"),
        "pt": "p-grid",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBSUBW001": {
        "display": "Subway",
        "discount": 5.5,
        "pal": ("#FF9F1C", "#F2542D"),
        "pt": "p-rings",
        "use": "In-store",
        "use_icon": "i-store",
    },
    "EGCGBWS002": {
        "display": "Westside",
        "discount": 5.25,
        "pal": ("#7C3FD6", "#30177D"),
        "pt": "p-waves",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
    "EGCGBAJIORRL001": {
        "display": "AJIO",
        "discount": 3.25,
        "pal": ("#7C3FD6", "#30177D"),
        "pt": "p-waves",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGCGBGRDM001": {
        "display": "Giva Silver Coin",
        "discount": 0.75,
        "pal": ("#0A7368", "#17BF91"),
        "pt": "p-grid",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGCGBZOMA001": {
        "display": "Zomato",
        "discount": 2.5,
        "pal": ("#FF7457", "#C9302B"),
        "pt": "p-rings",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGCGBBLINK002": {
        "display": "Blinkit",
        "discount": 2.5,
        "pal": ("#17BF91", "#0A7368"),
        "pt": "p-lines",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGCGBBBS001": {
        "display": "Bigbasket",
        "discount": 1.0,
        "pal": ("#7FC93A", "#1F8F57"),
        "pt": "p-zig",
        "use": "Online",
        "use_icon": "i-globe",
    },
    "EGVGBAPOPHA001": {
        "display": "Apollo Pharmacy",
        "discount": 5.5,
        "pal": ("#C2337A", "#541750"),
        "pt": "p-grid",
        "use": "Online & in-store",
        "use_icon": "i-store",
    },
}


def brand_size_class(display_name: str) -> str:
    length = len(display_name or "")
    if length > 30:
        return "x3"
    if length > 22:
        return "xxl"
    if length > 14:
        return "xl"
    if length > 9:
        return "long"
    return ""
