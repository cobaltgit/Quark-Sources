use alsa::mixer::{Mixer, SelemId};
use inotify::{Inotify, WatchMask};
use nix::unistd::sync;
use nix::sys::reboot::{reboot, RebootMode};
use std::collections::HashMap;
use std::fs;
use std::os::unix::fs::FileTypeExt;
use std::os::unix::process::CommandExt;
use std::process::Command;

pub struct SystemConfig {
    values: HashMap<String, String>,
}

impl SystemConfig {
    pub fn get_string(&self, key: &str) -> Option<String> {
        self.values.get(key).cloned()
    }
    
    pub fn get_int(&self, key: &str) -> Option<i64> {
        self.values.get(key)?.parse().ok()
    }
}

fn get_system_json() -> Result<SystemConfig, Box<dyn std::error::Error>> {
    let json = fs::read_to_string("/mnt/UDISK/system.json")?;
    Ok(parse_system_json(&json))
}


fn parse_system_json(input: &str) -> SystemConfig {
    let mut values = HashMap::new();
    
    for line in input.lines() {
        if let Some(colon_pos) = line.find(':') {
            let (key_part, value_part) = line.split_at(colon_pos);
            
            let key = key_part
                .trim()
                .trim_matches(|c| c == '"' || c == '\t' || c == ' ')
                .to_string();
            
            let value = value_part[1..]
                .trim()
                .trim_end_matches(|c| c == ',' || c == '}' || c == '"')
                .trim_start_matches('"')
                .trim()
                .to_string();
            
            if !key.is_empty() && !value.is_empty() && key.chars().all(|c| c.is_alphanumeric()) {
                values.insert(key, value);
            }
        }
    }

    println!("{:?}", values);
    SystemConfig { values }
}

fn get_volume(config: &SystemConfig) -> Option<i64> {
    config.get_int("vol")
}

fn get_theme_path(config: &SystemConfig) -> Option<String> {
    config.get_string("theme").map(|s| {
        let mut path = s;
        if !path.ends_with('/') {
            path.push('/');
        }
        path
    })
}


fn is_character_device(path: &str) -> bool {
    fs::metadata(path)
        .map(|m| m.file_type().is_char_device())
        .unwrap_or(false)
}

fn set_volume(volume: i64) -> Result<(), Box<dyn std::error::Error>> {
    if !is_character_device("/dev/audio1") {
        return Ok(());
    }

    let mut mixer = Mixer::new("hw:1", false)?;
    mixer.attach(c"default")?;
    mixer.load()?;

    let selem_id = SelemId::new("PCM", 0);
    let selem = mixer
        .find_selem(&selem_id)
        .ok_or("PCM element not found")?;

    let (min, max) = selem.get_playback_volume_range();

    selem.set_playback_volume_all(min + (max - min) * volume * 5 / 100)?;
    Ok(())
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let json = get_system_json()?;
    let theme_path = get_theme_path(&json).unwrap_or_default();
    let mut volume = get_volume(&json).unwrap_or(0);

    let mut inotify = Inotify::init()?;
    
    inotify.watches().add("/mnt/UDISK/system.json", WatchMask::MODIFY)?;
    inotify.watches().add("/dev", WatchMask::CREATE)?;

    let mut buffer = [0u8; 4096];

    loop {
        let events = inotify.read_events_blocking(&mut buffer)?;

        for event in events {
            if event.wd == inotify.watches().add("/mnt/UDISK/system.json", WatchMask::MODIFY)? {
                let json = match get_system_json() {
                    Ok(j) => j,
                    Err(e) => {
                        eprintln!("Error reading JSON: {}", e);
                        continue;
                    }
                };

                if let Some(new_theme_path) = get_theme_path(&json) {
                    if new_theme_path != theme_path {
                        let bootlogo_path = format!("{}skin/bootlogo.bmp", new_theme_path);
                        if fs::metadata(&bootlogo_path).is_ok() {
                            Command::new("/bin/sh")
                                .args(&[
                                    "/mnt/SDCARD/Apps/BootLogo/bootlogo.sh",
                                    &bootlogo_path,
                                ])
                                .exec();
                        }

                        sync();
                        reboot(RebootMode::RB_AUTOBOOT)?;
                    } else {
                        println!("Equality is great, don'tcha think?");
                    }
                } else {
                    println!("WHERE IS THE DAMN THEME PATH");
                }

                if let Some(new_volume) = get_volume(&json) {
                    if new_volume != volume {
                        volume = new_volume;
                        if let Err(e) = set_volume(volume) {
                            eprintln!("Error setting volume: {}", e);
                        }
                    }
                }
            }
            
            if let Some(name) = event.name {
                if name.to_string_lossy() == "audio1" && is_character_device("/dev/audio1") {
                    if let Ok(json) = get_system_json() {
                        if let Some(volume) = get_volume(&json) {
                            if let Err(e) = set_volume(volume) {
                                eprintln!("Error setting volume: {}", e);
                            }
                        }
                    }
                }
            }
        }
    }
}

