#![no_std]
#![no_main]

extern crate libc;

#[unsafe(no_mangle)]
pub extern "C" fn main() -> isize {
    unsafe {
        libc::sync();
        libc::reboot(libc::RB_AUTOBOOT);
    }
    0
}

#[panic_handler]
fn my_panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
