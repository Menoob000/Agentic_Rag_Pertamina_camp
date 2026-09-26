@extends('layouts.app')

@section('title', 'Audit Trail')

@section('content')
<div class="page-header">
    <h1 class="page-title">Audit Trail</h1>
    <p class="page-desc">Catatan seluruh aktivitas dari semua pengguna sistem. Hanya dapat diakses oleh administrator.</p>
</div>

{{-- Statistik Ringkasan --}}
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{{ number_format($stats['total']) }}</div>
        <div class="stat-label">Total Aktivitas</div>
    </div>
    <div class="stat-card stat-success">
        <div class="stat-value">{{ number_format($stats['success']) }}</div>
        <div class="stat-label">Berhasil</div>
    </div>
    <div class="stat-card stat-danger">
        <div class="stat-value">{{ number_format($stats['failed']) }}</div>
        <div class="stat-label">Gagal</div>
    </div>
    <div class="stat-card stat-info">
        <div class="stat-value">
            {{ $stats['avg_time'] ? number_format($stats['avg_time'] / 1000, 1) . 's' : '—' }}
        </div>
        <div class="stat-label">Rata-rata Waktu</div>
    </div>
</div>

{{-- Filter --}}
<div class="card filter-card">
    <form method="GET" action="{{ route('audit.index') }}" class="filter-form">
        <div class="filter-group">
            <label for="search" class="form-label">Cari</label>
            <input type="text" id="search" name="search" class="form-input"
                   value="{{ request('search') }}"
                   placeholder="Cari jenis pekerjaan, lokasi, atau nama pengguna...">
        </div>
        <div class="filter-group">
            <label for="status" class="form-label">Status</label>
            <select id="status" name="status" class="form-input form-select">
                <option value="">Semua Status</option>
                <option value="success" {{ request('status') === 'success' ? 'selected' : '' }}>Berhasil</option>
                <option value="failed" {{ request('status') === 'failed' ? 'selected' : '' }}>Gagal</option>
                <option value="processing" {{ request('status') === 'processing' ? 'selected' : '' }}>Proses</option>
            </select>
        </div>
        <div class="filter-group filter-actions">
            <button type="submit" class="btn btn-primary">
                <svg class="btn-icon-sm" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                </svg>
                Filter
            </button>
            @if(request()->hasAny(['search', 'status']))
            <a href="{{ route('audit.index') }}" class="btn btn-secondary">Reset</a>
            @endif
        </div>
    </form>
</div>

{{-- Tabel Audit --}}
<div class="card">
    <div class="table-responsive">
        <table class="data-table" id="audit-table">
            <thead>
                <tr>
                    <th>No</th>
                    <th>Tanggal</th>
                    <th>Pengguna</th>
                    <th>Jenis Pekerjaan</th>
                    <th>Lokasi</th>
                    <th>File</th>
                    <th>Status</th>
                    <th>Waktu</th>
                </tr>
            </thead>
            <tbody>
                @forelse($logs as $index => $log)
                <tr>
                    <td class="text-center">{{ $logs->firstItem() + $index }}</td>
                    <td class="text-nowrap">
                        <div class="date-cell">
                            <span class="date-main">{{ $log->created_at->format('d M Y') }}</span>
                            <span class="date-sub">{{ $log->created_at->format('H:i:s') }}</span>
                        </div>
                    </td>
                    <td>
                        <div class="user-cell">
                            <span class="user-cell-name">{{ $log->user->name ?? '—' }}</span>
                            <span class="user-cell-role">{{ ucfirst($log->user->role ?? '') }}</span>
                        </div>
                    </td>
                    <td><strong>{{ Str::limit($log->jenis_pekerjaan, 40) }}</strong></td>
                    <td>{{ $log->lokasi ?: '—' }}</td>
                    <td class="text-nowrap">{{ Str::limit($log->original_filename, 25) }}</td>
                    <td class="text-center">
                        @if($log->status === 'success')
                            <span class="badge badge-success">Berhasil</span>
                        @elseif($log->status === 'processing')
                            <span class="badge badge-warning">Proses</span>
                        @else
                            <span class="badge badge-danger" title="{{ $log->error_message }}">Gagal</span>
                        @endif
                    </td>
                    <td class="text-center text-nowrap">
                        @if($log->processing_time_ms)
                            {{ number_format($log->processing_time_ms / 1000, 1) }}s
                        @else
                            —
                        @endif
                    </td>
                </tr>
                @empty
                <tr>
                    <td colspan="8" class="text-center" style="padding: 40px;">
                        Tidak ada data yang sesuai dengan filter.
                    </td>
                </tr>
                @endforelse
            </tbody>
        </table>
    </div>

    @if($logs->hasPages())
    <div class="pagination-wrapper">
        {{ $logs->links() }}
    </div>
    @endif
</div>
@endsection
