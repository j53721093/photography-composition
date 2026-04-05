COMPOSITION_CATEGORIES = {
    "三分構圖 (Rule of Thirds Composition)": "rule_of_thirds",
    "中心構圖 (Centered Composition)": "centered",
    "留白構圖 (Negative Space Composition)": "negative_space",
    "對稱構圖 (Symmetry Composition)": "symmetry",
    "對角線構圖 (Diagonal Composition)": "diagonal",
    "框架構圖 (Framing Composition)": "framing",
    "引導線構圖 (Leading Lines Composition)": "leading_lines",
    "黃金螺旋構圖 (Golden Ratio Composition)": "golden_ratio",
    "黃金三角構圖 (Golden Triangle Composition)": "golden_triangle",
    "其他 (Others)": "others"
}

def get_tag_name(display_name):
    return COMPOSITION_CATEGORIES.get(display_name, "others")

def get_display_names():
    return list(COMPOSITION_CATEGORIES.keys())
