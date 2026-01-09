package main

import (
  "crypto/aes"
  "crypto/cipher"
)

func main() {
  block, _ := aes.NewCipher([]byte("example key 1234"))
  _, _ = cipher.NewGCM(block)
}
