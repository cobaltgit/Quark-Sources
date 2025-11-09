use image::{ImageBuffer, RgbaImage};
use std::collections::HashSet;
use std::{fs, thread, time};
use std::io::Read;
use sysinfo::{System, Signal, Pid, ProcessesToUpdate, ProcessRefreshKind};

pub fn kill_cmd_to_run() {
    let mut sys = System::new_all();
    sys.refresh_processes_specifics(ProcessesToUpdate::All, true, ProcessRefreshKind::everything());

    if let Some(cmd_to_run) = get_cmd_to_run(&sys) {
        let mut tree: HashSet<Pid> = HashSet::new();
        tree.insert(cmd_to_run);
        get_children(&sys, cmd_to_run, &mut tree);

        for pid in &tree {
            if let Some(proc) = sys.process(*pid) {
                proc.kill_with(Signal::Term);
            }
        }
    }
}

fn get_cmd_to_run(sys: &System) -> Option<Pid> {
    for (pid, proc) in sys.processes() {
        if proc.cmd().iter().any(|arg| arg.to_string_lossy().contains("/tmp/cmd_to_run.sh")) {
            return Some(*pid);
        }
    }
    None
}

fn get_children(sys: &System, parent: Pid, pids: &mut HashSet<Pid>) {
    for (pid, proc) in sys.processes() {
        if let Some(ppid) = proc.parent() {
            if ppid == parent {
                pids.insert(*pid);
                get_children(sys, *pid, pids)
            }
        }
    }
}

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
