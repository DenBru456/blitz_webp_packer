# Adaption of Qirashi's packed_webp(github) for context menu and more stuff

import os
import sys
import struct
import argparse
from pathlib import Path
from typing import List
from io import StringIO

EXTR_SIGNATURE = b"extr"
RIFF_HEADER = b"RIFF"

def log_err(msg: str, e: Exception = None):
    """Logs an error message to stderr."""
    if e:
        sys.stderr.write(f"Error: {msg}: {e}\n")
    else:
        sys.stderr.write(f"Error: {msg}\n")

def unpack_webp(packed_file: Path, backup: bool):
    """
    Unpacks a .packed.webp file. If backup is True, moves the original file.
    """
    if not packed_file.name.endswith(".packed.webp"):
        log_err(f"Cannot unpack '{packed_file.name}'. It is not a '.packed.webp' file.")
        return
    try:
        data = packed_file.read_bytes()
        extr_index = data.rfind(EXTR_SIGNATURE)
        if extr_index == -1:
            log_err(f"'extr' signature not found in {packed_file.name}")
            return
        header_size = 8
        if len(data) < extr_index + header_size:
            log_err(f"Invalid file structure in {packed_file.name}. File is too small.")
            return
        extra_data_len = struct.unpack_from('<I', data, extr_index + 4)[0]
        if len(data) < extr_index + header_size + extra_data_len:
            log_err(f"Invalid file structure in {packed_file.name}. Extra data length is incorrect.")
            return
        extra_data = data[extr_index + header_size : extr_index + header_size + extra_data_len]
        base_name = packed_file.name[:-len('.packed.webp')]
        txt_file = packed_file.with_name(base_name).with_suffix('.txt')
        txt_file.write_bytes(extra_data)
        webp_data = bytearray(data[:extr_index])
        if not webp_data.startswith(RIFF_HEADER):
            log_err(f"Invalid RIFF header in {packed_file.name}.")
            os.remove(txt_file)
            return
        new_size = len(webp_data) - 8
        struct.pack_into('<I', webp_data, 4, new_size)
        webp_file = packed_file.with_name(base_name).with_suffix('.webp')
        webp_file.write_bytes(webp_data)

        if backup:
            backup_dir = packed_file.parent / "_backup"
            backup_dir.mkdir(exist_ok=True)
            os.rename(packed_file, backup_dir / packed_file.name)
            print(f"Successfully unpacked: {packed_file.name} -> {webp_file.name} (Original moved to _backup)")
        else:
            os.remove(packed_file)
            print(f"Successfully unpacked: {packed_file.name} -> {webp_file.name} and {txt_file.name}")

    except Exception as e:
        log_err(f"An unexpected error occurred during unpack", e)

def pack_webp(file_to_pack: Path, backup: bool):
    """
    Packs .webp and .txt files. This is now fully resilient to race conditions.
    """
    if file_to_pack.suffix not in ['.webp', '.txt']:
        log_err(f"Cannot pack '{file_to_pack.name}'. It must be a '.webp' or '.txt' file.")
        return
        
    try:
        webp_file = file_to_pack.with_suffix('.webp')
        txt_file = file_to_pack.with_suffix('.txt')
        
        webp_data = bytearray(webp_file.read_bytes())
        extra_data = txt_file.read_bytes()

        if not webp_data.startswith(RIFF_HEADER):
            log_err(f"Invalid RIFF header in {webp_file.name}.")
            return
        packed_data = webp_data + EXTR_SIGNATURE + struct.pack('<I', len(extra_data)) + extra_data
        if len(extra_data) % 2 != 0:
            packed_data += b'\x00'
        new_size = len(packed_data) - 8
        struct.pack_into('<I', packed_data, 4, new_size)
        packed_file = webp_file.with_suffix('.packed.webp')
        packed_file.write_bytes(packed_data)
        
        if backup:
            backup_dir = file_to_pack.parent / "_backup"
            backup_dir.mkdir(exist_ok=True)
            os.rename(webp_file, backup_dir / webp_file.name)
            os.rename(txt_file, backup_dir / txt_file.name)
            print(f"Successfully packed: {webp_file.name} -> {packed_file.name} (Originals moved to _backup)")
        else:
            os.remove(webp_file)
            os.remove(txt_file)
            print(f"Successfully packed: {webp_file.name} and {txt_file.name} -> {packed_file.name}")

    except FileNotFoundError:
        return
    except Exception as e:
        log_err(f"An unexpected error occurred during pack", e)

def process_paths(paths: List[Path], mode: str, recursive: bool, backup: bool):
    """
    Processes a list of files or folders based on the selected mode.
    """
    paths_to_process = [p for p in paths if p.exists()]
    if not paths_to_process:
        return

    for path in paths_to_process:
        items_to_process = []
        if path.is_dir():
            print(f"--- Scanning folder: {path.name} ({mode} mode) ---")
            if recursive:
                print("Recursive mode enabled: scanning all subdirectories.")
                items_to_process.extend(list(path.rglob("*.*")))
            else:
                items_to_process.extend(path.iterdir())
        else:
            items_to_process.append(path)
            
        processed_pairs = set()
        for item in items_to_process:
            if not item.is_file():
                continue
            if mode == 'pack' and item.name.endswith('.packed.webp'):
                continue
            if mode in ['auto', 'unpack'] and item.name.endswith('.packed.webp'):
                unpack_webp(item, backup)
            elif mode in ['auto', 'pack'] and item.suffix in ['.txt', '.webp']:
                stem = item.stem 
                if stem in processed_pairs:
                    continue
                pack_webp(item, backup)
                processed_pairs.add(stem)
        if path.is_dir():
             print(f"--- Finished folder: {path.name} ---")


def main():
    parser = argparse.ArgumentParser(description="Pack and unpack extra data chunks in WebP files.", epilog="Use the context menu options or run from the command line.")
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('-p', '--pack', action='store_true', help="Force packing mode.")
    mode_group.add_argument('-u', '--unpack', action='store_true', help="Force unpacking mode.")
    mode_group.add_argument('-a', '--auto', action='store_true', help="Auto mode (for debugging).")
    parser.add_argument('paths', metavar='path', nargs='+', help="One or more file(s) or folder(s) to process.")
    parser.add_argument('-r', '--recursive', action='store_true', help="Process all subdirectories within a given folder.")
    parser.add_argument('-s', '--silent', action='store_true', help="Close the console window immediately on success.")
    parser.add_argument('-b', '--backup', action='store_true', help="Move original files to a '_backup' folder instead of deleting them.")
    
    args = parser.parse_args()
    mode = 'pack' if args.pack else 'unpack' if args.unpack else 'auto'
    path_objects = [Path(p) for p in args.paths]
    
    old_stderr = sys.stderr
    sys.stderr = captured_stderr = StringIO()
    
    process_paths(path_objects, mode, args.recursive, args.backup)
    
    sys.stderr = old_stderr
    error_output = captured_stderr.getvalue()
    if error_output:
        print(error_output, file=sys.stderr)
        input("Processing finished with ERRORS. Press Enter to exit.")
    elif not args.silent:
        input("Processing complete. Press Enter to exit.")


if __name__ == "__main__":
    main()