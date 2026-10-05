import re

def normalize(s): return re.sub(r"[^a-z0-9]+"," ",(s or "").lower()).strip()
def compare_requirement(requirement, offered):
    if not offered: return "Not Checked"
    r,o=normalize(requirement),normalize(offered)
    if r and r in o: return "Compliant"
    return "Review"
def build_compliance(requirements, offered_text=""):
    return [{"requirement":x.requirement,"offered":offered_text or None,"status":compare_requirement(x.requirement,offered_text),"source_page":x.page,"notes":"Manual verification recommended."} for x in requirements]
