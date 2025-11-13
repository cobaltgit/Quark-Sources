use evdev::{Device, EventSummary, KeyCode};
use std::collections::HashSet;
use std::os::unix::process::CommandExt;
use std::process;
use time::OffsetDateTime;

mod util;

struct HotkeyEvent {
    keys: Vec<KeyCode>,
    callback: fn()
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut device = Device::open("/dev/input/event0")?;
    let mut pressed_keys: HashSet<KeyCode> = HashSet::new();
    let hotkeys: Vec<HotkeyEvent> = vec![
        HotkeyEvent {
            keys: vec![KeyCode::KEY_RIGHTCTRL, KeyCode::KEY_PAGEDOWN],
            callback: screenshot_handler
        },
        HotkeyEvent {
            keys: vec![KeyCode::KEY_RIGHTCTRL, KeyCode::KEY_PAGEUP],
            callback: quicksave_handler
        },
        HotkeyEvent {
            keys: vec![KeyCode::KEY_ENTER, KeyCode::KEY_PAGEUP],
            callback: kill_handler
        }
    ];

   loop {
        for event in device.fetch_events()? {
        	match event.destructure() {
        		EventSummary::Key(_, keycode, value) => {
        			if value == 1 {
        				pressed_keys.insert(keycode);
                        for hotkey in &hotkeys {
                            if hotkey.keys.iter().all(|&key| pressed_keys.contains(&key)) {
                                (hotkey.callback)();
                            }
                        }
        			} else {
        				pressed_keys.remove(&keycode);
        			}
        		}
        		_ => continue,
        	}
        }
    }

    Ok(())
}

fn screenshot_handler() {
    util::set_led(2, true);
    let now = OffsetDateTime::now_utc();
    util::fbscreenshot(&format!("/mnt/SDCARD/Saves/screenshots/Screenshot_{:04}{:02}{:02}_{:02}{:02}{:02}.png", now.year(), now.month() as u8, 
        now.day(), now.hour(), now.minute(), now.second()));
    util::set_led(2, false);
}

fn quicksave_handler() {
    process::Command::new("/bin/sh")
        .arg("/mnt/SDCARD/System/scripts/quicksave.sh")
        .exec();
}

fn kill_handler() {
    util::kill_cmd_to_run();
}
