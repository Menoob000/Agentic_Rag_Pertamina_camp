<?php

namespace App\Jobs;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use App\Services\DapurApiService;
use App\Models\AuditLog;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Log;

class ProcessTenderGeneration implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    /**
     * Waktu maksimal eksekusi job (10 menit) sebelum dianggap timeout
     */
    public $timeout = 600;

    protected $data;
    protected $filePath;
    protected $auditLogId;
    protected $originalFilename;

    public function __construct(array $data, string $filePath, int $auditLogId, string $originalFilename)
    {
        $this->data = $data;
        $this->filePath = $filePath;
        $this->auditLogId = $auditLogId;
        $this->originalFilename = $originalFilename;
    }

    public function handle(DapurApiService $apiService)
    {
        $auditLog = AuditLog::find($this->auditLogId);
        if (!$auditLog) return;

        $startTime = microtime(true);

        try {
            // Path absolut dari storage Laravel
            $absoluteFilePath = Storage::path($this->filePath);

            if (!file_exists($absoluteFilePath)) {
                throw new \Exception('File PDF sumber tidak ditemukan di server.');
            }

            // Panggil API Dapur AI
            $response = $apiService->generateTenderFromPath($this->data, $absoluteFilePath, $this->originalFilename);
            
            $processingTimeMs = (int) ((microtime(true) - $startTime) * 1000);

            if ($response->successful()) {
                // Simpan docx hasil AI ke storage public agar bisa didownload dari halaman Riwayat
                $filename = 'Tender_' . str_replace('/', '_', $this->data['nomor_tender']) . '_' . date('Ymd_His') . '.docx';
                
                Storage::disk('public')->put('documents/' . $filename, $response->body());

                $auditLog->update([
                    'status' => 'success',
                    'file_path' => 'documents/' . $filename,
                    'processing_time_ms' => $processingTimeMs,
                ]);
            } else {
                $auditLog->update([
                    'status' => 'failed', 
                    'error_message' => 'Status: ' . $response->status() . ' - ' . substr($response->body(), 0, 500),
                    'processing_time_ms' => $processingTimeMs,
                ]);
            }
        } catch (\Exception $e) {
            $processingTimeMs = (int) ((microtime(true) - $startTime) * 1000);
            $auditLog->update([
                'status' => 'failed', 
                'error_message' => substr($e->getMessage(), 0, 1000),
                'processing_time_ms' => $processingTimeMs,
            ]);
        } finally {
            // Selalu hapus file PDF mentah sementara (menghemat storage server)
            if (Storage::exists($this->filePath)) {
                Storage::delete($this->filePath);
            }
        }
    }
}
