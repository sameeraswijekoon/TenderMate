import os,json
def sync_google_sheets(payload):
    # Optional: enable with GOOGLE_SHEETS_WEBHOOK_URL. A webhook can be a Google Apps Script endpoint.
    url=os.getenv('GOOGLE_SHEETS_WEBHOOK_URL')
    if not url:return {'enabled':False,'status':'not_configured'}
    try:
        import urllib.request
        req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=15) as r:return {'enabled':True,'status':'ok','http_status':r.status}
    except Exception as e:return {'enabled':True,'status':'error','message':str(e)}
def sync_firebase(payload):
    # Optional: enable with FIREBASE_WEBHOOK_URL using a controlled HTTPS endpoint.
    url=os.getenv('FIREBASE_WEBHOOK_URL')
    if not url:return {'enabled':False,'status':'not_configured'}
    try:
        import urllib.request
        req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=15) as r:return {'enabled':True,'status':'ok','http_status':r.status}
    except Exception as e:return {'enabled':True,'status':'error','message':str(e)}
