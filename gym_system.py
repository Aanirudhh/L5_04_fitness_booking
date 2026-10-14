"""Fitness club class booking ledger.

Books members into classes up to a capacity limit, handles cancellations,
and exports the rosters to a JSON file.
"""

import json
import os
import glob

CLASS_CAPACITY = {"Yoga": 3, "HIIT": 2, "Spin": 4}
rosters = {}


def book_class(member_id, class_name, attendance_log=None):
    """Book a member into a class if it exists and has free capacity."""
    if attendance_log is None:
        attendance_log = []
    if class_name not in CLASS_CAPACITY:
        print("Unknown class:", class_name)
        return False
    rosters.setdefault(class_name, [])
    if len(rosters[class_name]) >= CLASS_CAPACITY[class_name]:
        print("Class full:", class_name)
        return False
    rosters[class_name].append(member_id)
    attendance_log.append(f"{member_id} -> {class_name}")
    return True


def cancel_booking(member_id, class_name):
    """Remove a member from a class roster, if they were booked."""
    try:
        rosters[class_name].remove(member_id)
    except (KeyError, ValueError):
        print("Nothing to cancel")


def set_capacity(class_name, seats):
    """Set the seat capacity for a class. Rejects non-positive values."""
    if seats <= 0:
        print("Capacity must be positive, ignoring:", seats)
        return
    CLASS_CAPACITY[class_name] = seats


def add_members(class_name, count):
    """Book `count` walk-in guests into a class."""
    for i in range(count):
        book_class(f"GUEST-{i}", class_name)


def export_roster(file="gym_schedule.json"):
    """Write the current rosters to a JSON file."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(rosters, f)


def clear_old_exports(prefix="old_"):
    """Delete previously exported JSON files matching a prefix."""
    for path in glob.glob(f"{prefix}*.json"):
        os.remove(path)


def show_rosters():
    """Print each class roster to the console."""
    for class_name, members in rosters.items():
        print(class_name, ":", ", ".join(str(m) for m in members))


def main():
    """Run a demo booking session."""
    book_class("M1", "Yoga")
    book_class("M2", "Yoga")
    book_class("M3", "Yoga")
    book_class("M4", "Yoga")
    book_class(55, "HIIT")
    book_class("M5", "Pilates")
    set_capacity("Spin", -2)
    add_members("Spin", 3)
    cancel_booking("M9", "Boxing")

    prompt = "How many walk-in guests for HIIT? (Enter for 1): "
    raw_input = input(prompt) or "1"
    try:
        guest_count = int(raw_input)
    except ValueError:
        print("Not a number, defaulting to 1 guest")
        guest_count = 1
    add_members("HIIT", guest_count)

    clear_old_exports()
    export_roster()
    show_rosters()


if __name__ == "__main__":
    main()