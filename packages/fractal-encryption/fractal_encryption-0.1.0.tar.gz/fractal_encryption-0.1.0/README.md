# Fractal Encryption System(FES)

A Python library for encrypting and decrypting messages using fractal-based techniques.

## Installation

```bash
pip install fractal_encryption
```

## Usage

```python
from fractal_encryption import generate_mandelbrot, generate_julia, generate_burningship, encrypt_message, decrypt_message
import secrets

# Generate fractal (Mandelbrot set)
width, height = 100, 100
max_iter = 256
seed = 12345  # User-defined seed value
iv = secrets.token_hex(16)  # Random initial vector
fractal_pixels = generate_mandelbrot(width, height, max_iter, seed, iv)

# Plain text
message = "Hello, Fractal Encryption!"

# Encrypt
encrypted_message = encrypt_message(message, fractal_pixels, iv)
print("Encrypted Message:", encrypted_message)

# Decrypt
decrypted_message = decrypt_message(encrypted_message, fractal_pixels, iv)
print("Decrypted Message:", decrypted_message)

# Generate fractal (Julia set)
c_real, c_imag = -0.7, 0.27015  # Julia set parameters
fractal_pixels = generate_julia(width, height, max_iter, seed, iv, c_real, c_imag)

# Encrypt
encrypted_message = encrypt_message(message, fractal_pixels, iv)
print("Encrypted Message (Julia):", encrypted_message)

# Decrypt
decrypted_message = decrypt_message(encrypted_message, fractal_pixels, iv)
print("Decrypted Message (Julia):", decrypted_message)

# Generate fractal (Burning Ship)
fractal_pixels = generate_burningship(width, height, max_iter, seed, iv)

# Encrypt
encrypted_message = encrypt_message(message, fractal_pixels, iv)
print("Encrypted Message (Burning Ship):", encrypted_message)

# Decrypt
decrypted_message = decrypt_message(encrypted_message, fractal_pixels, iv)
print("Decrypted Message (Burning Ship):", decrypted_message)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
