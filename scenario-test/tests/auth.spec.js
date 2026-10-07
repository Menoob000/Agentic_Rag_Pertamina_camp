const { test, expect } = require('@playwright/test');

test.describe('Modul Autentikasi', () => {
    
  test('TC-AUTH-01: Login dengan kredensial valid', async ({ page }) => {
    // 1. Buka halaman /login
    await page.goto('/login');

    // 2. Masukkan username dan password valid
    await page.fill('#email', 'admin@itec.ai');
    await page.fill('#password', 'password');

    // 3. Klik tombol Login
    await page.click('#btn-login');

    // Expected Result: Pengguna diarahkan ke Dashboard/Form RKS (/)
    await expect(page).toHaveURL('/');
  });

  test('TC-AUTH-02: Login dengan kredensial tidak valid', async ({ page }) => {
    // 1. Buka halaman /login
    await page.goto('/login');

    // 2. Masukkan password salah
    await page.fill('#email', 'admin@itec.ai');
    await page.fill('#password', 'salah12345');

    // 3. Klik tombol Login
    await page.click('#btn-login');

    // Expected Result: Muncul pesan error dan pengguna tetap di halaman login
    const errorAlert = page.locator('#login-alert');
    await expect(errorAlert).toBeVisible();
    await expect(page).toHaveURL('/login');
  });

});
