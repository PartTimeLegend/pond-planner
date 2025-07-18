#!/usr/bin/env python3
"""
Pond Planning Application
Calculates pond capacity, fish stocking, and equipment sizing using metric measurements
"""

from PondPlanner import PondPlanner


def main():
    """
    Main entry point for the Pond Planning Application.

    This function provides an interactive command-line interface for users to:
    1. Input pond dimensions (length, width, depth)
    2. Select a pond shape from available options
    3. Add fish to the pond by selecting fish types and quantities
    4. Generate and display a comprehensive pond planning report
    """
    try:
        planner = PondPlanner()

        print("🐟 Pond Planning Application 🐟")
        print("=" * 40)

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
        print("\nAvailable fish types:")
        fish_types = planner.get_fish_types_list()
        for i, fish_type in enumerate(fish_types, 1):
            fish = planner.fish_database[fish_type]
            print(
                f"{i:2d}. {fish_type}: {fish.name} ({fish.min_liters_per_fish} L/fish)"
            )

        print(
            f"\nAdd fish to your pond (enter number 1-{len(fish_types)} or fish name):"
        )
        print("Press Enter with empty input to finish:")

        while True:
            fish_input = input("Fish type: ").strip()
            if not fish_input:
                break

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
                        print("Unknown fish type! Please try again.")
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
                print(f"Added {quantity} {fish_display_name} to pond")

            except (ValueError, KeyError, AttributeError) as e:
                print(f"Error adding fish: {e}")

        # Generate and display report
        print("\n" + planner.generate_report())

    except (KeyboardInterrupt, EOFError):
        print("\nApplication interrupted by user.")
    except (ImportError, AttributeError) as e:
        print(f"Application setup error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
