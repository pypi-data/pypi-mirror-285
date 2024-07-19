import unittest
from fractal_encryption import (
    generate_mandelbrot,
    generate_julia,
    generate_burningship,
    encrypt_message,
    decrypt_message
)
import secrets

class TestFractalEncryption(unittest.TestCase):
    def setUp(self):
        self.width = 100
        self.height = 100
        self.max_iter = 256
        self.seed = 12345
        self.iv = secrets.token_hex(16)
        self.message = "Hello, Fractal Encryption!"
        self.c_real = -0.7
        self.c_imag = 0.27015

    def test_generate_mandelbrot(self):
        pixels = generate_mandelbrot(self.width, self.height, self.max_iter, self.seed, self.iv)
        self.assertEqual(len(pixels), self.height)
        self.assertEqual(len(pixels[0]), self.width)

    def test_generate_julia(self):
        pixels = generate_julia(self.width, self.height, self.max_iter, self.seed, self.iv, self.c_real, self.c_imag)
        self.assertEqual(len(pixels), self.height)
        self.assertEqual(len(pixels[0]), self.width)

    def test_generate_burningship(self):
        pixels = generate_burningship(self.width, self.height, self.max_iter, self.seed, self.iv)
        self.assertEqual(len(pixels), self.height)
        self.assertEqual(len(pixels[0]), self.width)

    def test_encrypt_decrypt_mandelbrot(self):
        pixels = generate_mandelbrot(self.width, self.height, self.max_iter, self.seed, self.iv)
        encrypted_message = encrypt_message(self.message, pixels, self.iv)
        decrypted_message = decrypt_message(encrypted_message, pixels, self.iv)
        self.assertEqual(self.message, decrypted_message)

    def test_encrypt_decrypt_julia(self):
        pixels = generate_julia(self.width, self.height, self.max_iter, self.seed, self.iv, self.c_real, self.c_imag)
        encrypted_message = encrypt_message(self.message, pixels, self.iv)
        decrypted_message = decrypt_message(encrypted_message, pixels, self.iv)
        self.assertEqual(self.message, decrypted_message)

    def test_encrypt_decrypt_burningship(self):
        pixels = generate_burningship(self.width, self.height, self.max_iter, self.seed, self.iv)
        encrypted_message = encrypt_message(self.message, pixels, self.iv)
        decrypted_message = decrypt_message(encrypted_message, pixels, self.iv)
        self.assertEqual(self.message, decrypted_message)

if __name__ == '__main__':
    unittest.main()
