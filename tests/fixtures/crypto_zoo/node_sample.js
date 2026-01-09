const crypto = require('crypto');

function encrypt(key, iv, data) {
  return crypto.createCipheriv('aes-256-gcm', key, iv);
}
