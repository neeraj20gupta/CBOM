const crypto = require('crypto');

const ALG = "aes-256-gcm";
const TEMPLATE_ALG = `aes-192-cbc`;

crypto.createCipheriv(ALG, Buffer.alloc(32), Buffer.alloc(16));
crypto.createCipheriv(TEMPLATE_ALG, Buffer.alloc(24), Buffer.alloc(16));
crypto.createHash('sha256');

crypto.pbkdf2('secret', 'salt', 1000, 32, 'sha256', () => {});
crypto.pbkdf2Sync('secret', 'salt', 1000, 32, 'sha256');
crypto.scrypt('secret', 'salt', 32, () => {});
crypto.scryptSync('secret', 'salt', 32);
crypto.hkdf('sha256', 'salt', 'ikm', 'info', 32, () => {});

crypto.createPublicKey('pem');
crypto.createPrivateKey('pem');
crypto.createSecretKey(Buffer.alloc(32));
crypto.generateKey('rsa', { modulusLength: 2048 }, () => {});

crypto.diffieHellman({ privateKey: 'key', publicKey: 'pub' });
crypto.createDiffieHellman(2048);
crypto.createECDH('prime256v1');

crypto.sign('RSA-SHA256', Buffer.from('data'), 'key');
crypto.verify('RSA-SHA256', Buffer.from('data'), 'key', Buffer.from('sig'));

crypto.webcrypto.subtle.digest('SHA-256', Buffer.from('data'));
crypto.webcrypto.subtle.sign('RSASSA-PKCS1-v1_5', 'key', Buffer.from('data'));
crypto.webcrypto.subtle.verify('RSASSA-PKCS1-v1_5', 'key', Buffer.from('data'), Buffer.from('sig'));
