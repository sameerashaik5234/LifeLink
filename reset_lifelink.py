import mysql.connector

# =========================================================
# LifeLink - Database Test Data Reset
# =========================================================

DB_PASSWORD = "lifelink@2324"


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=DB_PASSWORD,
        database="lifelink"
    )


print()
print("==========================================")
print("       LifeLink Database Reset")
print("==========================================")
print()

print("WARNING:")
print("This will delete existing TEST DATA only.")
print("Database tables and project files will NOT be deleted.")
print()

confirm = input("Type RESET to continue: ")

if confirm != "RESET":
    print()
    print("Reset cancelled.")
    exit()


conn = get_connection()
cursor = conn.cursor()

try:

    print()
    print("Deleting old test data...")
    print()

    # -----------------------------------------------------
    # Disable foreign key checks temporarily
    # -----------------------------------------------------

    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    # -----------------------------------------------------
    # Delete child tables first
    # -----------------------------------------------------

    cursor.execute("DELETE FROM donor_responses")
    print("✓ Donor responses cleared")

    cursor.execute("DELETE FROM donations")
    print("✓ Donations cleared")

    cursor.execute("DELETE FROM blood_requests")
    print("✓ Blood requests cleared")

    # -----------------------------------------------------
    # Delete hospitals
    # -----------------------------------------------------

    cursor.execute("DELETE FROM hospitals")
    print("✓ Hospitals cleared")

    # -----------------------------------------------------
    # Delete users
    # -----------------------------------------------------

    cursor.execute("DELETE FROM users")
    print("✓ Users cleared")

    # -----------------------------------------------------
    # Reset AUTO_INCREMENT counters
    # -----------------------------------------------------

    cursor.execute(
        "ALTER TABLE donor_responses AUTO_INCREMENT = 1"
    )

    cursor.execute(
        "ALTER TABLE donations AUTO_INCREMENT = 1"
    )

    cursor.execute(
        "ALTER TABLE blood_requests AUTO_INCREMENT = 1"
    )

    cursor.execute(
        "ALTER TABLE hospitals AUTO_INCREMENT = 1"
    )

    cursor.execute(
        "ALTER TABLE users AUTO_INCREMENT = 1"
    )

    # -----------------------------------------------------
    # Enable foreign key checks again
    # -----------------------------------------------------

    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    conn.commit()

    print()
    print("==========================================")
    print("       RESET COMPLETED SUCCESSFULLY")
    print("==========================================")
    print()

    print("Old test data removed.")
    print("Database tables are still safe.")
    print("AUTO_INCREMENT counters reset.")
    print()

    print("Now you can create fresh:")
    print("1. Admin")
    print("2. Hospital")
    print("3. Donor")
    print("4. Patient")
    print("5. Blood Requests")
    print()

except Exception as e:

    conn.rollback()

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    except:
        pass

    print()
    print("ERROR:")
    print(e)
    print()
    print("Reset was not completed.")

finally:

    cursor.close()
    conn.close()