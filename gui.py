import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import tkinter.font as tkfont
from campaign import Campaign
from village import create_starting_village, BuildingType
from items import TRADER_STOCK, EquipmentSlot, ItemQuality, create_item_by_name
from roster import generate_starting_roster, create_starting_ship, generate_basic_equipment_for_viking
from save_manager import save_campaign, load_campaign, save_exists, save_filename_for_slot
from models import FavoredGod, CrewRole
from ship_upgrades import ShipPart, get_next_ship_upgrade

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

class GoingVikingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Going Viking")
        self.root.geometry("1200x800")
        self.configure_fonts()

        self.campaign = self.launch_start_screen()

        self.selected_job = None

        self.build_ui()
        self.refresh_all()
        
    def configure_fonts(self):
        default_size = 14

        tkfont.nametofont("TkDefaultFont").configure(size=default_size)
        tkfont.nametofont("TkTextFont").configure(size=default_size)
        tkfont.nametofont("TkFixedFont").configure(size=default_size)
        tkfont.nametofont("TkMenuFont").configure(size=default_size)

        style = ttk.Style()
        style.configure("Treeview", font=("Consolas", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Consolas", 11, "bold"))
        style.configure("TButton", font=("Consolas", 11))
        style.configure("TLabel", font=("Consolas", 11))
        style.configure("TNotebook.Tab", font=("Consolas", 11))        

    def launch_start_screen(self):
        if save_exists():
            load = messagebox.askyesno("Load Save", "Load existing save?")

            if load:
                slot = simpledialog.askstring("Load Save", "Save slot number:")

                if slot:
                    filename = save_filename_for_slot(slot)

                    if save_exists(filename):
                        return load_campaign(filename)

                    messagebox.showwarning(
                        "Save Not Found",
                        f"No save found in slot {slot}. Starting new game.",
                    )

        return self.create_new_campaign_dialog()

    def show_expedition_screen(self, job_name: str):
        self.expedition_window = tk.Toplevel(self.root)
        self.expedition_window.title(f"Expedition - {job_name}")
        self.expedition_window.geometry("1000x750")
        self.expedition_window.grab_set()

        title = ttk.Label(
            self.expedition_window,
            text=job_name,
            font=("Consolas", 18, "bold"),
        )
        title.pack(fill="x", padx=12, pady=10)

        self.expedition_log_text = tk.Text(
            self.expedition_window,
            wrap="word",
            font=("Consolas", 12),
            bg="#111111",
            fg="#dddddd",
            insertbackground="white",
        )
        self.expedition_log_text.pack(fill="both", expand=True, padx=12, pady=8)

        self.expedition_back_button = ttk.Button(
            self.expedition_window,
            text="Back to Jobs",
            command=self.close_expedition_screen,
        )
        self.expedition_back_button.pack(pady=10)
        self.expedition_back_button.pack_forget()
        
    def close_expedition_screen(self):
        self.current_log_index = len(getattr(self, "current_log_lines", []))

        if hasattr(self, "expedition_window") and self.expedition_window.winfo_exists():
            self.expedition_window.destroy()

        self.refresh_all()        

    def create_new_campaign_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("New Campaign")
        dialog.geometry("400x320")
        dialog.grab_set()

        player_name_var = tk.StringVar(value="Ragnar")
        village_name_var = tk.StringVar(value="Ragnar's Holding")
        ship_name_var = tk.StringVar(value="Sea Wolf")
        god_var = tk.StringVar(value=FavoredGod.ODIN.value)

        ttk.Label(dialog, text="Player Name").pack(anchor="w", padx=12, pady=(12, 2))
        ttk.Entry(dialog, textvariable=player_name_var).pack(fill="x", padx=12)

        ttk.Label(dialog, text="Village Name").pack(anchor="w", padx=12, pady=(10, 2))
        ttk.Entry(dialog, textvariable=village_name_var).pack(fill="x", padx=12)

        ttk.Label(dialog, text="Ship Name").pack(anchor="w", padx=12, pady=(10, 2))
        ttk.Entry(dialog, textvariable=ship_name_var).pack(fill="x", padx=12)

        ttk.Label(dialog, text="Favored God").pack(anchor="w", padx=12, pady=(10, 2))
        ttk.Combobox(
            dialog,
            textvariable=god_var,
            values=[god.value for god in FavoredGod],
            state="readonly",
        ).pack(fill="x", padx=12)

        result = {"campaign": None}

        def confirm():
            player_name = player_name_var.get().strip() or "Ragnar"
            village_name = village_name_var.get().strip() or f"{player_name}'s Holding"
            ship_name = ship_name_var.get().strip() or "Sea Wolf"

            favored_god = FavoredGod(god_var.get())

            vikings = generate_starting_roster(player_name, favored_god)

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
                text=(
                    f"{player_name} became Jarl of {village.name}, "
                    f"with {ship.name} waiting at the shore."
                ),
                viking_ids=[
                    viking.viking_id
                    for viking in campaign.vikings.values()
                    if viking.is_player
                ],
            )

            for viking in campaign.vikings.values():
                for item in generate_basic_equipment_for_viking(viking):
                    campaign.add_item(item)

            campaign.refresh_recruit_pool()
            campaign.generate_seasonal_jobs()

            result["campaign"] = campaign
            dialog.destroy()

        ttk.Button(dialog, text="Start Saga", command=confirm).pack(pady=18)

        self.root.wait_window(dialog)

        return result["campaign"]

    def build_inventory_tab(self):
        self.inventory_tabs = ttk.Notebook(self.inventory_tab)
        self.inventory_tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.inventory_equipped_tab = ttk.Frame(self.inventory_tabs)
        self.inventory_unequipped_tab = ttk.Frame(self.inventory_tabs)

        self.inventory_tabs.add(self.inventory_equipped_tab, text="Equipped")
        self.inventory_tabs.add(self.inventory_unequipped_tab, text="Unequipped")

        button_frame = ttk.Frame(self.inventory_tab)
        button_frame.pack(fill="x", padx=8, pady=4)

        ttk.Button(
            button_frame,
            text="Equip Selected Item",
            command=self.equip_selected_inventory_item,
        ).pack(side="left", padx=4)

        ttk.Button(
            button_frame,
            text="Unequip Item From Viking",
            command=self.unequip_item_dialog,
        ).pack(side="left", padx=4)

        ttk.Button(
            button_frame,
            text="Auto Equip Best Items",
            command=self.auto_equip_best_items,
        ).pack(side="left", padx=4)

        columns = ["Name", "Type", "Slot", "Quality", "Value", "Equipped By"]

        self.equipped_items_tree = self.make_sortable_tree(
            self.inventory_equipped_tab,
            columns,
        )

        self.unequipped_items_tree = self.make_sortable_tree(
            self.inventory_unequipped_tab,
            columns,
        )
        
    def refresh_inventory(self):
        self.equipped_items_tree.delete(*self.equipped_items_tree.get_children())
        self.unequipped_items_tree.delete(*self.unequipped_items_tree.get_children())

        self.equipped_items = []
        self.unequipped_items = []

        items = self.campaign.get_inventory_list()

        equipped_ids = set()

        for viking in self.campaign.vikings.values():
            equipped_ids.update([
                viking.equipment.armor,
                viking.equipment.helm,
                viking.equipment.primary_weapon,
                getattr(viking.equipment, "secondary_weapon", None),
                viking.equipment.shield,
            ])

        equipped_ids.discard(None)

        for item in items:
            owner_name = ""

            for viking in self.campaign.vikings.values():
                if item.item_id in {
                    viking.equipment.armor,
                    viking.equipment.helm,
                    viking.equipment.primary_weapon,
                    getattr(viking.equipment, "secondary_weapon", None),
                    viking.equipment.shield,
                }:
                    owner_name = viking.display_name()
                    break

            row = [
                item.name,
                item.item_type.value,
                item.slot.value if item.slot else "-",
                item.quality.value if getattr(item, "quality", None) else "-",
                item.value,
                owner_name or "-",
            ]

            if item.item_id in equipped_ids:
                self.equipped_items.append(item)
                self.equipped_items_tree.insert("", "end", values=row)
            else:
                self.unequipped_items.append(item)
                self.unequipped_items_tree.insert("", "end", values=row)      

    def equip_selected_inventory_item(self):
        selection = self.unequipped_items_tree.selection()

        if not selection:
            messagebox.showwarning("No Item Selected", "Select an unequipped item first.")
            return

        index = self.unequipped_items_tree.index(selection[0])
        item = self.unequipped_items[index]

        vikings = list(self.campaign.vikings.values())
        names = [viking.display_name() for viking in vikings]

        chosen = simpledialog.askinteger(
            "Choose Viking",
            "\n".join(f"{i + 1}. {name}" for i, name in enumerate(names)),
        )

        if not chosen:
            return

        viking_index = chosen - 1

        if viking_index < 0 or viking_index >= len(vikings):
            messagebox.showwarning("Invalid Viking", "Invalid viking number.")
            return

        success, message = self.campaign.equip_item_to_viking(
            vikings[viking_index].viking_id,
            item.item_id,
        )

        if success:
            messagebox.showinfo("Item Equipped", message)
        else:
            messagebox.showwarning("Could Not Equip", message)

        self.refresh_all()


    def unequip_item_dialog(self):
        vikings = list(self.campaign.vikings.values())

        chosen_viking = simpledialog.askinteger(
            "Choose Viking",
            "\n".join(
                f"{i + 1}. {viking.display_name()}"
                for i, viking in enumerate(vikings)
            ),
        )

        if not chosen_viking:
            return

        viking_index = chosen_viking - 1

        if viking_index < 0 or viking_index >= len(vikings):
            messagebox.showwarning("Invalid Viking", "Invalid viking number.")
            return

        slots = list(EquipmentSlot)

        chosen_slot = simpledialog.askinteger(
            "Choose Slot",
            "\n".join(
                f"{i + 1}. {slot.value}"
                for i, slot in enumerate(slots)
            ),
        )

        if not chosen_slot:
            return

        slot_index = chosen_slot - 1

        if slot_index < 0 or slot_index >= len(slots):
            messagebox.showwarning("Invalid Slot", "Invalid slot number.")
            return

        success, message = self.campaign.unequip_item_from_viking(
            vikings[viking_index].viking_id,
            slots[slot_index],
        )

        if success:
            messagebox.showinfo("Item Unequipped", message)
        else:
            messagebox.showwarning("Could Not Unequip", message)

        self.refresh_all()


    def auto_equip_best_items(self):
        logs = self.campaign.auto_equip_best_items()

        messagebox.showinfo(
            "Auto Equip Results",
            "\n".join(logs) if logs else "No equipment changes.",
        )

        self.refresh_all()                

    def build_ui(self):
        self.summary_label = tk.Label(
            self.root,
            text="",
            anchor="w",
            justify="left",
            font=("Consolas", 11),
        )
        self.summary_label.pack(fill="x", padx=10, pady=8)

        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=5)

        self.dashboard_tab = ttk.Frame(self.tabs)
        self.jobs_tab = ttk.Frame(self.tabs)
        self.crew_tab = ttk.Frame(self.tabs)
        self.ship_tab = ttk.Frame(self.tabs)
        self.village_tab = ttk.Frame(self.tabs)
        self.inventory_tab = ttk.Frame(self.tabs)
        self.sagas_tab = ttk.Frame(self.tabs)
        self.save_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.dashboard_tab, text="Dashboard")
        self.tabs.add(self.jobs_tab, text="Jobs")
        self.tabs.add(self.crew_tab, text="Crew")
        self.tabs.add(self.ship_tab, text="Ship")
        self.tabs.add(self.village_tab, text="Village")
        self.tabs.add(self.inventory_tab, text="Inventory")
        self.tabs.add(self.sagas_tab, text="Sagas")
        self.tabs.add(self.save_tab, text="Save / Load")

        self.build_dashboard_tab()
        self.build_jobs_tab()
        self.build_crew_tab()
        self.build_ship_tab()
        self.build_village_tab()
        self.build_inventory_tab()
        self.build_sagas_tab()
        self.build_save_tab()

    def make_sortable_tree(self, parent, columns):
        tree = ttk.Treeview(parent, columns=columns, show="headings")

        column_widths = {
            "Name": 150,
            "Age": 45,
            "Class": 95,
            "Role": 80,
            "God": 70,
            "Status": 75,
            "OVR": 55,
            "POT": 55,
            "MGT": 50,
            "SKL": 50,
            "CUN": 50,
            "LDR": 50,
            "CRG": 50,
            "VIT": 50,
            "AGI": 50,
            "SEA": 50,
            "LOY": 50,
            "REN": 50,
            "Traits": 160,
            "Injuries": 160,
            "Trait": 130,
            "Description": 360,
            "Text": 500,
        }

        for col in columns:
            tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_treeview(tree, c, False),
            )

            tree.column(
                col,
                width=column_widths.get(col, 90),
                anchor="center",
                stretch=False,
            )

        tree.column("Name", anchor="w", stretch=False)

        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return tree


    def sort_treeview(self, tree, col, reverse):
        grade_order = {
            "S+": 15,
            "S": 14,
            "S-": 13,
            "A+": 12,
            "A": 11,
            "A-": 10,
            "B+": 9,
            "B": 8,
            "B-": 7,
            "C+": 6,
            "C": 5,
            "C-": 4,
            "D+": 3,
            "D": 2,
            "D-": 1,
            "F": 0,
        }

        items = []

        for child in tree.get_children(""):
            value = tree.set(child, col)

            if col in {"OVR", "POT"}:
                sort_value = grade_order.get(value, -999)

            else:
                try:
                    sort_value = float(value)
                except ValueError:
                    sort_value = value.lower()

            items.append((sort_value, child))

        items.sort(reverse=reverse)

        for index, (_, child) in enumerate(items):
            tree.move(child, "", index)

        tree.heading(
            col,
            command=lambda: self.sort_treeview(tree, col, not reverse),
        )

    def build_sagas_tab(self):
        left = ttk.Frame(self.sagas_tab)
        left.pack(side="left", fill="y", padx=8, pady=8)

        right = ttk.Frame(self.sagas_tab)
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        ttk.Label(left, text="Years").pack(anchor="w")

        self.saga_years_listbox = tk.Listbox(left, width=20)
        self.saga_years_listbox.pack(fill="y", expand=True)

        self.saga_years_listbox.bind("<<ListboxSelect>>", self.on_saga_year_selected)

        self.saga_text = tk.Text(right, wrap="word", font=("Consolas", 12))
        self.saga_text.pack(fill="both", expand=True)
        
    def refresh_sagas(self):
        self.saga_years_listbox.delete(0, tk.END)
        self.saga_text.delete("1.0", tk.END)

        self.saga_years = sorted({
            entry.year
            for entry in self.campaign.saga_entries
        })

        if not self.saga_years:
            self.saga_years = [self.campaign.year]

        for year in self.saga_years:
            self.saga_years_listbox.insert(tk.END, f"Year {year}")


    def on_saga_year_selected(self, event=None):
        selection = self.saga_years_listbox.curselection()

        if not selection:
            return

        year = self.saga_years[selection[0]]

        entries = [
            entry for entry in self.campaign.saga_entries
            if entry.year == year
        ]

        entries.sort(key=lambda entry: (entry.month, entry.week))

        lines = [f"THE SAGA - YEAR {year}", "-" * 80, ""]

        if not entries:
            lines.append("No saga entries recorded for this year.")
        else:
            for entry in entries:
                lines.append(
                    f"Year {entry.year}, Month {entry.month}, Week {entry.week}: "
                    f"{entry.text}"
                )
                lines.append("")

        self.saga_text.delete("1.0", tk.END)
        self.saga_text.insert("1.0", "\n".join(lines))        
        
    def build_save_tab(self):
        frame = ttk.Frame(self.save_tab)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ttk.Label(frame, text="Save Slot").pack(anchor="w")

        self.save_slot_var = tk.StringVar(value="1")

        ttk.Entry(
            frame,
            textvariable=self.save_slot_var,
            width=12,
        ).pack(anchor="w", pady=6)

        ttk.Button(
            frame,
            text="Save Game",
            command=self.save_game,
        ).pack(anchor="w", pady=4)

        ttk.Button(
            frame,
            text="Load Game",
            command=self.load_game,
        ).pack(anchor="w", pady=4)

        self.save_status_text = tk.Text(frame, wrap="word", height=12)
        self.save_status_text.pack(fill="x", pady=12)    

    def save_game(self):
        slot = self.save_slot_var.get().strip() or "1"
        filename = save_filename_for_slot(slot)

        save_path = save_campaign(self.campaign, filename)

        self.save_status_text.delete("1.0", tk.END)
        self.save_status_text.insert("1.0", f"Game saved to {save_path}.")


    def load_game(self):
        slot = self.save_slot_var.get().strip() or "1"
        filename = save_filename_for_slot(slot)

        if not save_exists(filename):
            messagebox.showwarning("Save Not Found", f"No save found in slot {slot}.")
            return

        self.campaign = load_campaign(filename)

        self.save_status_text.delete("1.0", tk.END)
        self.save_status_text.insert("1.0", f"Loaded save slot {slot}.")

        self.refresh_all()        

    def viking_row(self, viking):
        traits = ", ".join(
            trait.name
            for trait in getattr(viking, "traits", [])
        )

        injuries = ", ".join(
            injury.name
            for injury in getattr(viking, "active_injuries", [])
        )

        return [
            viking.display_name(),
            viking.age,
            viking.viking_class.value,
            viking.role.value,
            viking.favored_god.value,
            viking.status.value,
            viking.overall_grade(),
            viking.potential_overall_grade(),
            viking.effective_stat("might"),
            viking.effective_stat("skill"),
            viking.effective_stat("cunning"),
            viking.effective_stat("leadership"),
            viking.effective_stat("courage"),
            viking.effective_stat("vitality"),
            viking.effective_stat("agility"),
            viking.effective_stat("seamanship"),
            viking.loyalty,
            viking.renown,
            traits,
            injuries,
        ]


    def fill_viking_tree(self, tree, vikings):
        tree.delete(*tree.get_children())

        for viking in vikings:
            tree.insert(
                "",
                "end",
                values=self.viking_row(viking),
            )

    def build_dashboard_tab(self):
        self.dashboard_text = tk.Text(self.dashboard_tab, wrap="word")
        self.dashboard_text.pack(fill="both", expand=True, padx=8, pady=8)

        button_frame = ttk.Frame(self.dashboard_tab)
        button_frame.pack(fill="x", padx=8, pady=5)

        ttk.Button(
            button_frame,
            text="Advance 1 Week",
            command=self.advance_week,
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_all,
        ).pack(side="left", padx=5)

    def build_jobs_tab(self):
        self.selected_location = None
        self.selected_job = None
        self.locations = []
        self.jobs = []

        left = ttk.Frame(self.jobs_tab)
        left.pack(side="left", fill="y", padx=8, pady=8)

        main_area = ttk.Frame(self.jobs_tab)
        main_area.pack(side="left", fill="both", expand=True, padx=8, pady=8)

        top = ttk.Frame(main_area)
        top.pack(side="top", fill="both", expand=True)

        bottom = ttk.Frame(main_area)
        bottom.pack(side="bottom", fill="both", expand=True, pady=(8, 0))

        ttk.Label(left, text="Discovered Locations").pack(anchor="w")

        self.locations_listbox = tk.Listbox(left, width=34)
        self.locations_listbox.pack(fill="y", expand=True)

        self.locations_listbox.bind("<<ListboxSelect>>", self.on_location_selected)

        ttk.Button(
            left,
            text="Refresh Locations",
            command=self.refresh_jobs,
        ).pack(fill="x", pady=4)

        job_columns = [
            "Name",
            "Type",
            "Location",
            "Weeks",
            "Difficulty",
            "Danger",
            "Expected Crew",
            "Food Cost",
            "Employer",
        ]

        self.jobs_tree = ttk.Treeview(
            top,
            columns=job_columns,
            show="headings",
        )

        for col in job_columns:
            self.jobs_tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_treeview(self.jobs_tree, c, False),
            )
            self.jobs_tree.column(col, width=105, anchor="center")

        self.jobs_tree.column("Name", width=220, anchor="w")
        self.jobs_tree.column("Employer", width=150, anchor="w")

        self.jobs_tree.pack(fill="both", expand=True)
        self.jobs_tree.bind("<<TreeviewSelect>>", self.on_job_selected)

        job_buttons = ttk.Frame(top)
        job_buttons.pack(fill="x", pady=5)

        ttk.Button(
            job_buttons,
            text="Take Selected Job",
            command=self.take_selected_job,
        ).pack(side="left", padx=4)

        ttk.Button(
            job_buttons,
            text="Fast Sim Selected Job",
            command=self.fast_sim_selected_job,
        ).pack(side="left", padx=4)

        ttk.Label(bottom, text="Selected Job Details").pack(anchor="w")

        self.job_detail_text = tk.Text(
            bottom,
            wrap="word",
            height=14,
            font=("Consolas", 10),
        )
        self.job_detail_text.pack(fill="both", expand=True)
        
       

    def build_crew_tab(self):
        self.crew_tabs = ttk.Notebook(self.crew_tab)
        self.crew_tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.active_crew_tab = ttk.Frame(self.crew_tabs)
        self.growth_tab = ttk.Frame(self.crew_tabs)
        self.reserves_tab = ttk.Frame(self.crew_tabs)
        self.injured_tab = ttk.Frame(self.crew_tabs)
        self.recruits_tab = ttk.Frame(self.crew_tabs)
        self.traits_tab = ttk.Frame(self.crew_tabs)
        self.odins_hall_tab = ttk.Frame(self.crew_tabs)
        self.retired_tab = ttk.Frame(self.crew_tabs)

        self.crew_tabs.add(self.active_crew_tab, text="Active Crew")
        self.crew_tabs.add(self.growth_tab, text="Growth")
        self.crew_tabs.add(self.reserves_tab, text="Reserves")
        self.crew_tabs.add(self.injured_tab, text="Injured")
        self.crew_tabs.add(self.recruits_tab, text="Recruit Pool")
        self.crew_tabs.add(self.traits_tab, text="Traits")
        self.crew_tabs.add(self.odins_hall_tab, text="Odin's Hall")
        self.crew_tabs.add(self.retired_tab, text="Retired")

        crew_columns = [
            "Name", "Age", "Class", "Role", "God", "Status",
            "OVR", "POT",
            "MGT", "SKL", "CUN", "LDR",
            "CRG", "VIT", "AGI", "SEA",
            "LOY", "REN",
            "Traits", "Injuries",
        ]

        self.active_crew_tree = self.make_sortable_tree(self.active_crew_tab, crew_columns)
        self.growth_tree = self.make_sortable_tree(self.growth_tab, crew_columns)
        self.reserves_tree = self.make_sortable_tree(self.reserves_tab, crew_columns)
        self.injured_tree = self.make_sortable_tree(self.injured_tab, crew_columns)
        trait_columns = ["Name", "Trait", "Description"]
        self.traits_tree = self.make_sortable_tree(self.traits_tab, trait_columns)

        recruit_button_frame = ttk.Frame(self.recruits_tab)
        recruit_button_frame.pack(fill="x", pady=4)

        ttk.Button(
            recruit_button_frame,
            text="Refresh Recruit Pool",
            command=self.refresh_recruits,
        ).pack(side="left", padx=4)

        ttk.Button(
            recruit_button_frame,
            text="Hire Selected Recruit",
            command=self.hire_selected_recruit,
        ).pack(side="left", padx=4)

        self.recruit_tree = self.make_sortable_tree(
            self.recruits_tab,
            crew_columns,
        )

        for tree in [
            self.active_crew_tree,
            self.growth_tree,
            self.reserves_tree,
            self.injured_tree,
            self.traits_tree,
            self.recruit_tree,
        ]:
            tree.bind("<Double-1>", self.on_viking_tree_double_click)

        legacy_columns = ["Name", "Year", "Text"]

        self.odins_hall_tree = self.make_sortable_tree(
            self.odins_hall_tab,
            legacy_columns,
        )

        self.retired_tree = self.make_sortable_tree(
            self.retired_tab,
            legacy_columns,
        )

    def on_viking_tree_double_click(self, event):
        tree = event.widget
        selection = tree.selection()

        if not selection:
            return

        item_id = selection[0]
        values = tree.item(item_id, "values")

        if not values:
            return

        name = values[0]

        for viking in self.campaign.vikings.values():
            if viking.display_name() == name or viking.name == name:
                self.open_viking_page(viking.viking_id)
                return

        for candidate in getattr(self, "recruits", []):
            viking = candidate.viking
            if viking.display_name() == name or viking.name == name:
                self.open_viking_page(viking.viking_id)
                return


    def build_ship_tab(self):
        self.ship_tabs = ttk.Notebook(self.ship_tab)
        self.ship_tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.ship_status_tab = ttk.Frame(self.ship_tabs)
        self.ship_crew_tab = ttk.Frame(self.ship_tabs)
        self.ship_reserves_tab = ttk.Frame(self.ship_tabs)
        self.ship_upgrades_tab = ttk.Frame(self.ship_tabs)

        self.ship_tabs.add(self.ship_status_tab, text="Status")
        self.ship_tabs.add(self.ship_crew_tab, text="Ship Crew")
        self.ship_tabs.add(self.ship_reserves_tab, text="Add Reserves")
        self.ship_tabs.add(self.ship_upgrades_tab, text="Upgrades")

        status_area = ttk.Frame(self.ship_status_tab)
        status_area.pack(fill="both", expand=True, padx=8, pady=8)

        self.ship_status_text = tk.Text(status_area, wrap="word")
        self.ship_status_text.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.ship_crew_scores_text = tk.Text(status_area, wrap="word")
        self.ship_crew_scores_text.pack(side="left", fill="both", expand=True)

        status_buttons = ttk.Frame(self.ship_status_tab)
        status_buttons.pack(fill="x", padx=8, pady=4)

        ttk.Button(
            status_buttons,
            text="Repair Ship",
            command=self.repair_ship,
        ).pack(side="left", padx=4)

        ship_crew_columns = [
            "Name", "Age", "Class", "Role", "God", "Status",
            "OVR", "POT",
            "MGT", "SKL", "CUN", "LDR",
            "CRG", "VIT", "AGI", "SEA",
            "LOY", "REN",
            "Traits", "Injuries",
        ]

        crew_buttons = ttk.Frame(self.ship_crew_tab)
        crew_buttons.pack(fill="x", pady=4)

        ttk.Button(
            crew_buttons,
            text="Remove Selected From Ship",
            command=self.remove_selected_ship_crew,
        ).pack(side="left", padx=4)

        ttk.Button(
            crew_buttons,
            text="Assign Selected as Captain",
            command=self.assign_selected_captain,
        ).pack(side="left", padx=4)

        self.ship_crew_tree = self.make_sortable_tree(
            self.ship_crew_tab,
            ship_crew_columns,
        )

        reserve_buttons = ttk.Frame(self.ship_reserves_tab)
        reserve_buttons.pack(fill="x", pady=4)

        ttk.Button(
            reserve_buttons,
            text="Add Selected Reserve to Ship",
            command=self.add_selected_reserve_to_ship,
        ).pack(side="left", padx=4)

        self.ship_reserves_tree = self.make_sortable_tree(
            self.ship_reserves_tab,
            ship_crew_columns,
        )

        upgrade_buttons = ttk.Frame(self.ship_upgrades_tab)
        upgrade_buttons.pack(fill="x", pady=4)

        ttk.Button(
            upgrade_buttons,
            text="Start Selected Upgrade",
            command=self.start_selected_ship_upgrade,
        ).pack(side="left", padx=4)

        self.ship_upgrade_tree = ttk.Treeview(
            self.ship_upgrades_tab,
            columns=[
                "Part", "Upgrade", "From", "To", "Silver",
                "Timber", "Fine Metal", "Weeks", "Requires", "Description",
            ],
            show="headings",
        )

        for col in self.ship_upgrade_tree["columns"]:
            self.ship_upgrade_tree.heading(
                col,
                text=col,
                command=lambda c=col: self.sort_treeview(self.ship_upgrade_tree, c, False),
            )
            self.ship_upgrade_tree.column(col, width=110, anchor="center")

        self.ship_upgrade_tree.column("Description", width=360, anchor="w")
        self.ship_upgrade_tree.pack(fill="both", expand=True)

    def build_market_tab(self):
        market_buttons = ttk.Frame(self.village_market_tab)
        market_buttons.pack(fill="x", padx=8, pady=6)

        ttk.Button(
            market_buttons,
            text="Buy Selected Item",
            command=self.buy_selected_trader_item,
        ).pack(side="left", padx=4)

        ttk.Button(
            market_buttons,
            text="Sell Selected Unequipped Item",
            command=self.sell_selected_market_item,
        ).pack(side="left", padx=4)

        self.market_tabs = ttk.Notebook(self.village_market_tab)
        self.market_tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.market_buy_tab = ttk.Frame(self.market_tabs)
        self.market_sell_tab = ttk.Frame(self.market_tabs)

        self.market_tabs.add(self.market_buy_tab, text="Buy")
        self.market_tabs.add(self.market_sell_tab, text="Sell")

        market_columns = ["Name", "Type", "Slot", "Value"]

        self.market_buy_tree = self.make_sortable_tree(self.market_buy_tab, market_columns)
        self.market_sell_tree = self.make_sortable_tree(self.market_sell_tab, market_columns)


    def build_smithy_tab(self):
        smithy_buttons = ttk.Frame(self.village_smithy_tab)
        smithy_buttons.pack(fill="x", padx=8, pady=6)

        ttk.Button(
            smithy_buttons,
            text="Buy Selected Smithy Item",
            command=self.buy_selected_smithy_item,
        ).pack(side="left", padx=4)

        ttk.Button(
            smithy_buttons,
            text="Upgrade Selected Item",
            command=self.upgrade_selected_smithy_item,
        ).pack(side="left", padx=4)

        self.smithy_tabs = ttk.Notebook(self.village_smithy_tab)
        self.smithy_tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.smithy_buy_tab = ttk.Frame(self.smithy_tabs)
        self.smithy_upgrade_tab = ttk.Frame(self.smithy_tabs)

        self.smithy_tabs.add(self.smithy_buy_tab, text="Buy Equipment")
        self.smithy_tabs.add(self.smithy_upgrade_tab, text="Upgrade Quality")

        buy_columns = ["Name", "Silver Cost", "Fine Metal Cost"]
        upgrade_columns = ["Name", "Current", "Next", "Fine Metal Cost", "Equipped"]

        self.smithy_buy_tree = self.make_sortable_tree(self.smithy_buy_tab, buy_columns)
        self.smithy_upgrade_tree = self.make_sortable_tree(self.smithy_upgrade_tab, upgrade_columns)

    def build_village_tab(self):
        self.village_tabs = ttk.Notebook(self.village_tab)
        self.village_tabs.pack(fill="both", expand=True, padx=8, pady=8)

        self.village_overview_tab = ttk.Frame(self.village_tabs)
        self.village_build_tab = ttk.Frame(self.village_tabs)
        self.village_injury_tab = ttk.Frame(self.village_tabs)
        
        self.village_market_tab = ttk.Frame(self.village_tabs)
        self.village_smithy_tab = ttk.Frame(self.village_tabs)

        self.village_tabs.add(self.village_overview_tab, text="Overview")
        self.village_tabs.add(self.village_build_tab, text="Build / Upgrade")
        self.village_tabs.add(self.village_injury_tab, text="Injury Report")
        
        self.village_tabs.add(self.village_market_tab, text="Market")
        self.village_tabs.add(self.village_smithy_tab, text="Smithy")

        self.village_text = tk.Text(self.village_overview_tab, wrap="word")
        self.village_text.pack(fill="both", expand=True, padx=8, pady=8)

        overview_buttons = ttk.Frame(self.village_overview_tab)
        overview_buttons.pack(fill="x", padx=8, pady=4)

        ttk.Button(
            overview_buttons,
            text="Purchase New Tile",
            command=self.purchase_village_tile,
        ).pack(side="left", padx=4)

        ttk.Button(
            overview_buttons,
            text="Conquer Tile Debug",
            command=self.conquer_village_tile_debug,
        ).pack(side="left", padx=4)

        build_top = ttk.Frame(self.village_build_tab)
        build_top.pack(fill="x", padx=8, pady=8)

        ttk.Label(build_top, text="Tile X").pack(side="left", padx=4)
        self.village_x_var = tk.StringVar(value="0")
        ttk.Entry(build_top, textvariable=self.village_x_var, width=6).pack(side="left", padx=4)

        ttk.Label(build_top, text="Tile Y").pack(side="left", padx=4)
        self.village_y_var = tk.StringVar(value="0")
        ttk.Entry(build_top, textvariable=self.village_y_var, width=6).pack(side="left", padx=4)

        ttk.Label(build_top, text="Building").pack(side="left", padx=4)

        self.buildable_buildings = [
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

        self.building_var = tk.StringVar(value=self.buildable_buildings[0].value)

        ttk.Combobox(
            build_top,
            textvariable=self.building_var,
            values=[building.value for building in self.buildable_buildings],
            state="readonly",
            width=24,
        ).pack(side="left", padx=4)

        ttk.Button(
            build_top,
            text="Build Facility",
            command=self.build_selected_village_facility,
        ).pack(side="left", padx=4)

        ttk.Button(
            build_top,
            text="Upgrade Tile Building",
            command=self.upgrade_selected_village_building,
        ).pack(side="left", padx=4)

        self.village_build_text = tk.Text(self.village_build_tab, wrap="word")
        self.village_build_text.pack(fill="both", expand=True, padx=8, pady=8)

        self.village_injury_text = tk.Text(self.village_injury_tab, wrap="word")
        self.village_injury_text.pack(fill="both", expand=True, padx=8, pady=8)

        injury_buttons = ttk.Frame(self.village_injury_tab)
        injury_buttons.pack(fill="x", padx=8, pady=4)

        ttk.Button(
            injury_buttons,
            text="Refresh Injury Report",
            command=self.refresh_village_injury_report,
        ).pack(side="left", padx=4)
        self.build_market_tab()
        self.build_smithy_tab()
        
    def refresh_all(self):
        self.refresh_summary()
        self.refresh_dashboard()
        self.refresh_jobs()
        self.refresh_crew()
        self.refresh_ship()
        self.refresh_village()
        self.refresh_inventory()
        self.refresh_sagas()

    def refresh_summary(self):
        self.summary_label.config(text=self.campaign.summary())

    def refresh_dashboard(self):
        self.dashboard_text.delete("1.0", tk.END)

        text = [
            self.campaign.summary(),
            "",
            "Recent Completed Jobs:",
        ]

        for job in self.campaign.completed_jobs[-10:]:
            if isinstance(job, dict):
                text.append(
                    f"- {job.get('job_name', 'Unknown Job')} | "
                    f"Success: {job.get('success', '?')}"
                )
            else:
                text.append(f"- {job}")

        self.dashboard_text.insert("1.0", "\n".join(text))

    def refresh_jobs(self):
        self.locations_listbox.delete(0, tk.END)
        self.jobs_tree.delete(*self.jobs_tree.get_children())
        self.job_detail_text.delete("1.0", tk.END)

        self.locations = self.campaign.get_discovered_locations()
        self.jobs = []
        self.selected_location = None
        self.selected_job = None

        for location in self.locations:
            self.locations_listbox.insert(
                tk.END,
                f"{location.name} | {location.region.value} | Range {location.required_range}"
            )
            
    def on_location_selected(self, event=None):
        selection = self.locations_listbox.curselection()

        if not selection:
            return

        index = selection[0]
        self.selected_location = self.locations[index]

        self.jobs_tree.delete(*self.jobs_tree.get_children())
        self.job_detail_text.delete("1.0", tk.END)
        self.selected_job = None

        self.jobs = self.campaign.get_available_jobs(self.selected_location)

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

        for job in self.jobs:
            expected_crew = expected_crew_by_difficulty.get(
                max(1, min(10, job.difficulty)),
                26,
            )

            employer = job.employer if job.employer else "Independent"

            self.jobs_tree.insert(
                "",
                "end",
                values=[
                    job.name,
                    job.job_type.value,
                    job.location_name,
                    job.duration_weeks,
                    job.difficulty,
                    job.danger,
                    expected_crew,
                    self.campaign.calculate_food_cost(job),
                    employer,
                ],
            )            

    def open_viking_page(self, viking_id: str):
        viking = self.campaign.vikings.get(viking_id)

        if not viking:
            for candidate in getattr(self, "recruits", []):
                if candidate.viking.viking_id == viking_id:
                    viking = candidate.viking
                    break

        if not viking:
            return

        window = tk.Toplevel(self.root)
        window.title(viking.display_name())
        window.geometry("1100x800")

        left = ttk.Frame(window)
        left.pack(side="left", fill="y", padx=12, pady=12)

        right = ttk.Frame(window)
        right.pack(side="left", fill="both", expand=True, padx=12, pady=12)

        try:
            image = tk.PhotoImage(file="viking.png")
            image_label = ttk.Label(left, image=image)
            image_label.image = image
            image_label.pack(pady=8)
        except Exception:
            ttk.Label(left, text="[viking.png missing]").pack(pady=8)

        ttk.Label(
            left,
            text=viking.display_name(),
            font=("Consolas", 16, "bold"),
        ).pack(pady=(4, 2))

        ttk.Label(
            left,
            text=f"{viking.viking_class.value} | {viking.favored_god.value}",
        ).pack()

        ttk.Label(
            left,
            text=f"Age {viking.age} | {viking.status.value}",
        ).pack()

        ttk.Label(
            left,
            text=f"OVR {viking.overall_grade()} / POT {viking.potential_overall_grade()}",
        ).pack(pady=(2, 10))

        ttk.Label(
            left,
            text="Equipment",
            font=("Consolas", 13, "bold"),
        ).pack(pady=(8, 4))

        equipment_slots = [
            ("Helm", EquipmentSlot.HELM),
            ("Armor", EquipmentSlot.ARMOR),
            ("Weapon", EquipmentSlot.PRIMARY_WEAPON),
            ("Shield", EquipmentSlot.SHIELD),
        ]

        for label, slot in equipment_slots:
            item_id = viking.equipment.get_slot_item_id(slot)
            item = self.campaign.inventory.get(item_id) if item_id else None
            item_name = item.name if item else "Empty"

            ttk.Button(
                left,
                text=f"{label}: {item_name}",
                command=lambda vid=viking.viking_id, s=slot: self.change_viking_equipment(vid, s),
            ).pack(fill="x", pady=3)

        tabs = ttk.Notebook(right)
        tabs.pack(fill="both", expand=True)

        current_tab = ttk.Frame(tabs)
        stats_tab = ttk.Frame(tabs)
        traits_tab = ttk.Frame(tabs)
        injuries_tab = ttk.Frame(tabs)
        jobs_tab = ttk.Frame(tabs)

        tabs.add(current_tab, text="Current Stats")
        tabs.add(stats_tab, text="Stats by Age")
        tabs.add(traits_tab, text="Traits")
        tabs.add(injuries_tab, text="Injury History")
        tabs.add(jobs_tab, text="Job History")

        current_columns = [
            "Age",
            "OVR",
            "POT",
            "MGT",
            "SKL",
            "CUN",
            "LDR",
            "CRG",
            "VIT",
            "AGI",
            "SEA",
            "LOY",
            "REN",
        ]

        current_tree = self.make_sortable_tree(
            current_tab,
            current_columns,
        )

        current_tree.insert(
            "",
            "end",
            values=[
                viking.age,
                viking.overall_grade(),
                viking.potential_overall_grade(),
                viking.effective_stat("might"),
                viking.effective_stat("skill"),
                viking.effective_stat("cunning"),
                viking.effective_stat("leadership"),
                viking.effective_stat("courage"),
                viking.effective_stat("vitality"),
                viking.effective_stat("agility"),
                viking.effective_stat("seamanship"),
                viking.effective_stat("loyalty"),
                viking.renown,
            ],
        )

        current_tree = self.make_sortable_tree(current_tab, current_columns)

        stat_rows = [
            ("MGT", "might"),
            ("SKL", "skill"),
            ("CUN", "cunning"),
            ("LDR", "leadership"),
            ("CRG", "courage"),
            ("VIT", "vitality"),
            ("AGI", "agility"),
            ("SEA", "seamanship"),
            ("LOY", "loyalty"),
        ]

        for label, stat in stat_rows:
            current_tree.insert(
                "",
                "end",
                values=[
                    label,
                    getattr(viking, stat),
                    viking.effective_stat(stat),
                    viking.stat_potential.get(stat, ""),
                ],
            )

        history_columns = [
            "Age", "MGT", "SKL", "CUN", "LDR",
            "CRG", "VIT", "AGI", "SEA",
            "OVR", "POT",
        ]

        history_tree = self.make_sortable_tree(stats_tab, history_columns)

        history = getattr(viking, "stat_history", [])

        if not history:
            history = [{
                "age": viking.age,
                "might": viking.might,
                "skill": viking.skill,
                "cunning": viking.cunning,
                "leadership": viking.leadership,
                "courage": viking.courage,
                "vitality": viking.vitality,
                "agility": viking.agility,
                "seamanship": viking.seamanship,
                "overall": viking.overall_grade(),
                "potential": viking.potential_overall_grade(),
            }]

        for row in history:
            history_tree.insert(
                "",
                "end",
                values=[
                    row.get("age", ""),
                    row.get("might", ""),
                    row.get("skill", ""),
                    row.get("cunning", ""),
                    row.get("leadership", ""),
                    row.get("courage", ""),
                    row.get("vitality", ""),
                    row.get("agility", ""),
                    row.get("seamanship", ""),
                    row.get("overall", ""),
                    row.get("potential", ""),
                ],
            )

        trait_columns = ["Trait", "Description"]

        trait_tree = self.make_sortable_tree(
            traits_tab,
            trait_columns,
        )

        for trait in getattr(viking, "traits", []):
            trait_tree.insert(
                "",
                "end",
                values=[
                    trait.name,
                    trait.description,
                ],
            )

        injury_text = tk.Text(injuries_tab, wrap="word", font=("Consolas", 12))
        injury_text.pack(fill="both", expand=True)

        injury_history = getattr(viking, "injury_history", [])

        if injury_history:
            injury_text.insert("1.0", "\n\n".join(injury_history))
        else:
            injury_text.insert("1.0", "No recorded injury history yet.")

        job_text = tk.Text(jobs_tab, wrap="word", font=("Consolas", 12))
        job_text.pack(fill="both", expand=True)

        job_history = getattr(viking, "job_history", [])

        if job_history:
            job_text.insert("1.0", "\n\n".join(job_history))
        else:
            job_text.insert("1.0", "No recorded job history yet.")

    def change_viking_equipment(self, viking_id: str, slot):
        viking = self.campaign.vikings.get(viking_id)

        if not viking:
            return

        valid_items = [
            item for item in self.campaign.get_unequipped_items()
            if item.is_equippable()
            and item.slot == slot
            and self.campaign.viking_can_equip_item(viking, item)[0]
        ]

        if not valid_items:
            messagebox.showinfo("No Items", "No valid unequipped items for this slot.")
            return

        choice = simpledialog.askinteger(
            "Choose Item",
            "\n".join(
                f"{i + 1}. {item.name}"
                for i, item in enumerate(valid_items)
            ),
        )

        if not choice:
            return

        index = choice - 1

        if index < 0 or index >= len(valid_items):
            messagebox.showwarning("Invalid Choice", "Invalid item number.")
            return

        item = valid_items[index]

        success, message = self.campaign.equip_item_to_viking(
            viking.viking_id,
            item.item_id,
        )

        if success:
            messagebox.showinfo("Equipped", message)
        else:
            messagebox.showwarning("Could Not Equip", message)

        self.refresh_all()

    def refresh_crew(self):
        self.refresh_active_crew()
        self.refresh_growth()
        self.refresh_reserves()
        self.refresh_injured()
        self.refresh_recruits()
        self.refresh_traited_vikings()
        self.refresh_odins_hall()
        self.refresh_retired()
        
    def refresh_active_crew(self):
        self.fill_viking_tree(
            self.active_crew_tree,
            self.campaign.get_active_crew_list(),
        )


    def refresh_growth(self):
        vikings = [
            viking for viking in self.campaign.vikings.values()
            if viking.status not in {
                type(viking.status).DEAD,
                type(viking.status).DESERTED,
                type(viking.status).RETIRED,
            }
        ]

        self.fill_viking_tree(self.growth_tree, vikings)


    def refresh_reserves(self):
        self.fill_viking_tree(
            self.reserves_tree,
            self.campaign.get_reserve_vikings(),
        )


    def refresh_injured(self):
        injured = [
            viking for viking in self.campaign.vikings.values()
            if getattr(viking, "active_injuries", None)
        ]

        self.fill_viking_tree(self.injured_tree, injured)


    def refresh_traited_vikings(self):
        self.traits_tree.delete(*self.traits_tree.get_children())

        traited = [
            viking for viking in self.campaign.vikings.values()
            if getattr(viking, "traits", None)
            and viking.status not in {
                type(viking.status).DEAD,
                type(viking.status).DESERTED,
                type(viking.status).RETIRED,
            }
        ]

        traited.sort(key=lambda viking: viking.display_name())

        for viking in traited:
            first_trait = True

            for trait in viking.traits:
                self.traits_tree.insert(
                    "",
                    "end",
                    values=[
                        viking.display_name() if first_trait else "",
                        trait.name,
                        trait.description,
                    ],
                )

                first_trait = False


    def refresh_recruits(self):
        self.campaign.refresh_recruit_pool()

        self.recruit_tree.delete(*self.recruit_tree.get_children())
        self.recruits = list(self.campaign.recruit_pool.candidates)

        for candidate in self.recruits:
            self.recruit_tree.insert(
                "",
                "end",
                values=self.viking_row(candidate.viking),
            )

    def hire_selected_recruit(self):
        selection = self.recruit_tree.selection()

        if not selection:
            messagebox.showwarning("No Recruit Selected", "Select a recruit first.")
            return

        index = self.recruit_tree.index(selection[0])
        candidate = self.recruits[index]

        success, message = self.campaign.hire_recruit(candidate.candidate_id)

        if success:
            messagebox.showinfo("Recruit Hired", message)
        else:
            messagebox.showwarning("Could Not Hire Recruit", message)

        self.refresh_all()

    def refresh_odins_hall(self):
        self.odins_hall_tree.delete(*self.odins_hall_tree.get_children())

        for entry in self.campaign.odins_hall:
            self.odins_hall_tree.insert(
                "",
                "end",
                values=[
                    entry.get("name", "Unknown"),
                    entry.get("year", ""),
                    entry.get("text", ""),
                ],
            )

    def refresh_retired(self):
        self.retired_tree.delete(*self.retired_tree.get_children())

        for entry in self.campaign.retired_vikings:
            self.retired_tree.insert(
                "",
                "end",
                values=[
                    entry.get("name", "Unknown"),
                    entry.get("year", ""),
                    entry.get("text", ""),
                ],
            )    

    def refresh_ship(self):
        self.refresh_ship_status()
        self.refresh_ship_crew_scores()
        self.refresh_ship_crew()
        self.refresh_ship_reserves()
        self.refresh_ship_upgrades()
        
    def refresh_ship_crew_scores(self):
        from expedition import calculate_crew_strength
        from events import average_crew_stat, average_top_crew_stat

        self.ship_crew_scores_text.delete("1.0", tk.END)

        crew = self.campaign.get_active_crew_list()

        if not crew:
            self.ship_crew_scores_text.insert(
                "1.0",
                "No active crew assigned."
            )
            return

        crew_strength = calculate_crew_strength(crew)

        derived_scores = [
            ("Combat", "combat_score"),
            ("Morale", "morale_score"),
            ("Scouting", "scouting_score"),
            ("Sailing", "sailing_score"),
            ("Evasion", "evasion_score"),
            ("Social", "social_score"),
            ("Command", "command_score"),
            ("Endurance", "endurance_score"),
            ("Skirmish", "skirmish_score"),
            ("Raiding", "raiding_score"),
            ("Navigation", "navigation_score"),
            ("Survival", "survival_score"),
        ]

        lines = [
            "CREW ANALYSIS",
            "-" * 55,
            f"Active Crew: {len(crew)}",
            f"Crew Strength: {crew_strength}",
            "",
            f"{'Score':<15}{'Crew Avg':>10}{'Top Half':>12}",
            "-" * 55,
        ]

        for label, attr in derived_scores:
            avg_score = average_crew_stat(crew, attr)
            top_score = average_top_crew_stat(crew, attr)

            lines.append(
                f"{label:<15}{avg_score:>10}{top_score:>12}"
            )

        self.ship_crew_scores_text.insert(
            "1.0",
            "\n".join(lines)
        )  
        
    def refresh_ship_status(self):
        self.ship_status_text.delete("1.0", tk.END)

        ship = self.campaign.ship

        lines = [
            f"Name: {ship.name}",
            f"Hull: {ship.hull}/{ship.max_hull}",
            f"Crew: {len(ship.crew)}/{ship.max_crew}",
            f"Range: {ship.range}",
            f"Cargo Capacity: {getattr(ship, 'cargo_capacity', '?')}",
            "",
            f"Hull Level: {ship.get_part_level(ShipPart.HULL)}",
            f"Cargo Level: {ship.get_part_level(ShipPart.CARGO)}",
            f"Crew Level: {ship.get_part_level(ShipPart.CREW)}",
            f"Sail Level: {ship.get_part_level(ShipPart.SAIL)}",
            f"Navigation Level: {ship.get_part_level(ShipPart.NAVIGATION)}",
            "",
            f"Resources:",
            f"Silver: {self.campaign.silver}",
            f"Ship Timber: {self.campaign.ship_timber}",
            f"Fine Metal: {self.campaign.fine_metal}",
            "",
            f"Pending Upgrade: {self.campaign.pending_ship_upgrade_name or 'None'}",
            f"Weeks Remaining: {self.campaign.pending_ship_weeks_remaining}",
        ]

        self.ship_status_text.insert("1.0", "\n".join(lines))


    def refresh_ship_crew(self):
        crew = self.campaign.get_ship_crew()
        self.fill_viking_tree(self.ship_crew_tree, crew)


    def refresh_ship_reserves(self):
        reserves = self.campaign.get_reserve_vikings()
        self.fill_viking_tree(self.ship_reserves_tree, reserves)


    def refresh_ship_upgrades(self):
        self.ship_upgrade_tree.delete(*self.ship_upgrade_tree.get_children())
        self.ship_upgrade_options = []

        parts = [
            ShipPart.HULL,
            ShipPart.CARGO,
            ShipPart.CREW,
            ShipPart.SAIL,
            ShipPart.NAVIGATION,
        ]

        for part in parts:
            current_level = self.campaign.ship.get_part_level(part)
            upgrade = get_next_ship_upgrade(part, current_level)

            if not upgrade:
                continue

            self.ship_upgrade_options.append((part, upgrade))

            requires = (
                f"Shipwright Lv.{upgrade.required_shipyard_level}, "
                f"Woodwright Lv.{upgrade.required_carpenters_hut_level}"
            )

            self.ship_upgrade_tree.insert(
                "",
                "end",
                values=[
                    part.value,
                    upgrade.name,
                    current_level,
                    upgrade.level,
                    upgrade.silver_cost,
                    upgrade.ship_timber_cost,
                    upgrade.fine_metal_cost,
                    upgrade.build_weeks,
                    requires,
                    upgrade.description,
                ],
            )  

    def get_selected_viking_from_tree(self, tree, vikings):
        selection = tree.selection()

        if not selection:
            return None

        index = tree.index(selection[0])

        if index < 0 or index >= len(vikings):
            return None

        return vikings[index]


    def remove_selected_ship_crew(self):
        crew = self.campaign.get_ship_crew()
        viking = self.get_selected_viking_from_tree(self.ship_crew_tree, crew)

        if not viking:
            messagebox.showwarning("No Crew Selected", "Select a ship crew member first.")
            return

        success, message = self.campaign.remove_crew_member_from_ship(viking.viking_id)

        if success:
            messagebox.showinfo("Crew Removed", message)
        else:
            messagebox.showwarning("Could Not Remove Crew", message)

        self.refresh_all()


    def add_selected_reserve_to_ship(self):
        reserves = self.campaign.get_reserve_vikings()
        viking = self.get_selected_viking_from_tree(self.ship_reserves_tree, reserves)

        if not viking:
            messagebox.showwarning("No Reserve Selected", "Select a reserve first.")
            return

        success, message = self.campaign.add_reserve_to_ship(viking.viking_id)

        if success:
            messagebox.showinfo("Reserve Added", message)
        else:
            messagebox.showwarning("Could Not Add Reserve", message)

        self.refresh_all()


    def assign_selected_captain(self):
        crew = self.campaign.get_ship_crew()
        viking = self.get_selected_viking_from_tree(self.ship_crew_tree, crew)

        if not viking:
            messagebox.showwarning("No Crew Selected", "Select a ship crew member first.")
            return

        success, message = self.campaign.assign_crew_role(
            viking.viking_id,
            CrewRole.CAPTAIN,
        )

        if success:
            messagebox.showinfo("Captain Assigned", message)
        else:
            messagebox.showwarning("Could Not Assign Captain", message)

        self.refresh_all()


    def repair_ship(self):
        success, message = self.campaign.repair_ship_at_shipyard()

        if success:
            messagebox.showinfo("Ship Repaired", message)
        else:
            messagebox.showwarning("Could Not Repair Ship", message)

        self.refresh_all()


    def start_selected_ship_upgrade(self):
        selection = self.ship_upgrade_tree.selection()

        if not selection:
            messagebox.showwarning("No Upgrade Selected", "Select a ship upgrade first.")
            return

        index = self.ship_upgrade_tree.index(selection[0])

        if index < 0 or index >= len(self.ship_upgrade_options):
            messagebox.showwarning("Invalid Selection", "Could not find that upgrade.")
            return

        part, upgrade = self.ship_upgrade_options[index]

        success, message = self.campaign.start_ship_upgrade(part)

        if success:
            messagebox.showinfo("Upgrade Started", message)
        else:
            messagebox.showwarning("Could Not Start Upgrade", message)

        self.refresh_all()            

    def refresh_market(self):
        self.market_buy_tree.delete(*self.market_buy_tree.get_children())
        self.market_sell_tree.delete(*self.market_sell_tree.get_children())

        self.market_buy_items = list(TRADER_STOCK)
        self.market_sell_items = self.campaign.get_unequipped_items()

        for item in self.market_buy_items:
            slot_text = item.slot.value if item.slot else "-"

            self.market_buy_tree.insert(
                "",
                "end",
                values=[
                    item.name,
                    item.item_type.value,
                    slot_text,
                    item.value,
                ],
            )

        for item in self.market_sell_items:
            slot_text = item.slot.value if item.slot else "-"
            sale_value = max(1, item.value // 2)

            self.market_sell_tree.insert(
                "",
                "end",
                values=[
                    item.name,
                    item.item_type.value,
                    slot_text,
                    sale_value,
                ],
            )


    def refresh_smithy(self):
        self.smithy_buy_tree.delete(*self.smithy_buy_tree.get_children())
        self.smithy_upgrade_tree.delete(*self.smithy_upgrade_tree.get_children())

        self.smithy_buy_items = []
        self.smithy_upgrade_items = [
            item for item in self.campaign.inventory.values()
            if getattr(item, "quality", None) in QUALITY_UPGRADES
        ]

        for item_name in SMITHY_BUY_ITEMS:
            preview = create_item_by_name(item_name, ItemQuality.FINE)

            if not preview:
                continue

            silver_cost = max(1, preview.value // 2)
            metal_cost = 2

            self.smithy_buy_items.append((item_name, silver_cost, metal_cost))

            self.smithy_buy_tree.insert(
                "",
                "end",
                values=[
                    item_name,
                    silver_cost,
                    metal_cost,
                ],
            )

        for item in self.smithy_upgrade_items:
            current_quality = item.quality
            next_quality = QUALITY_UPGRADES[current_quality]
            metal_cost = QUALITY_UPGRADE_COSTS[current_quality]
            equipped_text = "Yes" if self.campaign.item_is_equipped(item.item_id) else "No"

            self.smithy_upgrade_tree.insert(
                "",
                "end",
                values=[
                    item.name,
                    current_quality.value,
                    next_quality.value,
                    metal_cost,
                    equipped_text,
                ],
            )

    def buy_selected_trader_item(self):
        selection = self.market_buy_tree.selection()

        if not selection:
            messagebox.showwarning("No Item Selected", "Select an item to buy.")
            return

        index = self.market_buy_tree.index(selection[0])
        item = self.market_buy_items[index]

        success, message = self.campaign.buy_trader_item(item)

        if success:
            messagebox.showinfo("Item Bought", message)
        else:
            messagebox.showwarning("Could Not Buy", message)

        self.refresh_all()


    def sell_selected_market_item(self):
        selection = self.market_sell_tree.selection()

        if not selection:
            messagebox.showwarning("No Item Selected", "Select an unequipped item to sell.")
            return

        index = self.market_sell_tree.index(selection[0])
        item = self.market_sell_items[index]

        success, message = self.campaign.sell_item_to_trader(item.item_id)

        if success:
            messagebox.showinfo("Item Sold", message)
        else:
            messagebox.showwarning("Could Not Sell", message)

        self.refresh_all()


    def buy_selected_smithy_item(self):
        if not self.campaign.has_smithy():
            messagebox.showwarning("No Smithy", "You need to build a Smithy first.")
            return

        selection = self.smithy_buy_tree.selection()

        if not selection:
            messagebox.showwarning("No Item Selected", "Select a smithy item to buy.")
            return

        index = self.smithy_buy_tree.index(selection[0])
        item_name, silver_cost, metal_cost = self.smithy_buy_items[index]

        if self.campaign.silver < silver_cost:
            messagebox.showwarning("Not Enough Silver", f"Need {silver_cost} silver.")
            return

        if self.campaign.fine_metal < metal_cost:
            messagebox.showwarning("Not Enough Fine Metal", f"Need {metal_cost} fine metal.")
            return

        item = create_item_by_name(item_name, ItemQuality.FINE)

        if not item:
            messagebox.showwarning("Could Not Create Item", "That item could not be created.")
            return

        self.campaign.silver -= silver_cost
        self.campaign.fine_metal -= metal_cost
        self.campaign.add_item(item)

        messagebox.showinfo("Item Bought", f"Purchased {item.name}.")
        self.refresh_all()


    def upgrade_selected_smithy_item(self):
        if not self.campaign.has_smithy():
            messagebox.showwarning("No Smithy", "You need to build a Smithy first.")
            return

        selection = self.smithy_upgrade_tree.selection()

        if not selection:
            messagebox.showwarning("No Item Selected", "Select an item to upgrade.")
            return

        index = self.smithy_upgrade_tree.index(selection[0])
        item = self.smithy_upgrade_items[index]

        current_quality = item.quality
        next_quality = QUALITY_UPGRADES[current_quality]
        metal_cost = QUALITY_UPGRADE_COSTS[current_quality]

        if self.campaign.fine_metal < metal_cost:
            messagebox.showwarning("Not Enough Fine Metal", f"Need {metal_cost} fine metal.")
            return

        self.campaign.fine_metal -= metal_cost

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

        messagebox.showinfo("Item Upgraded", f"Upgraded {item.name} to {next_quality.value}.")
        self.refresh_all()

    def refresh_village(self):
        self.refresh_village_overview()
        self.refresh_village_buildings()
        self.refresh_village_injury_report()
        self.refresh_market()
        self.refresh_smithy()
        
    def refresh_village_overview(self):
        self.village_text.delete("1.0", tk.END)
        self.village_text.insert("1.0", self.campaign.village.summary())


    def refresh_village_buildings(self):
        self.village_build_text.delete("1.0", tk.END)

        village = self.campaign.village

        lines = [
            f"Village: {village.name}",
            "",
            "Tiles / Buildings:",
            "-" * 80,
        ]

        for tile in village.tiles.values():
            building = getattr(tile, "building", None)

            if building:
                status = ""
                if building.is_under_construction:
                    status = f" | Under construction: {building.weeks_remaining}w"

                lines.append(
                    f"({tile.x}, {tile.y}) "
                    f"{building.building_type.value} Lv.{building.level}"
                    f"{status}"
                )
            else:
                lines.append(f"({tile.x}, {tile.y}) Empty")

        self.village_build_text.insert("1.0", "\n".join(lines))


    def refresh_village_injury_report(self):
        self.village_injury_text.delete("1.0", tk.END)

        injured = [
            viking for viking in self.campaign.vikings.values()
            if getattr(viking, "active_injuries", None)
        ]

        lines = ["INJURY REPORT", "-" * 100]

        if not injured:
            lines.append("No active injuries.")
        else:
            for viking in injured:
                lines.append(
                    f"\n{viking.display_name()} | "
                    f"{viking.viking_class.value} | "
                    f"{viking.status.value}"
                )

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
                        if getattr(injury, "pending_title", None)
                        else ""
                    )

                    lines.append(
                        f"  - {injury.name}: {recovery_text} | "
                        f"{deploy_text} | {mod_text}{pending_title_text}"
                    )

        self.village_injury_text.insert("1.0", "\n".join(lines))

    def get_selected_village_coordinates(self):
        try:
            x = int(self.village_x_var.get().strip())
            y = int(self.village_y_var.get().strip())
        except ValueError:
            messagebox.showwarning(
                "Invalid Coordinates",
                "Tile X and Tile Y must be numbers.",
            )
            return None

        return x, y


    def get_selected_building_type(self):
        selected = self.building_var.get()

        for building_type in self.buildable_buildings:
            if building_type.value == selected:
                return building_type

        return None


    def build_selected_village_facility(self):
        coords = self.get_selected_village_coordinates()

        if coords is None:
            return

        building_type = self.get_selected_building_type()

        if building_type is None:
            messagebox.showwarning("Invalid Building", "Select a valid building.")
            return

        x, y = coords

        success, message = self.campaign.build_village_facility(
            x,
            y,
            building_type,
        )

        if success:
            messagebox.showinfo("Building Started", message)
        else:
            messagebox.showwarning("Could Not Build", message)

        self.refresh_all()


    def upgrade_selected_village_building(self):
        coords = self.get_selected_village_coordinates()

        if coords is None:
            return

        x, y = coords

        success, message = self.campaign.upgrade_village_building(x, y)

        if success:
            messagebox.showinfo("Upgrade Started", message)
        else:
            messagebox.showwarning("Could Not Upgrade", message)

        self.refresh_all()


    def purchase_village_tile(self):
        success, message = self.campaign.purchase_village_tile()

        if success:
            messagebox.showinfo("Tile Purchased", message)
        else:
            messagebox.showwarning("Could Not Purchase Tile", message)

        self.refresh_all()


    def conquer_village_tile_debug(self):
        success, message = self.campaign.conquer_village_tile_debug()

        if success:
            messagebox.showinfo("Tile Conquered", message)
        else:
            messagebox.showwarning("Could Not Conquer Tile", message)

        self.refresh_all()        

    def on_job_selected(self, event=None):
        selection = self.jobs_tree.selection()

        if not selection:
            return

        index = self.jobs_tree.index(selection[0])

        if index < 0 or index >= len(self.jobs):
            return

        self.selected_job = self.jobs[index]
        job = self.selected_job

        reward_parts = []

        if job.guaranteed_silver > 0:
            reward_parts.append(f"{job.guaranteed_silver} silver")

        if job.guaranteed_food > 0:
            reward_parts.append(f"{job.guaranteed_food} food")

        if job.reward_renown > 0:
            reward_parts.append(f"{job.reward_renown} renown")

        if job.reward_thralls > 0:
            reward_parts.append(f"{job.reward_thralls} thralls")

        if job.reward_ship_timber > 0:
            reward_parts.append(f"{job.reward_ship_timber} ship timber")

        if job.reward_fine_metal > 0:
            reward_parts.append(f"{job.reward_fine_metal} fine metal")

        reward_text = ", ".join(reward_parts) if reward_parts else "None"

        details = [
            f"Name: {job.name}",
            f"Type: {job.job_type.value}",
            f"Location: {job.location_name}",
            f"Employer: {job.employer if job.employer else 'Independent'}",
            "",
            f"Duration: {job.duration_weeks} weeks",
            f"Food Cost: {self.campaign.calculate_food_cost(job)}",
            f"Required Range: {job.required_range}",
            f"Required Crew: {job.required_min_crew}",
            f"Difficulty: {job.difficulty}",
            f"Danger: {job.danger}",
            f"Travel: {job.travel_type.value}",
            "",
            f"Guaranteed Rewards: {reward_text}",
            "",
            job.description,
        ]

        self.job_detail_text.delete("1.0", tk.END)
        self.job_detail_text.insert("1.0", "\n".join(details))

    def take_selected_job(self):
        if not self.selected_job:
            messagebox.showwarning("No Job Selected", "Select a job first.")
            return

        job_name = self.selected_job.name
        success, message = self.campaign.take_job(self.selected_job)

        self.show_expedition_screen(job_name)

        self.current_log_lines = message.split("\n")
        self.current_log_index = 0

        self.stream_expedition_log()

        if not success:
            messagebox.showwarning("Expedition Failed", "The expedition failed.")
        
    def stream_expedition_log(self):
        if (
            not hasattr(self, "expedition_window")
            or not self.expedition_window.winfo_exists()
        ):
            return

        if (
            not hasattr(self, "expedition_log_text")
            or not self.expedition_log_text.winfo_exists()
        ):
            return

        if self.current_log_index >= len(self.current_log_lines):
            if hasattr(self, "expedition_back_button") and self.expedition_back_button.winfo_exists():
                self.expedition_back_button.pack(pady=10)
            return

        line = self.current_log_lines[self.current_log_index]

        self.expedition_log_text.insert(tk.END, line + "\n")
        self.expedition_log_text.see(tk.END)

        self.current_log_index += 1

        self.root.after(700, self.stream_expedition_log)        
        
    def fast_sim_selected_job(self):
        if not self.selected_job:
            messagebox.showwarning("No Job Selected", "Select a job first.")
            return

        job_name = self.selected_job.name
        success, message = self.campaign.take_job(self.selected_job)

        result_text = "SUCCESS" if success else "FAILURE"

        self.job_detail_text.delete("1.0", tk.END)
        self.job_detail_text.insert(
            "1.0",
            f"Fast sim complete: {result_text} - {job_name}",
        )

        if not success:
            messagebox.showwarning("Job Failed", message)

        self.refresh_summary()
        self.refresh_dashboard()
        self.refresh_crew()
        self.refresh_ship()
        self.refresh_village()
        self.refresh_jobs()        

    def advance_week(self):
        logs = self.campaign.advance_weeks(1, print_logs=False)

        self.job_detail_text.delete("1.0", tk.END)
        self.job_detail_text.insert("1.0", "\n".join(logs) or "One week passed.")

        self.refresh_all()


def main():
    root = tk.Tk()
    app = GoingVikingGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()