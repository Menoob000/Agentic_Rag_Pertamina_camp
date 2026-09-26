<?php

namespace App\Http\Controllers;

use App\Models\AuditLog;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;

class AuditController extends Controller
{
    /**
     * Tampilkan halaman audit trail (admin only).
     * Menampilkan semua aktivitas dari semua user.
     */
    public function index(Request $request)
    {
        // Hanya admin yang boleh akses
        if (!Auth::user()->isAdmin()) {
            abort(403, 'Anda tidak memiliki akses ke halaman ini.');
        }

        $query = AuditLog::with('user')
            ->orderByDesc('created_at');

        // Filter berdasarkan status
        if ($request->filled('status')) {
            $query->where('status', $request->input('status'));
        }

        // Filter berdasarkan pencarian
        if ($request->filled('search')) {
            $search = $request->input('search');
            $query->where(function ($q) use ($search) {
                $q->where('jenis_pekerjaan', 'like', "%{$search}%")
                  ->orWhere('lokasi', 'like', "%{$search}%")
                  ->orWhereHas('user', function ($uq) use ($search) {
                      $uq->where('name', 'like', "%{$search}%");
                  });
            });
        }

        $logs = $query->paginate(20)->withQueryString();

        // Statistik ringkasan
        $stats = [
            'total'   => AuditLog::count(),
            'success' => AuditLog::where('status', 'success')->count(),
            'failed'  => AuditLog::where('status', 'failed')->count(),
            'avg_time' => AuditLog::where('status', 'success')
                ->whereNotNull('processing_time_ms')
                ->avg('processing_time_ms'),
        ];

        return view('audit.index', compact('logs', 'stats'));
    }
}
