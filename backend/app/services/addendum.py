import difflib
def compare_pages(old_pages,new_pages):
    old={p['page']:p['text'] for p in old_pages}; new={p['page']:p['text'] for p in new_pages}; out=[]
    for page in sorted(set(old)|set(new)):
        a,b=old.get(page,''),new.get(page,'')
        if a.strip()!=b.strip(): out.append({'page':page,'similarity':round(difflib.SequenceMatcher(None,a,b).ratio(),3),'old_text':a[:4000],'new_text':b[:4000]})
    return out
