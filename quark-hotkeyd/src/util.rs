use image::{ImageBuffer, RgbaImage};
use std::fs;
use std::io::Read;


pub fn set_led(led: u8, on: bool) -> Result<(), Box<dyn std::error::Error>> {
    let led_path = format!("/sys/devices/platform/sunxi-led/leds/led{}/trigger", led);
    let led_status = if on {
        "default-on"
    } else {
        "none"
    };
    
    fs::write(&led_path, led_status.as_bytes())?;
    Ok(())
}

pub fn fbscreenshot(output: String) -> Result<(), Box<dyn std::error::Error>> {    
    let stride = fs::read_to_string("/sys/class/graphics/fb0/stride")?
        .trim()
        .parse::<u32>()?;
    
    let bits_per_pixel = fs::read_to_string("/sys/class/graphics/fb0/bits_per_pixel")?
        .trim()
        .parse::<u32>()?;
    
    let mut fb_file = fs::File::open("/dev/fb0")?;
    let mut fb_data = Vec::new();
    fb_file.read_to_end(&mut fb_data)?;

    let width = 240;
    let height = 320;
    let bytes_per_pixel = bits_per_pixel / 8;
    
    let img: RgbaImage = ImageBuffer::from_fn(width, height, |x, y| {
        let idx = (y * stride + x * bytes_per_pixel) as usize;
        if idx + 1 < fb_data.len() {
            let pixel = u16::from_le_bytes([fb_data[idx], fb_data[idx + 1]]);
            let r = ((pixel >> 11) & 0x1F) as u8;
            let g = ((pixel >> 5) & 0x3F) as u8;
            let b = (pixel & 0x1F) as u8;
            
            image::Rgba([
                (r << 3) | (r >> 2),
                (g << 2) | (g >> 4),
                (b << 3) | (b >> 2),
                255
            ])
        } else {
            image::Rgba([0, 0, 0, 255])
        }
    });

    let rotated = image::imageops::rotate90(&img);
    rotated.save(output)?;

    Ok(())
}   
