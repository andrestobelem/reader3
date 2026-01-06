import os
import tarfile
import zipfile
import sys

def fix_epub_tar_to_zip(input_path, output_path):
    """
    Converts an EPUB file that is erroneously compressed as TAR 
    to a correct EPUB ZIP file, normalizing its structure.
    """
    if not tarfile.is_tarfile(input_path):
        print(f"Error: The file '{input_path}' is not a valid TAR file.")
        return False

    print(f"Opening TAR: {input_path}")
    
    with tarfile.open(input_path, "r:*") as tar:
        members = tar.getmembers()
        
        # 1. Identify the root by locating the 'mimetype' file
        mimetype_member = next((m for m in members if os.path.basename(m.name) == 'mimetype'), None)
        
        if not mimetype_member:
            print("Error: 'mimetype' file not found. Is this a valid EPUB?")
            return False
            
        root = os.path.dirname(mimetype_member.name)
        if root and not root.endswith('/'):
            root += '/'
            
        if root:
            print(f"Detected root directory: {root} (it will be stripped)")
        else:
            print("The file is already at the root level.")

        # 2. Create the new ZIP file (correct EPUB)
        print(f"Creating ZIP: {output_path}")
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for member in members:
                if member.isfile():
                    # Extract content
                    f = tar.extractfile(member)
                    if f:
                        # Normalize path: strip the root prefix if it exists
                        arcname = member.name[len(root):] if member.name.startswith(root) else member.name
                        
                        # Write to ZIP
                        zip_file.writestr(arcname, f.read())
                        print(f"  + {arcname}")

    print(f"\nSuccess! Fixed file saved at: {output_path}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python epub_fixer.py <input_file.epub> [output_file.epub]")
        sys.exit(1)

    input_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_file = sys.argv[2]
    else:
        # Default: append '_fixed' to the filename
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_fixed{ext}"

    if fix_epub_tar_to_zip(input_file, output_file):
        print("\nProcess finished.")
    else:
        sys.exit(1)

