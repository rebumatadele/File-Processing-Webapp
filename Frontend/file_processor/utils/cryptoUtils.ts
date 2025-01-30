// src/utils/cryptoUtils.ts
/**
 * Reads a file and returns its data as Uint8Array.
 */
export async function readFileAsUint8Array(file: File): Promise<Uint8Array> {
    return new Promise<Uint8Array>((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result instanceof ArrayBuffer) {
          resolve(new Uint8Array(reader.result));
        } else {
          reject(new Error("Unable to read file as ArrayBuffer."));
        }
      };
      reader.onerror = () => reject(reader.error);
      reader.readAsArrayBuffer(file);
    });
  }
  
/**
 * Generates a random Uint8Array of a specified length.
 * Uses window.crypto.getRandomValues if available for cryptographic security.
 * Falls back to Math.random if window.crypto.getRandomValues is unavailable.
 * 
 * @param {number} length - The length of the key to generate.
 * @returns {Uint8Array} - The generated random key.
 */
export function generateRandomKey(length: number): Uint8Array {
  if (typeof window !== 'undefined' && window.crypto && window.crypto.getRandomValues) {
    try {
      const keyArray = new Uint8Array(length);
      window.crypto.getRandomValues(keyArray);
      console.log("Secure random key generated using window.crypto.getRandomValues");
      return keyArray;
    } catch (err) {
      console.warn("window.crypto.getRandomValues failed, falling back to Math.random", err);
      // Proceed to fallback
    }
  }

  // Fallback: Less secure random key generation
  console.warn("window.crypto.getRandomValues not available. Generating key using Math.random (Not secure)");
  const keyArray = new Uint8Array(length);
  for (let i = 0; i < length; i++) {
    keyArray[i] = Math.floor(Math.random() * 256);
  }
  return keyArray;
}
  
  
  /**
   * XORs data with a key (must be the same length).
   */
  export function xorData(data: Uint8Array, key: Uint8Array): Uint8Array {
    if (data.length !== key.length) {
      throw new Error("Data and key must be the same length to XOR.");
    }
    const result = new Uint8Array(data.length);
    for (let i = 0; i < data.length; i++) {
      result[i] = data[i] ^ key[i];
    }
    return result;
  }
  
  /**
   * Utility to convert a Uint8Array to a base64-encoded string.
   */
  export function toBase64(uint8Array: Uint8Array): string {
    // In modern browsers, you can do:
    // return btoa(String.fromCharCode(...uint8Array));
    // But below is a more robust approach for large data:
    let binary = '';
    const len = uint8Array.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(uint8Array[i]);
    }
    return window.btoa(binary);
  }
  