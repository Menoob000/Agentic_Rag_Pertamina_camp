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

@endsection

@section('scripts')
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
