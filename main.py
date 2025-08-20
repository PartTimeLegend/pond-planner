#!/usr/bin/env python3
"""
Pond Planning Application
Calculates pond capacity, fish stocking, and equipment sizing using metric measurements
"""

from PondPlanner import PondPlanner


def show_menu():
    """Display the main menu options."""
    print("\n🐟 Pond Planning Application 🐟")
    print("=" * 40)
    print("1. Create new pond plan")
    print("2. Load saved pond plan")
    print("3. List saved pond plans")
    print("4. Delete saved pond plan")
    print("5. Exit")
    print("-" * 40)


def create_new_pond(planner):
    """Create a new pond plan interactively."""
    print("\n📐 Creating New Pond Plan")
    print("=" * 30)

    # Get pond dimensions with validation
    print("\nEnter pond dimensions:")
    while True:
        try:
            length = float(input("Length (meters): "))
            width = float(input("Width (meters): "))
            depth = float(input("Average depth (meters): "))

            if length <= 0 or width <= 0 or depth <= 0:
                print("All dimensions must be positive values. Please try again.")
                continue
            break
        except ValueError:
            print("Please enter valid numbers for dimensions.")

    # Shape selection
    print("\nAvailable shapes:")
    shapes = planner.get_available_shapes()
    for i, shape in enumerate(shapes, 1):
        print(f"{i:2d}. {shape}")

    shape_input = input(f"Shape (1-{len(shapes)} or name) [rectangular]: ").strip()
    if shape_input.isdigit():
        shape_index = int(shape_input) - 1
        if 0 <= shape_index < len(shapes):
            shape = shapes[shape_index]
        else:
            shape = "rectangular"
    else:
        shape = shape_input.lower() if shape_input else "rectangular"

    planner.set_dimensions(length, width, depth, shape)

    # Fish stocking
    add_fish_to_pond(planner)

    # Show report
    print("\n" + planner.generate_report())

    # Ask if user wants to save
    save_choice = (
        input("\nWould you like to save this pond plan? (y/n): ").strip().lower()
    )
    if save_choice in ["y", "yes"]:
        save_pond_plan(planner)


def add_fish_to_pond(planner):
    """Add fish to the pond interactively."""
    print("\n🐠 Fish Stocking")
    print("=" * 20)

    print("Available fish types (showing first 20):")
    fish_types = planner.get_fish_types_list()
    for i, fish_type in enumerate(fish_types[:20], 1):
        fish = planner.fish_database[fish_type]
        print(f"{i:2d}. {fish_type}: {fish.name} ({fish.min_liters_per_fish} L/fish)")

    if len(fish_types) > 20:
        print(f"... and {len(fish_types) - 20} more fish types")

    print(f"\nAdd fish to your pond (enter number 1-{len(fish_types)} or fish name):")
    print("Type 'list' to see all fish types, or press Enter to finish:")

    while True:
        fish_input = input("Fish type: ").strip()
        if not fish_input:
            break

        if fish_input.lower() == "list":
            print("\nAll available fish types:")
            for i, fish_type in enumerate(fish_types, 1):
                fish = planner.fish_database[fish_type]
                print(f"{i:3d}. {fish_type}: {fish.name}")
            continue

        try:
            # Check if input is a number
            if fish_input.isdigit():
                fish_index = int(fish_input) - 1
                if 0 <= fish_index < len(fish_types):
                    selected_fish = fish_types[fish_index]
                else:
                    print(f"Invalid number! Please enter 1-{len(fish_types)}")
                    continue
            else:
                # Check if input matches a fish name
                fish_input_lower = fish_input.lower()
                if fish_input_lower in planner.fish_database:
                    selected_fish = fish_input_lower
                else:
                    print(
                        "Unknown fish type! Please try again or type 'list' to see all options."
                    )
                    continue

            # Get quantity and add fish
            fish_display_name = planner.fish_database[selected_fish].name
            while True:
                try:
                    quantity = int(input(f"Number of {fish_display_name}: "))
                    if quantity <= 0:
                        print("Quantity must be positive. Please try again.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number for quantity.")

            planner.add_fish(selected_fish, quantity)
            print(f"✅ Added {quantity} {fish_display_name} to pond")

        except (ValueError, KeyError, AttributeError) as e:
            print(f"Error adding fish: {e}")


def save_pond_plan(planner):
    """Save the current pond plan."""
    try:
        name = input("Enter a name for this pond plan: ").strip()
        if not name:
            print("❌ Pond name cannot be empty.")
            return

        description = input("Enter a description (optional): ").strip()

        filename = planner.save_pond(name, description)
        print(f"✅ Pond plan saved as: {filename}")

    except Exception as e:
        print(f"❌ Error saving pond plan: {e}")


def load_pond_plan(planner):
    """Load a saved pond plan."""
    try:
        saved_ponds = planner.list_saved_ponds()
        if not saved_ponds:
            print("❌ No saved pond plans found.")
            return False

        print("\n📂 Saved Pond Plans:")
        print("=" * 25)
        for i, pond in enumerate(saved_ponds, 1):
            created_date = pond["created_at"][:10]  # Just the date part
            print(f"{i:2d}. {pond['name']}")
            print(
                f"    Shape: {pond['shape']}, Fish: {pond['fish_count']}, Created: {created_date}"
            )
            if pond["description"]:
                print(f"    Description: {pond['description']}")
            print()

        choice = input(f"Select pond to load (1-{len(saved_ponds)}): ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(saved_ponds):
                filename = saved_ponds[index]["filename"]
                planner.load_pond(filename)
                print(f"✅ Loaded pond plan: {saved_ponds[index]['name']}")
                return True
            else:
                print("❌ Invalid selection.")
        else:
            print("❌ Please enter a valid number.")
        return False

    except Exception as e:
        print(f"❌ Error loading pond plan: {e}")
        return False


def list_saved_ponds(planner):
    """List all saved pond plans."""
    try:
        saved_ponds = planner.list_saved_ponds()
        if not saved_ponds:
            print("❌ No saved pond plans found.")
            return

        print("\n📂 Saved Pond Plans:")
        print("=" * 25)
        for i, pond in enumerate(saved_ponds, 1):
            created_date = pond["created_at"][:10]  # Just the date part
            print(f"{i:2d}. {pond['name']}")
            print(
                f"    Shape: {pond['shape']}, Fish: {pond['fish_count']}, Created: {created_date}"
            )
            if pond["description"]:
                print(f"    Description: {pond['description']}")
            print(f"    Filename: {pond['filename']}.json")
            print()

    except Exception as e:
        print(f"❌ Error listing pond plans: {e}")


def delete_pond_plan(planner):
    """Delete a saved pond plan."""
    try:
        saved_ponds = planner.list_saved_ponds()
        if not saved_ponds:
            print("❌ No saved pond plans found.")
            return

        print("\n🗑️  Delete Pond Plan:")
        print("=" * 22)
        for i, pond in enumerate(saved_ponds, 1):
            created_date = pond["created_at"][:10]
            print(f"{i:2d}. {pond['name']} (Created: {created_date})")

        choice = input(f"Select pond to delete (1-{len(saved_ponds)}): ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(saved_ponds):
                pond_name = saved_ponds[index]["name"]
                confirm = (
                    input(f"Are you sure you want to delete '{pond_name}'? (y/n): ")
                    .strip()
                    .lower()
                )
                if confirm in ["y", "yes"]:
                    filename = saved_ponds[index]["filename"]
                    if planner.delete_saved_pond(filename):
                        print(f"✅ Deleted pond plan: {pond_name}")
                    else:
                        print(f"❌ Failed to delete pond plan: {pond_name}")
                else:
                    print("❌ Delete cancelled.")
            else:
                print("❌ Invalid selection.")
        else:
            print("❌ Please enter a valid number.")

    except Exception as e:
        print(f"❌ Error deleting pond plan: {e}")


def main():
    """
    Main entry point for the Pond Planning Application.

    This function provides an interactive command-line interface for users to:
    1. Create new pond plans with dimensions and fish stocking
    2. Save and load pond configurations
    3. Manage saved pond plans
    4. Generate comprehensive pond planning reports
    """
    try:
        planner = PondPlanner()

        while True:
            show_menu()
            choice = input("Select an option (1-5): ").strip()

            if choice == "1":
                create_new_pond(planner)
            elif choice == "2":
                if load_pond_plan(planner):
                    # Show the loaded pond
                    print("\n" + planner.generate_report())
                    # Ask if they want to modify it
                    modify = (
                        input("\nWould you like to add more fish? (y/n): ")
                        .strip()
                        .lower()
                    )
                    if modify in ["y", "yes"]:
                        add_fish_to_pond(planner)
                        print("\n" + planner.generate_report())
                        # Ask if they want to save changes
                        save_choice = input("\nSave changes? (y/n): ").strip().lower()
                        if save_choice in ["y", "yes"]:
                            save_pond_plan(planner)
            elif choice == "3":
                list_saved_ponds(planner)
            elif choice == "4":
                delete_pond_plan(planner)
            elif choice == "5":
                print("\n👋 Thank you for using Pond Planning Application!")
                break
            else:
                print("❌ Invalid option. Please select 1-5.")

            input("\nPress Enter to continue...")

    except (KeyboardInterrupt, EOFError):
        print("\n👋 Application interrupted by user. Goodbye!")
    except (ImportError, AttributeError) as e:
        print(f"❌ Application setup error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
