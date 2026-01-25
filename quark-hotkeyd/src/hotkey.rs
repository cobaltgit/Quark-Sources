use evdev::KeyCode;
use std::time::{Duration, Instant};

pub struct HotkeyEvent {
    pub keys: Vec<KeyCode>,
    pub trigger: Trigger,
    pub callback: fn(),
    pub state: HotkeyState,
}

impl HotkeyEvent {
    pub fn should_fire(&mut self, chord_down: bool) -> bool {
        match self.trigger {
            Trigger::Press => {
                let fire = chord_down && !self.state.was_down;
                self.state.was_down = chord_down;
                fire
            }
            Trigger::Hold { duration } => {
                if chord_down {
                    if self.state.fired {
                        return false;
                    }
                    match self.state.armed_at {
                        None => {
                            self.state.armed_at = Some(Instant::now());
                            false
                        }
                        Some(t0) => {
                            if t0.elapsed() >= duration {
                                self.state.fired = true;
                                true
                            } else {
                                false
                            }
                        }
                    }
                } else {
                    self.state.armed_at = None;
                    self.state.fired = false;
                    false
                }
            }
        }
    }
}

#[derive(Clone, Copy)]
pub enum Trigger {
    Press,
    Hold { duration: Duration },
}

#[derive(Default)]
pub struct HotkeyState {
    pub was_down: bool,
    pub armed_at: Option<Instant>,
    pub fired: bool,
}
