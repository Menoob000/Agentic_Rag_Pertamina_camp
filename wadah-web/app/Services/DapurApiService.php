<?php

namespace App\Services;

use Illuminate\Support\Facades\Http;
use Illuminate\Http\Client\Response;
use Illuminate\Http\UploadedFile;
use Exception;

/**
 * DapurApiService
 *
 * Konektor API (HTTP Client) ke Zona Dapur (AI Microservice / FastAPI).
 * Bertanggung jawab untuk:
 * - Mengemas data input dan berkas PDF menggunakan multipart/form-data
 * - Mengirimkan permintaan ke endpoint POST /api/generate-rks
 * - Mengelola timeout jaringan yang memadai (300 detik) untuk proses LLM
 * - Menerima response berupa file .docx (FileResponse)
 */
class DapurApiService
{
    private string $baseUrl;
    private int $timeout;
    private string $endpoint;

    public function __construct()
    {
        $config = config('services.dapur_ai');
        $this->baseUrl  = rtrim($config['base_url'], '/');
        $this->timeout  = $config['timeout'];
        $this->endpoint = $config['endpoint'];
    }

    /**
     * Kirim request generate RKS ke Zona Dapur.
     *
     * @param string       $jenisPekerjaan  Jenis pekerjaan tender
     * @param string       $detailPekerjaan Detail/deskripsi pekerjaan
     * @param string       $lokasi          Lokasi pekerjaan
     * @param UploadedFile $pdfFile         File PDF BOQ yang diupload
     *
     * @return Response Response dari Dapur AI (binary .docx atau JSON error)
     *
     * @throws Exception Jika koneksi gagal atau timeout
     */
    public function generateRks(
        string $jenisPekerjaan,
        string $detailPekerjaan,
        string $lokasi,
        UploadedFile $pdfFile
    ): Response {
        $url = $this->baseUrl . $this->endpoint;

        try {
            $response = Http::timeout($this->timeout)
                ->connectTimeout(30)
                ->attach(
                    'file',
                    fopen($pdfFile->getRealPath(), 'r'),
                    $pdfFile->getClientOriginalName()
                )
                ->post($url, [
                    'jenis_pekerjaan'  => $jenisPekerjaan,
                    'detail_pekerjaan' => $detailPekerjaan,
                    'lokasi'           => $lokasi,
                ]);

            return $response;

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            throw new Exception(
                'Tidak dapat terhubung ke server AI (Zona Dapur). ' .
                'Pastikan layanan dapur-ai sedang berjalan. ' .
                'Detail: ' . $e->getMessage()
            );
        } catch (\Illuminate\Http\Client\RequestException $e) {
            throw new Exception(
                'Terjadi kesalahan saat berkomunikasi dengan server AI. ' .
                'Status: ' . $e->response?->status() . '. ' .
                'Detail: ' . $e->getMessage()
            );
        }
    }

    /**
     * Cek apakah Zona Dapur bisa dijangkau (health check).
     *
     * @return bool
     */
    public function isHealthy(): bool
    {
        try {
            $response = Http::timeout(10)
                ->get($this->baseUrl . '/docs');
            return $response->successful();
        } catch (Exception $e) {
            return false;
        }
    }

    /**
     * Kirim request generate Tender ke Zona Dapur.
     *
     * @param array        $data    Data inputan form tender
     * @param UploadedFile $pdfFile File PDF yang diupload
     *
     * @return Response Response dari Dapur AI (binary .docx atau JSON error)
     *
     * @throws Exception Jika koneksi gagal atau timeout
     */
    public function generateTender(array $data, UploadedFile $pdfFile): Response
    {
        $url = $this->baseUrl . '/api/generate-tender';

        // Buang 'file' dan field tak relevan lainnya dari $data untuk dikirim sebagai POST fields biasa
        unset($data['file'], $data['_token']);

        try {
            $response = Http::timeout($this->timeout)
                ->connectTimeout(30)
                ->attach(
                    'file',
                    fopen($pdfFile->getRealPath(), 'r'),
                    $pdfFile->getClientOriginalName()
                )
                ->post($url, $data);

            return $response;

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            throw new Exception(
                'Tidak dapat terhubung ke server AI (Zona Dapur). ' .
                'Pastikan layanan dapur-ai sedang berjalan. ' .
                'Detail: ' . $e->getMessage()
            );
        } catch (\Illuminate\Http\Client\RequestException $e) {
            throw new Exception(
                'Terjadi kesalahan saat berkomunikasi dengan server AI. ' .
                'Status: ' . $e->response?->status() . '. ' .
                'Detail: ' . $e->getMessage()
            );
        }
    }

    /**
     * Kirim request generate Tender ke Zona Dapur (Dari Background Job)
     * Menggunakan absolute path karena Job tidak memiliki instance UploadedFile HTTP.
     *
     * @param array  $data              Data inputan form tender
     * @param string $absoluteFilePath  Lokasi absolut file PDF di server
     * @param string $originalFilename  Nama file asli
     *
     * @return Response Response dari Dapur AI (binary .docx atau JSON error)
     *
     * @throws Exception Jika koneksi gagal atau timeout
     */
    public function generateTenderFromPath(array $data, string $absoluteFilePath, string $originalFilename): Response
    {
        $url = $this->baseUrl . '/api/generate-tender';

        // Buang field sistem yang tidak perlu
        unset($data['file'], $data['_token']);

        try {
            $response = Http::timeout($this->timeout)
                ->connectTimeout(30)
                ->attach(
                    'file',
                    fopen($absoluteFilePath, 'r'),
                    $originalFilename
                )
                ->post($url, $data);

            return $response;

        } catch (\Illuminate\Http\Client\ConnectionException $e) {
            throw new Exception('Koneksi ke Dapur AI gagal. Detail: ' . $e->getMessage());
        } catch (\Illuminate\Http\Client\RequestException $e) {
            throw new Exception('Dapur AI mengembalikan Error HTTP. Detail: ' . $e->getMessage());
        }
    }
}
