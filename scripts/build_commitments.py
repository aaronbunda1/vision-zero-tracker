#!/usr/bin/env python3
"""Generate data/commitments.json from the Vision Zero Reimagined Action Plan List.

Actions transcribed from the official plan PDF (source/Vision-Zero-Reimagined-2026.pdf),
"Action Plan List" section, document pages 93-99. Marquee flags and targets come from
the "Marquee Action Items" section (document pages 11-13).

Re-running this script resets commitments.json to the seed state — it will
OVERWRITE any status updates recorded there. It exists for provenance and
one-time seeding, not for routine use.
"""
import json
import pathlib

PRESS_RELEASE = "https://www.nyc.gov/mayors-office/news/2026/09/mayor-mamdani-unveilsvision-zero-reimagined-to-make-streets-safe"
STREETSBLOG = "https://nyc.streetsblog.org/2026/09/15/vision-zero-report-2026-mayor-zohran-mamdani-street-safety-dot"
ANNOUNCED = "2026-09-15"

# (id_suffix, agencies, group, title, target, marquee, page)
# id_suffix mirrors the plan's per-goal numbering (e.g. "3.1"); "m1" = marquee-only item.
GOALS = {
    1: {
        "page": 93,
        "actions": [
            ("1.1", ["DOT", "DANY"], "Make dangerous driving a key legislative priority in Albany", "Pass the Drugged Driving Bill (S2214)", None, True),
            ("1.2", ["DANY"], "Make dangerous driving a key legislative priority in Albany", "Pursue state legislation to allow virtual traffic court testimony", None, True),
            ("1.3", ["DANY"], "Make dangerous driving a key legislative priority in Albany", "Expand power of OATH to adjudicate Failure to Yield violations", None, True),
            ("1.4", ["DANY", "TF"], "Make dangerous driving a key legislative priority in Albany", "Pursue state legislation to limit conditional licenses and strengthen DMV enforcement", None, True),
            ("2.1", ["NYPD"], "Physically remove or disable vehicles operated by dangerous drivers", "Explore strategies to expand towing capacity", None, False),
            ("2.2", ["NYPD"], "Physically remove or disable vehicles operated by dangerous drivers", "Expand booting, including the Barnacle device", None, False),
            ("2.3", ["DOT"], "Physically remove or disable vehicles operated by dangerous drivers", "Pursue state legislation to authorize license plate seizure", None, False),
            ("2.4", ["SHERIFF"], "Physically remove or disable vehicles operated by dangerous drivers", "Monitor entry points into the City for serial traffic offender scofflaw vehicles", None, False),
            ("3.1", ["DOT"], "Use automated enforcement to target repeat violators", "Launch New York City's first-ever Super Speeder Program requiring extreme recidivist speeders to install an intelligent speed assistance (ISA) device on their vehicles", "Extreme repeat speed violators required to install ISA devices", True),
            ("3.2", ["DOT"], "Use automated enforcement to target repeat violators", "Pursue state legislation to increase penalties for serial recidivists", None, False),
            ("3.3", ["SHERIFF"], "Use automated enforcement to target repeat violators", "Target top automated enforcement violators for scofflaw enforcement", None, False),
            ("4.1", ["DOT", "NYPD"], "Combat ghost plates with technology", "Pursue state legislation to require smart license plates or registration stickers", None, False),
            ("4.2", ["DOT", "NYPD"], "Combat ghost plates with technology", "Pursue state legislation to allow traffic tickets to be issued to the VIN only", None, False),
            ("4.3", ["DOT", "NYPD"], "Combat ghost plates with technology", "Advocate for OEM VIN-verification technology", None, False),
            ("5", ["MTA"], None, "Install Automated Camera Enforcement on MTA buses", None, False),
            ("6.1", ["DOT"], "Raise standards for maintaining and restoring driver's licenses", "Pursue state legislation to require driver training and education programs prior to license reinstatement", None, False),
            ("6.2", ["DOT"], "Raise standards for maintaining and restoring driver's licenses", "Pursue state legislation to implement regular driving reevaluations and reeducation based on crash history", None, False),
            ("7", ["TLC"], None, "Pursue state legislation to strengthen TLC enforcement capacity", None, False),
        ],
    },
    2: {
        "page": 94,
        "actions": [
            ("1.1", ["DOT"], "Regulate third-party delivery services", "Launch a robust, comprehensive online safety training program for all bicycle and e-bike delivery workers", None, True),
            ("1.2", ["DOT"], "Regulate third-party delivery services", "Require third-party delivery companies to provide trip-level data on deliveries, worker penalties and safety incidents", None, True),
            ("1.3", ["DOT"], "Regulate third-party delivery services", "Use delivery data to establish safe delivery time standards and regulations for penalties imposed on workers", None, True),
            ("1.4", ["DOT"], "Regulate third-party delivery services", "Require enhanced training for delivery workers who repeatedly engage in unsafe riding behavior", None, True),
            ("2.1", ["DOT"], "Leverage bike share and e-scooter share to promote safety", "Expand capacity and geographic coverage of bike share and e-scooter share services", None, False),
            ("2.2", ["DOT"], "Leverage bike share and e-scooter share to promote safety", "Require in-app safety training for new and teen riders", None, False),
            ("3", ["DOT"], None, "Pursue state legislation to create e-bike regulations consistent with national and international safety standards", None, False),
            ("4", ["NYPD"], None, "Remove illegal and unlicensed micromobility devices from City streets", None, False),
            ("5.1", ["DOT"], "Promote safe moped and motorcycle usage", "Explore the implementation of subsidized motorcycle safety training programs", None, False),
            ("5.2", ["DOT"], "Promote safe moped and motorcycle usage", "Create licensing pathways through training for all motorcycle riders", None, False),
            ("5.3", ["DOT"], "Promote safe moped and motorcycle usage", "Require proof of license endorsement for motorcycle purchases", None, False),
        ],
    },
    3: {
        "page": 95,
        "actions": [
            ("1.1", ["DOT", "MTA"], "Partner with MTA to build a world-class bus system", "Expand fast and reliable bus service on corridors with bus lanes", None, False),
            ("1.2", ["DOT", "MTA"], "Partner with MTA to build a world-class bus system", "Build more bus lanes and expand Transit Signal Priority (TSP) coverage", None, False),
            ("1.3", ["DOT", "MTA"], "Partner with MTA to build a world-class bus system", "Enhance bus stop accessibility and improve customer experience", None, False),
            ("1.4", ["DOT", "MTA"], "Partner with MTA to build a world-class bus system", "Diversify and expand the distribution of bus stop amenities citywide", None, False),
            ("2", ["DOT"], None, "Explore the creation of a mobility wallet for low-income New Yorkers", None, False),
            ("3", ["DOT"], None, "Expand the protected and low-stress bicycle network to all communities citywide", None, False),
            ("4", ["DOT"], None, "Make Citi Bike and e-scooter share more affordable", None, False),
            ("5", ["DOT"], None, "Expand accessible bike share and e-scooter share options", None, False),
            ("6", ["DOT"], None, "Launch the Office of Curb Management at the Department of Transportation", None, True),
            ("7", ["DOT"], None, "Expand the car share parking program", None, False),
            ("8.1", ["DOT"], "Encourage walking by improving convenience, safety, and comfort", "Build connected and accessible walking networks", None, False),
            ("8.2", ["DOT"], "Encourage walking by improving convenience, safety, and comfort", "Establish pedestrian-only and pedestrian-priority districts", None, False),
            ("9", ["DOT"], None, "Promote safer street use through public programs", None, False),
            ("10", ["DOT"], None, "Encourage walking and biking to school", None, False),
        ],
    },
    4: {
        "page": 96,
        "actions": [
            ("1.1", ["TF"], "Pursue federal action for safer vehicle standards", "A safe vehicle rating standard via NHTSA that protects pedestrians and bicyclists", None, False),
            ("1.2", ["TF"], "Pursue federal action for safer vehicle standards", "Safer NHTSA vehicle design requirements for pedestrian protection and driver visibility", None, False),
            ("1.3", ["TF"], "Pursue federal action for safer vehicle standards", "Truck safety technologies (e.g., cameras, sensors, mirrors)", None, False),
            ("2", ["TF"], None, "Advocate for state and federal legislation that empowers local oversight of autonomous vehicles", None, False),
            ("3", ["DOT"], None, "Evaluate the benefits of imposing higher tolls for larger passenger vehicles", None, False),
            ("4", ["DOT"], None, "Shift freight from heavy vehicles to safer, more sustainable modes", None, False),
        ],
    },
    5: {
        "page": 96,
        "actions": [
            ("1.1", ["DOT"], "Expand the implementation of Sammy's Law", "Create 15 MPH School Slow Zones at every eligible school location citywide", "Every eligible school location", True),
            ("1.2", ["DOT"], "Expand the implementation of Sammy's Law", "Expand 20 MPH speed limits within entire neighborhoods or other defined zones", None, True),
            ("2.1", ["DOT"], "Update roadway designs for micromobility users", "Implement Green Wave signal coordination for micromobility", None, False),
            ("2.2", ["DOT"], "Update roadway designs for micromobility users", "Enhance and expand the micromobility network", None, False),
            ("2.3", ["DOT"], "Update roadway designs for micromobility users", "Strengthen physical protection for bike lanes", None, False),
            ("2.4", ["DOT"], "Update roadway designs for micromobility users", "Expand the City's corridor and neighborhood design toolkit", None, False),
            ("3", ["DOT"], None, "Implement Hardened Daylighting or Better at a minimum of 1,000 intersections each year", "≥ 1,000 intersections per year", True),
            ("4", ["DOT"], None, "Improve quality and durability of on-street materials", None, False),
            ("5", ["DOT"], None, "Develop a highway safety toolkit to address injury hotspots", None, False),
            ("6", ["DOT"], None, "Develop a new safety design standards toolkit for roadways around schools", None, False),
            ("7", ["AGING"], None, "Research infrastructure and design improvements to support older New Yorkers", None, False),
            ("8", ["TLC", "DOT"], None, "Explore safer pickup and drop-off strategies at curbs", None, False),
            ("9", ["DOT"], None, "Implement curb management design plans to prevent dangerous illegal parking", None, False),
            ("10", ["DOT"], None, "Enhance street safety and accessibility for people with disabilities", None, False),
            ("m1", ["DOT"], None, "Complete safety treatments on all Vision Zero Priority Corridors", "Nearly 200 corridors citywide", True),
        ],
    },
    6: {
        "page": 97,
        "actions": [
            ("1", ["NYPD"], None, "Ensure all vehicles are properly registered and have valid license plates", None, False),
            ("2", ["DOT"], None, "Explore different types of automated enforcement and expand citywide", None, False),
            ("3", ["BIC"], None, "Establish new agency partnerships for joint trade waste truck enforcement operations and expand efforts to enforce compliance with safety regulations", None, False),
            ("4", ["BIC"], None, "Expand the BIC Online Portal to digitize trade waste truck inspection and safety equipment submission processes", None, False),
            ("5", ["DOT"], None, "Integrate Vision Zero lessons into citywide NYC Public Schools curriculum", None, True),
            ("6", ["DCAS"], None, "Provide City-approved driver and rider safety training curricula for businesses", None, False),
            ("7", ["DOT"], None, "Deepen connections with the public through e-bike and moped user outreach and education programs", None, False),
            ("8", ["DANY", "DOT", "NYPD"], None, "Create a comprehensive safety education campaign focused on laws, legislative changes, and tailored neighborhood outreach", None, False),
            ("9", ["DOT"], None, "Provide regular Vision Zero updates to the news media", None, False),
            ("10", ["DOT"], None, "Develop strategic communication based on current safety data trends", None, False),
            ("11", ["DOT"], None, "Leverage City assets to disseminate information on traffic safety projects and policies", None, False),
            ("12", ["HH"], None, "Leverage public health venues to deliver Vision Zero messages and engage communities", None, False),
            ("13", ["DOHMH"], None, "Develop messaging connecting Vision Zero priorities to broader health benefits, including physical activity through activity-friendly routes", None, False),
            ("14", ["HH"], None, "Integrate Vision Zero messaging into existing injury prevention efforts", None, False),
            ("15", ["TF"], None, "Coordinate with neighboring municipalities to share Vision Zero practices and regional messaging", None, False),
            ("16", ["DOT", "TF"], None, "Publish studies and reports on Vision Zero enforcement best practices", None, False),
            ("17", ["TF"], None, "Foster connections with grassroots Vision Zero community groups", None, False),
            ("18", ["AGING"], None, "Support neighborhood groups in NORCs and other older adult priority areas", None, False),
            ("19", ["AGING"], None, "Partner with DOT's Street Education Outreach team to train Older Adult Center staff as local safety advocates", None, False),
            ("20", ["MTA"], None, "Update the MTA Vision Zero training curriculum for bus operators", None, False),
        ],
    },
    7: {
        "page": 98,
        "actions": [
            ("1.1", ["DOT", "DOHMH"], "Focus future traffic safety research on key areas", "Motorized two-wheelers", None, False),
            ("1.2", ["DOT"], "Focus future traffic safety research on key areas", "Dangerous pedestrian behaviors", None, False),
            ("1.3", ["DANY", "DOT"], "Focus future traffic safety research on key areas", "Impaired and intoxicated driving", None, False),
            ("1.4", ["DOT", "MOPD", "DOHMH"], "Focus future traffic safety research on key areas", "Crash patterns and injury trends for people with disabilities", None, False),
            ("1.5", ["DOT"], "Focus future traffic safety research on key areas", "Safety implications of electric vehicles", None, False),
            ("1.6", ["DOT", "MTA"], "Focus future traffic safety research on key areas", "MTA bus crashes", None, False),
            ("1.7", ["TLC"], "Focus future traffic safety research on key areas", "Fatigued driving and crash risk among taxi and for-hire vehicle drivers", None, False),
            ("2", ["TF"], None, "Create a Unified Vision Zero Data Warehouse", None, True),
            ("3", ["DOT"], None, "Develop citywide models of volume and exposure for all road users", None, False),
            ("4", ["DOT"], None, "Expand access to user-friendly online safety data and tools", None, False),
            ("5", ["DOT"], None, "Implement connected streetlights for rapid response to outages", None, True),
            ("6", ["MTA"], None, "Pilot and study bus safety technologies", None, False),
        ],
    },
    8: {
        "page": 99,
        "actions": [
            ("1.1", ["DCAS"], "Implement existing safety technologies in all City fleet vehicles", "Expand use of Intelligent Speed Assistance", None, True),
            ("1.2", ["DCAS"], "Implement existing safety technologies in all City fleet vehicles", "Install lane departure warning systems", None, True),
            ("1.3", ["DCAS"], "Implement existing safety technologies in all City fleet vehicles", "Install audible alerts on trucks", None, True),
            ("1.4", ["DCAS"], "Implement existing safety technologies in all City fleet vehicles", "Install automated emergency braking systems", None, True),
            ("2", ["TLC"], None, "Study adoption and safety impacts of in-vehicle technologies across the TLC fleet", None, False),
            ("3", ["BIC"], None, "Incentivize safer vehicles in the regulated trade waste industry", None, False),
            ("4", ["DCAS"], None, "Procure trucks with high-vision cabs and alternative designs wherever feasible", None, False),
            ("5", ["DCAS"], None, "Expand fleet safety driver training to contracted drivers and school bus operators", None, False),
            ("6", ["DCAS"], None, "Leverage the City fleet's procurement power to encourage manufacturers to improve and expand vehicle safety features", None, False),
            ("7", ["DCAS"], None, "Install surround cameras or higher-vision designs in all City and City-contracted vehicles", None, False),
            ("8", ["BIC", "DSNY", "DOT"], None, "Continue to ensure DSNY-contracted waste haulers meet safety goals", None, False),
            ("9.1", ["MTA"], "MTA Bus Collision and Customer Crash Reduction Plan", "Audit bus stops, terminals, and routes for hazards", None, False),
            ("9.2", ["MTA"], "MTA Bus Collision and Customer Crash Reduction Plan", "Update training programs to reflect current collision trends", None, False),
            ("10", ["MTA"], None, "Deploy four state-of-the-art MTA bus simulators to enhance safety training", None, False),
            ("11", ["MTA"], None, "Expand use of E-Mirrors and Collision Warning System", None, False),
            ("12", ["MTA"], None, "Expand the use of Bus Operator Full Enclosure on new bus purchases", None, False),
        ],
    },
}

# Actions building on programs already underway at announcement, per press coverage.
IN_PROGRESS_AT_LAUNCH = {
    "vz-g5-3": ("Builds on DOT's existing intersection daylighting program; the plan raises it to a 1,000/year floor.", STREETSBLOG),
    "vz-g3-3": ("Protected bike network expansion is an ongoing DOT program the plan commits to extending citywide.", STREETSBLOG),
}


def main() -> None:
    out = []
    for goal, spec in GOALS.items():
        for suffix, agencies, group, title, target, marquee in spec["actions"]:
            cid = f"vz-g{goal}-{suffix}"
            status, note, source = "not_started", "Announced in Vision Zero Reimagined", PRESS_RELEASE
            if cid in IN_PROGRESS_AT_LAUNCH:
                status = "in_progress"
                note, source = IN_PROGRESS_AT_LAUNCH[cid]
            out.append({
                "id": cid,
                "title": title,
                "group": group,
                "goal": goal,
                "agencies": agencies,
                "target": target,
                "marquee": marquee,
                "page": 11 if suffix == "m1" else spec["page"],
                "status": status,
                "updates": [{"date": ANNOUNCED, "status": status, "note": note, "source": source}],
            })
    path = pathlib.Path(__file__).resolve().parent.parent / "data" / "commitments.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"Wrote {len(out)} commitments to {path}")


if __name__ == "__main__":
    main()
