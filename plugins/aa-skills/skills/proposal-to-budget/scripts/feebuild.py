import json,subprocess
def gws(*a):
    r=subprocess.run(["gws",*a],capture_output=True,text=True)
    if '"error"' in r.stdout or r.returncode: print(r.stdout[-900:]); raise SystemExit(1)
    o=r.stdout; return json.loads(o[o.find("{"):]) if "{" in o else {}
def c(h): return {"red":int(h[0:2],16)/255,"green":int(h[2:4],16)/255,"blue":int(h[4:6],16)/255}
DARK,SAL,WHITE,GREY,YEL,BLUE,TINT=c("36354d"),c("f5a17d"),c("FFFFFF"),c("F2F2F2"),c("FFF2CC"),c("1155CC"),c("FDEBE2")
NC=9  # A Task, B ID, C Qty, D ED, E PM, F Amb, G Total, H Fee, I Notes
def build(S,SH,proj,phases,variables,standards=(),addons=None,months=None,rates=(210,180,0),subs=None,reimb=None,dry=False):
    """phases: list of (label, name, [ (task,id,ed,pm,amb,note), ...])"""
    rows={}
    def put(r,v): rows[r]=v
    put(1,["Architecture + Advocacy | Fee Worksheet"])
    put(2,["How to use: edit only the yellow cells with blue text. Enter each phase's length in months, then each task's Qty (link it to a Variable; blank Qty counts as 1, Qty 0 = not included) and hours per unit for each staff member (in-person tasks: add the drive-time variable). Project Management rows calculate from the phase length and PM variables. Fee = hours x bill rate, summed across staff. Rules tab has the standing rules."])
    put(4,["Project Data"])
    for i,(k,v) in enumerate(proj): put(5+i,[k,v])
    put(11,["Billing Rates ($/hr)"]); put(12,["Executive Director",rates[0]]); put(13,["Project Manager",rates[1]]); put(14,["Ambassador",rates[2]])
    blocks=phases+([("Add-ons","Add-ons",addons)] if addons is not None else [])
    nb=len(blocks)
    put(16,["Variables (change a count here and every linked task, phase, and fee updates)"]); put(17,["Variable","Value","Used by"])
    V={}; vr=18
    for (key,label,val,used) in variables:
        put(vr,[label,val,used]); V[key]=f"$B${vr}"; vr+=1
    std_rows=[["Standard values (linked into the Fee Worksheet)","Value","Applies to"]]
    for j,(key,label,val,used) in enumerate(standards):
        std_rows.append([label,val,used]); V[key]=f"Rules!$F${j+2}"
    var_end=vr-1
    PS=vr+2; S0=PS+2; tot_row=S0+nb
    put(PS,["Phase Summary"]); put(PS+1,["Phase","Months","Weeks","ED Hrs","PM Hrs","Amb Hrs","Total Hrs","Fee","% of Fee"])
    sub_v=lambda x: x.format(**V) if isinstance(x,str) else x
    r=tot_row+4
    put(r,["Effort Analysis"]); r+=1
    put(r,["Task","Menu ID","Qty","ED Hrs / Unit","PM Hrs / Unit","Amb Hrs / Unit","Total Hrs","Fee","Notes / Basis"]); hdr_row=r; r+=1
    put(r,["Hourly Billing Rate","","","=B12","=B13","=B14"]); rate_row=r; put(r+1,["Number of Staff","","",1,1,1]); staff_row=r+1; r+=3
    heads=[]; inputs=[]; grp_heads=[]; lvl2_rows=[]
    rate=f"$D${rate_row}:$F${rate_row}"
    def rowf(rr,label,i,q,ed,pm,amb,note):
        put(rr,[label,i,sub_v(q),sub_v(ed),sub_v(pm),sub_v(amb),f"=IF(C{rr}=\"\",1,N(C{rr}))*SUMPRODUCT(D{rr}:F{rr},$D${staff_row}:$F${staff_row})",f"=IF(C{rr}=\"\",1,N(C{rr}))*SUMPRODUCT(D{rr}:F{rr},$D${staff_row}:$F${staff_row},{rate})",note])
    for k,(lab,name,tasks) in enumerate(blocks):
        isadd=(lab=="Add-ons")
        num="A" if isadd else (lab.split(".")[0] if lab[0].isdigit() else lab.split(" ")[-1])
        copp=[x for x in tasks if x[0]!="PM"]; pmx=[x[1:] for x in tasks if x[0]=="PM"]
        wk=f"$C${S0+k}"
        pmrows=[] if isadd else [
            ("Project Management: Schedule + Coordination","PM",1 if k==0 else "",f"={{kickoff}}" if k==0 else "","","","Rule: ED kicks off every project with 5 hrs of schedule coordination" if k==0 else "No rule yet: set Qty + hours"),
            ("Project Management: Client Meetings","PM",f"=ROUNDUP(N({wk})*{V['pmfreq']})","={vmtg}","={vmtg}","","Rule: 1-hr virtual meeting every other week (ED + PM). Qty = weeks x PM meetings/week"),
            ("Project Management: Emails + Phone Calls","PM",f"=N({wk})","={emailed}","={emailpm}","","Rule: up to 1 hr/week ED + 1 hr/week PM. Qty = weeks")]
        sow=any(x[0]=="G" and len(x)==3 for _b in blocks for x in _b[2])
        groups=[(None,copp)] if isadd else ([("Community Outreach + Public Participation",copp),("Project Management",pmx+pmrows)] if not sow else None)
        if sow:
            items=[x for x in tasks if x[0]!="PM"]+[("G","Project Management",pmx+pmrows)]
            nrows=sum(1+len(x[2]) if x[0]=="G" else 1 for x in items)+len(items)-1
        else:
            nrows=sum((0 if g[0] is None else 1)+sum((1+len(it[4]) if it[0]=="G" else 1)+1 for it in g[1]) for g in groups)-1
        h=r; first=r+1; last=r+nrows
        put(h,[lab if isadd else (f"{lab}: {name}" if not lab[0].isdigit() else f"{lab} {name}"),"","",*[f"=SUMPRODUCT(IF($C{first}:$C{last}=\"\",1,$C{first}:$C{last}),{col}{first}:{col}{last})*{col}${staff_row}" for col in "DEF"],f"=SUM(D{h}:F{h})",f"=SUMPRODUCT(D{h}:F{h},{rate})"])
        rr=first; n=1; rngs=[]
        if sow:
            for x in items:
                if x[0]=="G":
                    _,gname,kids=x; a_=rr+1; b_=rr+len(kids)
                    put(rr,[f"   {num}.{n} {gname}","","","","","",f"=SUM(G{a_}:G{b_})" if kids else 0,f"=SUM(H{a_}:H{b_})" if kids else 0]); grp_heads.append(rr); lvl2_rows.append((rr,True)); rr+=1
                    for m_,it in enumerate(kids,1):
                        t,i,q,ed,pm,amb,note=it
                        rowf(rr,f"      {num}.{n}.{m_} {t}",i,q,ed,pm,amb,note)
                        if not (i=="PM" and t!="Project Management: Schedule + Coordination"): rngs.append((rr,rr))
                        rr+=1
                else:
                    t,i,q,ed,pm,amb,note=x
                    rowf(rr,f"   {num}.{n} {t}",i,q,ed,pm,amb,note); rngs.append((rr,rr)); lvl2_rows.append((rr,False)); rr+=1
                if x is not items[-1]: rr+=1
                n+=1
            groups=[]
        for gname,items in groups:
            ind="      "
            if gname is not None:
                a_=rr+1; b_=rr+len(items)
                put(rr,["   "+gname,"","","","","",f"=SUM(G{a_}:G{b_})" if items else 0,f"=SUM(H{a_}:H{b_})" if items else 0]); grp_heads.append(rr); rr+=1
            else: ind="   "
            for it in items:
                if it[0]=="G":
                    _,gname,gid,gnote,kids=it; a_=rr+1; b_=rr+len(kids)
                    put(rr,[f"{ind}{num}.{n} {gname}",gid,"","","","",f"=SUM(G{a_}:G{b_})",f"=SUM(H{a_}:H{b_})",gnote]); lvl2_rows.append((rr,True)); rr+=1
                    for m_,(t,i,q,ed,pm,amb,note) in enumerate(kids,1):
                        rowf(rr,f"{ind}   {num}.{n}.{m_} {t}",i,q,ed,pm,amb,note); rngs.append((rr,rr)); rr+=1
                    rr+=1; n+=1; continue
                t,i,q,ed,pm,amb,note=it
                rowf(rr,f"{ind}{num}.{n} {t}",i,q,ed,pm,amb,note)
                if not (i=="PM" and t!="Project Management: Schedule + Coordination"): rngs.append((rr,rr))
                lvl2_rows.append((rr,False)); rr+=2; n+=1
        inputs.append(rngs); heads.append(h); r=rr+1 if sow else rr
        # summary row
        sr=S0+k
        put(sr,[name if isadd else f"{lab}: {name}" if not lab[0].isdigit() else f"{lab} {name}", "" if isadd else (months[k] if months else ""), "" if isadd else f"=ROUND(N(B{sr})*52/12,1)",f"=D{h}",f"=E{h}",f"=F{h}",f"=G{h}",f"=H{h}",f"=IF($H${tot_row}=0,0,H{sr}/$H${tot_row})"])
    put(tot_row,["Total",*[f"=SUM({c}{S0}:{c}{tot_row-1})" for c in "BCDEFGHI"]])
    put(tot_row+1,[f'=IF(SUM(B{S0}:B{tot_row-1})=0,"Enter each phase\'s length in months so Project Management calculates.","")'])
    sub=r; put(sub,["Subtotal (All Phases"+(" + Add-ons" if addons is not None else "")+")","","",*["="+"+".join(f"{col}{h}" for h in heads) for col in "DEFGH"]]); r+=3
    put(r,["Sub-consultants","","","","","","","Fee"]); sc_h=r; r+=1; sc0=r
    for n in (subs or ["Graphic Designer","Acquisition / Development Consultant","Capital Campaign Consultant","",""]): put(r,[n]); r+=1
    put(r,["Sub-consultant Total","","","","","","",f"=SUM(H{sc0}:H{r-1})"]); sct=r; r+=3
    put(r,["Hard Costs / Reimbursables (billed at cost + markup, separate NTE)","Qty (events / trips / sets)","Per event (people / miles)","Unit cost ($)","","","Cost","Billed (cost + markup)"]); rb_h=r; r+=1; rb0=r
    for n in (reimb or ["Food for engagement events","Gift cards for participants ($25 each)","Workshop materials + mock-up supplies","Reprographics / printing","Entertainment (DJs, artists, etc.)","Photographers","Parking","Governmental fees + permits","Translation / interpretation","Other"]): put(r,[n,"","","","","",f"=IF(COUNT(B{r}:D{r})=0,\"\",N(B{r})*IF(C{r}=\"\",1,N(C{r}))*N(D{r}))",f"=IF(N(G{r})=0,\"\",G{r}*(1+N({V['markup']})))"]); r+=1
    put(r,["Hard Costs Total","","","","","",f"=SUM(G{rb0}:G{r-1})",f"=SUM(H{rb0}:H{r-1})"]); rbt=r; r+=3
    fs=r; put(r,["Fee Summary"]); r+=1; F={}
    for lab in ["Effort-Based Fee","Contingency (%)","Contingency ($)","Sub-consultants","Total Proposed Fee (NTE, excl. reimbursables)","Hard Costs incl. markup (separate NTE)","Client Target Budget","Over / (Under) Client Budget","Total Hours","Effective Hourly Rate"]:
        F[lab]=r; r+=1
    vals={"Effort-Based Fee":f"=H{sub}","Contingency (%)":0.1,"Contingency ($)":f"=B{F['Effort-Based Fee']}*B{F['Contingency (%)']}","Sub-consultants":f"=H{sct}",
          "Total Proposed Fee (NTE, excl. reimbursables)":f"=B{F['Effort-Based Fee']}+B{F['Contingency ($)']}+B{F['Sub-consultants']}","Hard Costs incl. markup (separate NTE)":f"=H{rbt}",
          "Client Target Budget":"=B9","Over / (Under) Client Budget":f'=IF(N(B9)=0,"",B{F["Total Proposed Fee (NTE, excl. reimbursables)"]}-B9)',"Total Hours":f"=G{sub}",
          "Effective Hourly Rate":f"=IF(G{sub}=0,0,(B{F['Effort-Based Fee']}+B{F['Contingency ($)']})/G{sub})"}
    for k,v in vals.items(): put(F[k],[k,v])
    if dry: return rows
    gws("sheets","spreadsheets","values","clear","--params",json.dumps({"spreadsheetId":S,"range":"Rules!E1:G60"}))
    if standards: gws("sheets","spreadsheets","values","update","--params",json.dumps({"spreadsheetId":S,"range":"Rules!E1","valueInputOption":"USER_ENTERED"}),"--json",json.dumps({"values":std_rows}))
    # write
    gws("sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":S}),"--json",json.dumps({"requests":[{"unmergeCells":{"range":{"sheetId":SH}}},{"updateCells":{"range":{"sheetId":SH},"fields":"*"}}]}))
    data=[{"range":f"'Fee Worksheet'!A{k}","values":[v]} for k,v in sorted(rows.items())]
    gws("sheets","spreadsheets","values","batchUpdate","--params",json.dumps({"spreadsheetId":S}),"--json",json.dumps({"valueInputOption":"USER_ENTERED","data":data}))
    R=[]
    def rg(r0,r1,c0,c1): return {"sheetId":SH,"startRowIndex":r0-1,"endRowIndex":r1,"startColumnIndex":c0,"endColumnIndex":c1}
    def fmt(rng,f,fields): R.append({"repeatCell":{"range":rng,"cell":{"userEnteredFormat":f},"fields":",".join("userEnteredFormat."+x for x in fields)}})
    tf=lambda **k: {"textFormat":{"fontFamily":k.get("font","Nunito"),"fontSize":k.get("size",10),"bold":k.get("bold",False),"italic":k.get("italic",False),"foregroundColor":k.get("color",DARK)}}
    fmt({"sheetId":SH},{**tf(),"verticalAlignment":"MIDDLE"},["textFormat","verticalAlignment"])
    fmt(rg(1,1,0,1),tf(font="Public Sans",size=16,bold=True),["textFormat"])
    R.append({"mergeCells":{"range":rg(2,2,0,NC),"mergeType":"MERGE_ALL"}}); fmt(rg(2,2,0,NC),{**tf(italic=True),"wrapStrategy":"WRAP"},["textFormat","wrapStrategy"])
    R.append({"updateDimensionProperties":{"range":{"sheetId":SH,"dimension":"ROWS","startIndex":1,"endIndex":2},"properties":{"pixelSize":48},"fields":"pixelSize"}})
    for x in (4,11,16,PS,tot_row+4,fs): fmt(rg(x,x,0,4),tf(font="Public Sans",size=12,bold=True,color=SAL),["textFormat"])
    def hdr(x,n): fmt(rg(x,x,0,n),{**tf(font="Public Sans",bold=True,color=WHITE),"backgroundColor":DARK,"wrapStrategy":"WRAP","horizontalAlignment":"CENTER"},["textFormat","backgroundColor","wrapStrategy","horizontalAlignment"])
    hdr(17,3); hdr(PS+1,9); hdr(hdr_row,NC); hdr(sc_h,8); hdr(rb_h,8)
    inp=lambda rng: fmt(rng,{**tf(color=BLUE),"backgroundColor":YEL},["textFormat","backgroundColor"])
    inp(rg(5,9,1,2)); inp(rg(12,14,1,2)); inp(rg(18,var_end,1,2));  fmt(rg(18,var_end,2,3),tf(italic=True,size=9),['textFormat']); inp(rg(S0,S0+len(phases)-1,1,2)); inp(rg(F["Contingency (%)"],F["Contingency (%)"],1,2))
    for h,ab in zip(heads,inputs):
        fmt(rg(h,h,0,NC),{**tf(font="Public Sans",bold=True),"backgroundColor":GREY},["textFormat","backgroundColor"])
        for (a,b) in ab:
            if b>=a: inp(rg(a,b,2,6))
    for (lr,kids) in lvl2_rows:
        fmt(rg(lr,lr,0,NC-1),{**tf(bold=True),"backgroundColor":c("FAFAFA")},["textFormat","backgroundColor"])
        if not kids: fmt(rg(lr,lr,2,6),{**tf(bold=True,color=BLUE),"backgroundColor":YEL},["textFormat","backgroundColor"])
    for gh in grp_heads: fmt(rg(gh,gh,0,NC-1),{**tf(bold=True),"backgroundColor":c("FAFAFA")},["textFormat","backgroundColor"])
    inp(rg(staff_row,staff_row,3,6))
    fmt(rg(hdr_row+2,r,8,9),{**tf(italic=True,size=9),"wrapStrategy":"WRAP"},["textFormat","wrapStrategy"])
    inp(rg(sc0,sct-1,0,1)); inp(rg(sc0,sct-1,7,8)); inp(rg(rb0,rbt-1,0,1)); inp(rg(rb0,rbt-1,1,4)); fmt(rg(rb0,rbt-1,3,4),{"numberFormat":{"type":"CURRENCY","pattern":"$#,##0.00"}},["numberFormat"]); fmt(rg(rb_h,rb_h,1,4),{**tf(font="Public Sans",bold=True,color=WHITE),"backgroundColor":DARK,"wrapStrategy":"WRAP","horizontalAlignment":"CENTER"},["textFormat","backgroundColor","wrapStrategy","horizontalAlignment"])
    for x in (sub,sct,rbt,tot_row,F["Total Proposed Fee (NTE, excl. reimbursables)"]): fmt(rg(x,x,0,NC),tf(bold=True),["textFormat"])
    fmt(rg(F["Total Proposed Fee (NTE, excl. reimbursables)"],F["Total Proposed Fee (NTE, excl. reimbursables)"],0,2),{"backgroundColor":TINT},["backgroundColor"])
    R.append({"setDataValidation":{"range":rg(7,7,1,2),"rule":{"condition":{"type":"ONE_OF_LIST","values":[{"userEnteredValue":"Engagement Sub-consultant"},{"userEnteredValue":"Community-Backed Strategic Plan"}]},"showCustomUi":True,"strict":False}}})
    cur={"numberFormat":{"type":"CURRENCY","pattern":"$#,##0"}}; pct={"numberFormat":{"type":"PERCENT","pattern":"0%"}}; hrs={"numberFormat":{"type":"NUMBER","pattern":"#,##0.0"}}
    fmt(rg(9,14,1,2),cur,["numberFormat"]); fmt(rg(S0,tot_row,2,7),hrs,["numberFormat"]); fmt(rg(S0,tot_row,7,8),cur,["numberFormat"]); fmt(rg(S0,tot_row,8,9),pct,["numberFormat"])
    fmt(rg(rate_row,rate_row,3,6),cur,["numberFormat"]); fmt(rg(rate_row+1,sub,2,7),hrs,["numberFormat"]); fmt(rg(rate_row+1,sub,7,8),cur,["numberFormat"]); fmt(rg(sc0,rbt,6,8),cur,["numberFormat"])
    fmt(rg(fs+1,fs+10,1,2),cur,["numberFormat"]); fmt(rg(F["Contingency (%)"],F["Contingency (%)"],1,2),pct,["numberFormat"]); fmt(rg(F["Total Hours"],F["Total Hours"],1,2),hrs,["numberFormat"])
    fmt(rg(tot_row+1,tot_row+1,0,1),tf(italic=True,color=c("CC0000")),["textFormat"])
    for i,w in enumerate([400,65,55,85,85,85,80,90,380,70]):
        R.append({"updateDimensionProperties":{"range":{"sheetId":SH,"dimension":"COLUMNS","startIndex":i,"endIndex":i+1},"properties":{"pixelSize":w},"fields":"pixelSize"}})
    if standards:
        n=len(standards)+1; RS=1
        R.append({"repeatCell":{"range":{"sheetId":RS,"startRowIndex":0,"endRowIndex":1,"startColumnIndex":4,"endColumnIndex":7},"cell":{"userEnteredFormat":{"backgroundColor":DARK,"textFormat":{"bold":True,"foregroundColor":WHITE,"fontFamily":"Public Sans","fontSize":10}}},"fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})
        R.append({"repeatCell":{"range":{"sheetId":RS,"startRowIndex":1,"endRowIndex":n,"startColumnIndex":5,"endColumnIndex":6},"cell":{"userEnteredFormat":{"backgroundColor":YEL,"textFormat":{"foregroundColor":BLUE,"fontFamily":"Nunito","fontSize":10}}},"fields":"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat"}})
        R.append({"repeatCell":{"range":{"sheetId":RS,"startRowIndex":1,"endRowIndex":n,"startColumnIndex":4,"endColumnIndex":7},"cell":{"userEnteredFormat":{"wrapStrategy":"WRAP","verticalAlignment":"TOP"}},"fields":"userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment"}})
        for i_,w_ in [(3,30),(4,300),(5,70),(6,260)]: R.append({"updateDimensionProperties":{"range":{"sheetId":RS,"dimension":"COLUMNS","startIndex":i_,"endIndex":i_+1},"properties":{"pixelSize":w_},"fields":"pixelSize"}})
        mk=[j for j,(k_,_,_,_) in enumerate(standards) if k_=="markup"]
        if mk: R.append({"repeatCell":{"range":{"sheetId":RS,"startRowIndex":mk[0]+1,"endRowIndex":mk[0]+2,"startColumnIndex":5,"endColumnIndex":6},"cell":{"userEnteredFormat":{"numberFormat":{"type":"PERCENT","pattern":"0%"}}},"fields":"userEnteredFormat.numberFormat"}})
    gws("sheets","spreadsheets","batchUpdate","--params",json.dumps({"spreadsheetId":S}),"--json",json.dumps({"requests":R}))
    return dict(sub=sub,F=F,tot_row=tot_row,heads=heads,S0=S0,V=V)
