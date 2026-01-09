use ring::aead::{LessSafeKey, UnboundKey, AES_256_GCM};

fn sample() {
    let key_bytes = [0u8; 32];
    let unbound = UnboundKey::new(&AES_256_GCM, &key_bytes).unwrap();
    let _key = LessSafeKey::new(unbound);
}
