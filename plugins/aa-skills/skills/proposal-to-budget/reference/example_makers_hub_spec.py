"""Example build spec: Makers Hub (Compton Makers-Campus Strategic Plan), first full draft, Oct 2026.
Shows the spec format: STD = Rules standards (all projects), VARS = project Variables,
phases = (number, name, items). An item is a row tuple (task, menu_id, qty, ed, pm, amb, note),
("PM", ...row) to place it under Project Management, or ("G", sub-task name, [rows]) for a sub-task
with sub-sub tasks. {key} in a cell links to a Variable or Rules standard.
The live Makers Hub sheet was edited by hand after this build; treat the numbers here as a pattern, not current values.
Run: python3 example_makers_hub_spec.py   (rebuilds the whole Fee Worksheet tab: only for a new, unedited copy)
"""
STD=[("drive","Drive time per in-person trip, per person (hrs)",1,"½ hr to + ½ hr from, every in-person meeting"),
("vmtg","Virtual meeting length (hrs)",1,"All virtual meetings incl. PM Client Meetings"),
("emailed","Emails / calls per week: ED (hrs)",1,"PM: Emails + Phone Calls, every phase"),
("emailpm","Emails / calls per week: PM (hrs)",1,"PM: Emails + Phone Calls, every phase"),
("kickoff","Kickoff schedule + coordination: ED (hrs)",5,"First phase, PM: Schedule + Coordination"),
("rep_short","Short report / slide deck: PM (hrs)",5,"First draft; revisions separate"),
("rev_short","Short report / slide deck: ED review (hrs)",1,"First draft; revisions separate"),
("rep_long","Longer report: PM (hrs)",10,"First draft; revisions separate"),
("rev_long","Longer report: ED review (hrs)",2,"First draft; revisions separate"),
("rep_intense","Intense graphic layout or writing chapter: PM (hrs)",20,"First draft; revisions separate"),
("rev_intense","Intense graphic layout or writing chapter: ED review (hrs)",3,"First draft; revisions separate"),
("followup_hrs","Outreach follow-up (hrs each)",0.25,"Contact + follow-ups on outreach"),
("followups","Follow-ups per outreach contact",3,"Contact + follow-ups on outreach"),
("markup","Hard cost markup",0.15,"Hard costs billed at cost + 15%"),
("food_pp","Food per attendee ($)",15,"Wetlands draft 6: focus group food $300/meeting (~20 people); open house $15 x 50"),
("gift_pp","Gift card per attendee ($)",25,"Wetlands draft 6: $25 x first 15-20 attendees"),
("print_mtg","Printing per meeting ($)",50,"Wetlands draft 6: focus group printing $50/meeting"),
("art_event","Art / workshop supplies per event ($)",50,"Wetlands draft 6: focus group art supplies $50/round"),
("mile_rate","Mileage rate ($/mile)",0.7,"Wetlands draft 6 mileage rate"),
("miles_trip","Miles per in-person trip",20,"Wetlands draft 6 mileage lines")]
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts'))
from feebuild import build
W="Wetlands draft 6"
VARS=[
("pmfreq","PM meetings per week",0.5,"Rule: every other week; Project Management rows"),
("cusd","CUSD + police staff interviews",10,"1.0 Site viability interviews"),
("partners","Makers Hub partner interviews",10,"1.0 Pathway research"),
("funders","Funder interviews",10,"1.0 Pathway research"),
("charrette","Internal charrette length (hrs)",3,"2.0 Internal charrette"),
("focusgroups","Focus groups",5,"2.0 Focus groups"),
("fglen","Focus group session length (hrs)",2,"2.0 Focus groups; 3.0 Draft presentation"),
("draftpres","Draft presentations to focus group members",1,"3.0 Draft presentation"),
("revisions","Revision rounds",2,"4.0 Revisions"),
("launch","Launch events",1,"4.0 Launch event"),
("launchlen","Launch event length (hrs)",4,"4.0 Launch event"),
("decks","Pitch deck audiences",3,"4.0 Pitch decks Qty (hours not yet set)"),
("renderings","Interior renderings",3,"3.0 Renderings Qty (hours not yet set)")]
B=lambda t,q=1:(t,"",q,"","","","New task; no Wetlands precedent. Fill in hours.")
LAB={"short":"short report / slide deck","long":"longer report","intense":"intense layout / chapter"}
def RP(t,z,q=1,extra=""): return (t,"",q,f"={{rev_{z}}}",f"={{rep_{z}}}","",f"Rule: {LAB[z]} = PM draft + ED review from Rules (excl. revisions){extra}")
p1=[("G","Site Viability",[
   ("Interviews with up to 10 CUSD + police staff (virtual)","","={cusd}",0.5,"={vmtg}","",f"Erin set ED 0.5/interview. {W}, 04 Research 4.01A: zoom staff interview. If in person, add drive time."),
   B("Due diligence: zoning + building condition"),
   RP("Research Report","short",extra=". Erin set PM 5 = short")]),
 ("G","Stakeholder Identification",[
   ("Stakeholder power map","O-03",1,3,8,"",f"{W}, 04 Research 4.01B: ED 3, WC 8 (power map + contact lists together)"),
   ("Stakeholder contact list","",1,"","","","Included in power map hours per Wetlands")]),
 ("G","Acquisition Pathway Research",[
   ("Interview up to 10 Makers Hub partners (virtual)","","={partners}","={vmtg}","={vmtg}+{followup_hrs}*{followups}","",f"{W}, 04 Research 4.02A: CBO virtual meeting + contact/follow-ups (Rules)"),
   RP("Research CUSD priorities","short"),
   RP("Document Site underuse / higher and better use","short"),
   RP("Research lease precedents","short"),
   B("Full cost to acquire the building"),
   B("Typical capital campaign timelines + strategies"),
   ("Research + interview up to 10 funders (virtual)","","={funders}","={vmtg}","={vmtg}+{followup_hrs}*{followups}","","Same structure as partner interviews"),
   RP("Research bank acquisition loans + repayment structures","short"),
   RP("Acquisition Strategy Recommendation","long"),
   B("Deliverables for the selected pathway"),
   ("Detailed Project Work Plan + Schedule","D-02",1,12,1,"",f"{W}, 01 Initiation 1.1A: ED write/review 10 + setup 1 + internal mtgs 1; WC internal mtgs 1")])]
p3=[B("Design outreach templates, flyers + communications strategy"),
 ("In-person internal charrette (3 hrs)","E-09",1,"={charrette}+{drive}","={charrette}+0.5+{drive}","",f"Meeting + drive (Rules); WC draft agenda 0.5 per {W}"),
 ("Host up to 5 focus groups","E-05","={focusgroups}","={fglen}+{drive}+0.5+IF(N({focusgroups})=0,0,4/N({focusgroups}))","=1+0.5+0.5+{fglen}+{drive}+3+IF(N({focusgroups})=0,0,5.5/N({focusgroups}))","",f"{W}, 05 Visioning 5.05A per group: ED attend + compile 0.5; WC coordinate 1, adapt 0.5, reminders 0.5, attend, compile 3. One-time design (ED 4, WC 5.5) spread across groups. 'Attend 4 hr' read as 2 hr session + 2 hr drive"),
 ("Engagement summary (presentation + written report)","S-06",1,2,5,"",f"{W}, 08 Draft 8.03D presentation of results: ED 2, WC 5. Written report portion not in Wetlands; add hours"),
 RP("Updated floor plans + diagrams","intense")]
p4=[B("Acquisition strategy plan + research (selected pathway)"),
 ("G","Branded Draft Strategic Plan",[
   RP("Impact of Makers Hub","long"),RP("Vision","intense"),RP("Precedents (2-3 case studies)","long"),RP("Community Engagement Strategy","long"),
   RP("Floor Plans + Renderings","intense",extra=". Up to 3 renderings not yet sized; add hours"),
   RP("Phasing Strategy + Timeline","intense"),RP("Detailed Budgets","intense"),RP("Risk Analysis + Mitigation","long"),
   ("Compile, write + review full plan","S-07",1,12,16,"",f"Not a separate SOW line. {W}, 08 Draft 8.01A: ED drafting 6 + reviewing 6; WC drafting 10 + reviewing 6")]),
 ("Present the draft to focus group members (in person)","S-08","={draftpres}","=4+{fglen}+{drive}+0.5","=0.5+0.5+4+{fglen}+{drive}+1.5","",f"{W}, 08 Draft 8.04A focus group: ED design 4, attend, compile 0.5; WC agenda 0.5, reminders 0.5, design 4, attend, compile 1.5"),
 B("Coordination of A+A sub-consultants")]
p5=[("G","Two rounds of revisions + supporting marketing documents",[
   ("Revision rounds","L-01","={revisions}",6,9,"",f"{W}, 09 Final 9.01A 'Reviewing' per round: ED 6, WC 6 x 1.5 staff"),
   RP("Pitch deck adapted per audience","short",q="={decks}"),RP("Sponsorship package","long"),RP("One-pager","short")]),
 ("Present the final plan at a launch event","L-06","={launch}","=11.5+{launchlen}+{drive}","=17.5+{launchlen}+{drive}","",f"{W}, 09 Final 9.06A open house: ED vendors 1, internal mtgs 2, outreach 2, client coordination 2, design 4, compile 0.5; WC outreach 5, agenda 0.5, internal mtgs 2, design 6, compile 4"),
 B("Coordination of A+A sub-consultants")]
phases=[("1.0","Research",p1),("2.0","Focus Group Engagement",p3),("3.0","Draft Strategic Plan",p4),("4.0","Final Strategic Plan",p5)]
proj=[("Project Name","Compton Makers-Campus Strategic Plan"),("Client","Makers Hub"),("Product Line","Community-Backed Strategic Plan"),("Proposal Date","10.19.26"),("Client Target Budget","")]
print(build("1nJLaFdeSnyqCu5Bp-GR1ThvSTQCk-gbG0aQphj8U3KE",996518806,proj,phases,VARS,standards=STD,months=[3,2,3,1]))
