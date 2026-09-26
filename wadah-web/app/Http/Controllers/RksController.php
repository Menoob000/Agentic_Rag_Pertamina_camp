<?php

namespace App\Http\Controllers;

use App\Models\AuditLog;
use App\Services\DapurApiService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Exception;

class RksController extends Controller
{
    /**
     * Tampilkan halaman form input RKS.
     */
    public function showForm()
    {
        return view('rks.form');
    }

    /**
     * Proses generate dokumen RKS.
     *
     * Alur:
     * 1. Validasi input form + file PDF
     * 2. Simpan audit log (status: processing)
     * 3. Kirim ke Zona Dapur via DapurApiService
     * 4. Terima file .docx dari Dapur
     * 5. Update audit log (status: success/failed)
     * 6. Return file download ke browser
     */
    public function generate(Request $request)
    {
        $request->validate([
            'jenis_pekerjaan'  => ['required', 'string', 'max:255'],
            'detail_pekerjaan' => ['required', 'string', 'max:5000'],
            'lokasi'           => ['nullable', 'string', 'max:255'],
            'file'             => ['required', 'file', 'mimes:pdf', 'max:51200'], // Max 50MB
        ], [
            'jenis_pekerjaan.required'  => 'Jenis pekerjaan wajib diisi.',
            'detail_pekerjaan.required' => 'Detail pekerjaan wajib diisi.',
            'file.required'             => 'File PDF BOQ wajib diunggah.',
            'file.mimes'                => 'File harus berformat PDF.',
            'file.max'                  => 'Ukuran file maksimal 50MB.',
        ]);

        $startTime = microtime(true);

        // 1. Simpan audit log awal
        $auditLog = AuditLog::create([
            'user_id'           => Auth::id(),
            'jenis_pekerjaan'   => $request->input('jenis_pekerjaan'),
            'detail_pekerjaan'  => $request->input('detail_pekerjaan'),
            'lokasi'            => $request->input('lokasi', ''),
            'original_filename' => $request->file('file')->getClientOriginalName(),
            'status'            => 'processing',
        ]);

        try {
            // 2. Kirim request ke Zona Dapur
            $dapurService = new DapurApiService();
            $response = $dapurService->generateRks(
                jenisPekerjaan:  $request->input('jenis_pekerjaan'),
                detailPekerjaan: $request->input('detail_pekerjaan'),
                lokasi:          $request->input('lokasi', ''),
                pdfFile:         $request->file('file'),
            );

            $processingTime = (int) ((microtime(true) - $startTime) * 1000);

            // 3. Cek response dari Dapur
            if ($response->successful()) {
                // Cek apakah response adalah file binary (docx)
                $contentType = $response->header('Content-Type');

                if (str_contains($contentType, 'application/vnd.openxmlformats') ||
                    str_contains($contentType, 'application/octet-stream')) {

                    // Update audit log — sukses
                    $auditLog->update([
                        'status'             => 'success',
                        'processing_time_ms' => $processingTime,
                    ]);

                    // Tentukan nama file output
                    $safeJenis = preg_replace('/[^a-zA-Z0-9_\-]/', '_', $request->input('jenis_pekerjaan'));
                    $filename  = "RKS_{$safeJenis}_" . date('Ymd_His') . '.docx';

                    // Return file sebagai force download
                    return response($response->body(), 200, [
                        'Content-Type'        => 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                        'Content-Disposition' => 'attachment; filename="' . $filename . '"',
                    ]);
                }

                // Response sukses tapi bukan file — mungkin JSON info
                $auditLog->update([
                    'status'             => 'success',
                    'processing_time_ms' => $processingTime,
                ]);

                return back()->with('success',
                    'Dokumen RKS berhasil di-generate! Namun server tidak mengembalikan file secara langsung. ' .
                    'Cek output di server AI.'
                );
            }

            // Response gagal dari Dapur
            $errorBody = $response->json('detail', $response->body());
            $auditLog->update([
                'status'             => 'failed',
                'error_message'      => is_string($errorBody) ? substr($errorBody, 0, 1000) : json_encode($errorBody),
                'processing_time_ms' => $processingTime,
            ]);

            return back()
                ->withInput()
                ->with('error',
                    'Gagal memproses dokumen RKS. Server AI mengembalikan error: ' .
                    (is_string($errorBody) ? $errorBody : json_encode($errorBody))
                );

        } catch (Exception $e) {
            $processingTime = (int) ((microtime(true) - $startTime) * 1000);

            $auditLog->update([
                'status'             => 'failed',
                'error_message'      => substr($e->getMessage(), 0, 1000),
                'processing_time_ms' => $processingTime,
            ]);

            return back()
                ->withInput()
                ->with('error', $e->getMessage());
        }
    }

    /**
     * Tampilkan riwayat generasi dokumen RKS milik user.
     */
    public function history()
    {
        $logs = AuditLog::where('user_id', Auth::id())
            ->orderByDesc('created_at')
            ->paginate(15);

        return view('rks.history', compact('logs'));
    }
}
