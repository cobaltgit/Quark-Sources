#!/usr/bin/env python3
"""
SD Card Flasher GUI for Linux
A tool to download, verify, and flash SD card images with GUI progress indicators
Runs as root user
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import base64
import threading
import subprocess
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
import hashlib
import zipfile
import time
import tempfile
import re
import json
import shutil

XML_URL = "https://raw.githubusercontent.com/cobaltgit/Quark-Sources/refs/heads/main/releases.xml"
LOGO_BASE64 = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAYAAACOEfKtAAAFYklEQVR42u2UXUzVZRzHv5wkXy7ONM3W2HzLtRoO1yx7w3amiAfjOHCcOZ1kwWSoDRFfwdSz5CZblPPCaK41uSkv0jMaK21BW8pFydxqvcyxLtiscLFhrkDkfPspsGf4H5zD/+E558/Z8/3ue8PVj8//PB9MRtat4yMlJWzZvZv9RUVsCgQ4DR4LAR9DoQZWVfVx06Z2rlnzGFIf+kIhNtTUcCASIUe2axdvB4PcCY+EweA2Vlb2Uh1J7t17l0VFTQwEUvOx5VdXWlnJXnWTc+Xl/DMvj7lIUZifv4KlpZ08dmzsI3fuvM316yuRrAiQZ7Zu5c/qpvF3+DDlxbBdgD+OJIWBwDyWlLSwri6WyJH3AW/b1iXAX4KZKM/V1jLmvCH+9u3jXeVHw56rqRmgmyPlays/GvKc3pQfTXpOYw4/GvGc/pQfTXlOf8qPmp7TmIYfNTynMQ0/6nlOTdePxj0nM+LHwkIe1/GcAT+a8py+HzdsaCTgM+05fT+a95y+H3NyvpfXEKOXAFZUkEuX8hqGc3nRor/uyB+9dKRAI3NyYgAizMw8wdzc6+Jjpvh1kCtWkD4fCfA7DOc00BsBeCU7m4N79qTqQOVCeR6cPp0EeB/gyPz+RhYX9yT9pRw5QhYUjNw0MidAGU9kZvL3QIDyjyQf3pYt5OzZ6kgFcPSyss6zrKwvaTfNmaNuGh+g2kd+P3uKi6m+tmGnLFigjhsfoFp29hVWVw8au2nhQnXLxACqXcjKYl95uVmnZGSQwMQBxvOjvue0AKopPxrxnMwtwNF+DIVuqhej7bnJAzhJfhzSQTjs8JwGQH0/Oj1nBKC+H52e0weo40en58wB1PKj03PmATr96MJzZgE6/Vhd7cJzJgE6/SggNW4yBlD58XpuLllb6/BcygGqX+SPGreYBKjWIiA1jjILEOjwPMAoYAFagBagBWgBWoAWoAVoAVqAFqAHAH4mh9Z7DeAfss0YTjNw6l1g0GMA/5XVYyhfPwec7fQAwH7ZSZkfD+QyMP8c0FbvDYDNssVw5ss3gA9vpQhgs2wJoJLP/KfuDVD5Bnj+LNCZIoBXZaswfiI+4IsG4L2BJAG8KnsFUAkxNGsjN35+iIdidayLhRluK2CBH1D5Cig7DfyTJIA3ZBWyh5B4WucB59qAelMAb8p2y0YdJaAOVLGqL8LRrWb1HQHbAKhEAF8UaBzyoxGA/bKTMj9cxIUfO1x7bi3Xri9neXeE47eCFT1BBsNu/Rh14TntKD+evqUH0Om51Vz9xGZuvnaURxlJsMekpSztFD8um6gfoxqe0058P3a48lyE7urGj1ENz8WNvh87XHjORTX8GDXguUn0Y4eW5+JX349Rk57T92NHfM9pVd+PUQ3PGU7rNOCXFyfbc5Ptx5+Alwn44O3oe86QH72fnO6cVdu5/e8IvdV7N63kymfh+VzAx0suLuGOgR2egfem9EkpiLIpARARMOPtDC7/YTn3x/anDNxB6QtSnxTE1AI4shnvz2BeVx7fkiYL3BFpSDpLCtWpCFBt7tm5DPeGjcN7TTpfCtV0AKim/GjIc6rpCTCOH3U9l/4A4/hR13PpD1Dbj07PWYAOPybmOQswIT86PWcBJrKZH8xk8EaQUs6UYqgW4EQ3XAvQArQALUAL0AK0AC1AC9ACtAAtwPESxRkPA3wdnk8rZuA8mvAOBj0EsEd2UPYwpky+xWJ8inYcTynAAVmj7FFM2VxEPj5BVwoAXpItQ9qkBQdwCv8lAeCvskJoJI38mOaeM+/HNPeceT8a91z6+3GM/iYrtODi+nFsz1lgCfnRes59LuFVnEE3iBbZ014983+M57Y2jZx91QAAAABJRU5ErkJggg=="
SIZE_UNITS = ['B', 'K', 'M', 'G', 'T', 'P', 'E']

class SDFlasherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quark Burner")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Variables
        self.selected_disk = tk.StringVar()
        self.selected_image = tk.StringVar()
        self.images_data = []
        self.temp_dir = None
        self.logo_image = None
        
        # Check if running as root
        if os.geteuid() != 0:
            messagebox.showerror("Error", 
                               "This program must be run as root.\n"
                               "Please run with sudo or as root user.")
            sys.exit(1)
        
        self.setup_ui()
        self.refresh_disks()
        self.load_xml()  # Auto-load XML on startup
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Logo section
        try:
            logo_data = base64.b64decode(LOGO_BASE64.strip())
            self.logo_image = tk.PhotoImage(data=logo_data)
            
            logo_label = ttk.Label(main_frame, image=self.logo_image)
            logo_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
            
        except Exception as e:
            # If logo fails to load, show a text placeholder
            logo_label = ttk.Label(main_frame, text="Quark SD Card Flasher", 
                                 font=("Arial", 16, "bold"))
            logo_label.grid(row=row, column=0, columnspan=2, pady=(0, 20))
            self.log(f"Logo loading failed: {str(e)}")
        
        row += 1
        
        # Image selection
        ttk.Label(main_frame, text="Select Image:").grid(row=row, column=0, sticky=tk.W, pady=2)
        self.image_combo = ttk.Combobox(main_frame, textvariable=self.selected_image, 
                                       state="readonly", width=50)
        self.image_combo.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        
        row += 1
        
        # Disk selection
        ttk.Label(main_frame, text="Select Disk:").grid(row=row, column=0, sticky=tk.W, pady=2)
        disk_frame = ttk.Frame(main_frame)
        disk_frame.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=2)
        disk_frame.columnconfigure(0, weight=1)
        
        self.disk_combo = ttk.Combobox(disk_frame, textvariable=self.selected_disk, 
                                      state="readonly", width=40)
        self.disk_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.refresh_btn = ttk.Button(disk_frame, text="Refresh", command=self.refresh_disks)
        self.refresh_btn.grid(row=0, column=1)
        
        row += 1
        
        # Progress section
        ttk.Separator(main_frame, orient='horizontal').grid(row=row, column=0, columnspan=2, 
                                                           sticky=(tk.W, tk.E), pady=10)
        row += 1

        # Warning text
        self.warning_label = tk.Label(main_frame, text="WARNING: Flashing an image will ERASE ALL DATA on the selected drive.", fg="#800000", font=("Arial", 12, "bold"))
        self.warning_label.grid(row=row, column=0, columnspan=2, pady=2, sticky=tk.W)

        row += 1

        # Flash button
        flash_btn_frame = ttk.Frame(main_frame)
        flash_btn_frame.grid(row=row, column=0, columnspan=2, pady=10)

        self.flash_btn = tk.Button(flash_btn_frame, text="Write Quark to Drive", 
                            command=self.start_flash, state="disabled", bg="#007acc", fg="#ffffff", width=100, height=1, font=("Arial", 16, "bold"))
        self.flash_btn.pack(side=tk.BOTTOM, padx=5)

        row += 1
        
        # Progress label
        self.progress_label = ttk.Label(main_frame, text="Ready")
        self.progress_label.grid(row=row, column=0, columnspan=2, pady=2)
        
        row += 1
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        row += 1
        
        # Log text area
        ttk.Label(main_frame, text="Log:").grid(row=row, column=0, sticky=(tk.W, tk.N), pady=2)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=row, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=2)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        row += 1
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=2, pady=10)
        
        self.clear_log_btn = ttk.Button(button_frame, text="Clear Log", 
                                       command=self.clear_log)
        self.clear_log_btn.pack(side=tk.LEFT, padx=5)
        
        self.quit_btn = ttk.Button(button_frame, text="Quit", command=self.quit_app)
        self.quit_btn.pack(side=tk.LEFT, padx=5)
    
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, value, text=""):
        """Update progress bar and label"""
        self.progress_bar['value'] = value
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def update_flash_button_state(self):
        """Update flash button state based on selections"""
        if (self.images_data and
            self.disk_combo['values'] and
            self.selected_image.get() and
            self.selected_disk.get()):
            self.flash_btn.config(state="normal")
        else:
            self.flash_btn.config(state="disabled")
    
    def refresh_disks(self):
        """Refresh the list of available disks"""
        def refresh_thread():
            try:
                self.log("Refreshing disk list...")
                self.root.after(0, lambda: self.update_progress(30, "Scanning disks..."))
                
                disks = []
                for dev in os.scandir("/sys/block"):
                    name = os.path.basename(dev.path)
                
                    with open(os.path.join(dev.path, "removable"), 'r') as f:
                        if f.read().strip() == '0':
                            continue # ignore internal devices

                    vendor_path = os.path.join(dev.path, 'device', 'vendor')
                    if os.path.exists(vendor_path):
                        with open(vendor_path, "r") as f:
                            vendor = f.read().strip()
                    else:
                        vendor = "Unknown"

                    model_path = os.path.join(dev.path, 'device', 'model')
                    if os.path.exists(model_path):
                        with open(model_path, 'r') as f:
                            model = f.read().strip()
                    else:
                        model = ""

                    size_path = os.path.join(dev.path, 'size')
                    dev_size_in_bytes = 0
                    if os.path.exists(size_path):
                        with open(size_path, "r") as size_f:
                            dev_size_in_bytes = int(size_f.read().strip()) * 512

                    unit_index = 0
                    size = float(dev_size_in_bytes)
                    
                    while size >= 1024 and unit_index < len(SIZE_UNITS) - 1:
                        size /= 1024
                        unit_index += 1
                    
                    if unit_index == 0:
                        size_human = f"{int(size)}{SIZE_UNITS[unit_index]}"
                    else:
                        size_human = f"{size:.1f}{SIZE_UNITS[unit_index]}"

                    disks.append(f"/dev/{name} ({size_human}) - {vendor} {model}")
                
                # Update UI on main thread
                self.root.after(0, lambda: self.update_disk_list(disks))
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error refreshing disks: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to refresh disk list: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.update_progress(0, "Ready"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def update_disk_list(self, disks):
        """Update disk combobox with found disks"""
        self.disk_combo['values'] = disks
        if not disks:
            messagebox.showerror("Error", "No removable drives detected", icon="warning")
        else:
            self.disk_combo.current(0)

        self.log(f"Found {len(disks)} disks")
        self.update_flash_button_state()
    
    def load_xml(self):
        """Load and parse XML file from hardcoded URL"""
        def load_xml_thread():
            try:
                self.log(f"Loading XML from: {XML_URL}")
                self.root.after(0, lambda: self.update_progress(10, "Downloading XML..."))
                
                with urllib.request.urlopen(XML_URL, timeout=30) as response:
                    xml_content = response.read()
                
                self.root .after(0, lambda: self.update_progress(50, "Parsing XML..."))
                
                root = ET.fromstring(xml_content)
                self.images_data = [ # todo: write formal apology to Guido
                    {
                        "version": version.text,
                        "url": url.text,
                        "sha256_url": getattr(image.find("sha256"), "text", None)
                    }
                    for image in root.findall("image")
                    if (version := image.find("version")) is not None 
                    and (url := image.find("url")) is not None
                ]
                               
                # Update UI on main thread
                self.root.after(0, self.update_image_list)
                
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Error loading XML: {str(e)}"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to load XML: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.update_progress(0, "Ready"))
        
        threading.Thread(target=load_xml_thread, daemon=True).start()
    
    def update_image_list(self):
        """Update the image combobox with loaded images"""
        versions = [img['version'] for img in self.images_data]
        self.image_combo['values'] = versions
        if versions:
            self.image_combo.current(0)
        
        self.log(f"Loaded {len(versions)} images")
        self.update_flash_button_state()
    
    def get_selected_image_data(self):
        """Get the data for the currently selected image"""
        selected_version = self.selected_image.get()
        for img in self.images_data:
            if img['version'] == selected_version:
                return img
        return None
    
    def get_selected_disk_device(self):
        """Extract device name from selected disk string"""
        if selected := self.selected_disk.get():
            # Extract /dev/sdX from the selection
            if match := re.match(r'(/dev/\w+)', selected):
                return match.group(1)
        return None
    
    def download_file(self, url, filepath, description="file"):
        """Download a file with progress updates"""
        self.log(f"Downloading {description} from: {url}")

        def progress_hook(block_num, block_size, total_size):
            if total_size > 0:
                downloaded = block_num * block_size
                progress = min((downloaded / total_size) * 100, 100)
                self.update_progress(progress, f"Downloading {description}... {progress:.1f}%")
        
        urllib.request.urlretrieve(url, filepath, reporthook=progress_hook)
        
        file_size = os.path.getsize(filepath)
        self.log(f"Downloaded {description} ({file_size} bytes)")
        return filepath
    
    def verify_sha256(self, filepath, sha256_url):
        """Verify file SHA256 hash"""
        try:
            self.log("Downloading SHA256 hash...")
            with urllib.request.urlopen(sha256_url, timeout=30) as response:
                hash_content = response.read().decode('utf-8')
            
            expected_hash = hash_content.strip().split()[0]  # Take first part (hash only)
            
            self.log("Calculating file hash...")
            sha256_hash = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            
            calculated_hash = sha256_hash.hexdigest()
            
            if calculated_hash.lower() == expected_hash.lower():
                self.log("✓ SHA256 verification successful")
                return True
            else:
                self.log(f"✗ SHA256 verification failed!")
                self.log(f"Expected: {expected_hash}")
                self.log(f"Got:      {calculated_hash}")
                return False
                
        except Exception as e:
            self.log(f"Error verifying SHA256: {str(e)}")
            return False
    
    def format_disk(self, device):
        """Format the disk with FAT32 using fdisk"""
        try:
            self.log(f"Formatting {device}...")
            self.update_progress(0, "Formatting disk...")
            
            # Unmount any mounted partitions
            try:
                subprocess.run(['sh', '-c', f'umount {device}* 2>/dev/null || true'], 
                            capture_output=True, check=False)
            except:
                pass  # Ignore errors if nothing was mounted
            
            # Create new partition table and partition using fdisk
            fdisk_commands = "\n".join("onp1  tcw")
            
            # Run fdisk with commands piped to stdin
            process = subprocess.Popen(['fdisk', device], 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    text=True)
            stdout, stderr = process.communicate(input=fdisk_commands)
            
            if process.returncode != 0:
                self.log(f"fdisk output: {stdout}")
                self.log(f"fdisk error: {stderr}")
                raise Exception(f"fdisk failed with return code {process.returncode}")
            
            # Wait a moment for the kernel to recognize the new partition
            time.sleep(1)
            
            # Format as FAT32
            partition = f"{device}1"
            subprocess.run(['mkfs.vfat', '-F', '32', partition], 
                        capture_output=True, check=True)
            
            self.log(f"✓ Formatted {device} with FAT32")
            return partition
            
        except Exception as e:
            self.log(f"✗ Error formatting disk: {e}")
            raise
    
    def extract_zip(self, zip_path, mount_point):
        """Extract ZIP file to mounted partition"""
        self.log(f"Extracting ZIP to {mount_point}...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)
            
            for i, file_name in enumerate(file_list):
                zip_ref.extract(file_name, mount_point)
                progress = ((i + 1) / total_files) * 100
                self.update_progress(progress, f"Extracting... {progress:.1f}%")
        
        self.log(f"✓ Extracted {total_files} files")
    
    def start_flash(self):
        """Start the flashing process in a separate thread"""
        if not self.validate_inputs():
            return
        
        # Disable UI during flashing
        self.flash_btn.config(state="disabled")
        self.quit_btn.config(state="disabled")
        self.refresh_btn.config(state="disabled")
        
        threading.Thread(target=self.flash_process, daemon=True).start()
    
    def validate_inputs(self):
        """Validate all inputs before starting"""
        if not self.images_data:
            messagebox.showerror("Error", "No image data available")
            return False
        
        if not self.selected_image.get():
            messagebox.showerror("Error", "Please select an image")
            return False
        
        if not self.selected_disk.get():
            messagebox.showerror("Error", "Please select a disk")
            return False
        
        device = self.get_selected_disk_device()
        if not device:
            messagebox.showerror("Error", "Invalid disk selection")
            return False
        
        # Confirm dangerous operation
        result = messagebox.askyesno(
            "Confirm Format", 
            f"This will completely erase {device}!\n"
            f"Are you sure you want to continue?",
            icon="warning"
        )
        
        return result
    
    def flash_process(self):
        """Main flashing process"""
        try:
            # Get selections
            image_data = self.get_selected_image_data()
            device = self.get_selected_disk_device()
            
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="sd_flasher_")
            zip_path = os.path.join(self.temp_dir, "image.zip")
            
            # Step 1: Download ZIP
            self.download_file(image_data['url'], zip_path, "image ZIP")
            
            # Step 2: Verify SHA256 if available
            if image_data['sha256_url']:
                if not self.verify_sha256(zip_path, image_data['sha256_url']):
                    raise Exception("SHA256 verification failed")
            else:
                self.log("No SHA256 hash provided, skipping verification")
            
            # Step 3: Format disk
            partition = self.format_disk(device)
            
            # Step 4: Mount partition
            mount_point = os.path.join(self.temp_dir, "mount")
            os.makedirs(mount_point)
            
            subprocess.run(['mount', partition, mount_point], 
                         capture_output=True, check=True)
            
            try:
                # Step 5: Extract ZIP
                self.extract_zip(zip_path, mount_point)
                
                # Step 6: Sync and unmount
                self.update_progress(95, "Syncing filesystem...")
                os.sync()
                
            finally:
                try:
                    subprocess.run(['umount', mount_point], 
                                 capture_output=True, check=True)
                except:
                    pass  # Ignore unmount errors
            
            # Success!
            self.update_progress(100, "Complete!")
            self.log("✓ SD card flashing completed successfully!")
            
            self.root.after(0, lambda: messagebox.showinfo("Success", 
                                                          "SD card flashing completed successfully!"))
            
        except Exception as e:
            error_msg = f"Error during flashing: {str(e)}"
            self.log(f"✗ {error_msg}")
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
        
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
            
            # Re-enable UI
            self.root.after(0, self.enable_ui)
    
    def enable_ui(self):
        """Re-enable UI after flashing"""
        self.update_flash_button_state()
        self.quit_btn.config(state="normal")
        self.refresh_btn.config(state="normal")
        self.update_progress(0, "Ready")
    
    def quit_app(self):
        """Clean shutdown"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.root.quit()

def main():
    # Check for required tools
    required_tools = ['fdisk', 'mkfs.vfat', 'mount', 'umount']
    missing_tools = [tool for tool in required_tools if shutil.which(tool) is None]
    
    if missing_tools:
        print(f"Error: Missing required tools: {', '.join(missing_tools)}")
        print("Please install the required packages:")
        print("- fdisk (disk partitioning)")
        print("- dosfstools (FAT32 formatting)")
        print("- util-linux (mount/umount)")
        sys.exit(1)
    
    root = tk.Tk()
    SDFlasherGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()