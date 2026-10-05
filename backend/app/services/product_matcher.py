CATALOG=[
{"model":"Lenovo ThinkBook 16 G8 IAL","type":"Laptop","keywords":["thinkbook","16","ultra 5","225u","16gb","512gb","71wh"]},
{"model":"Lenovo ThinkCentre M90q Gen 5","type":"Desktop","keywords":["m90q","tiny","q870","16gb","512gb"]},
{"model":"Lenovo ThinkCentre M70t Gen 6","type":"Desktop","keywords":["m70t","tower","ultra 5","225","16gb","512gb"]},
{"model":"Lenovo ThinkCentre Neo 50t Gen 5","type":"Desktop","keywords":["neo 50t","tower","i5","14400","16gb","1tb"]},
{"model":"HP EliteBook 6 G1i 16","type":"Laptop","keywords":["elitebook","16","ultra 5","225u"]},
{"model":"HP ProDesk 4 Tower G1i","type":"Desktop","keywords":["prodesk","tower","ultra 7","265","q870"]}]
def match_products(text,limit=6):
    low=(text or "").lower(); scored=[]
    for x in CATALOG:
        hits=[k for k in x["keywords"] if k.lower() in low]; score=len(hits)/len(x["keywords"])
        if score: scored.append({**x,"score":round(score,2),"matched_keywords":hits})
    return sorted(scored,key=lambda x:x["score"],reverse=True)[:limit]
