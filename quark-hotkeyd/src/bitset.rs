#[derive(Clone)]
pub struct KeyBitSet {
    bits: [u64; 12],
}

impl KeyBitSet {
    pub fn new() -> Self {
        Self { bits: [0; 12] }
    }

    #[inline(always)]
    pub fn set(&mut self, code: u16, down: bool) {
        let idx = (code as usize) >> 6;
        let mask = 1u64 << ((code as usize) & 63);

        if idx >= self.bits.len() {
            return;
        }

        if down {
            self.bits[idx] |= mask;
        } else {
            self.bits[idx] &= !mask;
        }
    }

    #[inline(always)]
    pub fn get(&self, code: u16) -> bool {
        let idx = (code as usize) >> 6;
        let bit = (code as usize) & 63;

        if idx >= self.bits.len() {
            return false;
        }

        (self.bits[idx] >> bit) & 1 == 1
    }

    #[inline(always)]
    fn clear(&mut self) {
        self.bits = [0; 12];
    }
}
