const { test, expect } = require('@playwright/test');
const path = require('path');

test.describe('Modul Pembuatan RKS (RKS Generation)', () => {

  test('TC-RKS-01: Generate RKS dengan parameter lengkap', async ({ page }) => {
    // Memberikan waktu ekstra karena proses AI bisa memakan waktu 2-5 menit
    test.setTimeout(360000); // 6 Menit (360.000 ms)

    // 1. Login terlebih dahulu
    await page.goto('/login');
    await page.fill('#email', 'admin@itec.ai');
    await page.fill('#password', 'password');
    await page.click('#btn-login');

    // Pastikan berhasil masuk ke Dashboard (Form RKS)
    await expect(page).toHaveURL('/');

    // 2. Isi Parameter Pengadaan
    await page.fill('#jenis_pekerjaan', 'Pekerjaan Overhaul Tangki');
    await page.fill('#detail_pekerjaan', 'Pekerjaan overhaul tangki timbun termasuk penggantian sistem proteksi.');
    await page.fill('#lokasi', 'Terminal BBM Plumpang');

    // 3. Upload Dokumen PDF
    // Menggunakan file asli yang sudah ada di folder dapur-ai Anda
    const pdfPath = path.resolve(__dirname, '../../dapur-ai/RAG/Data/RKS-041T304-PEKERJAAN OVERHAUL TANKI.pdf');
    
    // Playwright langsung memasukkan file ke dalam input type="file"
    await page.setInputFiles('#file', pdfPath);

    // Verifikasi bahwa nama file muncul di UI setelah diunggah (Sesuai script JS di blade)
    await expect(page.locator('#file-name')).toContainText('RKS-041T304');

    // 4. Klik Generate dan Tunggu Proses AI (Tunggu File Diunduh)
    // Setup pendeteksi unduhan (download) sebelum menekan tombol
    const downloadPromise = page.waitForEvent('download', { timeout: 350000 });
    
    // Klik tombol generate
    await page.click('#btn-generate');

    // Verifikasi layar loading muncul dengan benar
    await expect(page.locator('#loading-overlay')).toBeVisible();

    // Robot akan menunggu dengan sabar sampai ada respon unduhan dari web
    const download = await downloadPromise;
    
    // Pastikan ekstensi file hasil unduhan adalah .docx
    expect(download.suggestedFilename()).toMatch(/\.docx$/);
    
    // Simpan file unduhan hasil robot ke folder scenario-test agar Anda bisa melihat buktinya
    const savePath = path.resolve(__dirname, '../dokumen-rks-hasil-robot.docx');
    await download.saveAs(savePath);

    console.log('Dokumen RKS berhasil digenerate dan disimpan di:', savePath);
  });

});
