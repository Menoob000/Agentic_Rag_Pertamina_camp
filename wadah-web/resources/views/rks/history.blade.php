@extends('layouts.app')

@section('title', 'Riwayat Generate RKS')

@section('content')
<div class="page-header">
    <h1 class="page-title">Riwayat Generate Dokumen</h1>
    <p class="page-desc">Daftar seluruh aktivitas pembuatan dokumen RKS yang pernah Anda lakukan.</p>
</div>

@if($logs->isEmpty())
<div class="empty-state">
    <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
    </svg>
    <h3 class="empty-title">Belum Ada Riwayat</h3>
    <p class="empty-text">Anda belum pernah membuat dokumen RKS. Mulai dengan mengisi formulir.</p>
    <a href="{{ route('rks.form') }}" class="btn btn-primary">Buat RKS Sekarang</a>
</div>
@else
<div class="card">
    <div class="table-responsive">
        <table class="data-table" id="history-table">
            <thead>
                <tr>
                    <th>No</th>
                    <th>Tanggal</th>
                    <th>Jenis Pekerjaan</th>
                    <th>Lokasi</th>
                    <th>File Referensi</th>
                    <th>Status</th>
                    <th>Waktu Proses</th>
                    <th>Aksi</th>
                </tr>
            </thead>
            <tbody>
                @foreach($logs as $index => $log)
                <tr>
                    <td class="text-center">{{ $logs->firstItem() + $index }}</td>
                    <td class="text-nowrap">
                        <div class="date-cell">
                            <span class="date-main">{{ $log->created_at->format('d M Y') }}</span>
                            <span class="date-sub">{{ $log->created_at->format('H:i') }} WIB</span>
                        </div>
                    </td>
                    <td>
                        <strong>{{ $log->jenis_pekerjaan }}</strong>
                        @if($log->detail_pekerjaan)
                            <p class="cell-desc">{{ Str::limit($log->detail_pekerjaan, 80) }}</p>
                        @endif
                    </td>
                    <td>{{ $log->lokasi ?: '—' }}</td>
                    <td class="text-nowrap">{{ $log->original_filename }}</td>
                    <td class="text-center">
                        @if($log->status === 'success')
                            <span class="badge badge-success">Berhasil</span>
                        @elseif($log->status === 'processing')
                            <span class="badge badge-warning">
                                <svg class="spin-icon" viewBox="0 0 24 24" width="14" height="14" stroke="currentColor" stroke-width="2" fill="none" style="animation: spin 1s linear infinite; margin-right: 4px; vertical-align: middle;">
                                    <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                                    <path d="M12 2a10 10 0 0 1 10 10"></path>
                                </svg>
                                Diproses
                            </span>
                        @else
                            <span class="badge badge-danger" title="{{ $log->error_message }}">Gagal</span>
                        @endif
                    </td>
                    <td class="text-center text-nowrap">
                        @if($log->processing_time_ms)
                            {{ number_format($log->processing_time_ms / 1000, 1) }} detik
                        @else
                            —
                        @endif
                    </td>
                    <td class="text-center">
                        @if($log->status === 'success' && $log->file_path)
                            <a href="{{ Storage::url($log->file_path) }}" class="btn btn-sm btn-primary" download>
                                <svg viewBox="0 0 24 24" width="16" height="16" stroke="currentColor" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px; vertical-align: middle;">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                    <polyline points="7 10 12 15 17 10"></polyline>
                                    <line x1="12" y1="15" x2="12" y2="3"></line>
                                </svg>
                                Download
                            </a>
                        @elseif($log->status === 'processing')
                            <button class="btn btn-sm btn-outline" disabled>Mohon Tunggu</button>
                        @else
                            —
                        @endif
                    </td>
                </tr>
                @endforeach
            </tbody>
        </table>
    </div>

    {{-- Pagination --}}
    @if($logs->hasPages())
    <div class="pagination-wrapper">
        {{ $logs->links() }}
    </div>
    @endif
</div>
@endif
@endsection
