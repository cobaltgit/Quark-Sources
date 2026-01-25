use evdev::{Device, EventSummary, KeyCode};
use std::collections::HashSet;
use std::io::Write;
use std::os::fd::AsRawFd;
use std::os::unix::process::CommandExt;
use std::process;
use std::thread;
use std::time::Duration;
use time::OffsetDateTime;

mod bitset;
mod util;
mod hotkey;

use bitset::KeyBitSet;
use crate::hotkey::{HotkeyEvent, HotkeyState, Trigger};

const INPUT_DEV: &str = "/dev/input/event0";

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut device = Device::open(INPUT_DEV)?;
    let _ = device.set_nonblocking(true);

    let mut pressed_keys = KeyBitSet::new();

    let mut hotkeys: Vec<HotkeyEvent> = vec![
        HotkeyEvent {
            keys: vec![KeyCode::KEY_RIGHTCTRL, KeyCode::KEY_PAGEDOWN],
            trigger: Trigger::Press,
            callback: screenshot_handler,
            state: HotkeyState::default(),
        },
        HotkeyEvent {
            keys: vec![KeyCode::KEY_RIGHTCTRL, KeyCode::KEY_PAGEUP],
            trigger: Trigger::Press,
            callback: quicksave_handler,
            state: HotkeyState::default(),
        },
        HotkeyEvent {
            keys: vec![KeyCode::KEY_ENTER, KeyCode::KEY_PAGEUP],
            trigger: Trigger::Press,
            callback: kill_handler,
            state: HotkeyState::default(),
        },
        HotkeyEvent {
            keys: vec![KeyCode::KEY_RIGHTCTRL, KeyCode::KEY_ENTER],
            trigger: Trigger::Hold {
                duration: Duration::from_secs(10),
            },
            callback: reboot_handler,
            state: HotkeyState::default(),
        },
    ];

    let fd = device.as_raw_fd();

    loop {
        if poll_readable(fd, 250)? { // we poll every 250ms
            for event in device.fetch_events()? {
                if let EventSummary::Key(_, keycode, value) = event.destructure() {
                    match value {
                        1 => {
                            pressed_keys.set(keycode.code(), true);
                        }
                        0 => {
                            pressed_keys.set(keycode.code(), false);
                        }
                        _ => continue,
                    }
                }
            }
        }

        for hk in &mut hotkeys {
            let chord_down = hk.keys.iter().all(|k| pressed_keys.get(k.code()));
            if hk.should_fire(chord_down) {
                (hk.callback)();
            }
        }
    }
}

fn poll_readable(fd: i32, timeout_ms: i32) -> std::io::Result<bool> {
    let mut pfd = libc::pollfd {
        fd,
        events: libc::POLLIN,
        revents: 0,
    };

    let rc = unsafe { libc::poll(&mut pfd as *mut libc::pollfd, 1, timeout_ms) };
    if rc < 0 {
        return Err(std::io::Error::last_os_error());
    }
    Ok(rc > 0 && (pfd.revents & libc::POLLIN) != 0)
}

fn screenshot_handler() {
    util::set_led(2, true);
    let now = OffsetDateTime::now_utc();
    util::fbscreenshot(&format!(
        "/mnt/SDCARD/Saves/screenshots/Screenshot_{:04}{:02}{:02}_{:02}{:02}{:02}.png",
        now.year(),
        now.month() as u8,
        now.day(),
        now.hour(),
        now.minute(),
        now.second()
    ));
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

fn reboot_handler() {
    util::kill_cmd_to_run();

    thread::sleep(Duration::from_millis(500));

    unsafe {
        libc::sync();
        libc::reboot(libc::RB_AUTOBOOT);
    }
}
