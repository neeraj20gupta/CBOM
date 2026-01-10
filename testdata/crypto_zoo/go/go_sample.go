package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/ecdsa"
	"crypto/ed25519"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"golang.org/x/crypto/chacha20poly1305"
	"golang.org/x/crypto/hkdf"
	"golang.org/x/crypto/pbkdf2"
	"golang.org/x/crypto/scrypt"
	"golang.org/x/crypto/ssh"
)

func main() {
	key := make([]byte, 32)
	iv := make([]byte, 16)

	block, _ := aes.NewCipher(key)
	cipher.NewGCM(block)
	cipher.NewCBCEncrypter(block, iv)
	cipher.NewCBCDecrypter(block, iv)
	cipher.NewCTR(block, iv)

	pbkdf2.Key([]byte("pw"), []byte("salt"), 4096, 32, nil)
	scrypt.Key([]byte("pw"), []byte("salt"), 1, 8, 1, 32)
	hkdf.New(nil, []byte("secret"), []byte("salt"), []byte("info"))
	chacha20poly1305.New(key)
	chacha20poly1305.NewX(key)

	ssh.Dial("tcp", "example.com:22", &ssh.ClientConfig{})
	tls.Dial("tcp", "example.com:443", &tls.Config{})
	tls.Listen("tcp", ":443", &tls.Config{})
	tls.LoadX509KeyPair("cert.pem", "key.pem")

	rsa.GenerateKey(rand.Reader, 2048)
	ecdsa.GenerateKey(elliptic.P256(), rand.Reader)
	ed25519.GenerateKey(rand.Reader)
}
