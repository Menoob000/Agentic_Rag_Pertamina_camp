<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Auth;
use App\Models\AuditLog;
use App\Services\DapurApiService;
use App\Jobs\ProcessTenderGeneration;
use Illuminate\Support\Facades\Storage;
use Exception;

class TenderController extends Controller
{
    protected DapurApiService $apiService;

    public function __construct(DapurApiService $apiService)
    {
        $this->apiService = $apiService;
    }

    /**
     * Tampilkan form pembuatan Dokumen Tender
     */
    public function showForm()
    {
        return view('tender.form');
    }

    /**
     * Terima request dari form, validasi, dan teruskan ke Dapur AI
     */
    public function generate(Request $request)
    {
        $request->validate([
            'nama_pengadaan' => 'required|string',
            'nomor_tender' => 'required|string',
            'tanggal' => 'required|string',
            'prime_cost' => 'required|numeric',
            'total_dengan_kr' => 'required|numeric',
            'resiko_csms' => 'required|string',
            'tkdn_minimal' => 'required|numeric',
            'metode_pemenuhan' => 'required|string',
            'jenis_kontrak' => 'required|string',
            'pejabat_procurement_nama' => 'required|string',
            'pejabat_procurement_jabatan' => 'required|string',
            'pejabat_berwenang' => 'required|string',
            'pengawas_pekerjaan' => 'required|string',
            'prebid_tanggal' => 'required|string',
            'prebid_waktu' => 'required|string',
            'prebid_tempat' => 'required|string',
            'pemasukan_mulai' => 'required|string',
            'pemasukan_selesai' => 'required|string',
            'file' => 'required|file|mimes:pdf|max:51200', // max 50MB
        ]);

        $file = $request->file('file');
        
        // 1. Simpan file PDF ke storage lokal (sementara) agar bisa dibaca oleh Background Job
        $originalFilename = $file->getClientOriginalName();
        $filePath = $file->store('temp_pdf');
        
        // 2. Catat di audit log bahwa proses dimulai
        $auditLog = AuditLog::create([
            'user_id' => Auth::id(),
            'jenis_pekerjaan' => '[TENDER] ' . $request->nama_pengadaan,
            'lokasi' => '-', 
            'original_filename' => $originalFilename,
            'status' => 'processing'
        ]);
        
        // 3. Lemparkan ke Antrean (Background Job)
        ProcessTenderGeneration::dispatch(
            $request->all(), 
            $filePath, 
            $auditLog->id, 
            $originalFilename
        );

        // 4. Langsung berikan response seketika (redirect)
        return redirect()->route('rks.history')->with('success', 'Dokumen Tender sedang diproses oleh AI di latar belakang. Silakan pantau statusnya di halaman ini.');
    }
}
