<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class KnowledgeController extends Controller
{
    public function index()
    {
        return view('knowledge.index');
    }

    public function upload(Request $request)
    {
        $request->validate([
            'document' => 'required|mimes:pdf|max:10240', // Max 10MB
        ]);

        $file = $request->file('document');

        try {
            // Send file to Dapur AI /api/ingest-pdf
            $dapurUrl = env('DAPUR_AI_URL', 'http://dapur-ai:8000') . '/api/ingest-pdf';
            
            $response = Http::timeout(60)->attach(
                'file', file_get_contents($file->getRealPath()), $file->getClientOriginalName()
            )->post($dapurUrl);

            if ($response->successful()) {
                $json = $response->json();
                return redirect()->route('knowledge.index')->with('success', 'Berhasil! ' . ($json['message'] ?? 'Dokumen telah diunggah dan proses pelatihan AI sedang berjalan.'));
            } else {
                return back()->with('error', 'Gagal menghubungi Dapur AI: ' . $response->body());
            }
        } catch (\Exception $e) {
            return back()->with('error', 'Terjadi kesalahan sistem: ' . $e->getMessage());
        }
    }
}
