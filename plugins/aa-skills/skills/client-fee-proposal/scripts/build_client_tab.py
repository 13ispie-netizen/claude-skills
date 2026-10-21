"""Build (or safely rebuild) the client-facing 'Client Fee Proposal' tab from a Fee Worksheet.
Usage: python3 build_client_tab.py <spreadsheetId> [--force]
- Every cell is a formula linked to 'Fee Worksheet' (live). Shows phases + sub-task (x.n) totals only.
- If the tab already exists and differs from what this script would write (someone edited it), it stops
  unless --force is given. Rerun after adding/removing sub-tasks so new rows appear.
"""
import json,subprocess,re,sys
S=sys.argv[1]; FORCE="--force" in sys.argv; FW="'Fee Worksheet'"; TITLE="Client Fee Proposal"
def gws(*a):
    o=subprocess.run(["gws",*a],capture_output=True,text=True).stdout
    assert '"error"' not in o, o[-600:]; return json.loads(o[o.find("{"):]) if "{" in o else {}
v=gws("sheets","spreadsheets","values","get","--params",json.dumps({"spreadsheetId":S,"range":f"{FW}!A1:I230","valueRenderOption":"FORMULA"}))["values"]
L=lambda i: (str(v[i-1][0]) if i-1<len(v) and v[i-1] else "")
N=len(v); find=lambda p:[i for i in range(1,N+1) if p(L(i))]
staff_row=find(lambda t:t.startswith("Number of Staff"))[0]; sub_row=find(lambda t:t.startswith("Subtotal (All Phases"))[0]
ps=find(lambda t:t=="Phase Summary")[0]; pt=[i for i in find(lambda t:t=="Total") if i>ps][0]
eff=find(lambda t:t.startswith("Effort Analysis"))[0]
svc=[]
for i in range(eff,sub_row):
    t=L(i)
    if re.match(r"^\d+\.0 ",t): svc.append(("P",i))
    elif re.match(r"^\s+\d+\.\d+ ",t):
        j=i+1; kids=[]
        while j<sub_row and re.match(r"^\s+\d+\.\d+\.\d+",L(j)): kids.append(j); j+=1
        svc.append(("S",i,kids))
rows=[]; st={}
def add(vals,kind=None,cur=(),hrs=(),pct=()):
    rows.append(vals); r=len(rows); st.setdefault(kind,[]).append(r) if kind else None
    for c in cur: st.setdefault("cur",[]).append((r,c))
    for c in hrs: st.setdefault("hrs",[]).append((r,c))
    for c in pct: st.setdefault("pct",[]).append((r,c))
    return r
add(["Project"],"label"); add([f"={FW}!B5"],"name")
add(["Client"],"label"); add([f"={FW}!B6"],"value")
add([])
add(["Fee Proposal From"],"label"); add(["Architecture + Advocacy"],"value"); add(["PO Box 18205, Los Angeles, CA 90018"],"small")
add([])
add(["Date Prepared"],"label"); add([f"={FW}!B8"],"value")
add([])
add(["Billing Rates"],"section"); add(["Role","Rate ($/hr)"],"colhdr")
for k in range(3): add([f"={FW}!A{12+k}",f"={FW}!B{12+k}"],"detail",cur=[1])
add([])
add(["Phase Summary"],"section"); add(["Phase","Months","Weeks","ED Hrs","PM Hrs","Amb Hrs","Total Hrs","Fee"],"colhdr")
for i in range(ps+2,pt+1):
    add([f"={FW}!{c}{i}" for c in "ABCDEFGH"],"svctotal" if i==pt else "detail",cur=[7],hrs=[2,3,4,5,6])
add([])
add(["Services"],"section"); add(["Task","","","ED Hrs","PM Hrs","Amb Hrs","Total Hrs","Fee"],"colhdr")
for it in svc:
    if it[0]=="P":
        i=it[1]; add([f"={FW}!A{i}","","",f"={FW}!D{i}",f"={FW}!E{i}",f"={FW}!F{i}",f"={FW}!G{i}",f"={FW}!H{i}"],"phase",cur=[7],hrs=[3,4,5,6])
    else:
        _,i,kids=it
        if kids:
            a,b=kids[0],kids[-1]; q=""
            role=[f"=SUMPRODUCT(IF({FW}!$C{a}:$C{b}=\"\",1,{FW}!$C{a}:$C{b}),{FW}!{c}{a}:{c}{b})*{FW}!{c}${staff_row}" for c in "DEF"]
        else:
            q=""
            role=[f"=IF({FW}!C{i}=\"\",1,N({FW}!C{i}))*N({FW}!{c}{i})*{FW}!{c}${staff_row}" for c in "DEF"]
        add([f"={FW}!A{i}","",q,*role,f"={FW}!G{i}",f"={FW}!H{i}"],"subtask",cur=[7],hrs=[2,3,4,5,6])
add(["Total Service Fee","","",f"={FW}!D{sub_row}",f"={FW}!E{sub_row}",f"={FW}!F{sub_row}",f"={FW}!G{sub_row}",f"={FW}!H{sub_row}"],"svctotal",cur=[7],hrs=[3,4,5,6])
add([])
sc=find(lambda t:t=="Sub-consultants")[0]; sct=find(lambda t:t.startswith("Sub-consultant Total"))[0]
add(["Sub-consultants"],"section"); add(["Sub-consultant","","","","","","","Fee"],"colhdr")
for i in range(sc+1,sct):
    if L(i).strip(): add([f"={FW}!A{i}","","","","","","",f"={FW}!H{i}"],"detail",cur=[7])
add(["Sub-consultant Total","","","","","","",f"={FW}!H{sct}"],"subtotal",cur=[7])
add([])
hc=find(lambda t:t.startswith("Hard Costs /"))[0]; hct=find(lambda t:t.startswith("Hard Costs Total"))[0]
add(["Hard Costs"],"section"); add(["Item","","","","","","","Cost"],"colhdr")
for i in range(hc+1,hct):
    if L(i).strip(): add([f"={FW}!A{i}","","","","","","",f"={FW}!H{i}"],"detail",cur=[7])
add(["Hard Costs Total","","","","","","",f"={FW}!H{hct}"],"subtotal",cur=[7])
add([])
fs=find(lambda t:t=="Fee Summary")[0]
add(["Fee Summary"],"section")
i=fs+1
while i<=N and L(i).strip():
    t=L(i).strip()
    if t.startswith("Total Proposed"):
        add([f"={FW}!A{i}","","","","","","",f"={FW}!B{i}"],"grand",cur=[7])
    else:
        add([f"={FW}!A{i}","","","","","","",f"={FW}!B{i}"],"detail",pct=[7] if "(%)" in t else (),cur=[] if "(%)" in t else [7])
    i+=1
# create or safely rewrite tab
meta=gws("sheets","spreadsheets","get","--params",json.dumps({"spreadsheetId":S,"fields":"sheets.properties(sheetId,title)"}))
tabs={x["properties"]["title"]:x["properties"]["sheetId"] for x in meta["sheets"]}
if TITLE in tabs:
    SH=tabs[TITLE]
    live=gws("sheets","spreadsheets","values","get","--params",json.dumps({"spreadsheetId":S,"range":f"'{TITLE}'!A1:J200","valueRenderOption":"FORMULA"})).get("values",[])
    def nz(x):
        x=[str(y) for y in x]
        while x and x[-1]=="": x.pop()
        return x
    # compare only the rows the old build would have produced (same structure); any edited label/value -> stop
    diffs=[i+1 for i in range(max(len(live),len(rows))) if nz(live[i] if i<len(live) else [])!=nz(rows[i] if i<len(rows) else [])]
    if diffs and not FORCE:
        for i in diffs[:15]: print(i,"LIVE",nz(live[i-1] if i-1<len(live) else [])[:3],"| NEW",nz(rows[i-1] if i-1<len(rows) else [])[:3])
        print(f"STOP: {len(diffs)} rows differ (hand edits, or Fee Worksheet structure changed). Show Erin, then rerun with --force if she approves."); sys.exit(1)
else:
    SH=gws("sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":S}),"--json",json.dumps({"requests":[{"addSheet":{"properties":{"title":TITLE,"index":1,"gridProperties":{"rowCount":len(rows)+40,"columnCount":10}}}}]}))["replies"][0]["addSheet"]["properties"]["sheetId"]
gws("sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":S}),"--json",json.dumps({"requests":[{"updateCells":{"range":{"sheetId":SH},"fields":"*"}},{"updateBorders":{"range":{"sheetId":SH},"top":{"style":"NONE"},"bottom":{"style":"NONE"},"innerHorizontal":{"style":"NONE"}}}]}))
gws("sheets","spreadsheets","values","update","--params",json.dumps({"spreadsheetId":S,"range":f"'{TITLE}'!A1","valueInputOption":"USER_ENTERED"}),"--json",json.dumps({"values":rows}))
def c(h): return {"red":int(h[0:2],16)/255,"green":int(h[2:4],16)/255,"blue":int(h[4:6],16)/255}
DARK,SAL,WHITE,GRY=c("36354d"),c("f49f7c"),c("FFFFFF"),c("999999")
rg=lambda r0,r1,c0,c1:{"sheetId":SH,"startRowIndex":r0-1,"endRowIndex":r1,"startColumnIndex":c0,"endColumnIndex":c1}
F=lambda rng,f,fields:{"repeatCell":{"range":rng,"cell":{"userEnteredFormat":f},"fields":",".join("userEnteredFormat."+x for x in fields)}}
tf=lambda size=10,bold=False,color=DARK:{"fontFamily":"Public Sans","fontSize":size,"bold":bold,"foregroundColor":color}
R=[F({"sheetId":SH},{"textFormat":tf(),"verticalAlignment":"MIDDLE","backgroundColor":WHITE},["textFormat","verticalAlignment","backgroundColor"])]
sty={"label":({"textFormat":tf(10,False,SAL)},1),"name":({"textFormat":tf(14,True)},1),"value":({"textFormat":tf(12,True)},1),"small":({"textFormat":tf(10)},1),
     "section":({"textFormat":tf(12,True)},1),"colhdr":({"textFormat":tf(10,False,GRY)},8),"detail":({"textFormat":tf(10)},8),
     "phase":({"textFormat":tf(11,True),"backgroundColor":c("efefef")},8),"subtask":({"textFormat":tf(10,False),"backgroundColor":WHITE},8),
     "subtotal":({"textFormat":tf(10,True),"backgroundColor":c("efefef")},8),"svctotal":({"textFormat":tf(13,True),"backgroundColor":c("cccccc")},8)}
for k,(f,w) in sty.items():
    for r in st.get(k,[]): R.append(F(rg(r,r,0,w),f,list(f.keys())))
for r in st.get("svctotal",[]): R.append({"updateBorders":{"range":rg(r,r,0,8),"top":{"style":"SOLID","color":DARK}}})
for r in st.get("grand",[]):
    R.append(F(rg(r,r,0,2),{"backgroundColor":SAL,"textFormat":tf(18,True,WHITE)},["backgroundColor","textFormat"]))
    R.append(F(rg(r,r,2,8),{"textFormat":tf(15,True,SAL)},["textFormat"]))
    R.append({"updateBorders":{"range":rg(r,r,0,8),"top":{"style":"SOLID","color":DARK}}})
    R.append({"mergeCells":{"range":rg(r,r,0,2),"mergeType":"MERGE_ALL"}})
for k,pat in [("cur",{"type":"CURRENCY","pattern":"$#,##0"}),("hrs",{"type":"NUMBER","pattern":"#,##0.0"}),("pct",{"type":"PERCENT","pattern":"0%"})]:
    for (r,col) in st.get(k,[]): R.append(F(rg(r,r,col,col+1),{"numberFormat":pat,"horizontalAlignment":"RIGHT"},["numberFormat","horizontalAlignment"]))
for r in st.get("colhdr",[]): R.append(F(rg(r,r,1,8),{"horizontalAlignment":"RIGHT"},["horizontalAlignment"]))
for i,w in enumerate([400,90,55,75,75,75,80,100]): R.append({"updateDimensionProperties":{"range":{"sheetId":SH,"dimension":"COLUMNS","startIndex":i,"endIndex":i+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
R.append({"updateSheetProperties":{"properties":{"sheetId":SH,"gridProperties":{"hideGridlines":True}},"fields":"gridProperties.hideGridlines"}})
gws("sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":S}),"--json",json.dumps({"requests":R}))
print("rows",len(rows))
