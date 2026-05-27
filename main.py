from campaign import Campaign
from village import create_starting_village, BuildingType
from roster import generate_starting_roster, create_starting_ship, print_roster
from save_manager import (
    save_campaign,
    load_campaign,
    save_exists,
    save_filename_for_slot,
)
from models import CrewRole, FavoredGod
from items import EquipmentSlot, ItemQuality
import time
import random

EVENT_DELAY = 1.0

def display_name(viking) -> str:
    if hasattr(viking, "display_name"):
        return viking.display_name()
    return viking.name


def debug_event_counter() -> None:
    from collections import Counter
    from events import JOB_TYPE_EVENTS

    print("\nEVENT COUNTER")
    print("-" * 80)

    total_counter = Counter()

    for job_type, event_pool in JOB_TYPE_EVENTS.items():
        pool_counter = Counter(event.__name__ for event in event_pool)

        print(f"\n{job_type.value}")
        print("-" * 40)

        for event_name, count in pool_counter.most_common():
            clean_name = event_name.replace("event_", "").replace("_", " ").title()
            print(f"{clean_name:35} x{count}")

        total_counter.update(pool_counter)

    print("\nTOTAL EVENT FREQUENCY")
    print("-" * 80)

    for event_name, count in total_counter.most_common():
        clean_name = event_name.replace("event_", "").replace("_", " ").title()
        print(f"{clean_name:35} x{count}")

def debug_menu(campaign: Campaign) -> None:
    while True:
        print("\nDEBUG MENU")
        print("1. Advance 1 Month")
        print("2. Add 1000 Silver")
        print("3. Gain 100 Food")
        print("4. Gain 100 Ship Timber")
        print("5. Gain 100 Fine Metal")
        print("6. Gain 10 Thralls")
        print("7. Set Build Timers to 1 Week")
        print("8. Event Counter")
        print("9. Back")
        print("I. Toggle injuries")
        print("L. Set non-Jarl active crew loyalty to 5")
        print("X. Fatal injury test")
        print("Y. Advance 1 year without upkeep")
        print("Z. Toggle birthday processing")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            campaign.advance_weeks(4)
            print("Advanced 1 month.")

        elif choice == "2":
            campaign.silver += 1000
            print("Added 1000 silver.")


        elif choice == "3":
            campaign.food += 100
            print("Added 100 food.")
            
        elif choice == "4":
            campaign.ship_timber += 100
            print("Added 100 ship timber.")   

        elif choice == "5":
            campaign.fine_metal += 100
            print("Added 100 fine metal.")    

        elif choice == "6":
            campaign.thralls += 10
            print("Added 10 thralls.")

        elif choice == "7":
            updated = 0

            for tile in campaign.village.tiles.values():
                building = tile.building

                if not building:
                    continue

                if building.is_under_construction and building.weeks_remaining > 1:
                    building.weeks_remaining = 1
                    updated += 1

            print(f"Set {updated} active build/upgrade timers to 1 week.")
            
        elif choice == "8":
            debug_event_counter()
            

        elif choice == "9":
            return
            
        elif choice.lower() == "i":
            campaign.debug_disable_injuries = (
                not campaign.debug_disable_injuries
            )

            if campaign.debug_disable_injuries:
                print("Injuries disabled.")
            else:
                print("Injuries enabled.") 

        elif choice.lower() == "l":
            updated = 0

            for viking in campaign.get_active_crew_list():
                if viking.is_player:
                    continue

                viking.loyalty = 5
                updated += 1

            print(f"Set loyalty to 5 for {updated} active non-Jarl crew.")                
            
        elif choice.lower() == "x":
            from injury import (
                InjuryType,
                InjurySeverity,
                get_templates,
                apply_injury_to_viking,
            )

            crew = campaign.get_active_crew_list()

            test_targets = [
                viking for viking in crew
                if not viking.is_player
            ]

            if not test_targets:
                print("No non-Jarl active crew available for fatal injury test.")
                continue

            victim = random.choice(test_targets)
            fatal_templates = get_templates(InjuryType.COMBAT, InjurySeverity.FATAL)
            injury = random.choice(fatal_templates)

            class DebugResult:
                def __init__(self):
                    self.log = []
                    self.injuries = []
                    self.deaths = []
                    self.permanent_injuries = []
                    self.injury_records = []

            class DebugJob:
                name = "Debug Fatal Injury Test"
                job_id = "debug_fatal_injury_test"

            result = DebugResult()
            job = DebugJob()

            apply_injury_to_viking(
                result=result,
                viking=victim,
                injury=injury,
                job=job,
                witnesses=crew,
            )

            for record in getattr(result, "injury_records", []):
                campaign.add_saga_entry(
                    entry_type="death",
                    text=(
                        f"{record['viking_name']} was killed by "
                        f"{record['injury_name']} during {record['job_name']}."
                    ),
                    viking_ids=[record["viking_id"]],
                    job_id=record["job_id"],
                )

            campaign.remove_dead_from_ship()

            print("\n".join(result.log))  

        elif choice.lower() == "y":
            logs = campaign.advance_one_year_debug_no_upkeep()

            print("\nAdvanced 1 year without upkeep.")

            if logs:
                print("\nDevelopment / birthday logs:")
                for log in logs:
                    print(log)

        elif choice.lower() == "z":
            campaign.debug_skip_birthdays = not campaign.debug_skip_birthdays

            status = "OFF" if campaign.debug_skip_birthdays else "ON"
            print(f"Birthday processing is now {status}.")

        else:
            print("Invalid choice.")

def sagas_menu(campaign: Campaign) -> None:
    while True:
        years = sorted({
            entry.year
            for entry in campaign.saga_entries
        })

        if not years:
            years = [campaign.year]

        print("\nSAGAS")
        print("-" * 80)

        for i, year in enumerate(years, start=1):
            print(f"{i}. Year {year}")

        print(f"{len(years) + 1}. Back")

        choice = input("\nChoose: ").strip()

        if not choice.isdigit():
            print("Invalid choice.")
            continue

        index = int(choice) - 1

        if index == len(years):
            return

        if index < 0 or index >= len(years):
            print("Invalid choice.")
            continue

        selected_year = years[index]

        entries = [
            entry for entry in campaign.saga_entries
            if entry.year == selected_year
        ]

        print(f"\nTHE SAGA - YEAR {selected_year}")
        print("-" * 80)

        if not entries:
            print("No saga entries recorded for this year.")
            continue

        entries.sort(key=lambda entry: (entry.month, entry.week))

        for entry in entries:
            print(
                f"Year {entry.year}, Month {entry.month}, Week {entry.week}: "
                f"{entry.text}"
            )

def print_locations(campaign: Campaign) -> list:
    locations = campaign.get_discovered_locations()

    print("\nDISCOVERED LOCATIONS")
    print("-" * 80)

    if not locations:
        print("No discovered locations.")
        return []

    for i, location in enumerate(locations, start=1):
        print(
            f"{i}. {location.name} | {location.region.value} | "
            f"Range {location.required_range}"
        )
        print(f"   {location.description}")

    return locations

def print_injury_report(campaign: Campaign) -> None:
    injured = [
        viking for viking in campaign.vikings.values()
        if viking.active_injuries
    ]

    print("\nINJURY REPORT")
    print("-" * 100)

    if not injured:
        print("No active injuries.")
        return

    for viking in injured:
        print(f"\n{display_name(viking)} | {viking.viking_class.value} | {viking.status.value}")

        for injury in viking.active_injuries:
            mods = []

            for stat, value in injury.stat_modifiers.items():
                if value != 0:
                    mods.append(f"{stat} {value:+}")

            mod_text = ", ".join(mods) if mods else "No temporary stat penalty"

            deploy_text = (
                "Can deploy"
                if injury.can_deploy_while_injured
                else "Cannot deploy"
            )

            recovery_text = (
                f"{injury.weeks_remaining} weeks remaining"
                if injury.recovery_started
                else f"{injury.weeks_remaining} weeks once recovery starts"
            )

            pending_title_text = (
                f" | Pending title: {injury.pending_title}"
                if injury.pending_title
                else ""
            )

            print(
                f"  - {injury.name}: {recovery_text} | "
                f"{deploy_text} | {mod_text}{pending_title_text}"
            )

def print_jobs_for_location(campaign: Campaign, location) -> list:
    jobs = campaign.get_available_jobs(location)

    print(f"\nAVAILABLE JOBS - {location.name}")
    print("-" * 80)

    if not jobs:
        print("No jobs available here.")
        return []

    for i, job in enumerate(jobs, start=1):
        employer_text = job.employer if job.employer else "Independent"
        expected_crew_by_difficulty = {
            1: 5,
            2: 6,
            3: 7,
            4: 8,
            5: 10,
            6: 12,
            7: 15,
            8: 18,
            9: 22,
            10: 26,
        }

        expected_crew = expected_crew_by_difficulty.get(
            max(1, min(10, job.difficulty)),
            26,
        )

        print(
            f"{i}. {job.name} | {job.job_type.value} | "
            f"{job.duration_weeks} weeks | Difficulty {job.difficulty} | "
            f"Expected Crew {expected_crew} | "
            f"Danger {job.danger} | Employer: {employer_text} | "
            f"Food Cost: {campaign.calculate_food_cost(job)}"
        )
        reward_parts = []

        if job.guaranteed_silver > 0:
            reward_parts.append(f"{job.guaranteed_silver} silver")

        if job.guaranteed_food > 0:
            reward_parts.append(f"{job.guaranteed_food} food")

        if getattr(job, "guaranteed_ship_timber", 0) > 0:
            reward_parts.append(f"{job.guaranteed_ship_timber} ship timber")

        if getattr(job, "guaranteed_fine_metal", 0) > 0:
            reward_parts.append(f"{job.guaranteed_fine_metal} fine metal")

        if getattr(job, "guaranteed_thralls", 0) > 0:
            reward_parts.append(f"{job.guaranteed_thralls} thralls")

        if job.reward_renown > 0:
            reward_parts.append(f"{job.reward_renown} renown")

        reward_text = ", ".join(reward_parts) if reward_parts else "None"

        print(f"   Guaranteed Rewards: {reward_text}")
        print(f"   {job.description}")

    return jobs


def jobs_menu(campaign: Campaign) -> None:
    while True:
        print("\nJOBS")
        print("1. View Discovered Locations")
        print("2. Take a Job")
        print("3. Back")
        print("4. Fast Sim Job")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            print_locations(campaign)

        elif choice == "2":
            locations = print_locations(campaign)

            if not locations:
                continue

            location_choice = input("\nChoose location number, or B to go back: ").strip()

            if location_choice.lower() == "b":
                continue

            if not location_choice.isdigit():
                print("Invalid choice.")
                continue

            location_index = int(location_choice) - 1

            if location_index < 0 or location_index >= len(locations):
                print("Invalid location number.")
                continue

            location = locations[location_index]
            jobs = print_jobs_for_location(campaign, location)

            if not jobs:
                continue

            job_choice = input("\nChoose job number, or B to go back: ").strip()

            if job_choice.lower() == "b":
                continue

            if not job_choice.isdigit():
                print("Invalid choice.")
                continue

            job_index = int(job_choice) - 1

            if job_index < 0 or job_index >= len(jobs):
                print("Invalid job number.")
                continue

            success, message = campaign.take_job(jobs[job_index])

            print("\nEXPEDITION RESULT")
            print("-" * 80)

            for line in message.split("\n"):
                print(line)
                time.sleep(EVENT_DELAY)

        elif choice == "3":
            return

        elif choice == "4":
            locations = print_locations(campaign)

            if not locations:
                continue

            location_choice = input("\nChoose location number, or B to go back: ").strip()

            if location_choice.lower() == "b":
                continue

            if not location_choice.isdigit():
                print("Invalid choice.")
                continue

            location_index = int(location_choice) - 1

            if location_index < 0 or location_index >= len(locations):
                print("Invalid location number.")
                continue

            location = locations[location_index]
            jobs = print_jobs_for_location(campaign, location)

            if not jobs:
                continue

            job_choice = input("\nChoose job number, or B to go back: ").strip()

            if job_choice.lower() == "b":
                continue

            if not job_choice.isdigit():
                print("Invalid choice.")
                continue

            job_index = int(job_choice) - 1

            if job_index < 0 or job_index >= len(jobs):
                print("Invalid job number.")
                continue

            success, message = campaign.take_job(jobs[job_index])

            print(
                f"\nFast sim complete: {'SUCCESS' if success else 'FAILURE'} - "
                f"{jobs[job_index].name}"
            )

        else:
            print("Invalid choice.")


def print_crew_summary(campaign: Campaign) -> None:
    crew = campaign.get_active_crew_list()

    print("\nCREW SUMMARY")
    print("-" * 80)

    if not crew:
        print("No active crew.")
        return

    score_methods = [
        ("Combat", "combat_score"),
        ("Raiding", "raiding_score"),
        ("Skirmish", "skirmish_score"),
        ("Command", "command_score"),
        ("Morale", "morale_score"),
        ("Scouting", "scouting_score"),
        ("Sailing", "sailing_score"),
        ("Navigation", "navigation_score"),
        ("Evasion", "evasion_score"),
        ("Endurance", "endurance_score"),
        ("Survival", "survival_score"),
        ("Social", "social_score"),
    ]

    print(f"Active Crew: {len(crew)}")
    
    crew_strength = sum(
        (
            viking.raiding_score()
            + viking.sailing_score()
            + viking.command_score()
            + viking.survival_score()
        ) // 4
        for viking in crew
        if viking.is_available()
    )

    print(f"Total Crew Strength: {crew_strength}")    

    for label, method_name in score_methods:
        scores = [
            getattr(viking, method_name)()
            for viking in crew
            if viking.is_available()
        ]

        total = sum(scores)
        average = total // len(scores) if scores else 0

        top_half_average = 0

        if scores:
            sorted_scores = sorted(scores, reverse=True)
            top_count = max(1, round(len(sorted_scores) * 0.5))
            top_scores = sorted_scores[:top_count]
            top_half_average = sum(top_scores) // len(top_scores)

        print(
            f"{label:10} | Total {total:4} | "
            f"Average {average:3} | Top Half Avg {top_half_average:3}"
        )

def print_traited_vikings(campaign: Campaign) -> None:
    vikings = [
        viking for viking in campaign.vikings.values()
        if viking.traits
        and viking.status not in {
            type(viking.status).DEAD,
            type(viking.status).DESERTED,
            type(viking.status).RETIRED,
        }
    ]

    print("\nVIKINGS WITH TRAITS")
    print("-" * 100)

    if not vikings:
        print("No vikings with traits.")
        return

    vikings.sort(key=lambda viking: (not viking.is_player, viking.name))

    for i, viking in enumerate(vikings, start=1):
        trait_text = ", ".join(
            f"{trait.name} ({trait.description})"
            for trait in viking.traits
        )

        print(
            f"{i}. {display_name(viking)} | "
            f"{viking.viking_class.value} | "
            f"{trait_text}"
        )

def print_crew_growth(campaign: Campaign) -> None:
    crew = [
        viking for viking in campaign.vikings.values()
        if viking.status not in {
            type(viking.status).DEAD,
            type(viking.status).DESERTED,
            type(viking.status).RETIRED,
        }
    ]

    crew.sort(key=lambda viking: (not viking.is_player, viking.name))
    
    print("\nCREW GROWTH")
    print("-" * 160)

    if not crew:
        print("No active crew.")
        return

    stats = [
        "might",
        "skill",
        "cunning",
        "leadership",
        "courage",
        "vitality",
        "agility",
        "seamanship",
    ]

    labels = {
        "might": "MGT",
        "skill": "SKL",
        "cunning": "CUN",
        "leadership": "LDR",
        "courage": "CRG",
        "vitality": "VIT",
        "agility": "AGI",
        "seamanship": "SEA",
    }

    def stat_growth_text(viking, stat_name: str) -> str:
        current = getattr(viking, stat_name)
        original = viking.original_stats.get(stat_name, current)
        change = current - original

        if change == 0:
            return str(current)

        return f"{current}({change:+})"

    for viking in crew:
        stat_parts = [
            f"{labels[stat]} {stat_growth_text(viking, stat)}"
            for stat in stats
        ]

        print(
            f"{display_name(viking):24} "
            f"Age {viking.age:2} | "
            + " ".join(stat_parts)
        )

def crew_menu(campaign: Campaign) -> None:
    while True:
        print("1. View Active Crew")
        print("2. View Crew Growth")
        print("3. View Reserves")
        print("4. View Injured Vikings")
        print("5. View Recruit Pool")
        print("6. Hire Recruit")
        print("7. View Odin's Hall")
        print("8. View Retired Vikings")
        print("9. View Vikings with Traits")
        print("10. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            active_crew = {
                viking.viking_id: viking
                for viking in campaign.get_active_crew_list()
            }

            print_crew_summary(campaign)
            print_roster(active_crew, campaign.inventory)
            
        elif choice == "2":
            print_crew_growth(campaign)    

        elif choice == "3":
            reserves = campaign.get_reserve_vikings()
            print("\nRESERVES")
            print("-" * 80)

            if not reserves:
                print("No reserve vikings.")
            else:
                for i, viking in enumerate(reserves, start=1):
                    print(
                        f"{i}. {display_name(viking)} | "
                        f"{viking.status.value} | "
                        f"{viking.role.value} | "
                        f"{viking.viking_class.value} | "
                        f"Age {viking.age}"
                    )
                    
        elif choice == "4":
            injured = campaign.get_injured_vikings()

            print("\nINJURED VIKINGS")
            print("-" * 80)

            if not injured:
                print("No injured vikings.")
            else:
                for i, viking in enumerate(injured, start=1):
                    injuries = ", ".join(viking.injuries) or "Injured"
                    print(
                        f"{i}. {display_name(viking)} | "
                        f"{viking.viking_class.value} | "
                        f"{injuries} | "
                        f"{viking.injury_weeks_remaining} weeks remaining"
                    )                    

        elif choice == "5":
            campaign.refresh_recruit_pool()

            print("\nRECRUIT POOL")
            print("-" * 100)

            if not campaign.recruit_pool.candidates:
                print("No recruits available.")
            else:
                for i, candidate in enumerate(campaign.recruit_pool.candidates, start=1):
                    v = candidate.viking
                    print(
                        f"{i}. {v.name} | "
                        f"[OVR {v.overall_grade()} / POT {v.potential_overall_grade()}] | "
                        f"Age {v.age} | "
                        f"{v.viking_class.value} | "
                        f"Favored: {v.favored_god.value} | "
                        f"MGT {v.might} SKL {v.skill} CUN {v.cunning} "
                        f"LDR {v.leadership} CRG {v.courage} "
                        f"VIT {v.vitality} AGI {v.agility} "
                        f"SEA {v.seamanship} LOY {v.loyalty} | "
                        f"Waiting {candidate.seasons_waiting} seasons"
                    )

        elif choice == "6":
            campaign.refresh_recruit_pool()

            recruits = campaign.recruit_pool.candidates

            if not recruits:
                print("No recruits available.")
                continue

            for i, candidate in enumerate(recruits, start=1):
                v = candidate.viking
                print(f"{i}. {v.name} | {v.viking_class.value}")

            recruit_choice = input("\nChoose recruit: ").strip()

            if not recruit_choice.isdigit():
                print("Invalid choice.")
                continue

            index = int(recruit_choice) - 1

            if index < 0 or index >= len(recruits):
                print("Invalid recruit number.")
                continue

            success, message = campaign.hire_recruit(recruits[index].candidate_id)
            print(message)

        elif choice == "7":
            print("\nODIN'S HALL")
            print("-" * 80)

            if not campaign.odins_hall:
                print("No fallen vikings yet.")
            else:
                for entry in campaign.odins_hall:
                    print(entry["text"])

        elif choice == "8":
            print("\nRETIRED VIKINGS")
            print("-" * 80)

            if not campaign.retired_vikings:
                print("No retired vikings yet.")
            else:
                for entry in campaign.retired_vikings:
                    print(entry["text"])

        elif choice == "9":
            print_traited_vikings(campaign)

        elif choice == "10":
            return


def ship_upgrade_menu(campaign: Campaign) -> None:
    from ship_upgrades import ShipPart, get_next_ship_upgrade

    parts = [
        ShipPart.HULL,
        ShipPart.CARGO,
        ShipPart.CREW,
        ShipPart.SAIL,
        ShipPart.NAVIGATION,
    ]

    while True:
        print("\nSHIP UPGRADES")
        print("-" * 100)

        print(
            f"{campaign.ship.name} | "
            f"Range {campaign.ship.range} | "
            f"Hull {campaign.ship.hull}/{campaign.ship.max_hull} | "
            f"Cargo {campaign.ship.cargo_capacity} | "
            f"Crew {len(campaign.ship.crew)}/{campaign.ship.max_crew} | "
            f"Sail {campaign.ship.sail} | "
            f"Navigation {campaign.ship.navigation}"
        )

        print(
            f"\nResources: {campaign.silver} silver | "
            f"{campaign.ship_timber} ship timber | "
            f"{campaign.fine_metal} fine metal"
        )

        if campaign.pending_ship_upgrade_part:
            print(
                f"\nCurrent upgrade: {campaign.pending_ship_upgrade_name} "
                f"({campaign.pending_ship_weeks_remaining} weeks remaining)"
            )

        print("")

        available_options = []

        for part in parts:
            current_level = campaign.ship.get_part_level(part)
            upgrade = get_next_ship_upgrade(part, current_level)

            if not upgrade:
                print(f"- {part.value}: Level {current_level} / MAX")
                continue

            available_options.append((part, upgrade))

            print(
                f"{len(available_options)}. {upgrade.name} | "
                f"{part.value} Lv.{current_level} -> Lv.{upgrade.level} | "
                f"Cost: {upgrade.silver_cost} silver, "
                f"{upgrade.ship_timber_cost} timber, "
                f"{upgrade.fine_metal_cost} fine metal | "
                f"Time: {upgrade.build_weeks}w | "
                f"Requires Shipwright Lv.{upgrade.required_shipyard_level}, "
                f"Woodwright Lv.{upgrade.required_carpenters_hut_level}"
            )
            print(f"   {upgrade.description}")

        print(f"{len(available_options) + 1}. Back")

        choice = input("\nChoose upgrade: ").strip()

        if not choice.isdigit():
            print("Invalid choice.")
            continue

        index = int(choice)

        if index == len(available_options) + 1:
            return

        if not 1 <= index <= len(available_options):
            print("Invalid upgrade number.")
            continue

        part, upgrade = available_options[index - 1]
        success, message = campaign.start_ship_upgrade(part)
        print(message)

def ship_menu(campaign: Campaign) -> None:
    while True:
        print("\nSHIP")
        print("1. View Ship Status")
        print("2. Add Reserve to Ship")
        print("3. Remove Crew from Ship")
        print("4. Assign Captain")
        print("5. Repair Ship")
        print("6. Upgrade Ship")
        print("7. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            print(campaign.summary())

        elif choice == "2":
            reserves = campaign.get_reserve_vikings()
            if not reserves:
                print("No reserve vikings available.")
                continue

            for i, viking in enumerate(reserves, start=1):
                print(f"{i}. {viking.name} | {viking.status.value} | {viking.role.value}")

            choice_num = input("\nChoose reserve to add: ").strip()
            if not choice_num.isdigit():
                print("Invalid choice.")
                continue

            index = int(choice_num) - 1
            if index < 0 or index >= len(reserves):
                print("Invalid reserve number.")
                continue

            success, message = campaign.add_reserve_to_ship(reserves[index].viking_id)
            print(message)
            
        elif choice == "3":
            crew = campaign.get_ship_crew()

            if not crew:
                print("No crew on ship.")
                continue

            for i, viking in enumerate(crew, start=1):
                print(
                    f"{i}. {viking.name} | "
                    f"{viking.status.value} | "
                    f"{viking.role.value} | "
                    f"{viking.viking_class.value}"
                )

            choice_num = input("\nChoose crew member to remove: ").strip()

            if not choice_num.isdigit():
                print("Invalid choice.")
                continue

            index = int(choice_num) - 1

            if index < 0 or index >= len(crew):
                print("Invalid crew number.")
                continue

            success, message = campaign.remove_crew_member_from_ship(
                crew[index].viking_id
            )
            print(message)    

        elif choice == "4":
            crew = campaign.get_ship_crew()
            for i, viking in enumerate(crew, start=1):
                print(
                    f"{i}. {viking.name} | Role: {viking.role.value} | "
                    f"Class: {viking.viking_class.value}"
                )

            choice_num = input("\nChoose crew member: ").strip()
            if not choice_num.isdigit():
                print("Invalid choice.")
                continue

            index = int(choice_num) - 1
            if index < 0 or index >= len(crew):
                print("Invalid crew number.")
                continue

            roles = list(CrewRole)
            for i, role in enumerate(roles, start=1):
                print(f"{i}. {role.value}")

            role_choice = input("\nChoose new role: ").strip()
            if not role_choice.isdigit():
                print("Invalid role choice.")
                continue

            role_index = int(role_choice) - 1
            if role_index < 0 or role_index >= len(roles):
                print("Invalid role number.")
                continue

            success, message = campaign.assign_crew_role(
                crew[index].viking_id,
                roles[role_index],
            )
            print(message)

        elif choice == "5":
            success, message = campaign.repair_ship_at_shipyard()
            print(message)

        elif choice == "6":
            ship_upgrade_menu(campaign)

        elif choice == "7":
            return
            
            
def trader_menu(campaign: Campaign) -> None:
    from items import TRADER_STOCK

    while True:
        print("\nTRADER")
        print("1. Buy")
        print("2. Sell")
        print("3. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            print("\nTRADER STOCK")
            print("-" * 80)

            for i, item in enumerate(TRADER_STOCK, start=1):
                slot_text = item.slot.value if item.slot else "-"
                print(
                    f"{i}. {item.name} | {item.item_type.value} | "
                    f"Slot: {slot_text} | Value {item.value}"
                )

            buy_choice = input("\nChoose item to buy: ").strip()

            if not buy_choice.isdigit():
                print("Invalid choice.")
                continue

            index = int(buy_choice) - 1

            if index < 0 or index >= len(TRADER_STOCK):
                print("Invalid item number.")
                continue

            success, message = campaign.buy_trader_item(TRADER_STOCK[index])
            print(message)

        elif choice == "2":
            items = campaign.get_unequipped_items()

            print("\nSELL UNEQUIPPED ITEMS")
            print("-" * 80)

            if not items:
                print("No unequipped items to sell.")
                continue

            for i, item in enumerate(items, start=1):
                sale_value = max(1, item.value // 2)
                slot_text = item.slot.value if item.slot else "-"
                print(
                    f"{i}. {item.name} | {item.item_type.value} | "
                    f"Slot: {slot_text} | Sell Value {sale_value}"
                )

            sell_choice = input("\nChoose item to sell: ").strip()

            if not sell_choice.isdigit():
                print("Invalid choice.")
                continue

            index = int(sell_choice) - 1

            if index < 0 or index >= len(items):
                print("Invalid item number.")
                continue

            success, message = campaign.sell_item_to_trader(items[index].item_id)
            print(message)

        elif choice == "3":
            return

        else:
            print("Invalid choice.")            


def village_menu(campaign: Campaign) -> None:
    while True:
        print("\nVILLAGE")
        print("1. View Village")
        print("2. Build Facility")
        print("3. Upgrade Building")
        print("4. Purchase New Tile")
        print("5. Trader")
        print("6. Conquer New Tile Debug")
        print("7. Injury Report - Herbalist's Hut")
        print("8. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            print("\n" + campaign.village.summary())

        elif choice == "2":
            buildable = [
                BuildingType.FARM,
                BuildingType.FLETCHER,
                BuildingType.GREAT_HALL,
                BuildingType.SHRINE_OF_ODIN,
                BuildingType.HERBALISTS_HUT,
                BuildingType.CARPENTERS_HUT,
                BuildingType.HUNTERS_SHACK,
                BuildingType.SEERS_HUT,
                BuildingType.TRAINING_GROUNDS,
                BuildingType.THRALL_QUARTERS,
                BuildingType.SMITHY,
                BuildingType.MINE,
            ]

            print("\nBUILD FACILITY")
            print("-" * 80)

            for i, building_type in enumerate(buildable, start=1):
                print(f"{i}. {building_type.value}")

            building_choice = input("\nChoose building: ").strip()
            if not building_choice.isdigit():
                print("Invalid choice.")
                continue

            building_index = int(building_choice) - 1
            if building_index < 0 or building_index >= len(buildable):
                print("Invalid building number.")
                continue

            x_text = input("Tile X: ").strip()
            y_text = input("Tile Y: ").strip()

            if not x_text.isdigit() or not y_text.isdigit():
                print("Invalid coordinates.")
                continue

            success, message = campaign.build_village_facility(
                int(x_text),
                int(y_text),
                buildable[building_index],
            )

            print(message)

        elif choice == "3":
            x_text = input("Tile X to upgrade: ").strip()
            y_text = input("Tile Y to upgrade: ").strip()

            if not x_text.isdigit() or not y_text.isdigit():
                print("Invalid coordinates.")
                continue

            success, message = campaign.upgrade_village_building(
                int(x_text),
                int(y_text),
            )

            print(message)

        elif choice == "4":
            success, message = campaign.purchase_village_tile()
            print(message)

        elif choice == "5":
            trader_menu(campaign)

        elif choice == "6":
            success, message = campaign.conquer_village_tile_debug()
            print(message)

        elif choice == "7":
            print_injury_report(campaign)

        elif choice == "8":
            return


def save_menu(campaign: Campaign) -> Campaign:
    while True:
        print("\nSAVE / LOAD")
        print("1. Save Game")
        print("2. Load Game")
        print("3. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            slot = input("Save slot number: ").strip()
            filename = save_filename_for_slot(slot)
            save_path = save_campaign(campaign, filename)
            print(f"Game saved to {save_path}.")

        elif choice == "2":
            slot = input("Load slot number: ").strip()
            filename = save_filename_for_slot(slot)

            if not save_exists(filename):
                print(f"No save found in slot {slot}.")
                continue

            campaign = load_campaign(filename)
            print(f"Loaded save slot {slot}.")

        elif choice == "3":
            return campaign
            
            
def inventory_menu(campaign: Campaign) -> None:
    while True:
        print("\nINVENTORY")
        print("1. View Inventory")
        print("2. Equip Item")
        print("3. Unequip Item")
        print("4. Auto Equip Best Items")
        print("5. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            items = campaign.get_inventory_list()

            equipped_ids = set()

            for viking in campaign.vikings.values():
                equipped_ids.update([
                    viking.equipment.armor,
                    viking.equipment.helm,
                    viking.equipment.primary_weapon,
                    getattr(viking.equipment, "secondary_weapon", None),
                    viking.equipment.shield,
                ])

            equipped_ids.discard(None)

            equipped_items = [
                item for item in items
                if item.item_id in equipped_ids
            ]

            unequipped_items = [
                item for item in items
                if item.item_id not in equipped_ids
            ]

            print("\nEQUIPPED ITEMS")
            print("-" * 80)

            if not equipped_items:
                print("No equipped items.")
            else:
                for item in equipped_items:
                    owner_name = "Unknown"

                    for viking in campaign.vikings.values():
                        if item.item_id in {
                            viking.equipment.armor,
                            viking.equipment.helm,
                            viking.equipment.primary_weapon,
                            getattr(viking.equipment, "secondary_weapon", None),
                            viking.equipment.shield,
                        }:
                            owner_name = display_name(viking)
                            break

                    slot_text = item.slot.value if item.slot else "-"
                    print(
                        f"{item.name} | {slot_text} | "
                        f"Equipped by: {owner_name} | Value {item.value}"
                    )

            print("\nUNEQUIPPED ITEMS")
            print("-" * 80)

            if not unequipped_items:
                print("No unequipped items.")
            else:
                for i, item in enumerate(unequipped_items, start=1):
                    slot_text = item.slot.value if item.slot else "-"
                    print(
                        f"{i}. {item.name} | {item.item_type.value} | "
                        f"Slot: {slot_text} | Value {item.value}"
                    )

        elif choice == "2":
            vikings = list(campaign.vikings.values())
            items = [item for item in campaign.get_inventory_list() if item.is_equippable()]

            if not vikings:
                print("No vikings.")
                continue

            if not items:
                print("No equippable items.")
                continue

            print("\nVIKINGS")
            for i, viking in enumerate(vikings, start=1):
                print(f"{i}. {display_name(viking)} | {viking.viking_class.value}")

            v_choice = input("\nChoose viking: ").strip()
            if not v_choice.isdigit():
                print("Invalid choice.")
                continue

            v_index = int(v_choice) - 1
            if v_index < 0 or v_index >= len(vikings):
                print("Invalid viking number.")
                continue

            print("\nITEMS")
            for i, item in enumerate(items, start=1):
                print(f"{i}. {item.name} | {item.slot.value}")

            i_choice = input("\nChoose item: ").strip()
            if not i_choice.isdigit():
                print("Invalid choice.")
                continue

            i_index = int(i_choice) - 1
            if i_index < 0 or i_index >= len(items):
                print("Invalid item number.")
                continue

            success, message = campaign.equip_item_to_viking(
                vikings[v_index].viking_id,
                items[i_index].item_id,
            )
            print(message)

        elif choice == "3":
            vikings = list(campaign.vikings.values())

            print("\nVIKINGS")
            for i, viking in enumerate(vikings, start=1):
                print(f"{i}. {display_name(viking)}")

            v_choice = input("\nChoose viking: ").strip()
            if not v_choice.isdigit():
                print("Invalid choice.")
                continue

            v_index = int(v_choice) - 1
            if v_index < 0 or v_index >= len(vikings):
                print("Invalid viking number.")
                continue

            slots = list(EquipmentSlot)

            print("\nSLOTS")
            for i, slot in enumerate(slots, start=1):
                print(f"{i}. {slot.value}")

            s_choice = input("\nChoose slot: ").strip()
            if not s_choice.isdigit():
                print("Invalid choice.")
                continue

            s_index = int(s_choice) - 1
            if s_index < 0 or s_index >= len(slots):
                print("Invalid slot number.")
                continue

            success, message = campaign.unequip_item_from_viking(
                vikings[v_index].viking_id,
                slots[s_index],
            )
            print(message)

        elif choice == "4":
            logs = campaign.auto_equip_best_items()

            print("\nAUTO EQUIP RESULTS")
            print("-" * 80)

            for log in logs:
                print(log)

        elif choice == "5":
            return          


def choose_favored_god() -> FavoredGod:
    from models import FavoredGod
    from roster import GOD_STAT_BONUSES

    gods = list(GOD_STAT_BONUSES.keys())

    print("\nCHOOSE YOUR FAVORED GOD")
    print("-" * 80)

    for i, god in enumerate(gods, start=1):
        stat = GOD_STAT_BONUSES[god]
        label = stat.capitalize()
        print(f"{i}. {god.value} - {label}")

    while True:
        choice = input("\nChoose favored god: ").strip()

        if not choice.isdigit():
            print("Invalid choice.")
            continue

        index = int(choice) - 1

        if index < 0 or index >= len(gods):
            print("Invalid god number.")
            continue

        return gods[index]

def create_or_load_campaign() -> Campaign:
    from roster import generate_basic_equipment_for_viking

    if save_exists():
        load_choice = input("Load existing save? (y/n): ").strip().lower()

        if load_choice == "y":
            slot = input("Load save slot number: ").strip()
            filename = save_filename_for_slot(slot)

            if save_exists(filename):
                print(f"Save slot {slot} loaded.")
                return load_campaign(filename)

            print(f"No save found in slot {slot}. Starting new game.")

    player_name = input("Enter your name: ").strip() or "Ragnar"
    village_name = input("Enter your village name: ").strip() or f"{player_name}'s Holding"
    ship_name = input("Enter your ship's name: ").strip() or "Sea Wolf"
    player_favored_god = choose_favored_god()

    vikings = generate_starting_roster(player_name, player_favored_god)
    for viking in vikings.values():
        if not viking.original_stats:
            viking.original_stats = {
                "might": viking.might,
                "skill": viking.skill,
                "cunning": viking.cunning,
                "leadership": viking.leadership,
                "courage": viking.courage,
                "vitality": viking.vitality,
                "agility": viking.agility,
                "seamanship": viking.seamanship,
            }
    ship = create_starting_ship(vikings, ship_name)
    village = create_starting_village(village_name)

    campaign = Campaign(
        name=f"The Saga of {player_name}",
        ship=ship,
        vikings=vikings,
        village=village,
    )
    campaign.add_saga_entry(
        entry_type="campaign_start",
        text=f"{player_name} became Jarl of {village.name}, with {ship.name} waiting at the shore.",
        viking_ids=[
            viking.viking_id
            for viking in campaign.vikings.values()
            if viking.is_player
        ],
    )

    for viking in campaign.vikings.values():
        basic_items = generate_basic_equipment_for_viking(viking)

        for item in basic_items:
            campaign.add_item(item)

    campaign.refresh_recruit_pool()
    
    campaign.generate_seasonal_jobs()    



    return campaign


SMITHY_BUY_ITEMS = [
    "Nordic Axe",
    "Nordic Sword",
    "Nordic Spear",
    "Nordic Knife",
    "Nordic Bow",
    "Nordic Shield",
    "Nordic Armor",
    "Nordic Helm",
]


QUALITY_UPGRADE_COSTS = {
    ItemQuality.CRUDE: 2,
    ItemQuality.WORN: 3,
    ItemQuality.COMMON: 4,
    ItemQuality.FINE: 5,
    ItemQuality.SUPERIOR: 6,
    ItemQuality.MASTERWORK: 7,
}


QUALITY_UPGRADES = {
    ItemQuality.CRUDE: ItemQuality.WORN,
    ItemQuality.WORN: ItemQuality.COMMON,
    ItemQuality.COMMON: ItemQuality.FINE,
    ItemQuality.FINE: ItemQuality.SUPERIOR,
    ItemQuality.SUPERIOR: ItemQuality.MASTERWORK,
    ItemQuality.MASTERWORK: ItemQuality.SAGA_FORGED,
}


def smithy_menu(campaign: Campaign) -> None:
    if not campaign.has_smithy():
        print("\nYou need to build a Smithy first.")
        return

    while True:
        print("\nSMITHY")
        print("-" * 40)
        print(f"Silver: {campaign.silver}")
        print(f"Fine Metal: {campaign.fine_metal}")
        print("1. Buy Smithy Equipment")
        print("2. Upgrade Equipment Quality")
        print("3. Back")

        choice = input("> ").strip()

        if choice == "1":
            smithy_buy_equipment(campaign)

        elif choice == "2":
            smithy_upgrade_equipment(campaign)

        elif choice == "3":
            return

        else:
            print("Invalid choice.")


def smithy_buy_equipment(campaign: Campaign) -> None:
    from items import create_item_by_name, ItemQuality

    print("\nBUY SMITHY EQUIPMENT")
    print("-" * 40)

    for index, item_name in enumerate(SMITHY_BUY_ITEMS, start=1):
        preview = create_item_by_name(item_name, ItemQuality.FINE)

        if not preview:
            continue

        silver_cost = max(1, preview.value // 2)

        print(
            f"{index}. {item_name} "
            f"- {silver_cost} silver, 2 Fine Metal"
        )

    print(f"{len(SMITHY_BUY_ITEMS) + 1}. Back")

    choice = input("> ").strip()

    if not choice.isdigit():
        print("Invalid choice.")
        return

    index = int(choice)

    if index == len(SMITHY_BUY_ITEMS) + 1:
        return

    if not 1 <= index <= len(SMITHY_BUY_ITEMS):
        print("Invalid choice.")
        return

    item_name = SMITHY_BUY_ITEMS[index - 1]
    item = create_item_by_name(item_name, ItemQuality.FINE)

    if not item:
        print("That item could not be created.")
        return

    silver_cost = max(1, item.value // 2)
    metal_cost = 2

    if campaign.silver < silver_cost:
        print(f"Not enough silver. Need {silver_cost}.")
        return

    if campaign.fine_metal < metal_cost:
        print(f"Not enough Fine Metal. Need {metal_cost}.")
        return

    campaign.silver -= silver_cost
    campaign.fine_metal -= metal_cost
    campaign.add_item(item)

    print(f"Purchased {item.name}.")


def smithy_upgrade_equipment(campaign: Campaign) -> None:
    upgradeable_items = [
        item for item in campaign.inventory.values()
        if getattr(item, "quality", None) in QUALITY_UPGRADES
    ]

    if not upgradeable_items:
        print("\nNo upgradeable equipment.")
        return

    print("\nUPGRADE EQUIPMENT QUALITY")
    print("-" * 60)
    print(f"Fine Metal: {campaign.fine_metal}")

    for index, item in enumerate(upgradeable_items, start=1):
        current_quality = item.quality
        next_quality = QUALITY_UPGRADES[current_quality]
        metal_cost = QUALITY_UPGRADE_COSTS[current_quality]

        equipped_text = " Equipped" if campaign.item_is_equipped(item.item_id) else ""

        print(
            f"{index}. {item.name}{equipped_text} "
            f"{current_quality} -> {next_quality} "
            f"({metal_cost} Fine Metal)"
        )

    print(f"{len(upgradeable_items) + 1}. Back")

    choice = input("> ").strip()

    if not choice.isdigit():
        print("Invalid choice.")
        return

    index = int(choice)

    if index == len(upgradeable_items) + 1:
        return

    if not 1 <= index <= len(upgradeable_items):
        print("Invalid choice.")
        return

    item = upgradeable_items[index - 1]
    current_quality = item.quality
    next_quality = QUALITY_UPGRADES[current_quality]
    metal_cost = QUALITY_UPGRADE_COSTS[current_quality]

    if campaign.fine_metal < metal_cost:
        print(f"Not enough Fine Metal. Need {metal_cost}.")
        return

    campaign.fine_metal -= metal_cost

    base_name = item.name

    for quality in ItemQuality:
        prefix = f"{quality.value} "

        if base_name.startswith(prefix):
            base_name = base_name[len(prefix):]
            break

    item.quality = next_quality

    if next_quality == ItemQuality.FINE:
        item.name = base_name
    else:
        item.name = f"{next_quality.value} {base_name}"

    print(f"Upgraded {item.name} to {next_quality.value}.")

def main() -> None:
    print("GOING VIKING")
    print("=" * 80)

    campaign = create_or_load_campaign()

    while True:
        print("\n" + "=" * 80)
        print(campaign.summary())
        print("=" * 80)

        print("\nMAIN MENU")
        print("1. Crew & Recruitment")
        print("2. Ship & Expedition Prep")
        print("3. Village & Buildings")
        print("4. Jobs & Travel")
        print("5. Inventory & Equipment")
        print("6. Smithy")
        print("7. Advance One Week")
        print("8. Save / Load")
        print("9. Sagas")
        print("10. Debug")
        print("11. Quit")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            crew_menu(campaign)

        elif choice == "2":
            ship_menu(campaign)

        elif choice == "3":
            village_menu(campaign)

        elif choice == "4":
            jobs_menu(campaign)

        elif choice == "5":
            inventory_menu(campaign)

        elif choice == "6":
            smithy_menu(campaign)

        elif choice == "7":
            campaign.advance_weeks(1)
            print("Advanced one week.")

        elif choice == "8":
            campaign = save_menu(campaign)

        elif choice == "9":
            sagas_menu(campaign)

        elif choice == "10":
            debug_menu(campaign)

        elif choice == "11":
            print("Your saga pauses... for now.")
            break

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()