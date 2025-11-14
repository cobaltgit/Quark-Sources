use std::fs::{metadata, File, OpenOptions};
use std::io::{self, Read, Write};
use std::env::args;
use std::process::exit;

fn validate_bmp(path: &str) -> Result<bool, std::io::Error> {
    let meta = metadata(&path)?;

    if !meta.is_file() {
        eprintln!("{}: no such file", path);
        exit(1);
    }

    if meta.len() > 524288 {
        eprintln!("Bootlogo must be under 512KiB!");
        exit(1);
    }
    
    let mut file = File::open(path)?;
    let mut header = [0u8; 54];
    file.read_exact(&mut header)?;

    if &header[0..2] != b"BM" {
        eprintln!("Bootlogo is not a valid BMP image!");
        exit(1);
    }

    let width = i32::from_le_bytes([header[18], header[19], header[20], header[21]]);
    let height = i32::from_le_bytes([header[22], header[23], header[24], header[25]]);
    let bits_per_pixel = u16::from_le_bytes([header[28], header[29]]);
    let compression = u32::from_le_bytes([header[30], header[31], header[32], header[33]]);

    if bits_per_pixel != 16 || compression != 3 {
        eprintln!("Bootlogo must be 16-bit RGB565 format!");
        exit(1);
    } else if (width, height.abs()) != (240, 320) {
        eprintln!("Bootlogo must be 240x320 resolution!");
        exit(1);
    } else {
        Ok(true)
    }
}

fn write_bootlogo(path: &str) -> io::Result<()> {
    let mut bmp = File::open(&path)?;
    let mut bootlogo_data = Vec::new();
    bmp.read_to_end(&mut bootlogo_data)?;
    
    let mut file = OpenOptions::new()
        .write(true)
        .open("/dev/by-name/bootlogo")?;
    
    file.write_all(&bootlogo_data)?;
    file.sync_all()?;
    
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let argv: Vec<String> = args().collect();
    let bootlogo_path = argv.get(1)
        .map(String::as_str)
        .unwrap_or_else(|| "bootlogo.bmp");

    match validate_bmp(&bootlogo_path) {
        Err(e) => {
            eprintln!("Error validating bootlogo: {}", e);
            exit(1);
        }
        _ => {}
    };
    match write_bootlogo(&bootlogo_path) {
        Ok(()) => {
            println!("Bootlogo written successfully!");
            Ok(())
        }
        Err(e) => {
            eprintln!("Error writing bootlogo: {}", e);
            exit(1);
        }
    }
}
