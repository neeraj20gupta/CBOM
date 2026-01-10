#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/ec.h>
#include <openssl/bn.h>

void demo() {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_get_cipherbyname("aes-256-gcm");
    EVP_CIPHER_fetch(NULL, "AES-256-GCM", NULL);
    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);

    RSA *rsa = RSA_new();
    BIGNUM *e = BN_new();
    RSA_generate_key_ex(rsa, 2048, e, NULL);

    EC_KEY_new_by_curve_name(NID_X9_62_prime256v1);
}
