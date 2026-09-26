@extends('layouts.app')

@section('title', 'Buat Dokumen RKS')

@section('content')
<div class="page-header">
    <h1 class="page-title">Buat Dokumen RKS Baru</h1>
    <p class="page-desc">Isi formulir di bawah ini untuk menghasilkan dokumen Rencana Kerja dan Syarat-syarat secara otomatis menggunakan AI.</p>
</div>

<div class="card" id="rks-form-card">
    <form method="POST"
          action="{{ route('rks.generate') }}"
          enctype="multipart/form-data"
          id="rks-form"
          class="rks-form">
        @csrf

        {{-- Jenis Pekerjaan --}}
        <div class="form-group">
            <label for="jenis_pekerjaan" class="form-label">
                Jenis Pekerjaan <span class="required">*</span>
            </label>
            <input type="text"
                   id="jenis_pekerjaan"
                   name="jenis_pekerjaan"
                   class="form-input {{ $errors->has('jenis_pekerjaan') ? 'input-error' : '' }}"
                   value="{{ old('jenis_pekerjaan') }}"
                   placeholder="Contoh: Overhaul Tangki, Pengecatan Pipa, Pembangunan Gardu Listrik"
                   required>
            @error('jenis_pekerjaan')
                <span class="error-text">{{ $message }}</span>
            @enderror
            <p class="form-help">Masukkan kategori atau jenis pekerjaan tender yang akan dilaksanakan.</p>
        </div>

        {{-- Detail Pekerjaan --}}
        <div class="form-group">
            <label for="detail_pekerjaan" class="form-label">
                Detail Pekerjaan <span class="required">*</span>
            </label>
            <textarea id="detail_pekerjaan"
                      name="detail_pekerjaan"
                      class="form-input form-textarea {{ $errors->has('detail_pekerjaan') ? 'input-error' : '' }}"
                      rows="4"
                      placeholder="Contoh: Pekerjaan overhaul tangki timbun 15.000 KL termasuk penggantian roof plate, shell plate, dan sistem proteksi katodik di Terminal BBM Plumpang."
                      required>{{ old('detail_pekerjaan') }}</textarea>
            @error('detail_pekerjaan')
                <span class="error-text">{{ $message }}</span>
            @enderror
            <p class="form-help">Jelaskan secara rinci lingkup dan spesifikasi pekerjaan yang dibutuhkan.</p>
        </div>

        {{-- Lokasi --}}
        <div class="form-group">
            <label for="lokasi" class="form-label">Lokasi Pekerjaan</label>
            <input type="text"
                   id="lokasi"
                   name="lokasi"
                   class="form-input"
                   value="{{ old('lokasi') }}"
                   placeholder="Contoh: Terminal BBM Plumpang, Jakarta Utara">
            <p class="form-help">Lokasi pelaksanaan pekerjaan (opsional, namun disarankan untuk diisi).</p>
        </div>

        {{-- Upload File PDF --}}
        <div class="form-group">
            <label for="file" class="form-label">
                Dokumen Referensi (PDF BOQ) <span class="required">*</span>
            </label>
            <div class="file-upload-area" id="file-upload-area">
                <input type="file"
                       id="file"
                       name="file"
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
                    <p class="file-upload-hint">Format: PDF · Maksimal: 50MB</p>
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
            @error('file')
                <span class="error-text">{{ $message }}</span>
            @enderror
            <p class="form-help">Unggah file Bill of Quantities (BOQ) atau dokumen referensi proyek dalam format PDF.</p>
        </div>

        {{-- Submit Button --}}
        <div class="form-actions">
            <button type="submit" class="btn btn-primary btn-generate" id="btn-generate">
                <svg class="btn-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                </svg>
                <span class="btn-text">Generate Dokumen RKS</span>
            </button>
            <p class="form-help" style="margin-top: 12px; text-align: center;">
                ⏳ Proses generate membutuhkan waktu <strong>2 — 5 menit</strong> tergantung kompleksitas pekerjaan.
            </p>
        </div>
    </form>
</div>

{{-- Loading Overlay --}}
<div class="loading-overlay" id="loading-overlay" style="display:none">
    <div class="loading-card">
        <div class="loading-spinner"></div>
        <h3 class="loading-title">Sedang Memproses Dokumen RKS</h3>
        <p class="loading-text">AI sedang menganalisis dokumen dan menyusun draft RKS Anda...</p>
        <div class="loading-steps">
            <div class="loading-step active" id="step-1">
                <span class="step-number">1</span>
                <span class="step-text">Mengekstrak teks dari PDF</span>
            </div>
            <div class="loading-step" id="step-2">
                <span class="step-number">2</span>
                <span class="step-text">Menganalisis & meringkas konteks</span>
            </div>
            <div class="loading-step" id="step-3">
                <span class="step-number">3</span>
                <span class="step-text">Menyusun struktur dokumen RKS</span>
            </div>
            <div class="loading-step" id="step-4">
                <span class="step-number">4</span>
                <span class="step-text">Menghasilkan file Word (.docx)</span>
            </div>
        </div>
        <p class="loading-warn">Mohon jangan tutup halaman ini. Proses berlangsung 2 — 5 menit.</p>
    </div>
</div>
@endsection

@section('scripts')
<script>
    // File upload interaction
    const fileInput = document.getElementById('file');
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

    // Form submit — show loading overlay
    const form = document.getElementById('rks-form');
    const loadingOverlay = document.getElementById('loading-overlay');

    form.addEventListener('submit', function() {
        loadingOverlay.style.display = 'flex';

        // Animate loading steps
        const steps = document.querySelectorAll('.loading-step');
        let currentStep = 0;

        const interval = setInterval(function() {
            currentStep++;
            if (currentStep < steps.length) {
                steps[currentStep].classList.add('active');
            } else {
                clearInterval(interval);
            }
        }, 30000); // Switch step every 30 seconds
    });
</script>
@endsection
