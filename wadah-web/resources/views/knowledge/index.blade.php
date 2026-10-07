@extends('layouts.app')

@section('title', 'Manajemen Knowledge Base')

@section('content')
<div class="page-header">
    <h1 class="page-title">Manajemen Knowledge Base</h1>
    <p class="page-desc">Unggah dokumen referensi (PDF) baru untuk memperluas pengetahuan AI saat membuat RKS.</p>
</div>


<div class="card" id="knowledge-form-card">
    <form method="POST"
          action="{{ route('knowledge.upload') }}"
          enctype="multipart/form-data"
          id="knowledge-form"
          class="rks-form">
        @csrf

        {{-- Upload File PDF --}}
        <div class="form-group">
            <label for="document" class="form-label">
                Dokumen Referensi (PDF) <span class="required">*</span>
            </label>
            <div class="file-upload-area" id="file-upload-area">
                <input type="file"
                       id="document"
                       name="document"
                       class="file-input"
                       accept=".pdf"
                       required>
                <div class="file-upload-content" id="file-upload-content">
                    <svg class="file-upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                        <polyline points="17 8 12 3 7 8"/>
                        <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                    <p class="file-upload-text">Klik di sini atau seret file PDF untuk mengunggah</p>
                    <p class="file-upload-hint">Format: PDF · Maksimal: 10MB</p>
                </div>
                <div class="file-selected" id="file-selected" style="display:none">
                    <svg class="file-check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                    </svg>
                    <span class="file-name" id="file-name"></span>
                    <button type="button" class="file-remove" id="file-remove" title="Hapus file">&times;</button>
                </div>
            </div>
            @error('document')
                <span class="error-text">{{ $message }}</span>
            @enderror
            <p class="form-help">Unggah file standar teknis, pedoman, atau spesifikasi material dalam format PDF untuk dilatih oleh AI.</p>
        </div>

        {{-- Submit Button --}}
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-generate" id="btn-submit">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 19V6M5 12l7-7 7 7"/>
                </svg>
                <span class="btn-text">Unggah & Latih AI</span>
            </button>
            <p class="form-help" style="margin-top: 12px; text-align: center;">
                Proses ekstraksi (embedding) AI berjalan di latar belakang. Anda bisa meninggalkan halaman setelah pesan sukses muncul.
            </p>
        </div>
    </form>
</div>


<div class="card" id="knowledge-list-card" style="margin-top:24px">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:16px">
        <div>
            <h2 style="margin:0;font-size:1.1rem">Dokumen di Knowledge Base</h2>
            <p class="form-help" style="margin:4px 0 0">
                Total <strong id="kb-total-chunks">0</strong> chunk tersimpan di Qdrant
                <span id="kb-live" style="display:none">· <em>memperbarui status…</em></span>
            </p>
        </div>
        <form method="POST" action="{{ route('knowledge.ingestAll') }}" onsubmit="return confirm('Ingest ulang semua PDF di server? Proses bisa memakan beberapa menit.')">
            @csrf
            <button type="submit" class="btn btn-primary" id="btn-ingest-all">Ingest Semua PDF</button>
        </form>
    </div>

    <div class="alert alert-error" id="kb-error" style="display:none"></div>

    <table class="data-table" id="kb-table" style="width:100%;border-collapse:collapse">
        <thead>
            <tr style="text-align:left;border-bottom:1px solid #e5e7eb">
                <th style="padding:8px">Nama File</th>
                <th style="padding:8px">Status</th>
                <th style="padding:8px">Chunk</th>
                <th style="padding:8px"></th>
            </tr>
        </thead>
        <tbody id="kb-tbody">
            <tr id="kb-loading"><td colspan="4" style="padding:16px;text-align:center;color:#6b7280">Memuat daftar dokumen...</td></tr>
        </tbody>
    </table>
</div>

@endsection

@section('scripts')
<script>
    (function () {
        const labels = { done: 'Selesai ✔', processing: 'Memproses…', error: 'Gagal ✖', not_ingested: 'Belum di-ingest' };
        const tbody = document.getElementById('kb-tbody');
        const totalChunksEl = document.getElementById('kb-total-chunks');
        const liveEl = document.getElementById('kb-live');
        const errorEl = document.getElementById('kb-error');
        const destroyUrlBase = "{{ url('/knowledge') }}";

        function renderRows(items) {
            if (!items || items.length === 0) {
                tbody.innerHTML = '<tr id="kb-empty"><td colspan="4" style="padding:16px;text-align:center;color:#6b7280">Belum ada dokumen. Unggah PDF di atas atau klik "Ingest Semua PDF".</td></tr>';
                return;
            }
            const csrfToken = document.querySelector('input[name="_token"]')?.value || '{{ csrf_token() }}';
            tbody.innerHTML = items.map(it => {
                const label = labels[it.state] || it.state;
                const errTitle = it.error ? `title="${it.error.replace(/"/g, '&quot;')}"` : '';
                return `
                    <tr data-name="${it.filename}" style="border-bottom:1px solid #f3f4f6">
                        <td style="padding:8px">${it.filename}</td>
                        <td style="padding:8px" class="kb-state" data-raw="${it.state}" ${errTitle}>${label}</td>
                        <td style="padding:8px" class="kb-chunks">${it.chunks}</td>
                        <td style="padding:8px;text-align:right">
                            <form method="POST" action="${destroyUrlBase}/${encodeURIComponent(it.filename)}" onsubmit="return confirm('Hapus dokumen ini dari Knowledge Base?')" style="display:inline">
                                <input type="hidden" name="_token" value="${csrfToken}">
                                <input type="hidden" name="_method" value="DELETE">
                                <button type="submit" class="btn btn-secondary btn-delete-doc">Hapus</button>
                            </form>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        function loadStatus() {
            fetch('{{ route('knowledge.status') }}', { headers: { 'Accept': 'application/json' } })
                .then(r => {
                    if (!r.ok) throw new Error('Status HTTP ' + r.status);
                    return r.json();
                })
                .then(d => {
                    errorEl.style.display = 'none';
                    totalChunksEl.textContent = d.total_chunks || 0;
                    renderRows(d.items);
                    const hasProcessing = (d.items || []).some(it => it.state === 'processing');
                    liveEl.style.display = hasProcessing ? 'inline' : 'none';
                    if (hasProcessing) {
                        setTimeout(loadStatus, 4000);
                    }
                })
                .catch(err => {
                    errorEl.textContent = 'Tidak dapat membaca status Knowledge Base: ' + err.message;
                    errorEl.style.display = 'block';
                    tbody.innerHTML = '<tr><td colspan="4" style="padding:16px;text-align:center;color:#ef4444">Gagal memuat dokumen.</td></tr>';
                });
        }

        loadStatus();
    })();
</script>
<script>
    // File upload interaction
    const fileInput = document.getElementById('document');
    const uploadArea = document.getElementById('file-upload-area');
    const uploadContent = document.getElementById('file-upload-content');
    const fileSelected = document.getElementById('file-selected');
    const fileName = document.getElementById('file-name');
    const fileRemove = document.getElementById('file-remove');

    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            const file = this.files[0];
            fileName.textContent = file.name + ' (' + (file.size / 1024 / 1024).toFixed(1) + ' MB)';
            uploadContent.style.display = 'none';
            fileSelected.style.display = 'flex';
            uploadArea.classList.add('has-file');
        }
    });

    fileRemove.addEventListener('click', function() {
        fileInput.value = '';
        uploadContent.style.display = 'flex';
        fileSelected.style.display = 'none';
        uploadArea.classList.remove('has-file');
    });

    // Drag & drop
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', function() {
        this.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('drag-over');
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            fileInput.dispatchEvent(new Event('change'));
        }
    });

    // Form submit disable to prevent double upload
    const form = document.getElementById('knowledge-form');
    const btnSubmit = document.getElementById('btn-submit');
    const btnText = btnSubmit.querySelector('.btn-text');

    form.addEventListener('submit', function() {
        btnSubmit.disabled = true;
        btnSubmit.style.opacity = '0.7';
        btnText.textContent = 'Mengunggah...';
    });
</script>
@endsection
