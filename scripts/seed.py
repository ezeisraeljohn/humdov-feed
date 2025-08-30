"""Script to populate the database with demo data"""

import sys
from pathlib import Path

# Add the project root to the Python path so we can import our modules
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlmodel import Session
from app.core.session import engine
from app.services.seed_service import SeedService


def get_user_input():
    """Get seeding parameters from user with validation and defaults"""
    print("Configure your database seeding parameters")
    print("   (Press Enter to use default values)")
    print("-" * 50)

    def get_validated_input(prompt: str, min_value: int, default: int) -> int:
        """Get and validate user input with minimum value and default"""
        while True:
            try:
                user_input = input(
                    f"{prompt} (min: {min_value}, default: {default}): "
                ).strip()

                if user_input == "":
                    return default

                value = int(user_input)
                if value < min_value:
                    print(
                        f"Value must be at least {min_value}. Using default: {default}"
                    )
                    return default

                return value

            except ValueError:
                print("Please enter a valid number or press Enter for default.")

    # Get user inputs with validation
    num_users = get_validated_input("Number of users", 10, 20)
    posts_per_user = get_validated_input("Posts per user", 50, 100)
    num_tags = get_validated_input("Number of tags", 20, 50)
    likes_per_user = get_validated_input("Likes per user", 40, 40)
    comments_per_user = get_validated_input("Comments per user", 40, 40)

    # Show summary and confirm
    print("\nConfiguration Summary:")
    print(f"   • Users: {num_users}")
    print(
        f"   • Posts per user: {posts_per_user} (Total: {num_users * posts_per_user})"
    )
    print(f"   • Tags: {num_tags}")
    print(
        f"   • Likes per user: {likes_per_user} (Total: ~{num_users * likes_per_user})"
    )
    print(
        f"   • Comments per user: {comments_per_user} (Total: ~{num_users * comments_per_user})"
    )

    print(
        "\nNote: This will generate a large amount of data and may take several minutes!"
    )

    confirm = input("\nProceed with seeding? (yes/no): ").lower().strip()
    if confirm != "yes":
        print("Operation cancelled")
        return None

    return {
        "num_users": num_users,
        "posts_per_user": posts_per_user,
        "num_tags": num_tags,
        "likes_per_user": likes_per_user,
        "comments_per_user": comments_per_user,
    }


def main():
    """Main function to seed the database"""
    print("Humdov Feed Database Seeder")
    print("=" * 40)

    # Check if user wants to clear existing data
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        print("WARNING: This will delete ALL existing data!")
        confirm = input("Are you sure you want to continue? (yes/no): ").lower().strip()

        if confirm == "yes":
            with Session(engine) as session:
                SeedService.clear_all_data(session)
            print("Data cleared successfully")
        else:
            print("Operation cancelled")
        return

    # Quick seed with defaults
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        print("Quick seeding with default values...")
        try:
            with Session(engine) as session:
                SeedService.seed_all(session)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)
        except Exception as e:
            print(f"Error during seeding: {str(e)}")
            sys.exit(1)
        return

    # Show help
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h"]:
        print("Usage:")
        print(
            "  python scripts/seed.py          # Seed with custom parameters (interactive)"
        )
        print(
            "  python scripts/seed.py --quick  # Seed with default values (non-interactive)"
        )
        print("  python scripts/seed.py --clear  # Clear all existing data")
        print("  python scripts/seed.py --help   # Show this help message")
        print("\nDefault values:")
        print("  • Users: 20 (minimum: 10)")
        print("  • Posts per user: 500 (minimum: 50)")
        print("  • Tags: 50 (minimum: 20)")
        print("  • Likes per user: 40 (minimum: 40)")
        print("  • Comments per user: 40 (minimum: 40)")
        return

    try:
        # Get user configuration
        config = get_user_input()
        if config is None:
            return

        # Create database session and seed data
        print("\nStarting seeding process...")
        with Session(engine) as session:
            SeedService.seed_all(
                session,
                num_users=config["num_users"],
                posts_per_user=config["posts_per_user"],
                num_tags=config["num_tags"],
                likes_per_user=config["likes_per_user"],
                comments_per_user=config["comments_per_user"],
            )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error during seeding: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
