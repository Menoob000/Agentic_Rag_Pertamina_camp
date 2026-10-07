<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class KnowledgeController extends Controller
{
    private function dapurUrl(): string
    {
        return rtrim(config('services.dapur_ai.base_url', env('DAPUR_AI_URL', 'http://dapur-ai:8000')), '/');
    }

    /** Fetch KB listing from Dapur AI (null on failure). */
    private function fetchKnowledge(): array
    {
        try {
            $res = Http::timeout(30)->get($this->dapurUrl() . '/api/knowledge');
            if ($res->successful()) {
                return ['ok' => true, 'data' => $res->json()];
            }
            return ['ok' => false, 'error' => $res->json('detail') ?? $res->body()];
        } catch (\Exception $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function index()
    {
        return view('knowledge.index');
    }

    /** JSON for live status polling from the page. */
    public function status()
    {
        $kb = $this->fetchKnowledge();
        if (!$kb['ok']) {
            return response()->json(['error' => $kb['error']], 502);
        }
        return response()->json($kb['data']);
    }

    public function upload(Request $request)
    {
        $request->validate([
            'document' => 'required|mimes:pdf|max:10240', // Max 10MB
        ]);

        $file = $request->file('document');

        try {
            $response = Http::timeout(60)->attach(
                'file', file_get_contents($file->getRealPath()), $file->getClientOriginalName()
            )->post($this->dapurUrl() . '/api/ingest-pdf');

            if ($response->successful()) {
                $json = $response->json();
                return redirect()->route('knowledge.index')->with('success', 'Berhasil! ' . ($json['message'] ?? 'Dokumen diunggah dan proses ingest berjalan.'));
            }
            return back()->with('error', 'Gagal menghubungi Dapur AI: ' . $response->body());
        } catch (\Exception $e) {
            return back()->with('error', 'Terjadi kesalahan sistem: ' . $e->getMessage());
        }
    }

    public function ingestAll()
    {
        try {
            $response = Http::timeout(30)->post($this->dapurUrl() . '/api/ingest-all');
            if ($response->successful()) {
                return redirect()->route('knowledge.index')->with('success', $response->json('message') ?? 'Ingest semua dokumen dimulai.');
            }
            return back()->with('error', 'Gagal: ' . $response->body());
        } catch (\Exception $e) {
            return back()->with('error', 'Terjadi kesalahan sistem: ' . $e->getMessage());
        }
    }

    public function destroy(string $filename)
    {
        try {
            $response = Http::timeout(30)->delete($this->dapurUrl() . '/api/knowledge/' . rawurlencode($filename));
            if ($response->successful()) {
                return redirect()->route('knowledge.index')->with('success', $response->json('message') ?? 'Dokumen dihapus.');
            }
            return back()->with('error', 'Gagal menghapus: ' . $response->body());
        } catch (\Exception $e) {
            return back()->with('error', 'Terjadi kesalahan sistem: ' . $e->getMessage());
        }
    }
}
