export type QuantumSafety = {
  quantumSafe: number;
  notQuantumSafe: number;
  unknown: number;
};

export type Breakdown = Record<string, number>;

export type DashboardData = {
  totalAssets: number;
  totalPrimitives: number;
  totalFunctions: number;
  quantumSafety: QuantumSafety;
  primitives: Breakdown;
  functions: Breakdown;
};

type RawAsset = {
  algorithm?: string;
  mode?: string;
  assetType?: string;
  api?: string;
};

const PQ_ALGORITHMS = new Set([
  'KYBER',
  'DILITHIUM',
  'FALCON',
  'SPHINCS',
  'SPHINCS+',
  'BIKE',
  'SIKE'
]);

const PRIMITIVE_BUCKETS = [
  'hash',
  'mac',
  'block-cipher',
  'pke',
  'signature',
  'ae',
  'other'
] as const;

const FUNCTION_BUCKETS = [
  'keygen',
  'encrypt',
  'decrypt',
  'sign',
  'verify',
  'kdf',
  'tls',
  'rng'
] as const;

const normalizeValue = (value?: string) => (value ?? 'UNKNOWN').toUpperCase();

const extractAssets = (payload: unknown): RawAsset[] => {
  if (!payload || typeof payload !== 'object') {
    return [];
  }
  const record = payload as Record<string, unknown>;
  if (Array.isArray(record.cryptoAssets)) {
    return record.cryptoAssets.map((asset) => {
      const item = asset as Record<string, unknown>;
      return {
        algorithm: item.algorithm as string | undefined,
        mode: item.mode as string | undefined,
        assetType: item.assetType as string | undefined,
        api: item.api as string | undefined
      };
    });
  }
  if (Array.isArray(record.components)) {
    return record.components.map((component) => {
      const comp = component as Record<string, unknown>;
      const props = Array.isArray(comp.properties) ? comp.properties : [];
      const lookup: Record<string, string> = {};
      for (const prop of props) {
        const entry = prop as Record<string, unknown>;
        if (typeof entry.name === 'string' && typeof entry.value === 'string') {
          lookup[entry.name] = entry.value;
        }
      }
      return {
        algorithm: lookup['cbom:algorithm'],
        mode: lookup['cbom:mode'],
        assetType: lookup['cbom:assetType'],
        api: lookup['cbom:api']
      };
    });
  }
  return [];
};

const tally = (buckets: readonly string[]): Breakdown =>
  buckets.reduce((acc, key) => {
    acc[key] = 0;
    return acc;
  }, {} as Breakdown);

const classifyQuantumSafety = (algorithm: string) => {
  if (!algorithm || algorithm === 'UNKNOWN') {
    return 'unknown';
  }
  if (PQ_ALGORITHMS.has(algorithm)) {
    return 'quantumSafe';
  }
  return 'notQuantumSafe';
};

const classifyPrimitive = (asset: RawAsset) => {
  const assetType = normalizeValue(asset.assetType);
  const algorithm = normalizeValue(asset.algorithm);
  const mode = normalizeValue(asset.mode);

  if (assetType === 'HASH') {
    return 'hash';
  }
  if (assetType === 'MAC') {
    return 'mac';
  }
  if (assetType === 'SIGNATURE') {
    return 'signature';
  }
  if (assetType === 'ASYMMETRIC') {
    return 'pke';
  }
  if (assetType === 'AEAD' || (assetType === 'SYMMETRIC' && ['GCM', 'CCM', 'POLY1305'].includes(mode))) {
    return 'ae';
  }
  if (assetType === 'SYMMETRIC') {
    return 'block-cipher';
  }
  if (['PBKDF2', 'SCRYPT', 'HKDF'].includes(algorithm)) {
    return 'other';
  }
  return 'other';
};

const classifyFunction = (asset: RawAsset) => {
  const api = (asset.api ?? '').toLowerCase();
  const algorithm = normalizeValue(asset.algorithm);
  const assetType = normalizeValue(asset.assetType);

  const buckets: string[] = [];

  if (api.includes('encrypt')) buckets.push('encrypt');
  if (api.includes('decrypt')) buckets.push('decrypt');
  if (api.includes('sign')) buckets.push('sign');
  if (api.includes('verify')) buckets.push('verify');
  if (api.includes('generate') || api.includes('key') || assetType.includes('KEY')) buckets.push('keygen');
  if (assetType === 'KDF' || ['PBKDF2', 'SCRYPT', 'HKDF'].includes(algorithm)) buckets.push('kdf');
  if (api.includes('tls') || algorithm === 'TLS') buckets.push('tls');
  if (api.includes('rand') || api.includes('rng')) buckets.push('rng');

  return buckets;
};

export const parseCbom = (payload: unknown): DashboardData => {
  const assets = extractAssets(payload);
  const quantumSafety = {
    quantumSafe: 0,
    notQuantumSafe: 0,
    unknown: 0
  };
  const primitives = tally(PRIMITIVE_BUCKETS);
  const functions = tally(FUNCTION_BUCKETS);

  assets.forEach((asset) => {
    const algorithm = normalizeValue(asset.algorithm);
    const safetyBucket = classifyQuantumSafety(algorithm);
    quantumSafety[safetyBucket] += 1;

    const primitiveBucket = classifyPrimitive(asset);
    primitives[primitiveBucket] += 1;

    const functionBuckets = classifyFunction(asset);
    functionBuckets.forEach((bucket) => {
      functions[bucket] += 1;
    });
  });

  const totalPrimitives = Object.values(primitives).filter((value) => value > 0).length;
  const totalFunctions = Object.values(functions).filter((value) => value > 0).length;

  return {
    totalAssets: assets.length,
    totalPrimitives,
    totalFunctions,
    quantumSafety,
    primitives,
    functions
  };
};
