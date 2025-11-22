import os
import sys

def patch_installer(filename="ScreenConnect.ClientSetup.sh"):
    if not os.path.exists(filename):
        print(f"Error: {filename} not found.")
        return

    print(f"Reading {filename}...")

    # Read the file as binary to preserve the payload at the end
    with open(filename, 'rb') as f:
        data = f.read()

    # The logic we need to fix is inside determinePackageType.
    # We look for the 'elif which dpkg ... fi' block and append an 'else echo app' before the fi.

    # We search for the byte sequence corresponding to the end of that function.
    # Original:
    # elif which dpkg >/dev/null 2>&1; then echo $(determineLinuxPackageType "$sessionType" "$processType" "deb")
    # fi

    # Target replacement:
    # elif which dpkg >/dev/null 2>&1; then echo $(determineLinuxPackageType "$sessionType" "$processType" "deb")
    # else echo "app"
    # fi

    search_pattern = b'elif which dpkg >/dev/null 2>&1; then echo $(determineLinuxPackageType "$sessionType" "$processType" "deb")\n\tfi'

    # Note: script uses tabs (\t) or spaces? In the provided cleaned.sh, it looks like tabs/spaces.
    # Let's try a more robust search by looking for the specific dpkg line and the closing fi.

    pattern_start = b'elif which dpkg >/dev/null 2>&1; then echo $(determineLinuxPackageType "$sessionType" "$processType" "deb")'

    if pattern_start not in data:
        print("❌ Could not locate the specific code block. The file might differ slightly from expectations.")
        print("Attempting a looser search...")
        # Try matching just the part inside the if/fi structure
        pattern_start = b'then echo $(determineLinuxPackageType "$sessionType" "$processType" "deb")'
        if pattern_start not in data:
             print("❌ Critical: Could not find the determinePackageType logic.")
             return

    # Construct the replacement (injecting the else fallback)
    # We replace the detected 'deb")' followed by newline/space/fi with 'deb")\n\telse echo "app"\n\tfi'

    # We find where the `dpkg` check ends
    loc = data.find(pattern_start)

    # Find the next "fi" after this location
    fi_loc = data.find(b'fi', loc)

    if fi_loc == -1:
        print("❌ Error finding the closing 'fi' tag.")
        return

    # Check safety: ensure the distance isn't huge (meaning we missed the right fi)
    if (fi_loc - loc) > 200:
        print("❌ Safety check failed: 'fi' is too far away.")
        return

    # Create new content
    # Everything up to the "fi"
    new_data = data[:fi_loc]
    # Insert the fallback
    new_data += b'else echo "app"\n\t'
    # The rest of the file (including the original fi and the binary payload)
    new_data += data[fi_loc:]

    backup_name = filename + ".bak"
    try:
        with open(backup_name, 'wb') as backup:
            backup.write(data)
        print(f"Backup created at {backup_name}")

        with open(filename, 'wb') as f:
            f.write(new_data)

        print("✅ Patch applied successfully!")
        print(f"The script {filename} has been updated to fallback to 'app' mode on Arch Linux.")
        print("Try running it now: ./ScreenConnect.ClientSetup.sh")

    except Exception as e:
        print(f"Error writing file: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "ScreenConnect.ClientSetup.sh"
    patch_installer(target)
